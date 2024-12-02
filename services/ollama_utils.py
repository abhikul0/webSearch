import requests
import logging
from datetime import datetime

# datetime object containing current date and time
now = datetime.now()
# dd/mm/YY H:M:S
dateTime = now.strftime("%d/%m/%Y %H:%M:%S")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# OLLAMA API Configuration
OLLAMA_API_KEY = 'your_ollama_api_key'
OLLAMA_API_URL = 'http://localhost:11434'  # Update with your OLLAMA API URL


def fetch_models():
    headers = {'Authorization': f'Bearer {OLLAMA_API_KEY}'}
    try:
        logging.info("Fetching models from OLLAMA API")
        response = requests.get(f'{OLLAMA_API_URL}/api/tags', headers=headers)
        response.raise_for_status()
        models = response.json().get('models', [])
        #logging.info(f"Fetched models: {models}")
        return models
    except requests.RequestException as e:
        logging.error(f"Failed to fetch models: {e}")
        return []

def fetch_embeddings(text, model):
    headers = {'Authorization': f'Bearer {OLLAMA_API_KEY}', 'Content-Type': 'application/json'}
    payload = {
        "model": 'nomic-embed-text:latest',#model,
        "input": text,
        "stream": False
    }
    try:
        logging.info(f"Fetching embeddings for text: {text[:50]}... with model: {model}")
        response = requests.post(f'{OLLAMA_API_URL}/api/embed', headers=headers, json=payload)
        response.raise_for_status()
        embeddings = response.json().get('embeddings', [])
        if embeddings:
            embedding = embeddings[0]
            logging.info(f"Fetched embedding: {embedding[:10]}...")
            return embedding
        else:
            logging.error("No embeddings returned from OLLAMA API")
            return None
    except requests.RequestException as e:
        logging.error(f"Failed to fetch embeddings: {e}")
        return None

def summarize(text, model, query):
    headers = {'Authorization': f'Bearer {OLLAMA_API_KEY}', 'Content-Type': 'application/json'}
    payload = {
        "model": model,
        #"prompt": f"Summarize the following text:\n{text}",
        "prompt":f"""You are an AI model who is expert at searching the web and answering user's queries. You are also an expert at summarizing web pages or documents and searching for content in them.

    Generate a response that is informative and relevant to the user's query based on provided context (the context consits of search results containing a brief description of the content of that page).
    You must use this context to answer the user's query in the best way possible. Use an unbaised and journalistic tone in your response. Do not repeat the text.
    You must not tell the user to open any link or visit any website to get the answer. You must provide the answer in the response itself. If the user asks for links you can provide them.
    If the query contains some links and the user asks to answer from those links you will be provided the entire content of the page inside the \`context\` XML block. You can then use this content to answer the user's query.
    If the user asks to summarize content from some links, you will be provided the entire content of the page inside the \`context\` XML block. You can then use this content to summarize the text. The content provided inside the \`context\` block will be already summarized by another model so you just need to use that content to answer the user's query.
    Your responses should be medium to long in length be informative and relevant to the user's query. You can use markdowns to format your response. You should use bullet points to list the information. Make sure the answer is not short and is informative.
    Anything inside the following \`context\` HTML block provided below is for your knowledge returned by the search engine and is not shared by the user. You have to answer question on the basis of it and cite the relevant information from it but you do not have to
    talk about the context in your response.

    <context>
    {text}
    </context>

    If you think there's nothing relevant in the search results, you can say that 'Hmm, sorry I could not find any relevant information on this topic. Would you like me to search again or ask something else?'. You do not need to do this for summarization tasks.
    Anything between the \`context\` is retrieved from a search engine and is not a part of the conversation with the user. Keep in mind that the current date and time is {dateTime}. User's query: {query}.""",
        "options": {
          "num_ctx": 8192
        },
        "stream": False
    }
    try:
        logging.info(f"Summarizing text: {text[:50]}... with model: {model}")
        response = requests.post(f'{OLLAMA_API_URL}/api/generate', headers=headers, json=payload)
        response.raise_for_status()
        summary = response.json()['response']
        logging.info(f"Generated summary: {summary[:50]}...")
        return summary
    except requests.RequestException as e:
        logging.error(f"Failed to summarize text: {e}")
        return ""