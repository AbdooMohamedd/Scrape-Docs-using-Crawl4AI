### Code Source
### https://github.com/coleam00/ottomator-agents/blob/main/crawl4AI-agent-v2/crawl4AI-examples/3-crawl_sitemap_in_parallel.py

"""
3-crawl_docs_FAST.py
--------------------
Batch-crawls a list of documentation URLs in parallel using Crawl4AI's arun_many and a memory-adaptive dispatcher.
Tracks memory usage, prints a summary of successes/failures, and is suitable for large-scale doc scraping jobs.
Usage: Call main() or run as a script. Adjust max_concurrent for parallelism.
"""
import os
import sys
import psutil
import asyncio
import requests
from typing import List
from xml.etree import ElementTree
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, MemoryAdaptiveDispatcher
from urllib.parse import urlparse
import re

def create_filename_from_url(url: str) -> str:
    """
    Creates a filename from URL path after .com/
    
    Args:
        url (str): The full URL
        
    Returns:
        str: Filename for the content
    """
    parsed = urlparse(url)
    path = parsed.path
    
    # Remove leading slash and replace remaining slashes with underscores
    if path.startswith('/'):
        path = path[1:]
    
    if not path or path == '':
        filename = 'index'
    else:
        filename = path.replace('/', '_').replace('\\', '_')
        filename = re.sub(r'[^\w\-_.]', '_', filename)
    if not filename.endswith('.md'):
        filename += '.md'
    
    return filename

def save_content_to_file(content: str, url: str, base_folder: str):
    """
    Saves the scraped content to a file in the specified folder structure.
    
    Args:
        content (str): The markdown content to save
        url (str): The original URL
        base_folder (str): The base folder name (e.g., 'docs.crawl4ai.com')
    """
    try:
        # Create the base folder if it doesn't exist
        if not os.path.exists(base_folder):
            os.makedirs(base_folder)
        
        # Generate filename from URL
        filename = create_filename_from_url(url)
        filepath = os.path.join(base_folder, filename)
        
        # Save the content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Saved content to: {filepath}")
        
    except Exception as e:
        print(f"Error saving content for {url}: {e}")

def extract_domain_from_sitemap_url(sitemap_url: str) -> str:
    """
    Extracts the domain name from the sitemap URL to use as folder name.
    
    Args:
        sitemap_url (str): The sitemap URL
        
    Returns:
        str: Domain name to use as folder name
    """
    parsed = urlparse(sitemap_url)
    domain = parsed.netloc
    return domain

async def crawl_parallel(urls: List[str], max_concurrent: int = 10, sitemap_url: str = ""):
    print("\n=== Parallel Crawling with arun_many + Dispatcher ===")
    
    base_folder = extract_domain_from_sitemap_url(sitemap_url) if sitemap_url else "crawled_content"
    print(f"Saving content to folder: {base_folder}")

    # Track the peak memory usage for observability
    peak_memory = 0
    process = psutil.Process(os.getpid())
    def log_memory(prefix: str = ""):
        nonlocal peak_memory
        current_mem = process.memory_info().rss  
        if current_mem > peak_memory:
            peak_memory = current_mem
        print(f"{prefix} Current Memory: {current_mem // (1024 * 1024)} MB, Peak: {peak_memory // (1024 * 1024)} MB")

    browser_config = BrowserConfig(
        headless=True,
        verbose=False,
        extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"],
    )
    # Set up crawl config and dispatcher for batch crawling
    crawl_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, stream=False)
    dispatcher = MemoryAdaptiveDispatcher(
        memory_threshold_percent=70.0,  # Don't exceed 70% memory usage
        check_interval=1.0,             # Check memory every second
        max_session_permit=max_concurrent  # Max parallel browser sessions
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        log_memory("Before crawl: ")
        results = await crawler.arun_many(
            urls=urls,
            config=crawl_config,
            dispatcher=dispatcher
        )
        success_count = 0
        fail_count = 0
        for result in results:
            if result.success:
                success_count += 1
                # Save the content to file
                save_content_to_file(result.markdown.raw_markdown, result.url, base_folder)
            else:
                print(f"Error crawling {result.url}: {result.error_message}")
                fail_count += 1

        print(f"\nSummary:")
        print(f"  - Successfully crawled: {success_count}")
        print(f"  - Failed: {fail_count}")
        log_memory("After crawl: ")
        print(f"\nPeak memory usage (MB): {peak_memory // (1024 * 1024)}")

def get_pydantic_ai_docs_urls():
    """
    Fetches all URLs from the Pydantic AI documentation.
    Uses the sitemap (https://ai.pydantic.dev/sitemap.xml) to get these URLs.
    
    Returns:
        List[str]: List of URLs
    """            
    sitemap_url = "https://docs.crewai.com/sitemap.xml"
    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()
        
        # Parse the XML
        root = ElementTree.fromstring(response.content)
        
        # Extract all URLs from the sitemap
        # The namespace is usually defined in the root element
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = [loc.text for loc in root.findall('.//ns:loc', namespace)]
        
        return urls
    except Exception as e:
        print(f"Error fetching sitemap: {e}")
        return []        

async def main():
    sitemap_url = "https://docs.crawl4ai.com/sitemap.xml"
    urls = get_pydantic_ai_docs_urls()
    if urls:
        print(f"Found {len(urls)} URLs to crawl")
        await crawl_parallel(urls, max_concurrent=10, sitemap_url=sitemap_url)
    else:
        print("No URLs found to crawl")    

if __name__ == "__main__":
    asyncio.run(main())