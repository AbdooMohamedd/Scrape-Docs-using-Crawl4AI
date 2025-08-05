# 🕷️ Crawl4AI Website Scraper Collection

A powerful collection of web scraping scripts built with **Crawl4AI** - an open-source LLM-friendly Web Crawler & Scraper. Efficiently extract and save entire website documentation using sitemaps or recursive crawling strategies.

![Crawl4AI Scraper Demo](./Crawl_Test.gif)

## 🚀 Overview

This repository contains four specialized scraping scripts designed to handle different website crawling scenarios using the Crawl4AI framework. Whether you need to scrape documentation sites, extract content from sitemaps, or perform recursive crawling, these scripts provide robust, efficient solutions for large-scale content extraction.

## 📁 Scraping Scripts

### [🔗 crawl_docs_sequential.py](./crawl_docs_sequential.py)
**Sequential Documentation Crawler**
- Crawls URLs one by one using session reuse for efficiency
- Best for: Small to medium documentation sites, rate-limited APIs
- Features: Memory-efficient, session persistence, error handling
- Use case: When you need controlled, sequential processing

### [🔗 crawl_docs_FAST.py](./crawl_docs_FAST.py)
**Fast Parallel Crawler with Memory Management**
- Processes multiple URLs concurrently with browser reuse
- Best for: Large documentation sites requiring speed
- Features: Memory monitoring, batch processing, performance optimization
- Use case: When speed is priority and you have adequate system resources

### [🔗 crawl_sitemap_in_parallel.py](./crawl_sitemap_in_parallel.py)
**Advanced Parallel Sitemap Crawler**
- Uses `arun_many()` with MemoryAdaptiveDispatcher for intelligent resource management
- Best for: Enterprise-level scraping with automatic resource optimization
- Features: Adaptive memory management, intelligent concurrency control
- Use case: Professional scraping workflows requiring maximum efficiency

### [🔗 crawl_site_recursively.py](./crawl_site_recursively.py)
**Recursive Website Explorer**
- Discovers and crawls internal links recursively up to specified depth
- Best for: Exploring websites without sitemaps, discovering hidden content
- Features: Link discovery, depth control, duplicate prevention
- Use case: When sitemaps are unavailable or incomplete

## 🛠️ Installation & Setup

### 1. Install Crawl4AI

```bash
pip install crawl4ai
```

### 2. Initial Setup

```bash
crawl4ai-setup
```

This command:
- Installs required Playwright browsers (Chromium, Firefox, etc.)
- Performs OS-level checks
- Confirms your environment is ready to crawl

### 3. Verify Installation (Optional)

```bash
crawl4ai-doctor
```

### 4. Advanced Installation (Optional)

For additional features like clustering or transformers:

```bash
# For PyTorch-based features
pip install crawl4ai[torch]

# For Hugging Face transformers
pip install crawl4ai[transformer] 

# For all features
pip install crawl4ai[all]

# Run setup after installing extras
crawl4ai-setup
```

## 🎯 Quick Start

### Basic Usage

```python
import asyncio
from crawl4ai import AsyncWebCrawler

async def simple_crawl():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun("https://example.com")
        print(result.markdown[:300])

asyncio.run(simple_crawl())
```

### Using the Scripts

1. **Edit the target sitemap URL** in your chosen script:
   ```python
   sitemap_url = "https://your-target-site.com/sitemap.xml"
   ```

2. **Run the script**:
   ```bash
   python crawl_docs_FAST.py
   ```

3. **Find your scraped content** in the generated folder (named after the domain)

## 🗺️ Understanding Sitemaps

### Sitemap.xml

A sitemap.xml file is a structured document that lists all the important pages on a website, helping search engines discover and crawl content more efficiently. It's typically located at the root domain (e.g., `example.com/sitemap.xml`) and contains URLs along with metadata like last modification dates, change frequency, and page priority. 

For web scraping and data collection projects, sitemaps provide a valuable roadmap of available content and can significantly speed up the discovery process by providing direct links to all indexable pages on a site.

### sitemap-pages.xml

Some websites provide additional or alternative sitemaps such as `sitemap-pages.xml`, which specifically lists individual content or documentation pages. For example, the Flowise documentation site uses `https://docs.flowiseai.com/sitemap-pages.xml` to help crawlers and users discover all documentation pages efficiently. 

Checking for these specialized sitemaps can improve coverage and accuracy when collecting or indexing website data.

### Generate Sitemaps

If a website doesn't have a sitemap, you can generate one using:
**[XML Sitemaps Generator](https://www.xml-sitemaps.com/)**

Simply input the website URL and it will crawl and generate a sitemap for you.

## ⚙️ Configuration

### Browser Configuration

```python
from crawl4ai import BrowserConfig

browser_config = BrowserConfig(
    headless=True,  # Run without GUI
    verbose=False,  # Reduce logging
    extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"]
)
```

### Crawler Configuration

```python
from crawl4ai import CrawlerRunConfig, CacheMode

crawl_config = CrawlerRunConfig(
    cache_mode=CacheMode.BYPASS,  # Always fetch fresh content
    stream=False,  # Wait for all results
)
```

### Memory Management

```python
from crawl4ai import MemoryAdaptiveDispatcher

dispatcher = MemoryAdaptiveDispatcher(
    memory_threshold_percent=70.0,  # Don't exceed 70% memory
    check_interval=1.0,             # Check every second
    max_session_permit=10           # Max concurrent sessions
)
```

## 📊 Features

### ✅ Core Capabilities
- **Asynchronous Processing**: Fast, non-blocking crawling
- **Automatic Markdown Conversion**: Clean, readable output
- **Memory Management**: Intelligent resource optimization
- **Session Reuse**: Efficient browser session handling
- **Error Handling**: Robust failure recovery
- **Progress Tracking**: Real-time crawling status
- **Organized Output**: Domain-based folder structure

### ✅ Advanced Features
- **LLM-Friendly Output**: Optimized for AI processing
- **Content Filtering**: Remove noise and ads
- **Data Extraction**: CSS/XPath and LLM-based strategies
- **Dynamic Content**: JavaScript execution support
- **Proxy Support**: For rate limiting and geo-restrictions
- **Custom Headers**: Authentication and API access

## 🎨 Output Structure

```
docs.example.com/
├── index.md
├── getting-started.md
├── api_reference_authentication.md
├── configuration_deployment.md
└── ...
```

Each scraped page is saved as a markdown file with a filename derived from the URL path, making it easy to organize and reference the content.

## 🔧 Customization

### Modify Target Sites

1. Update the sitemap URL in your chosen script:
   ```python
   sitemap_url = "https://your-target-site.com/sitemap.xml"
   ```

2. Adjust the URL fetching function if needed:
   ```python
   def get_target_urls():
       sitemap_url = "https://your-site.com/sitemap.xml"
       # ... rest of the function
   ```

### Adjust Concurrency

```python
# For crawl_docs_FAST.py
await crawl_parallel(urls, max_concurrent=50)

# For crawl_sitemap_in_parallel.py  
await crawl_parallel(urls, max_concurrent=10)

# For crawl_site_recursively.py
await crawl_recursive_batch(start_urls, max_depth=3, max_concurrent=10)
```

### Custom File Processing

Modify the `save_content_to_file()` function to:
- Change file naming conventions
- Add content preprocessing
- Implement custom folder structures
- Add metadata extraction

## 📈 Performance Tips

1. **Choose the Right Script**:
   - Use `sequential` for small sites or rate-limited APIs
   - Use `FAST` for speed with adequate resources
   - Use `sitemap_parallel` for professional workflows
   - Use `recursive` when sitemaps are unavailable

2. **Optimize Concurrency**:
   - Start with lower values (5-10) and increase gradually
   - Monitor memory usage during crawling
   - Consider your network bandwidth

3. **Memory Management**:
   - Use MemoryAdaptiveDispatcher for large jobs
   - Clear cache between different sites
   - Monitor system resources

## 🤝 Contributing

Feel free to contribute improvements, bug fixes, or additional scraping strategies! The scripts are designed to be modular and extensible.

## 📚 Resources

- [Crawl4AI Documentation](https://docs.crawl4ai.com/)
- [GitHub Repository](https://github.com/unclecode/crawl4ai)
- [Examples & Tutorials](https://docs.crawl4ai.com/core/examples/)

## 📄 License

This project uses the Crawl4AI framework. Please refer to the [Crawl4AI license](https://github.com/unclecode/crawl4ai/blob/main/LICENSE) for terms and conditions.

---

**Happy Crawling! 🕷️**
