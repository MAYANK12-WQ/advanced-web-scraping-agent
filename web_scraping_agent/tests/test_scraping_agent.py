import os
import sys
import logging
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules to test
from strategies.beautifulsoup_strategy import BeautifulSoupStrategy
from strategies.selenium_strategy import SeleniumStrategy
from strategies.pyppeteer_strategy import PyppeteerStrategy
from strategies.scrapy_strategy import ScrapyStrategy
from api_integrations.scrapingbee_api import ScrapingBeeAPI
from api_integrations.webscrapingapi import WebScrapingAPI
from api_integrations.scrapeninja_api import ScrapeNinjaAPI
from api_integrations.twocaptcha_api import TwoCaptchaAPI
from utils.strategy_selector import StrategySelector
from utils.data_extractor import DataExtractor
from utils.proxy_rotator import ProxyRotator

# Configure logging
logging.basicConfig(level=logging.ERROR)

class TestScrapingStrategies(unittest.TestCase):
    """Test cases for scraping strategies"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_url = "https://example.com"
        self.html_content = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <h1>Test Heading</h1>
                <p>This is a test page with an email: test@example.com</p>
                <p>Contact us at: (123) 456-7890</p>
                <a href="https://example.com/page1">Internal Link</a>
                <a href="https://external-site.com">External Link</a>
            </body>
        </html>
        """
    
    @patch('requests.Session.get')
    def test_beautifulsoup_strategy(self, mock_get):
        """Test BeautifulSoup strategy"""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = self.html_content
        mock_get.return_value = mock_response
        
        # Create strategy and scrape
        strategy = BeautifulSoupStrategy()
        result = strategy.scrape(self.test_url)
        
        # Verify result
        self.assertEqual(result, self.html_content)
        mock_get.assert_called_once()
    
    @patch('selenium.webdriver.Chrome')
    def test_selenium_strategy(self, mock_chrome):
        """Test Selenium strategy"""
        # Mock the Chrome driver
        mock_driver = MagicMock()
        mock_driver.page_source = self.html_content
        mock_chrome.return_value = mock_driver
        
        # Create strategy and scrape
        strategy = SeleniumStrategy()
        result = strategy.scrape(self.test_url)
        
        # Verify result
        self.assertEqual(result, self.html_content)
        mock_driver.get.assert_called_once_with(self.test_url)
        mock_driver.quit.assert_called_once()
    
    @patch('asyncio.get_event_loop')
    def test_pyppeteer_strategy(self, mock_get_event_loop):
        """Test Pyppeteer strategy"""
        # Mock the event loop and browser
        mock_loop = MagicMock()
        mock_get_event_loop.return_value = mock_loop
        mock_loop.run_until_complete.return_value = self.html_content
        
        # Create strategy and scrape
        strategy = PyppeteerStrategy()
        result = strategy.scrape(self.test_url)
        
        # Verify result
        self.assertEqual(result, self.html_content)
        mock_loop.run_until_complete.assert_called_once()
    
    @patch('scrapy.crawler.CrawlerProcess.crawl')
    @patch('scrapy.crawler.CrawlerProcess.start')
    @patch('json.load')
    def test_scrapy_strategy(self, mock_json_load, mock_start, mock_crawl):
        """Test Scrapy strategy"""
        # Mock the JSON loading
        mock_json_load.return_value = [{'html_content': self.html_content}]
        
        # Create strategy and scrape
        strategy = ScrapyStrategy()
        result = strategy.scrape(self.test_url)
        
        # Verify result
        self.assertEqual(result, self.html_content)
        mock_crawl.assert_called_once()
        mock_start.assert_called_once()

class TestAPIIntegrations(unittest.TestCase):
    """Test cases for API integrations"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_url = "https://example.com"
        self.html_content = "<html><body>Test content</body></html>"
    
    @patch('requests.get')
    def test_scrapingbee_api(self, mock_get):
        """Test ScrapingBee API"""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = self.html_content
        mock_get.return_value = mock_response
        
        # Create API client and scrape
        with patch.dict(os.environ, {"SCRAPINGBEE_API_KEY": "test_key"}):
            api = ScrapingBeeAPI()
            result = api.scrape(self.test_url)
        
        # Verify result
        self.assertEqual(result, self.html_content)
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_webscrapingapi(self, mock_get):
        """Test WebScrapingAPI"""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = self.html_content
        mock_get.return_value = mock_response
        
        # Create API client and scrape
        with patch.dict(os.environ, {"WEBSCRAPINGAPI_API_KEY": "test_key"}):
            api = WebScrapingAPI()
            result = api.scrape(self.test_url)
        
        # Verify result
        self.assertEqual(result, self.html_content)
        mock_get.assert_called_once()
    
    @patch('requests.post')
    def test_scrapeninja_api(self, mock_post):
        """Test ScrapeNinja API"""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'body': self.html_content
        }
        mock_post.return_value = mock_response
        
        # Create API client and scrape
        with patch.dict(os.environ, {"SCRAPENINJA_API_KEY": "test_key"}):
            api = ScrapeNinjaAPI()
            result = api.scrape(self.test_url)
        
        # Verify result
        self.assertEqual(result, self.html_content)
        mock_post.assert_called_once()
    
    def test_twocaptcha_api(self):
        """Test 2Captcha API"""
        # Create API client and solve CAPTCHA
        with patch.dict(os.environ, {"TWOCAPTCHA_API_KEY": "test_key"}):
            api = TwoCaptchaAPI()
            result = api.solve_image_captcha(image_url="https://example.com/captcha.jpg")
        
        # Verify result (mock implementation returns fixed values)
        self.assertEqual(result, "mock_image_captcha_solution")

class TestUtilities(unittest.TestCase):
    """Test cases for utility modules"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.html_content = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <h1>Test Heading 1</h1>
                <h2>Test Heading 2</h2>
                <p>This is a test page with emails: test@example.com and another@example.org</p>
                <p>Contact us at: (123) 456-7890 or +1-987-654-3210</p>
                <a href="https://example.com/page1">Internal Link</a>
                <a href="https://external-site.com">External Link</a>
            </body>
        </html>
        """
    
    @patch('requests.get')
    def test_strategy_selector(self, mock_get):
        """Test strategy selector"""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = self.html_content
        mock_get.return_value = mock_response
        
        # Create selector and select strategy
        selector = StrategySelector()
        strategy = selector.select_strategy("https://example.com")
        
        # Verify result (should be one of the valid strategies)
        self.assertIn(strategy, ['beautifulsoup', 'selenium', 'pyppeteer', 'scrapy', 'api'])
    
    def test_data_extractor_emails(self):
        """Test data extractor for emails"""
        extractor = DataExtractor()
        emails = extractor.extract(self.html_content, 'emails')
        
        # Verify result
        self.assertEqual(len(emails), 2)
        self.assertIn('test@example.com', emails)
        self.assertIn('another@example.org', emails)
    
    def test_data_extractor_phone_numbers(self):
        """Test data extractor for phone numbers"""
        extractor = DataExtractor()
        phones = extractor.extract(self.html_content, 'phone_numbers')
        
        # Verify result
        self.assertEqual(len(phones), 2)
        self.assertTrue(any('123' in phone for phone in phones))
        self.assertTrue(any('987' in phone for phone in phones))
    
    def test_data_extractor_headings(self):
        """Test data extractor for headings"""
        extractor = DataExtractor()
        headings = extractor.extract(self.html_content, 'headings')
        
        # Verify result
        self.assertEqual(len(headings), 2)
        h1_headings = [h for h in headings if h['level'] == 1]
        h2_headings = [h for h in headings if h['level'] == 2]
        self.assertEqual(len(h1_headings), 1)
        self.assertEqual(len(h2_headings), 1)
        self.assertEqual(h1_headings[0]['text'], 'Test Heading 1')
        self.assertEqual(h2_headings[0]['text'], 'Test Heading 2')
    
    def test_data_extractor_links(self):
        """Test data extractor for links"""
        extractor = DataExtractor()
        links = extractor.extract(self.html_content, 'links')
        
        # Verify result
        self.assertEqual(len(links), 2)
        internal_links = [link for link in links if link['type'] == 'internal']
        external_links = [link for link in links if link['type'] == 'external']
        self.assertEqual(len(internal_links), 1)
        self.assertEqual(len(external_links), 1)
        self.assertTrue(any('example.com' in link['url'] for link in internal_links))
        self.assertTrue(any('external-site.com' in link['url'] for link in external_links))
    
    def test_proxy_rotator(self):
        """Test proxy rotator"""
        rotator = ProxyRotator()
        proxy = rotator.get_proxy()
        
        # Verify result
        self.assertIsNotNone(proxy)
        self.assertIn('http', proxy)
        self.assertIn('https', proxy)

if __name__ == '__main__':
    unittest.main()
