### Code Source
### https://github.com/coleam00/ottomator-agents/blob/main/crawl4AI-agent/crawl4AI-examples/3-crawl_docs_FAST.py

import os
import sys
import psutil
import asyncio
import requests
from xml.etree import ElementTree
from urllib.parse import urlparse
import re

__location__ = os.path.dirname(os.path.abspath(__file__))
__output__ = os.path.join(__location__, "output")
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from typing import List
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

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
    
    # If path is empty, use 'index'
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
        base_folder (str): The base folder name (e.g., 'docs.agpt.co')
    """
    try:
        # Create the base folder if it doesn't exist
        if not os.path.exists(base_folder):
            os.makedirs(base_folder)
        
        # Generate filename from URL
        filename = create_filename_from_url(url)
        filepath = os.path.join(base_folder, filename)
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

async def crawl_parallel(urls: List[str], max_concurrent: int = 3, sitemap_url: str = ""):
    print("\n=== Parallel Crawling with Browser Reuse + Memory Check ===")
    
    # Extract folder name from sitemap URL
    base_folder = extract_domain_from_sitemap_url(sitemap_url) if sitemap_url else "crawled_content"
    print(f"Saving content to folder: {base_folder}")
    peak_memory = 0
    process = psutil.Process(os.getpid())

    def log_memory(prefix: str = ""):
        nonlocal peak_memory
        current_mem = process.memory_info().rss
        if current_mem > peak_memory:
            peak_memory = current_mem
        print(f"{prefix} Current Memory: {current_mem // (1024 * 1024)} MB, Peak: {peak_memory // (1024 * 1024)} MB")

    # Minimal browser config
    browser_config = BrowserConfig(
        headless=False,
        verbose=False, 
        extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"],
    )
    crawl_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)

    # Create the crawler instance
    crawler = AsyncWebCrawler(config=browser_config)
    await crawler.start()

    try:
        # We'll chunk the URLs in batches of 'max_concurrent'
        success_count = 0
        fail_count = 0
        for i in range(0, len(urls), max_concurrent):
            batch = urls[i : i + max_concurrent]
            tasks = []

            for j, url in enumerate(batch):
                session_id = f"parallel_session_{i + j}"
                task = crawler.arun(url=url, config=crawl_config, session_id=session_id)
                tasks.append(task)

            # Check memory usage prior to launching tasks
            log_memory(prefix=f"Before batch {i//max_concurrent + 1}: ")
            results = await asyncio.gather(*tasks, return_exceptions=True)
            log_memory(prefix=f"After batch {i//max_concurrent + 1}: ")
            for url, result in zip(batch, results):
                if isinstance(result, Exception):
                    print(f"Error crawling {url}: {result}")
                    fail_count += 1
                elif result.success:
                    success_count += 1
                    save_content_to_file(result.markdown.raw_markdown, url, base_folder)
                else:
                    fail_count += 1

        print(f"\nSummary:")
        print(f"  - Successfully crawled: {success_count}")
        print(f"  - Failed: {fail_count}")

    finally:
        print("\nClosing crawler...")
        await crawler.close()
        log_memory(prefix="Final: ")
        print(f"\nPeak memory usage (MB): {peak_memory // (1024 * 1024)}")

def get_pydantic_ai_docs_urls():
    """
    Fetches all URLs from the Pydantic AI documentation.
    Uses the sitemap (https://ai.pydantic.dev/sitemap.xml) to get these URLs.
    
    Returns:
        List[str]: List of URLs
    """            
    sitemap_url = "https://docs.flowiseai.com/sitemap-pages.xml"
    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()
        root = ElementTree.fromstring(response.content)
        
        # Extract all URLs from the sitemap
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = [loc.text for loc in root.findall('.//ns:loc', namespace)]
        
        return urls
    except Exception as e:
        print(f"Error fetching sitemap: {e}")
        return []        

async def main():
    sitemap_url = "https://docs.flowiseai.com/sitemap-pages.xml"
    urls = get_pydantic_ai_docs_urls()
    if urls:
        print(f"Found {len(urls)} URLs to crawl")
        await crawl_parallel(urls, max_concurrent=50, sitemap_url=sitemap_url)
    else:
        print("No URLs found to crawl")    

if __name__ == "__main__":
    asyncio.run(main())