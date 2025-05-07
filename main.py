import streamlit as st
import requests
import json 



STREAMLIT_API_ENDPOINT_URL = "http://127.0.0.1:8000/summarize/" 

def run_streamlit_app():
    st.set_page_config(layout="wide", page_title="Web Content Summarizer", page_icon="🌐")

    # Custom CSS for better look and feel
    st.markdown("""
        <style>
            .stApp {
                background-color: #f0f2f6;
            }
            .stTextInput > div > div > input {
                background-color: #ffffff;
            }
            .stButton > button {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 10px 20px;
            }
            .stButton > button:hover {
                background-color: #45a049;
                color: white;
            }
            .stAlert {
                border-radius: 5px;
            }
            h1, h2, h3 {
                color: #333;
            }
        </style>
    """, unsafe_allow_html=True)

    st.title("🌐 Web Content Summarizer Agent")
    st.markdown("""
    Welcome! This tool leverages an agentic framework to process web content. 
    Simply paste a URL into the text box below. The system will:
    1.  **Crawl** the specified webpage to extract its content (via the backend API).
    2.  **Summarize** the extracted text into a structured JSON format (via the backend API).
    
    You'll see the final JSON summary displayed below.
    """)
    st.markdown("---")

    url_input = st.text_input(
        "Enter URL to Crawl and Summarize:", 
        placeholder="e.g., https://docs.python.org/3/tutorial/index.html",
        help="Paste the full URL of the webpage you want to process."
    )

    if st.button("🚀 Process and Summarize URL"):
        if url_input:
            with st.spinner("🤖 Agent at work... Contacting backend for crawling and summarizing. This might take a few moments..."):
                try:
                    payload = {"url": url_input}
                    # Increased timeout for potentially long processing
                    response = requests.post(STREAMLIT_API_ENDPOINT_URL, json=payload, timeout=180) 

                    if response.status_code == 200:
                        result = response.json() 
                        if result.get("status") == "success":
                            st.balloons()
                            st.subheader(f"✅ Summary for: {result.get('crawled_url', url_input)}")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Original Markdown Length (chars)", result.get('original_markdown_length', 'N/A'))
                            with col2:
                                st.metric("Summarized Markdown Length (chars)", result.get('summarized_markdown_length', 'N/A'))
                            
                            st.info("Below is the structured JSON summary of the web content:")
                            st.json(result.get("data", {}))
                        else:
                            st.error(f"😥 API reported an issue: {result.get('message', 'Unknown error from API payload.')}")
                            if 'detail' in result: 
                                st.json(result['detail'])
                    else:
                        error_details_str = f"Status Code: {response.status_code}"
                        try:
                            api_error_data = response.json() 
                            error_detail = api_error_data.get("detail", "No specific error detail from API.")
                            
                            if isinstance(error_detail, dict): 
                                message = error_detail.get("message", "Unknown error.")
                                source = error_detail.get("source", "N/A")
                                error_details_str += f" - Message: {message} (Source: {source})"
                            elif isinstance(error_detail, str): 
                                error_details_str += f" - Detail: {error_detail}"
                            else: # Fallback
                                error_details_str += f" - Response: {response.text[:500]}"

                        except json.JSONDecodeError:
                            error_details_str += f" - Response: {response.text[:500]}" 
                        st.error(f"🚫 Failed to process URL. {error_details_str}")

                except requests.exceptions.Timeout:
                    st.error(f"⏳ Network Error: The request to the backend API at `{STREAMLIT_API_ENDPOINT_URL}` timed out. The server might be busy, the URL could be very slow to process, or the timeout is too short.")
                except requests.exceptions.ConnectionError:
                    st.error(f"🔌 Network Error: Could not connect to the backend API at `{STREAMLIT_API_ENDPOINT_URL}`. Please ensure the FastAPI server (app.py) is running and accessible.")
                except requests.exceptions.RequestException as e:
                    st.error(f"📡 Network or API Error: An unexpected error occurred while communicating with the backend. Details: {e}")
                except Exception as e: 
                    st.error(f"🤯 An unexpected application error occurred in the UI: {e}")
                    st.exception(e) 
        else:
            st.warning("Please enter a URL to process.", icon="⚠️")

    st.markdown("---")
    st.markdown("<p style='text-align: center;'>Powered by an Agentic Framework with FastAPI & Streamlit</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    run_streamlit_app()