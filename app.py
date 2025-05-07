import asyncio
import json 
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from crawler import WebCrawler
from summarizer import ContentSummarizer 

async def process_url_and_summarize(target_url: str):
    """
    Crawls a URL and generates a structured JSON summary.
    Returns a dictionary with status and data/error message.
    """
    crawler = WebCrawler(max_depth=0, max_pages=1, verbose=False)
    
    crawl_results = []
    try:
        if not target_url or not target_url.strip():
            return {"status": "error", "source": "input_validation", "message": "Target URL cannot be empty."}
        crawl_results = await crawler.crawl(target_url)
    except Exception as e:
        print(f"Error during crawling {target_url}: {e}")
        return {"status": "error", "source": "crawler", "message": f"Crawling failed for {target_url}. Error: {str(e)}"}

    if not crawl_results:
        return {"status": "error", "source": "crawler", "message": f"No content retrieved from crawling {target_url}. The URL might be invalid, inaccessible, or have no scrapable content."}

    page_to_summarize = crawl_results[0]

    if not (hasattr(page_to_summarize, 'markdown') and \
            hasattr(page_to_summarize.markdown, 'raw_markdown') and \
            page_to_summarize.markdown.raw_markdown and \
            page_to_summarize.markdown.raw_markdown.strip()): # Check if markdown is not just whitespace
        return {"status": "error", "source": "crawler", "message": "Crawled page has no meaningful markdown content to summarize."}
        
    markdown_text = page_to_summarize.markdown.raw_markdown
    page_url = page_to_summarize.url # Use the actual URL from the crawl result
    
    # Summarize the content
    summarizer = ContentSummarizer() 

    if not summarizer.api_key_configured:
        return {"status": "error", "source": "summarizer_config", "message": "Summarizer not configured. Please check GEMINI_KEY in configs.py."}

    max_chars_for_api_call = 32000  
    if len(markdown_text) > max_chars_for_api_call:

        print(f"Warning (API): Markdown content from {page_url} is long ({len(markdown_text)} chars). Truncating to {max_chars_for_api_call} characters for summary API call.")
        markdown_text_for_summary = markdown_text[:max_chars_for_api_call]
    else:
        markdown_text_for_summary = markdown_text
    
    json_summary = None
    try:
        json_summary = await summarizer.generate_json_summary(markdown_text_for_summary, page_url)
    except Exception as e:

        print(f"Error during summary generation for {page_url}: {e}")
        return {"status": "error", "source": "summarizer_generation", "message": f"Summary generation failed. Error: {str(e)}"}

    if json_summary is not None:
        return {
            "status": "success",
            "data": json_summary,
            "crawled_url": page_url,
            "original_markdown_length": len(markdown_text),
            "summarized_markdown_length": len(markdown_text_for_summary)
        }
    else:
        # Summarizer's generate_json_summary prints detailed errors to server logs.
        return {"status": "error", "source": "summarizer_output", "message": "Failed to generate or parse JSON summary. Check server logs for more details from the Summarizer."}

# FastAPI App Definition
app = FastAPI(
    title="Web Content Summarizer API",
    description="API to crawl a webpage and generate a structured JSON summary.",
    version="1.0.0"
)

class URLRequest(BaseModel):
    url: str

@app.post("/summarize/")
async def api_summarize_url(request: URLRequest):
    """
    API endpoint to crawl a URL and return a structured JSON summary.
    """
    target_url = request.url
    if not target_url:
        raise HTTPException(status_code=400, detail="URL must be provided.")
    
    # validate URL 
    if not (target_url.startswith("http://") or target_url.startswith("https://")):
        raise HTTPException(status_code=400, detail="Invalid URL format. Must start with http:// or https://")

    print(f"FastAPI: Received request to summarize URL: {target_url}") # Server log
    result = await process_url_and_summarize(target_url)
    
    if result["status"] == "success":
        return result
    else:
        print(f"FastAPI: Error processing {target_url}: {result.get('message', 'Unknown error')}")
        error_detail_dict = {
            "message": result.get('message', 'Unknown error'),
            "source": result.get('source', 'unknown_backend_source')
        }
        if result.get("source") == "input_validation" or \
           (result.get("source") == "crawler" and "No content" in result.get("message", "")):
            status_code = 400 # Bad request (e.g. invalid URL, no content)
        elif result.get("source") == "summarizer_config":
            status_code = 503 # Service unavailable (config issue)
        else:
            status_code = 500 # Internal server error for other cases
        raise HTTPException(status_code=status_code, detail=error_detail_dict)