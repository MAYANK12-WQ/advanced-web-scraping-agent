import os
import random
import logging
from dotenv import load_dotenv
import requests
from fake_useragent import UserAgent

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class ProxyRotator:
    """
    Utility class for rotating proxies to avoid IP blocking.
    """
    
    def __init__(self):
        self.proxy_list = self._load_proxies()
        self.user_agent = UserAgent()
        logger.info("Proxy rotator initialized")
    
    def _load_proxies(self):
        """
        Load proxies from environment variable or default list
        
        Returns:
            list: List of proxy URLs
        """
        # Try to load from environment variable
        proxy_env = os.getenv("PROXY_LIST", "")
        
        if proxy_env:
            # Split by comma
            proxies = [proxy.strip() for proxy in proxy_env.split(",")]
            logger.info(f"Loaded {len(proxies)} proxies from environment variable")
            return proxies
        
        # Default to a mock list of free proxies
        # In a real implementation, these would be actual working proxies
        mock_proxies = [
            "103.152.112.162:80",
            "185.61.152.137:8080",
            "51.159.115.233:3128",
            "165.227.71.60:80",
            "178.128.243.15:80"
        ]
        
        logger.info(f"Using {len(mock_proxies)} default mock proxies")
        return mock_proxies
    
    def get_proxy(self):
        """
        Get a random proxy from the list
        
        Returns:
            dict: Proxy configuration for requests
        """
        if not self.proxy_list:
            logger.warning("No proxies available")
            return None
        
        # Select a random proxy
        proxy = random.choice(self.proxy_list)
        
        # Format as a requests-compatible proxy dictionary
        proxy_dict = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        }
        
        # Generate a random user agent
        user_agent = self.user_agent.random
        
        logger.info(f"Selected proxy: {proxy}")
        return proxy_dict
    
    def get_proxy_with_auth(self, username=None, password=None):
        """
        Get a random proxy with authentication
        
        Args:
            username (str, optional): Proxy username
            password (str, optional): Proxy password
            
        Returns:
            dict: Proxy configuration for requests
        """
        if not self.proxy_list:
            logger.warning("No proxies available")
            return None
        
        # Use provided credentials or try to get from environment
        username = username or os.getenv("PROXY_USERNAME")
        password = password or os.getenv("PROXY_PASSWORD")
        
        if not username or not password:
            logger.warning("No proxy authentication credentials available")
            return self.get_proxy()
        
        # Select a random proxy
        proxy = random.choice(self.proxy_list)
        
        # Format as a requests-compatible proxy dictionary with authentication
        proxy_dict = {
            "http": f"http://{username}:{password}@{proxy}",
            "https": f"http://{username}:{password}@{proxy}"
        }
        
        logger.info(f"Selected proxy with authentication: {proxy}")
        return proxy_dict
    
    def test_proxy(self, proxy_dict):
        """
        Test if a proxy is working
        
        Args:
            proxy_dict (dict): Proxy configuration
            
        Returns:
            bool: True if working, False otherwise
        """
        try:
            # Try to make a request to a test URL
            response = requests.get(
                "https://httpbin.org/ip", 
                proxies=proxy_dict, 
                timeout=5
            )
            
            # Check if request was successful
            if response.status_code == 200:
                logger.info(f"Proxy test successful: {proxy_dict}")
                return True
            
            logger.warning(f"Proxy test failed: {proxy_dict}, HTTP {response.status_code}")
            return False
            
        except Exception as e:
            logger.warning(f"Proxy test failed: {proxy_dict}, {str(e)}")
            return False
    
    def get_working_proxy(self, max_attempts=3):
        """
        Get a working proxy by testing multiple proxies
        
        Args:
            max_attempts (int): Maximum number of attempts
            
        Returns:
            dict: Working proxy configuration or None if all failed
        """
        for _ in range(max_attempts):
            proxy = self.get_proxy()
            
            if proxy and self.test_proxy(proxy):
                return proxy
        
        logger.error(f"Failed to find working proxy after {max_attempts} attempts")
        return None
