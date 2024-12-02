 # WebSearch Application

 ## Overview
 The WebSearch application is a powerful search tool that leverages the Ollama API to provide summarized search results and detailed search results from the web. It uses Flask as the backend framework and provides a simple and intuitive user interface built with HTML, CSS, and JavaScript.

 ## Features
 - Search Functionality: Users can enter a query and select a model to receive summarized search results and detailed search results from the web.
 - Responsive Design: The application is designed to be responsive and works well on various devices.
 - Progressive Web App (PWA): The application can be installed as a PWA, providing a seamless offline experience.

 ## Codebase Organization
```
webSearch/
├── app.py
├── services/
│   ├── ollama_utils.py
│   └── search.py
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── service-worker.js
│   └── images/
│       └── icons/
│           └── logo.png
├── templates/
│   └── index.html
├── manifest.json
└── README.md
```

## File Descriptions
- app.py: Main entry point for the Flask application, defining routes and handling requests.
- services/ollama_utils.py: Contains functions for interacting with the OLLAMA API, including fetching models and embeddings.
- services/search.py: Handles search operations, including fetching web content, processing it, and generating summaries.
- static/css/style.css: Stylesheets for the frontend, ensuring a consistent look and feel.
- static/js/service-worker.js: Manages caching strategies for offline support.
- templates/index.html: Main HTML template, defining the structure and layout of the application.
- manifest.json: Configuration file for PWA features, including app metadata and icons.

 ## Prerequisites
 Before running the application, ensure you have the following installed:
 - Python 3.8 or higher
 - pip (Python package manager)
 - waitress (WSGI server for production)
 - requests (HTTP library for making API calls)
 - beautifulsoup4 (HTML parser for web scraping)
 - faiss (Efficient similarity search and clustering of dense vectors)
 - numpy (Numerical computing library)
 - sentence-transformers (Library for sentence embeddings)

 ## Installation
 ### Clone the Repository:
 ```bash
  git clone https://github.com/yourusername/websearch-app.git
  cd websearch-app
 ```

 ### Install Dependencies:
 ```bash 
 pip install -r requirements.txt
 ```
 Alternatively, you can manually install the required packages:
 ```bash 
 pip install flask requests beautifulsoup4 faiss-cpu numpy sentence-transformers waitress
 ```

### Set Up Environment Variables: Create a .env file in the root directory and add your Ollama API key:
 ``OLLAMA_API_KEY=your_ollama_api_key``

 ## Configuration
 - Ollama API Key: Replace your_ollama_api_key in the .env file with your actual Ollama API key.
 - SearxNG API URL: Ensure the SEARXNG_API_URL in search.py points to your SearxNG instance. By default, it is set to http://localhost:4000/search.
  ``SEARXNG_API_URL = 'http://localhost:4000/search' ``

 ## Running the Application
 ### Start the Flask Application:
 ```bash
python app.py
 ```
 The application will be accessible at http://localhost:5000.

 ### Access the Application: Open your web browser and navigate to http://localhost:5000.

 ## Usage
 ### Search:
 - Enter a query in the search input field.
 - Select a model from the dropdown menu.
 - Click the "Search" button.
 - quickSearch toggle provides fast results without any processing through sentence-transformers.

 ### View Results:
 - The application will display a summary of the search results.
 - Click on a search result to open the URL in a new tab.

 ### Reset:
 - Click the "Reset" button to clear the search query and results.

 ## Frontend
 The frontend is built using HTML, CSS, and JavaScript. It provides a simple and intuitive user interface.
 - HTML (index.html): Structure of the web page.
 - CSS (style.css): Styling for the web page.
 - JavaScript: Handles search functionality and updates the UI in real-time.

 ## Backend
 The backend is built using Flask and handles the logic for processing search queries and interacting with the Ollama API.
 - Flask (app.py): Main application file.
 - Ollama Utilities (services/ollama_utils.py): Functions to interact with the Ollama API.
 - Search Logic (services/search.py): Functions to fetch search results, process content, and generate summaries.

 ## Progressive Web App (PWA)
 The application is configured as a PWA, allowing it to be installed on mobile devices and accessed offline.
 - Service Worker (static/js/service-worker.js): Handles caching and offline capabilities.
 - Manifest (manifest.json): Provides metadata for the PWA.

 ## Logging
 The application uses Python's logging module to log information, warnings, and errors. Logs are printed to the console.

 ## Contributing
 Contributions are welcome! Please follow these steps to contribute:
 - Fork the repository.
 - Create a new branch for your feature or bug fix.
 - Make your changes and commit them.
 - Push your changes to your fork.
 - Create a pull request.

 ## License
 This project is licensed under the MIT License. See the LICENSE file for details.
