# AI Web Content Modularizer

> A Python project that crawls a webpage, extracts its content, and uses Google's Gemini AI to identify and structure its functional "modules" and "submodules" into a JSON format.

This system provides a FastAPI backend API for the core logic and a Streamlit web interface for easy user interaction.

---

## Features

*   **Single-Page Web Crawling:** Extracts content from a specified URL.
*   **AI-Powered Structuring:** Leverages Google's Gemini model (`gemini-2.0-flash-001`) to understand and restructure web content.
*   **Modular JSON Output:** Identifies "modules" (major functional components) and "submodules" (specific features/capabilities) with descriptions.
*   **FastAPI Backend:** Exposes the functionality via a REST API endpoint.
*   **Streamlit Web UI:** Offers a user-friendly interface for URL submission and result viewing.
*   **Configuration:** Requires a Google Gemini API Key.
*   **Error Handling:** Implements basic error handling for crawling, API calls, and content processing.

---

## How It Works

1.  **User Input:** A URL is provided via the Streamlit UI or directly to the FastAPI endpoint.
2.  **Crawl (`crawl.py`):** The `WebCrawler` fetches content from the URL using `crawl4ai`.
3.  **Summarize & Structure (`summarize.py`):** The `ContentSummarizer` sends the extracted markdown to the Gemini API with a specific prompt.
4.  **AI Processing:** Gemini analyzes the content and returns a structured JSON identifying modules and submodules.
5.  **API Response (`app.py`):** The FastAPI backend formats the AI's response and returns it.
6.  **Display (`main.py`):** The Streamlit UI presents the JSON output to the user.

**Flow:**
`User -> Streamlit UI -> FastAPI Backend -> Web Crawler -> Gemini AI -> FastAPI Backend -> Streamlit UI -> User`

---

## Tech Stack

*   **Backend:** Python, FastAPI, Uvicorn
*   **Frontend:** Streamlit
*   **Web Crawling:** `crawl4ai`
*   **AI Integration:** `google-generativeai` (for Google Gemini)
*   **HTTP Requests:** `requests` (in Streamlit app)
*   **Async Operations:** `asyncio`

---

## Project Structure

├── app.py # FastAPI backend application
├── crawl.py # Web crawling logic
├── summarize.py # Content summarization and AI interaction
├── main.py # Streamlit frontend application
├── configs.py.example # Example for API key configuration
├── requirements.txt # Python dependencies (you'll need to create this)
└── README.md # This file


---

## Prerequisites

*   Python 3.10.0+
*   A Google Gemini API Key. You can obtain one from [Google AI Studio](https://aistudio.google.com/app/apikey).

---

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd <repository-name>
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows
    # venv\Scripts\activate
    # On macOS/Linux
    # source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure API Key:**
    *   Add your Google Gemini API Key to `configs.py`:
        ```python
        # configs.py
        GEMINI_KEY = "YOUR_GEMINI_API_KEY_HERE"
        ```

---

## Running the Application

You'll need two terminal windows: one for the FastAPI backend and one for the Streamlit frontend.

1.  **Start the FastAPI Backend:**
    Navigate to the project root directory in your terminal and run:
    ```bash
    uvicorn app:app --reload
    ```
    The backend API will typically be available at `http://127.0.0.1:8000`.

2.  **Start the Streamlit Frontend:**
    Open a new terminal, navigate to the project root directory, and run:
    ```bash
    streamlit run main.py
    ```
    The Streamlit UI will typically be available at `http://localhost:8501`.

---

## Usage

1.  Open the Streamlit application URL in your web browser.
2.  Enter the full URL of the webpage you want to process (e.g., a documentation page).
3.  Click the "🚀 Process and Summarize URL" button.
4.  Wait for the system to crawl the page and generate the summary.
5.  The structured JSON output identifying modules and submodules will be displayed.

---

## API Endpoint

The backend exposes the following endpoint:

*   **URL:** `/summarize/`
*   **Method:** `POST`
*   **Request Body (JSON):**
    ```json
    {
        "url": "https://example.com/docs/feature"
    }
    ```
*   **Success Response (200 OK):**
    ```json
    {
        "status": "success",
        "data": [
            {
                "module": "Module_Name",
                "Description": "Detailed description of the module...",
                "Submodules": {
                    "Submodule_Name_1": "Detailed description of submodule 1...",
                    "Submodule_Name_2": "Detailed description of submodule 2..."
                }
            }
            // ... more modules
        ],
        "crawled_url": "https://example.com/docs/feature",
        "original_markdown_length": 15000,
        "summarized_markdown_length": 15000
    }
    ```
*   **Error Responses:**
    *   `400 Bad Request`: Invalid input (e.g., missing URL, invalid URL format, no content found).
    *   `500 Internal Server Error`: Issues with crawling, AI summarization, or other backend processes.
    *   `503 Service Unavailable`: Summarizer not configured (e.g., missing API key).
    Error responses include a JSON body with `detail` containing `message` and `source`.

---