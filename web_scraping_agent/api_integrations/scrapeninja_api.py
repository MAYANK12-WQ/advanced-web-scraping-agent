import os
import requests
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class ScrapeNinjaAPI:
    """
    Integration with ScrapeNinja API for web scraping.
    ScrapeNinja provides 100 free API calls.
    """
    
    def __init__(self):
        self.name = "scrapeninja"
        self.api_key = os.getenv("SCRAPENINJA_API_KEY")
        self.base_url = "https://api.scrapeninja.net/scrape"
        logger.info("ScrapeNinja API integration initialized")
    
    def scrape(self, url, proxies=None, javascript=True, premium_proxy=False):
        """
        Scrape a website using ScrapeNinja API
        
        Args:
            url (str): URL to scrape
            proxies (dict, optional): Not used for API calls
            javascript (bool, optional): Whether to execute JavaScript
            premium_proxy (bool, optional): Whether to use premium proxies
            
        Returns:
            str: HTML content of the page
        
        Raises:
            Exception: If scraping fails
        """
        logger.info(f"Scraping {url} with ScrapeNinja API")
        
        if not self.api_key:
            error_msg = "ScrapeNinja API key not found. Please set SCRAPENINJA_API_KEY in .env file."
            logger.error(error_msg)
            raise Exception(error_msg)
        
        try:
            # Prepare API request payload
            headers = {
                'Content-Type': 'application/json',
                'X-API-KEY': self.api_key
            }
            
            payload = {
                'url': url,
                'javascript': javascript,
                'premium_proxy': premium_proxy
            }
            
            # Make API request
            response = requests.post(self.base_url, headers=headers, json=payload)
            
            # Check if request was successful
            if response.status_code != 200:
                error_msg = f"ScrapeNinja API error: HTTP {response.status_code}, {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            # Parse response
            data = response.json()
            
            # Check for API errors
            if data.get('success') is False:
                error_msg = f"ScrapeNinja API error: {data.get('error', 'Unknown error')}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            # Get HTML content
            html_content = data.get('body', '')
            
            # Validate HTML content
            if not html_content or len(html_content) < 100:
                logger.warning("Retrieved content is too small, might not be a valid HTML page")
            
            logger.info(f"Successfully scraped {url} with ScrapeNinja API")
            return html_content
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Request error while using ScrapeNinja API: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        except Exception as e:
            error_msg = f"Unexpected error while using ScrapeNinja API: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def get_remaining_credits(self):
        """
        Get remaining API credits
        
        Returns:
            int: Number of remaining credits or -1 if error
        """
        if not self.api_key:
            logger.error("ScrapeNinja API key not found")
            return -1
        
        try:
            # Check account statistics
            headers = {
                'X-API-KEY': self.api_key
            }
            
            response = requests.get("https://api.scrapeninja.net/account", headers=headers)
            
            if response.status_code != 200:
                logger.error(f"Error checking ScrapeNinja credits: HTTP {response.status_code}")
                return -1
            
            # Parse response to get remaining credits
            data = response.json()
            remaining = data.get('remaining_requests', -1)
            
            return remaining
            
        except Exception as e:
            logger.error(f"Error checking ScrapeNinja credits: {str(e)}")
            return -1
