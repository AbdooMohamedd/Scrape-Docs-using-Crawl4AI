### Code Source
### https://github.com/coleam00/ottomator-agents/blob/main/crawl4AI-agent-v2/crawl4AI-examples/5-crawl_site_recursively.py

"""
5-crawl_recursive_internal_links.py
----------------------------------
Recursively crawls a site starting from a root URL, using Crawl4AI's arun_many and a memory-adaptive dispatcher.
At each depth, all internal links are discovered and crawled in parallel, up to a specified depth, with deduplication.
Usage: Set the start URL and max_depth in main(), then run as a script.
"""
import asyncio
from urllib.parse import urldefrag, urlparse
import os
import re
from crawl4ai import (
    AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode,
    MemoryAdaptiveDispatcher
)

def create_filename_from_url(url: str) -> str:
    """
    Creates a filename from URL path after the domain
    
    Args:
        url (str): The full URL
        
    Returns:
        str: Filename for the content
    """
    parsed = urlparse(url)
    path = parsed.path
    
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

def save_content_to_file(content: str, url: str, base_folder: str, depth: int):
    """
    Saves the scraped content to a file in the specified folder structure.
    
    Args:
        content (str): The markdown content to save
        url (str): The original URL
        base_folder (str): The base folder name (e.g., 'www.youxel.com')
        depth (int): The crawling depth for organizing files (not used anymore)
    """
    try:
        # Create the base folder if it doesn't exist
        if not os.path.exists(base_folder):
            os.makedirs(base_folder)
        
        filename = create_filename_from_url(url)
        filepath = os.path.join(base_folder, filename)
        
        if os.path.exists(filepath):
            print(f"File already exists, skipping: {filepath}")
            return
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Saved content to: {filepath}")
        
    except Exception as e:
        print(f"Error saving content for {url}: {e}")

def extract_domain_from_url(url: str) -> str:
    """
    Extracts the domain name from the URL to use as folder name.
    
    Args:
        url (str): The URL
        
    Returns:
        str: Domain name to use as folder name
    """
    parsed = urlparse(url)
    domain = parsed.netloc
    return domain

async def crawl_recursive_batch(start_urls, max_depth=3, max_concurrent=10):
    # Extract base folder name from the first start URL
    base_folder = extract_domain_from_url(start_urls[0]) if start_urls else "crawled_content"
    print(f"Saving content to folder: {base_folder}")
    
    browser_config = BrowserConfig(headless=True, verbose=False)
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        stream=False
    )
    dispatcher = MemoryAdaptiveDispatcher(
        memory_threshold_percent=70.0,      # Don't exceed 70% memory usage
        check_interval=1.0,                 # Check memory every second
        max_session_permit=max_concurrent   # Max parallel browser sessions
    )

    # Track visited URLs to prevent revisiting and infinite loops (ignoring fragments)
    visited = set()
    def normalize_url(url):
        return urldefrag(url)[0]
    current_urls = set([normalize_url(u) for u in start_urls])

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for depth in range(max_depth):
            print(f"\n=== Crawling Depth {depth+1} ===")
            urls_to_crawl = [normalize_url(url) for url in current_urls if normalize_url(url) not in visited]

            if not urls_to_crawl:
                break

            # Batch-crawl all URLs at this depth in parallel
            results = await crawler.arun_many(
                urls=urls_to_crawl,
                config=run_config,
                dispatcher=dispatcher
            )

            next_level_urls = set()

            for result in results:
                norm_url = normalize_url(result.url)
                visited.add(norm_url)  
                if result.success:
                    print(f"[OK] {result.url} | Markdown: {len(result.markdown) if result.markdown else 0} chars")
                    # Save the content to file
                    save_content_to_file(result.markdown.raw_markdown, result.url, base_folder, depth+1)
                    # Collect all new internal links for the next depth
                    for link in result.links.get("internal", []):
                        next_url = normalize_url(link["href"])
                        if next_url not in visited:
                            next_level_urls.add(next_url)
                else:
                    print(f"[ERROR] {result.url}: {result.error_message}")
                    
            # Move to the next set of URLs for the next recursion depth
            current_urls = next_level_urls

if __name__ == "__main__":
    asyncio.run(crawl_recursive_batch(["https://medium.com/@yousefhosni"], max_depth=2, max_concurrent=10))