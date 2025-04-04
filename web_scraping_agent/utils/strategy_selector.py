import logging
import requests
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)

class StrategySelector:
    """
    Utility class for selecting the most appropriate scraping strategy
    based on website characteristics.
    """
    
    def __init__(self):
        logger.info("Strategy selector initialized")
    
    def select_strategy(self, url):
        """
        Select the most appropriate scraping strategy for the given URL
        
        Args:
            url (str): URL to analyze
            
        Returns:
            str: Selected strategy name ('beautifulsoup', 'selenium', 'pyppeteer', 'scrapy', 'api')
        """
        logger.info(f"Selecting strategy for URL: {url}")
        
        try:
            # Analyze the website to determine its characteristics
            characteristics = self._analyze_website(url)
            
            # Select strategy based on characteristics
            if characteristics['is_dynamic']:
                # For dynamic content, choose between Selenium and Pyppeteer
                # Pyppeteer is more lightweight but Selenium has better compatibility
                if characteristics['requires_browser_features']:
                    logger.info(f"Selected 'selenium' strategy for {url} (dynamic content with browser features)")
                    return 'selenium'
                else:
                    logger.info(f"Selected 'pyppeteer' strategy for {url} (dynamic content)")
                    return 'pyppeteer'
            
            elif characteristics['has_structured_data']:
                # For structured data, use Scrapy
                logger.info(f"Selected 'scrapy' strategy for {url} (structured data)")
                return 'scrapy'
            
            elif characteristics['has_anti_scraping']:
                # For websites with anti-scraping measures, use API-based scraping
                logger.info(f"Selected 'api' strategy for {url} (anti-scraping measures)")
                return 'api'
            
            else:
                # For simple static websites, use BeautifulSoup
                logger.info(f"Selected 'beautifulsoup' strategy for {url} (static content)")
                return 'beautifulsoup'
                
        except Exception as e:
            # If analysis fails, default to BeautifulSoup as it's the most lightweight
            logger.error(f"Error selecting strategy for {url}: {str(e)}")
            logger.info(f"Defaulting to 'beautifulsoup' strategy for {url}")
            return 'beautifulsoup'
    
    def _analyze_website(self, url):
        """
        Analyze website characteristics to determine the best scraping strategy
        
        Args:
            url (str): URL to analyze
            
        Returns:
            dict: Website characteristics
        """
        # Default characteristics
        characteristics = {
            'is_dynamic': False,
            'has_structured_data': False,
            'has_anti_scraping': False,
            'requires_browser_features': False
        }
        
        try:
            # Make a simple request to analyze the website
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            # Check if request was successful
            if response.status_code != 200:
                logger.warning(f"Failed to analyze {url}: HTTP {response.status_code}")
                return characteristics
            
            # Get HTML content
            html_content = response.text
            
            # Check for JavaScript frameworks and dynamic content
            js_frameworks = [
                'react', 'angular', 'vue', 'jquery', 'bootstrap.js',
                'ember', 'backbone', 'knockout', 'meteor', 'aurelia'
            ]
            
            for framework in js_frameworks:
                if framework in html_content.lower():
                    characteristics['is_dynamic'] = True
                    break
            
            # Check for AJAX calls or dynamic loading
            if re.search(r'(ajax|fetch|axios|xmlhttprequest)', html_content.lower()):
                characteristics['is_dynamic'] = True
            
            # Check for structured data
            structured_elements = [
                '<table', '<ul', '<ol', '<dl',
                'json-ld', 'structured-data', 'schema.org'
            ]
            
            for element in structured_elements:
                if element in html_content.lower():
                    characteristics['has_structured_data'] = True
                    break
            
            # Check for anti-scraping measures
            anti_scraping_indicators = [
                'captcha', 'recaptcha', 'hcaptcha', 'cloudflare',
                'distil', 'imperva', 'akamai', 'bot detection'
            ]
            
            for indicator in anti_scraping_indicators:
                if indicator in html_content.lower():
                    characteristics['has_anti_scraping'] = True
                    break
            
            # Check for features requiring a browser
            browser_features = [
                'onclick', 'onload', 'onscroll', 'addEventListener',
                'infinite scroll', 'lazy load'
            ]
            
            for feature in browser_features:
                if feature in html_content.lower():
                    characteristics['requires_browser_features'] = True
                    break
            
            # Parse with BeautifulSoup for more detailed analysis
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Check for iframes (often used in dynamic content)
            if soup.find('iframe'):
                characteristics['is_dynamic'] = True
            
            # Check for forms with JavaScript submission
            forms = soup.find_all('form')
            for form in forms:
                if form.get('onsubmit') or not form.get('action'):
                    characteristics['is_dynamic'] = True
                    break
            
            return characteristics
            
        except Exception as e:
            logger.error(f"Error analyzing website {url}: {str(e)}")
            return characteristics
