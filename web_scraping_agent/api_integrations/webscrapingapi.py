import os
import requests
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class WebScrapingAPI:
    """
    Integration with WebScrapingAPI for web scraping.
    WebScrapingAPI provides 1000 free API calls.
    """
    
    def __init__(self):
        self.name = "webscrapingapi"
        self.api_key = os.getenv("WEBSCRAPINGAPI_API_KEY")
        self.base_url = "https://api.webscrapingapi.com/v1"
        logger.info("WebScrapingAPI integration initialized")
    
    def scrape(self, url, proxies=None, render_js=True, premium_proxy=False):
        """
        Scrape a website using WebScrapingAPI
        
        Args:
            url (str): URL to scrape
            proxies (dict, optional): Not used for API calls
            render_js (bool, optional): Whether to render JavaScript
            premium_proxy (bool, optional): Whether to use premium proxies
            
        Returns:
            str: HTML content of the page
        
        Raises:
            Exception: If scraping fails
        """
        logger.info(f"Scraping {url} with WebScrapingAPI")
        
        if not self.api_key:
            error_msg = "WebScrapingAPI key not found. Please set WEBSCRAPINGAPI_API_KEY in .env file."
            logger.error(error_msg)
            raise Exception(error_msg)
        
        try:
            # Prepare API parameters
            params = {
                'api_key': self.api_key,
                'url': url,
                'render_js': '1' if render_js else '0',
                'premium_proxy': '1' if premium_proxy else '0'
            }
            
            # Make API request
            response = requests.get(self.base_url, params=params)
            
            # Check if request was successful
            if response.status_code != 200:
                error_msg = f"WebScrapingAPI error: HTTP {response.status_code}, {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            # Get HTML content
            html_content = response.text
            
            # Validate HTML content
            if not html_content or len(html_content) < 100:
                logger.warning("Retrieved content is too small, might not be a valid HTML page")
            
            logger.info(f"Successfully scraped {url} with WebScrapingAPI")
            return html_content
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Request error while using WebScrapingAPI: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        except Exception as e:
            error_msg = f"Unexpected error while using WebScrapingAPI: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def get_remaining_credits(self):
        """
        Get remaining API credits
        
        Returns:
            int: Number of remaining credits or -1 if error
        """
        if not self.api_key:
            logger.error("WebScrapingAPI key not found")
            return -1
        
        try:
            # Check account statistics
            params = {
                'api_key': self.api_key
            }
            
            response = requests.get(f"{self.base_url}/account", params=params)
            
            if response.status_code != 200:
                logger.error(f"Error checking WebScrapingAPI credits: HTTP {response.status_code}")
                return -1
            
            # Parse response to get remaining credits
            # This is a simplified implementation - actual response format may vary
            data = response.json()
            remaining = data.get('remaining_requests', -1)
            
            return remaining
            
        except Exception as e:
            logger.error(f"Error checking WebScrapingAPI credits: {str(e)}")
            return -1
