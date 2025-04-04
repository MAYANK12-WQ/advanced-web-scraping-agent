import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import logging
import tempfile
import os
import json
from scrapy import signals
from scrapy.signalmanager import dispatcher

logger = logging.getLogger(__name__)

class ScrapyStrategy:
    """
    Strategy for scraping websites using Scrapy.
    This strategy is suitable for structured data extraction and crawling multiple pages.
    """
    
    def __init__(self):
        self.name = "scrapy"
        logger.info("Scrapy strategy initialized")
    
    def scrape(self, url, proxies=None, timeout=60):
        """
        Scrape a website using Scrapy
        
        Args:
            url (str): URL to scrape
            proxies (dict, optional): Proxy configuration
            timeout (int, optional): Request timeout in seconds
            
        Returns:
            str: HTML content of the page
        
        Raises:
            Exception: If scraping fails
        """
        logger.info(f"Scraping {url} with Scrapy strategy")
        
        try:
            # Create a temporary file to store the results
            with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as temp_file:
                output_file = temp_file.name
            
            # Configure Scrapy settings
            settings = get_project_settings()
            settings.update({
                'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'ROBOTSTXT_OBEY': False,
                'DOWNLOAD_TIMEOUT': timeout,
                'FEED_FORMAT': 'json',
                'FEED_URI': output_file,
                'LOG_LEVEL': 'ERROR'
            })
            
            # Add proxy if provided
            if proxies and 'http' in proxies:
                settings.update({
                    'DOWNLOADER_MIDDLEWARES': {
                        'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110
                    },
                    'HTTP_PROXY': proxies['http']
                })
            
            # Create a custom spider for the URL
            spider = type('SinglePageSpider', (scrapy.Spider,), {
                'name': 'single_page_spider',
                'start_urls': [url],
                'custom_settings': settings,
                'parse': lambda self, response: {'html_content': response.text}
            })
            
            # Initialize the crawler process
            process = CrawlerProcess(settings)
            
            # Set up a container to store the results
            results = []
            
            # Set up a signal to capture the spider output
            def spider_closed(spider):
                logger.info(f"Spider closed: {spider.name}")
            
            dispatcher.connect(spider_closed, signal=signals.spider_closed)
            
            # Run the spider
            process.crawl(spider)
            process.start()  # This will block until the crawling is finished
            
            # Read the results from the output file
            with open(output_file, 'r') as f:
                try:
                    data = json.load(f)
                    if isinstance(data, list) and len(data) > 0:
                        html_content = data[0].get('html_content', '')
                    else:
                        html_content = ''
                except json.JSONDecodeError:
                    html_content = ''
            
            # Clean up the temporary file
            try:
                os.unlink(output_file)
            except Exception as e:
                logger.warning(f"Failed to delete temporary file {output_file}: {str(e)}")
            
            # Validate HTML content
            if not html_content or len(html_content) < 100:
                error_msg = "Retrieved content is too small, likely not a valid HTML page"
                logger.warning(error_msg)
                # Continue anyway, might be a very simple page
            
            logger.info(f"Successfully scraped {url} with Scrapy strategy")
            return html_content
            
        except Exception as e:
            error_msg = f"Unexpected error while scraping {url} with Scrapy: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def is_suitable_for(self, url):
        """
        Determine if this strategy is suitable for the given URL
        
        Args:
            url (str): URL to check
            
        Returns:
            bool: True if suitable, False otherwise
        """
        try:
            # Scrapy is particularly good for structured data and multiple pages
            # Check if the URL is likely to contain structured data
            structured_indicators = [
                'listing', 'products', 'catalog', 'directory',
                'search', 'results', 'items', 'collection'
            ]
            
            # Check URL for indicators
            url_lower = url.lower()
            for indicator in structured_indicators:
                if indicator in url_lower:
                    return True
            
            # Make a simple request to check for structured data
            import requests
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=5)
            
            # Check if the page contains tables or lists
            content = response.text.lower()
            structured_elements = [
                '<table', '<ul', '<ol', '<dl',
                'json-ld', 'structured-data', 'schema.org'
            ]
            
            for element in structured_elements:
                if element in content:
                    return True
            
            return False
            
        except Exception:
            # If we can't determine, assume it's not suitable
            return False
