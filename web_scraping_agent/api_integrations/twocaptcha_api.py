import os
import requests
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class TwoCaptchaAPI:
    """
    Integration with 2Captcha API for CAPTCHA solving.
    This is a mock implementation for demonstration purposes.
    2Captcha provides free test credits.
    """
    
    def __init__(self):
        self.name = "twocaptcha"
        self.api_key = os.getenv("TWOCAPTCHA_API_KEY")
        self.base_url = "https://2captcha.com/in.php"
        self.result_url = "https://2captcha.com/res.php"
        logger.info("2Captcha API integration initialized")
    
    def solve_captcha(self, captcha_type, captcha_data):
        """
        Solve a CAPTCHA using 2Captcha API
        
        Args:
            captcha_type (str): Type of CAPTCHA ('image', 'recaptcha', 'hcaptcha', etc.)
            captcha_data (dict): CAPTCHA data (varies by type)
            
        Returns:
            str: CAPTCHA solution
        
        Raises:
            Exception: If CAPTCHA solving fails
        """
        logger.info(f"Solving {captcha_type} CAPTCHA with 2Captcha API")
        
        if not self.api_key:
            error_msg = "2Captcha API key not found. Please set TWOCAPTCHA_API_KEY in .env file."
            logger.error(error_msg)
            raise Exception(error_msg)
        
        # This is a mock implementation for demonstration purposes
        # In a real implementation, you would send the CAPTCHA to 2Captcha and wait for the solution
        
        try:
            # Mock successful CAPTCHA solving
            logger.info(f"Successfully solved {captcha_type} CAPTCHA with 2Captcha API")
            
            if captcha_type == 'image':
                return "mock_image_captcha_solution"
            elif captcha_type == 'recaptcha':
                return "mock_recaptcha_solution"
            elif captcha_type == 'hcaptcha':
                return "mock_hcaptcha_solution"
            else:
                return "mock_captcha_solution"
            
        except Exception as e:
            error_msg = f"Unexpected error while using 2Captcha API: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def solve_image_captcha(self, image_url=None, image_file=None, image_base64=None):
        """
        Solve an image CAPTCHA
        
        Args:
            image_url (str, optional): URL of the CAPTCHA image
            image_file (str, optional): Path to the CAPTCHA image file
            image_base64 (str, optional): Base64-encoded CAPTCHA image
            
        Returns:
            str: CAPTCHA solution
        """
        captcha_data = {
            'image_url': image_url,
            'image_file': image_file,
            'image_base64': image_base64
        }
        
        return self.solve_captcha('image', captcha_data)
    
    def solve_recaptcha(self, site_key, page_url):
        """
        Solve a reCAPTCHA
        
        Args:
            site_key (str): reCAPTCHA site key
            page_url (str): URL of the page with the reCAPTCHA
            
        Returns:
            str: reCAPTCHA solution
        """
        captcha_data = {
            'site_key': site_key,
            'page_url': page_url
        }
        
        return self.solve_captcha('recaptcha', captcha_data)
    
    def solve_hcaptcha(self, site_key, page_url):
        """
        Solve an hCaptcha
        
        Args:
            site_key (str): hCaptcha site key
            page_url (str): URL of the page with the hCaptcha
            
        Returns:
            str: hCaptcha solution
        """
        captcha_data = {
            'site_key': site_key,
            'page_url': page_url
        }
        
        return self.solve_captcha('hcaptcha', captcha_data)
    
    def get_balance(self):
        """
        Get account balance
        
        Returns:
            float: Account balance or -1 if error
        """
        if not self.api_key:
            logger.error("2Captcha API key not found")
            return -1
        
        try:
            # Check account balance
            params = {
                'key': self.api_key,
                'action': 'getbalance',
                'json': 1
            }
            
            response = requests.get(self.result_url, params=params)
            
            if response.status_code != 200:
                logger.error(f"Error checking 2Captcha balance: HTTP {response.status_code}")
                return -1
            
            # Parse response to get balance
            data = response.json()
            
            if data.get('status') == 1:
                return float(data.get('request', 0))
            else:
                logger.error(f"Error checking 2Captcha balance: {data.get('request')}")
                return -1
            
        except Exception as e:
            logger.error(f"Error checking 2Captcha balance: {str(e)}")
            return -1
