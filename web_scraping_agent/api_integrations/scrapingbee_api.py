import os
import requests
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class ScrapingBeeAPI:
    """
    Integration with ScrapingBee API for web scraping.
    ScrapingBee provides 1000 free API calls.
    """
    
    def __init__(self):
        self.name = "scrapingbee"
        self.api_key = os.getenv("SCRAPINGBEE_API_KEY")
        self.base_url = "https://app.scrapingbee.com/api/v1/"
        logger.info("ScrapingBee API integration initialized")
    
    def scrape(self, url, proxies=None, render_js=True, premium_proxy=False):
        """
        Scrape a website using ScrapingBee API
        
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
        logger.info(f"Scraping {url} with ScrapingBee API")
        
        if not self.api_key:
            error_msg = "ScrapingBee API key not found. Please set SCRAPINGBEE_API_KEY in .env file."
            logger.error(error_msg)
            raise Exception(error_msg)
        
        try:
            # Prepare API parameters
            params = {
                'api_key': self.api_key,
                'url': url,
                'render_js': 'true' if render_js else 'false',
                'premium_proxy': 'true' if premium_proxy else 'false'
            }
            
            # Make API request
            response = requests.get(self.base_url, params=params)
            
            # Check if request was successful
            if response.status_code != 200:
                error_msg = f"ScrapingBee API error: HTTP {response.status_code}, {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            # Get HTML content
            html_content = response.text
            
            # Validate HTML content
            if not html_content or len(html_content) < 100:
                logger.warning("Retrieved content is too small, might not be a valid HTML page")
            
            logger.info(f"Successfully scraped {url} with ScrapingBee API")
            return html_content
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Request error while using ScrapingBee API: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        except Exception as e:
            error_msg = f"Unexpected error while using ScrapingBee API: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def get_remaining_credits(self):
        """
        Get remaining API credits
        
        Returns:
            int: Number of remaining credits or -1 if error
        """
        if not self.api_key:
            logger.error("ScrapingBee API key not found")
            return -1
        
        try:
            # This is a mock implementation as ScrapingBee doesn't have a direct credits endpoint
            # In a real implementation, you would need to parse this from account information
            # or track usage locally
            return 1000  # Assuming all credits are available
            
        except Exception as e:
            logger.error(f"Error checking ScrapingBee credits: {str(e)}")
            return -1
