from flask import jsonify
import requests
import json
from bs4 import BeautifulSoup
import faiss
import numpy as np
import logging
import random
import concurrent.futures
from .ollama_utils import fetch_embeddings, summarize

from sentence_transformers import SentenceTransformer, util

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the SentenceTransformer model
relevance_model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize Faiss index
dimension = 768#2048  # Example dimension, adjust based on your embeddings
faiss_index = faiss.IndexFlatL2(dimension)

# SearxNG API Configuration
SEARXNG_API_URL = 'http://localhost:4000/search'

# Hardcoded limit for search results
SEARCH_LIMIT = 5

# List of user agents to rotate
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1"
]

def relevancy_extract(contents, query):
    # Score sentences for relevance and select top sentences
    relevant_contents = []
    seen_sentences = set()  # To track unique sentences

    for content in contents:
        # Split content into sentences
        sentences = content.split('. ')
        # Encode query and sentences
        query_embedding = relevance_model.encode(query, convert_to_tensor=True)
        sentence_embeddings = relevance_model.encode(sentences, convert_to_tensor=True)
        
        # Compute cosine-similarities
        cos_scores = util.cos_sim(query_embedding, sentence_embeddings)[0]
        
        # Sort sentences by score
        ranked_sentences = sorted(zip(cos_scores, sentences), reverse=True)
        
        # Select top sentences (e.g., top 5) and ensure uniqueness
        top_sentences = []
        for score, sentence in ranked_sentences[:5]:
            if sentence.strip() and sentence not in seen_sentences:
                seen_sentences.add(sentence)
                top_sentences.append(sentence)
        
        relevant_contents.append(' '.join(top_sentences))

    return relevant_contents    

def fetch_webpage_content(url):
    headers = {'User-Agent': random.choice(USER_AGENTS)}
    try:
        logging.info(f"Fetching webpage content from URL: {url}")
        response = requests.get(url, headers=headers, timeout=10)  # Set timeout to 10 seconds
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract main content
        content = ""
        # Try to extract content from common tags
        for tag in ['article', 'section', 'main']:
            elements = soup.find_all(tag)
            if elements:
                for element in elements:
                    content += element.get_text(separator='\n', strip=True) + '\n'
        
        # If no main content found, fallback to paragraphs
        if not content.strip():
            paragraphs = soup.find_all('p')
            content = '\n'.join([para.get_text(strip=True) for para in paragraphs])
        
        logging.info(f"Fetched content from URL: {url}")
        return content.strip()
    except requests.Timeout:
        logging.error(f"Request timed out for URL: {url}")
    except requests.RequestException as e:
        logging.error(f"Failed to fetch {url}: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred while fetching {url}: {e}")
    return ""

def fetch_contents_concurrently(urls,quickSearch_en=False):
    contents = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(fetch_webpage_content, url): url for url in urls}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                content = future.result()
                if content:
                    # Split content into words and truncate to X number of words
                    if quickSearch_en:
                        words = content.split()
                        truncated_content = ' '.join(words[:150])
                        contents.append(truncated_content)
                    else:
                        contents.append(content)
            except Exception as e:
                logging.error(f"Error fetching content from {url}: {e}")
    return contents

def process_search(query, model, quickSearch_en=False):
    # Fetch search results from SearxNG
    params = {
        'q': query,
        'format': 'json',
        'categories': 'general',
        'safesearch': 1,
        'lang': 'en'
    }
    try:
        logging.info(f"Fetching search results for query: {query[:50]}...")
        search_response = requests.get(SEARXNG_API_URL, params=params, timeout=10)  # Set timeout to 10 seconds
        search_response.raise_for_status()
        search_results = search_response.json().get('results', [])[:SEARCH_LIMIT]  # Limit results here
        logging.info(f"Fetched search results: {search_results}")
    except requests.Timeout:
        logging.error(f"Request timed out for SearxNG search")
        search_results = []
    except requests.RequestException as e:
        logging.error(f"Failed to fetch search results: {e}")
        search_results = []
    except Exception as e:
        logging.error(f"An unexpected error occurred while fetching search results: {e}")
        search_results = []

    # Extract unique URLs and fetch webpages concurrently
    urls = [result['url'] for result in search_results]
    unique_urls = list(set(urls))  # Ensure unique URLs
    contents = fetch_contents_concurrently(unique_urls,quickSearch_en)

    # Filter out empty contents and ensure unique contents
    unique_contents = list(set(contents))  # Ensure unique contents
    unique_contents = [content for content in unique_contents if content.strip()]  # Filter out empty contents

    # Log unique contents for debugging
    logging.debug(f"Unique contents: {unique_contents}")

    # Convert contents to embeddings and store in Faiss
    if quickSearch_en:
        # Use the truncated contents directly
        scored_contents = unique_contents
    else:
        # Use relevancy_extract for non-quick search
        scored_contents = relevancy_extract(unique_contents, query)
    logging.debug(f"Scored contents: {scored_contents}")

    # Ensure unique more details! For now, let's log the unique sentences in scored_contents
    unique_scored_contents = []
    seen_sentences = set()

    for content in scored_contents:
        sentences = content.split('. ')
        unique_sentences = [sentence for sentence in sentences if sentence.strip() and sentence not in seen_sentences]
        seen_sentences.update(unique_sentences)
        unique_scored_contents.append(' '.join(unique_sentences))

    logging.debug(f"Unique scored contents: {unique_scored_contents}")

    embeddings = [fetch_embeddings(content, model) for content in unique_scored_contents if content]
    valid_embeddings = [emb for emb in embeddings if emb is not None and len(emb) == dimension]

    if valid_embeddings:
        embeddings_matrix = np.array(valid_embeddings).astype('float32')
        faiss_index.add(embeddings_matrix)  # Use the correct variable name
        logging.info(f"Added {len(valid_embeddings)} embeddings to Faiss index")
    else:
        logging.warning("No valid embeddings to add to Faiss index")

    # Convert query to embedding and search Faiss
    query_embedding = fetch_embeddings(query, model)
    if query_embedding and len(query_embedding) == dimension:
        query_embedding = np.array([query_embedding]).astype('float32')
        D, I = faiss_index.search(query_embedding, 3)  # len(valid_embeddings))  # Use the correct variable name

        # Retrieve relevant data and summarize
        relevant_contents = [unique_scored_contents[i] for i in I[0]]
        logging.debug(f"Retrieved relevant contents: {relevant_contents}")

        # Ensure unique relevant contents
        unique_relevant_contents = list(set(relevant_contents))
        logging.debug(f"Unique relevant contents: {unique_relevant_contents}")

        summary = summarize('\n'.join(unique_relevant_contents), model, query)
        logging.info(f"Generated summary: {summary[:50]}...")
    else:
        logging.error("Invalid query embedding")
        summary = "Failed to generate embeddings for the query."

    # Reset Faiss index to ensure statelessness
    faiss_index.reset()

    return {
        'summary': summary,
        'search_results': search_results
    }
