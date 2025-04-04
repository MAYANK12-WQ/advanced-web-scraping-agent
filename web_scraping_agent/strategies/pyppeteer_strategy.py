import asyncio
import pyppeteer
import logging
from pyppeteer import launch
import time

logger = logging.getLogger(__name__)

class PyppeteerStrategy:
    """
    Strategy for scraping dynamic websites using Pyppeteer.
    This strategy is suitable for JavaScript-heavy websites that require browser rendering.
    It's an alternative to Selenium, using the Puppeteer/Chromium approach.
    """
    
    def __init__(self):
        self.name = "pyppeteer"
        logger.info("Pyppeteer strategy initialized")
    
    def scrape(self, url, proxies=None, timeout=60, wait_time=5):
        """
        Scrape a website using Pyppeteer with Chromium in headless mode
        
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
        logger.info(f"Scraping {url} with Pyppeteer strategy")
        
        # Run the async scraping function
        try:
            return asyncio.get_event_loop().run_until_complete(
                self._scrape_async(url, proxies, timeout, wait_time)
            )
        except RuntimeError:
            # If there's no event loop in the current thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(
                self._scrape_async(url, proxies, timeout, wait_time)
            )
    
    async def _scrape_async(self, url, proxies=None, timeout=60, wait_time=5):
        """
        Asynchronous implementation of the scraping function
        """
        browser = None
        
        try:
            # Configure browser launch options
            launch_options = {
                'headless': True,
                'args': [
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--disable-gpu',
                    '--window-size=1920,1080',
                ]
            }
            
            # Add proxy if provided
            if proxies and 'http' in proxies:
                proxy = proxies['http'].replace('http://', '')
                launch_options['args'].append(f'--proxy-server={proxy}')
            
            # Launch browser
            browser = await launch(launch_options)
            
            # Open new page
            page = await browser.newPage()
            
            # Set user agent
            await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            
            # Set timeout
            await page.setDefaultNavigationTimeout(timeout * 1000)
            
            # Navigate to URL
            logger.info(f"Navigating to {url}")
            response = await page.goto(url, {'waitUntil': 'networkidle0'})
            
            # Check response status
            if response.status != 200:
                error_msg = f"Failed to fetch {url}: HTTP {response.status}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            # Wait additional time for JavaScript execution if specified
            if wait_time > 0:
                logger.info(f"Waiting {wait_time} seconds for JavaScript execution")
                await asyncio.sleep(wait_time)
            
            # Get page content
            html_content = await page.content()
            
            # Validate HTML content
            if not html_content or len(html_content) < 100:
                error_msg = "Retrieved content is too small, likely not a valid HTML page"
                logger.warning(error_msg)
                # Continue anyway, might be a very simple page
            
            logger.info(f"Successfully scraped {url} with Pyppeteer strategy")
            return html_content
            
        except pyppeteer.errors.PyppeteerError as e:
            error_msg = f"Pyppeteer error while scraping {url}: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
            
        except Exception as e:
            error_msg = f"Unexpected error while scraping {url}: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
            
        finally:
            # Clean up
            if browser:
                try:
                    await browser.close()
                except Exception as e:
                    logger.warning(f"Error while closing Pyppeteer browser: {str(e)}")
    
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
