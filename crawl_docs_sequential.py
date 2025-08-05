### Code Source
### https://github.com/coleam00/ottomator-agents/blob/main/crawl4AI-agent-v2/crawl4AI-examples/2-crawl_docs_sequential.py

import asyncio
from typing import List
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
import requests
from xml.etree import ElementTree
import os
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
        base_folder (str): The base folder name (e.g., 'docs.flowiseai.com')
    """
    try:
        # Create the base folder if it doesn't exist
        if not os.path.exists(base_folder):
            os.makedirs(base_folder)
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

async def crawl_sequential(urls: List[str], sitemap_url: str):
    print("\n=== Sequential Crawling with Session Reuse ===")
    
    # Extract folder name from sitemap URL
    base_folder = extract_domain_from_sitemap_url(sitemap_url)
    print(f"Saving content to folder: {base_folder}")

    browser_config = BrowserConfig(
        headless=True,
        extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"],
    )

    crawl_config = CrawlerRunConfig(
        markdown_generator=DefaultMarkdownGenerator()
    )

    # Create the crawler (opens the browser)
    crawler = AsyncWebCrawler(config=browser_config)
    await crawler.start()

    try:
        session_id = "session1"  
        for url in urls:
            result = await crawler.arun(
                url=url,
                config=crawl_config,
                session_id=session_id
            )
            if result.success:
                print(f"Successfully crawled: {url}")
                print(f"Markdown length: {len(result.markdown.raw_markdown)}")
                save_content_to_file(result.markdown.raw_markdown, url, base_folder)
            else:
                print(f"Failed: {url} - Error: {result.error_message}")
    finally:
        await crawler.close()

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
    sitemap_url = "https://docs.flowiseai.com/sitemap-pages.xml"
    urls = get_pydantic_ai_docs_urls()
    if urls:
        print(f"Found {len(urls)} URLs to crawl")
        await crawl_sequential(urls, sitemap_url)
    else:
        print("No URLs found to crawl")

if __name__ == "__main__":
    asyncio.run(main())