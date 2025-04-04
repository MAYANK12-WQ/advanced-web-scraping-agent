import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class BeautifulSoupStrategy:
    """
    Strategy for scraping static websites using BeautifulSoup.
    This is the simplest and fastest strategy, suitable for basic HTML pages.
    """
    
    def __init__(self):
        self.name = "beautifulsoup"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        logger.info("BeautifulSoup strategy initialized")
    
    def scrape(self, url, proxies=None, timeout=30):
        """
        Scrape a website using BeautifulSoup
        
        Args:
            url (str): URL to scrape
            proxies (dict, optional): Proxy configuration
            timeout (int, optional): Request timeout in seconds
            
        Returns:
            str: HTML content of the page
        
        Raises:
            Exception: If scraping fails
        """
        logger.info(f"Scraping {url} with BeautifulSoup strategy")
        
        try:
            # Configure session
            session = requests.Session()
            
            # Add proxies if provided
            if proxies:
                session.proxies.update(proxies)
            
            # Make the request
            response = session.get(url, headers=self.headers, timeout=timeout)
            
            # Check if request was successful
            if response.status_code != 200:
                error_msg = f"Failed to fetch {url}: HTTP {response.status_code}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            # Get HTML content
            html_content = response.text
            
            # Validate HTML content
            if not html_content or len(html_content) < 100:
                error_msg = "Retrieved content is too small, likely not a valid HTML page"
                logger.warning(error_msg)
                # Continue anyway, might be a very simple page
            
            logger.info(f"Successfully scraped {url} with BeautifulSoup strategy")
            return html_content
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Request error while scraping {url}: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        except Exception as e:
            error_msg = f"Unexpected error while scraping {url}: {str(e)}"
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
            # Make a HEAD request to check response headers
            response = requests.head(url, headers=self.headers, timeout=5)
            
            # Check content type
            content_type = response.headers.get('Content-Type', '')
            
            # If it's a simple HTML page, this strategy is suitable
            if 'text/html' in content_type and 'javascript' not in content_type:
                return True
            
            return False
            
        except Exception:
            # If we can't determine, assume it's not suitable
            return False
