from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
import logging
import time
import os

logger = logging.getLogger(__name__)

class SeleniumStrategy:
    """
    Strategy for scraping dynamic websites using Selenium.
    This strategy is suitable for JavaScript-heavy websites that require browser rendering.
    """
    
    def __init__(self):
        self.name = "selenium"
        logger.info("Selenium strategy initialized")
    
    def scrape(self, url, proxies=None, timeout=60, wait_time=5):
        """
        Scrape a website using Selenium with Chrome in headless mode
        
        Args:
            url (str): URL to scrape
            proxies (dict, optional): Proxy configuration
            timeout (int, optional): Page load timeout in seconds
            wait_time (int, optional): Time to wait for JavaScript execution in seconds
            
        Returns:
            str: HTML content of the page after JavaScript execution
        
        Raises:
            Exception: If scraping fails
        """
        logger.info(f"Scraping {url} with Selenium strategy")
        driver = None
        
        try:
            # Configure Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            # Set user agent
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            
            # Add proxy if provided
            if proxies and 'http' in proxies:
                proxy = proxies['http'].replace('http://', '')
                chrome_options.add_argument(f'--proxy-server={proxy}')
            
            # Initialize Chrome driver
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(timeout)
            
            # Navigate to URL
            logger.info(f"Navigating to {url}")
            driver.get(url)
            
            # Wait for JavaScript to execute
            logger.info(f"Waiting {wait_time} seconds for JavaScript execution")
            time.sleep(wait_time)
            
            # Get page source
            html_content = driver.page_source
            
            # Validate HTML content
            if not html_content or len(html_content) < 100:
                error_msg = "Retrieved content is too small, likely not a valid HTML page"
                logger.warning(error_msg)
                # Continue anyway, might be a very simple page
            
            logger.info(f"Successfully scraped {url} with Selenium strategy")
            return html_content
            
        except WebDriverException as e:
            error_msg = f"Selenium WebDriver error while scraping {url}: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
            
        except Exception as e:
            error_msg = f"Unexpected error while scraping {url}: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
            
        finally:
            # Clean up
            if driver:
                try:
                    driver.quit()
                except Exception as e:
                    logger.warning(f"Error while closing Selenium driver: {str(e)}")
    
    def is_suitable_for(self, url):
        """
        Determine if this strategy is suitable for the given URL
        
        Args:
            url (str): URL to check
            
        Returns:
            bool: True if suitable, False otherwise
        """
        try:
            # Check if the URL is likely to contain dynamic content
            # This is a simple heuristic and might need refinement
            dynamic_indicators = [
                '.js', 'javascript', 'angular', 'react', 'vue', 
                'spa', 'ajax', 'dynamic', 'interactive'
            ]
            
            # Check URL for indicators
            url_lower = url.lower()
            for indicator in dynamic_indicators:
                if indicator in url_lower:
                    return True
            
            # Make a simple request to check for JavaScript frameworks
            import requests
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=5)
            
            # Check content for JavaScript frameworks
            content = response.text.lower()
            js_frameworks = [
                'react', 'angular', 'vue', 'jquery', 'bootstrap.js',
                'ember', 'backbone', 'knockout', 'meteor', 'aurelia'
            ]
            
            for framework in js_frameworks:
                if framework in content:
                    return True
            
            return False
            
        except Exception:
            # If we can't determine, assume it's not suitable
            return False
