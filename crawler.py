import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy

class WebCrawler:
    """
    A simple web crawler that performs a Breadth-First Search (BFS) on a given webpage URL.
    The URL to crawl is passed to the 'crawl' method.
    """
    def __init__(self, max_depth: int = 1, 
                 include_external: bool = False, 
                 max_pages: int = 5, 
                 verbose: bool = True):
        """
        Initializes the SimpleWebCrawler with crawl configuration.
        """
        self.max_depth = max_depth
        self.include_external = include_external
        self.max_pages = max_pages
        self.verbose = verbose
        # Removed the print from __init__ for cleaner library use

    async def crawl(self, start_url: str):
        """
        Starts the web crawling process for the given start_url.
        """
        if not start_url or not start_url.strip():
            print("Error (Crawler): A valid start_url must be provided.")
            return []
        
        config = CrawlerRunConfig(
            deep_crawl_strategy=BFSDeepCrawlStrategy(
                max_depth=self.max_depth,
                include_external=self.include_external,
                max_pages=self.max_pages,
            ),
            scraping_strategy=LXMLWebScrapingStrategy(),
            verbose=self.verbose
        )
        results = []
        try:
            async with AsyncWebCrawler() as crawler_context:
                results = await crawler_context.arun(start_url, config=config)
        except Exception as e:
            print(f"Error (Crawler): An error occurred during crawling {start_url}: {e}")
        
        return results