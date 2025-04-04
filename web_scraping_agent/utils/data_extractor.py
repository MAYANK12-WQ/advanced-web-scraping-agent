import re
import logging
from bs4 import BeautifulSoup
import pandas as pd

logger = logging.getLogger(__name__)

class DataExtractor:
    """
    Utility class for extracting various types of data from HTML content.
    Supports extraction of emails, phone numbers, headings, and links.
    """
    
    def __init__(self):
        logger.info("Data extractor initialized")
    
    def extract(self, html_content, data_type):
        """
        Extract specified data type from HTML content
        
        Args:
            html_content (str): HTML content to extract data from
            data_type (str): Type of data to extract ('emails', 'phone_numbers', 'headings', 'links')
            
        Returns:
            list: Extracted data items
        """
        if not html_content:
            logger.warning("Empty HTML content provided for extraction")
            return []
        
        logger.info(f"Extracting {data_type} from HTML content")
        
        if data_type == 'emails':
            return self.extract_emails(html_content)
        elif data_type == 'phone_numbers':
            return self.extract_phone_numbers(html_content)
        elif data_type == 'headings':
            return self.extract_headings(html_content)
        elif data_type == 'links':
            return self.extract_links(html_content)
        else:
            logger.warning(f"Unknown data type: {data_type}")
            return []
    
    def extract_emails(self, html_content):
        """
        Extract email addresses from HTML content
        
        Args:
            html_content (str): HTML content to extract emails from
            
        Returns:
            list: Extracted email addresses
        """
        logger.info("Extracting email addresses")
        
        try:
            # Regular expression for email extraction
            # This pattern matches most common email formats
            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            
            # Find all matches
            emails = re.findall(email_pattern, html_content)
            
            # Remove duplicates and sort
            unique_emails = sorted(list(set(emails)))
            
            # Filter out invalid emails (basic validation)
            valid_emails = [
                email for email in unique_emails 
                if self._is_valid_email(email)
            ]
            
            logger.info(f"Found {len(valid_emails)} unique email addresses")
            return valid_emails
            
        except Exception as e:
            logger.error(f"Error extracting emails: {str(e)}")
            return []
    
    def _is_valid_email(self, email):
        """
        Validate email address format
        
        Args:
            email (str): Email address to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        # Basic validation to filter out false positives
        if len(email) > 7:  # a@b.com minimum length
            # Check for common invalid patterns
            invalid_patterns = [
                r'\.{2,}',  # Multiple consecutive dots
                r'@.*@',    # Multiple @ symbols
                r'^[.@]',   # Starting with . or @
                r'[.@]$',   # Ending with . or @
                r'[^\w.@+-]'  # Invalid characters
            ]
            
            for pattern in invalid_patterns:
                if re.search(pattern, email):
                    return False
            
            return True
        
        return False
    
    def extract_phone_numbers(self, html_content):
        """
        Extract phone numbers from HTML content
        
        Args:
            html_content (str): HTML content to extract phone numbers from
            
        Returns:
            list: Extracted phone numbers
        """
        logger.info("Extracting phone numbers")
        
        try:
            # Regular expressions for phone number extraction
            # These patterns match various phone number formats
            patterns = [
                # International format: +XX XXX XXX XXXX
                r'\+\d{1,3}[-.\s]?\d{1,3}[-.\s]?\d{3,4}[-.\s]?\d{3,4}',
                
                # US format: (XXX) XXX-XXXX
                r'\(\d{3}\)[-.\s]?\d{3}[-.\s]?\d{4}',
                
                # Simple format: XXX-XXX-XXXX
                r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',
                
                # European format: XX XXX XX XX
                r'\d{2}[-.\s]?\d{3}[-.\s]?\d{2}[-.\s]?\d{2}'
            ]
            
            # Find all matches for each pattern
            phone_numbers = []
            for pattern in patterns:
                matches = re.findall(pattern, html_content)
                phone_numbers.extend(matches)
            
            # Clean and normalize phone numbers
            cleaned_numbers = [
                self._clean_phone_number(number) 
                for number in phone_numbers
            ]
            
            # Remove duplicates and sort
            unique_numbers = sorted(list(set(cleaned_numbers)))
            
            # Filter out invalid numbers (basic validation)
            valid_numbers = [
                number for number in unique_numbers 
                if len(number) >= 8  # Most phone numbers have at least 8 digits
            ]
            
            logger.info(f"Found {len(valid_numbers)} unique phone numbers")
            return valid_numbers
            
        except Exception as e:
            logger.error(f"Error extracting phone numbers: {str(e)}")
            return []
    
    def _clean_phone_number(self, number):
        """
        Clean and normalize phone number format
        
        Args:
            number (str): Phone number to clean
            
        Returns:
            str: Cleaned phone number
        """
        # Remove all non-digit characters except + at the beginning
        if number.startswith('+'):
            cleaned = '+' + re.sub(r'\D', '', number[1:])
        else:
            cleaned = re.sub(r'\D', '', number)
        
        return cleaned
    
    def extract_headings(self, html_content):
        """
        Extract headings (h1, h2) from HTML content
        
        Args:
            html_content (str): HTML content to extract headings from
            
        Returns:
            list: Extracted headings with their levels
        """
        logger.info("Extracting headings")
        
        try:
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find all h1 and h2 elements
            headings = []
            
            for level in [1, 2]:
                tag = f'h{level}'
                for heading in soup.find_all(tag):
                    text = heading.get_text().strip()
                    if text:  # Only include non-empty headings
                        headings.append({
                            'level': level,
                            'text': text
                        })
            
            logger.info(f"Found {len(headings)} headings")
            return headings
            
        except Exception as e:
            logger.error(f"Error extracting headings: {str(e)}")
            return []
    
    def extract_links(self, html_content):
        """
        Extract links from HTML content, categorized as internal or external
        
        Args:
            html_content (str): HTML content to extract links from
            
        Returns:
            list: Extracted links with their types (internal/external)
        """
        logger.info("Extracting links")
        
        try:
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find all anchor elements
            links = []
            base_url = self._extract_base_url(html_content)
            
            for anchor in soup.find_all('a', href=True):
                href = anchor.get('href').strip()
                text = anchor.get_text().strip()
                
                # Skip empty or javascript links
                if not href or href.startswith('javascript:') or href == '#':
                    continue
                
                # Determine if link is internal or external
                is_internal = self._is_internal_link(href, base_url)
                
                links.append({
                    'url': href,
                    'text': text if text else href,
                    'type': 'internal' if is_internal else 'external'
                })
            
            logger.info(f"Found {len(links)} links")
            return links
            
        except Exception as e:
            logger.error(f"Error extracting links: {str(e)}")
            return []
    
    def _extract_base_url(self, html_content):
        """
        Extract base URL from HTML content
        
        Args:
            html_content (str): HTML content
            
        Returns:
            str: Base URL or None if not found
        """
        try:
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Check for base tag
            base_tag = soup.find('base', href=True)
            if base_tag:
                return base_tag.get('href')
            
            # Try to extract from canonical link
            canonical = soup.find('link', {'rel': 'canonical', 'href': True})
            if canonical:
                url = canonical.get('href')
                # Extract domain from URL
                match = re.match(r'(https?://[^/]+)', url)
                if match:
                    return match.group(1)
            
            return None
            
        except Exception:
            return None
    
    def _is_internal_link(self, href, base_url):
        """
        Determine if a link is internal or external
        
        Args:
            href (str): Link URL
            base_url (str): Base URL of the page
            
        Returns:
            bool: True if internal, False if external
        """
        # If no base URL is available, use heuristics
        if not base_url:
            return href.startswith('/') or not href.startswith(('http://', 'https://'))
        
        # If base URL is available, check if the link starts with it
        return href.startswith('/') or href.startswith(base_url)
    
    def format_as_json(self, extracted_data):
        """
        Format extracted data as JSON
        
        Args:
            extracted_data (dict): Extracted data
            
        Returns:
            dict: Formatted data
        """
        return extracted_data
    
    def format_as_csv(self, extracted_data):
        """
        Format extracted data as CSV
        
        Args:
            extracted_data (dict): Extracted data
            
        Returns:
            str: CSV formatted data
        """
        # Flatten the data for CSV format
        flattened_data = []
        
        for data_type, items in extracted_data.items():
            if data_type != 'metadata':
                if isinstance(items, list):
                    for item in items:
                        if isinstance(item, dict):
                            row = {'data_type': data_type}
                            row.update(item)
                            flattened_data.append(row)
                        else:
                            flattened_data.append({
                                'data_type': data_type,
                                'value': item
                            })
        
        # Convert to DataFrame and then to CSV
        df = pd.DataFrame(flattened_data)
        return df.to_csv(index=False)
