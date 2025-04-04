import os
import json
import gradio as gr
import pandas as pd
from dotenv import load_dotenv
import logging
from datetime import datetime

# Import strategy modules
from strategies.beautifulsoup_strategy import BeautifulSoupStrategy
from strategies.selenium_strategy import SeleniumStrategy
from strategies.pyppeteer_strategy import PyppeteerStrategy
from strategies.scrapy_strategy import ScrapyStrategy

# Import API integration modules
from api_integrations.scrapingbee_api import ScrapingBeeAPI
from api_integrations.webscrapingapi import WebScrapingAPI
from api_integrations.scrapeninja_api import ScrapeNinjaAPI
from api_integrations.twocaptcha_api import TwoCaptchaAPI

# Import utility modules
from utils.strategy_selector import StrategySelector
from utils.data_extractor import DataExtractor
from utils.proxy_rotator import ProxyRotator
from utils.logger import setup_logger

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logger()

class WebScrapingAgent:
    def __init__(self):
        self.strategy_selector = StrategySelector()
        self.data_extractor = DataExtractor()
        self.proxy_rotator = ProxyRotator()
        
        # Initialize API clients
        self.api_clients = {
            'scrapingbee': ScrapingBeeAPI(),
            'webscrapingapi': WebScrapingAPI(),
            'scrapeninja': ScrapeNinjaAPI(),
            'twocaptcha': TwoCaptchaAPI()
        }
        
        # Initialize scraping strategies
        self.strategies = {
            'beautifulsoup': BeautifulSoupStrategy(),
            'selenium': SeleniumStrategy(),
            'pyppeteer': PyppeteerStrategy(),
            'scrapy': ScrapyStrategy()
        }
        
        logger.info("Web Scraping Agent initialized successfully")
    
    def scrape(self, url, data_types, use_proxy=False, manual_strategy=None):
        """
        Main scraping function that orchestrates the scraping process
        
        Args:
            url (str): URL to scrape
            data_types (list): List of data types to extract (emails, phones, headings, links)
            use_proxy (bool): Whether to use proxy rotation
            manual_strategy (str): Manually selected strategy, if None will auto-select
            
        Returns:
            dict: Extracted data and metadata
        """
        logger.info(f"Starting scraping process for URL: {url}")
        
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            error_msg = "Invalid URL. Please provide a URL starting with http:// or https://"
            logger.error(error_msg)
            return {"error": error_msg}
        
        try:
            # Select strategy
            if manual_strategy:
                strategy_name = manual_strategy
                logger.info(f"Using manually selected strategy: {strategy_name}")
            else:
                strategy_name = self.strategy_selector.select_strategy(url)
                logger.info(f"Auto-selected strategy: {strategy_name}")
            
            # Configure proxy if enabled
            proxies = None
            if use_proxy:
                proxies = self.proxy_rotator.get_proxy()
                logger.info(f"Using proxy rotation: {proxies}")
            
            # Try scraping with selected strategy
            try:
                if strategy_name in self.strategies:
                    strategy = self.strategies[strategy_name]
                    html_content = strategy.scrape(url, proxies=proxies)
                else:
                    # Fallback to API-based scraping
                    html_content = self._try_api_scraping(url, proxies)
                
                # Extract requested data types
                result = {}
                for data_type in data_types:
                    result[data_type] = self.data_extractor.extract(html_content, data_type)
                
                # Add metadata
                result['metadata'] = {
                    'url': url,
                    'timestamp': datetime.now().isoformat(),
                    'strategy_used': strategy_name,
                    'proxy_used': bool(proxies)
                }
                
                logger.info(f"Scraping completed successfully for {url}")
                return result
                
            except Exception as e:
                logger.error(f"Error with strategy {strategy_name}: {str(e)}")
                # Try API-based scraping as fallback
                return self._try_api_scraping(url, proxies, data_types)
                
        except Exception as e:
            error_msg = f"Scraping failed: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def _try_api_scraping(self, url, proxies=None, data_types=None):
        """
        Try scraping using available APIs with automatic rotation
        """
        logger.info("Attempting API-based scraping")
        
        # Try each API in sequence
        for api_name, api_client in self.api_clients.items():
            try:
                logger.info(f"Trying {api_name} API")
                result = api_client.scrape(url, proxies=proxies)
                
                if data_types:
                    # Extract specific data types if requested
                    extracted_data = {}
                    for data_type in data_types:
                        extracted_data[data_type] = self.data_extractor.extract(result, data_type)
                    
                    # Add metadata
                    extracted_data['metadata'] = {
                        'url': url,
                        'timestamp': datetime.now().isoformat(),
                        'strategy_used': f"api:{api_name}",
                        'proxy_used': bool(proxies)
                    }
                    return extracted_data
                
                return result
            except Exception as e:
                logger.error(f"Error with {api_name} API: {str(e)}")
                continue
        
        # If all APIs fail
        error_msg = "All scraping methods failed. Please check the URL or try again later."
        logger.error(error_msg)
        return {"error": error_msg}

# Create Gradio interface
def create_interface():
    agent = WebScrapingAgent()
    
    with gr.Blocks(title="Advanced Web Scraping Agent", theme=gr.themes.Soft()) as interface:
        gr.Markdown("""
        # 🕸️ Advanced Web Scraping Agent
        
        A versatile web scraping tool that automatically selects the best scraping method based on website complexity.
        """)
        
        with gr.Row():
            with gr.Column(scale=3):
                url_input = gr.Textbox(
                    label="Website URL", 
                    placeholder="https://example.com",
                    info="Enter the full URL of the website you want to scrape"
                )
                
                with gr.Row():
                    with gr.Column():
                        data_types = gr.CheckboxGroup(
                            choices=["emails", "phone_numbers", "headings", "links"],
                            label="Data to Extract",
                            info="Select the types of data you want to extract"
                        )
                    
                    with gr.Column():
                        strategy = gr.Radio(
                            choices=["auto", "beautifulsoup", "selenium", "pyppeteer", "scrapy", "api"],
                            value="auto",
                            label="Scraping Strategy",
                            info="Select a specific strategy or let the agent choose automatically"
                        )
                
                with gr.Row():
                    use_proxy = gr.Checkbox(
                        label="Use Proxy Rotation", 
                        info="Enable proxy rotation to avoid IP blocking (if available)"
                    )
                    
                    output_format = gr.Radio(
                        choices=["json", "csv"],
                        value="json",
                        label="Output Format",
                        info="Select the format for downloading results"
                    )
                
                scrape_button = gr.Button("Start Scraping", variant="primary")
            
            with gr.Column(scale=2):
                log_output = gr.Textbox(
                    label="Scraping Logs", 
                    placeholder="Logs will appear here...",
                    lines=10,
                    max_lines=15
                )
        
        with gr.Row():
            with gr.Column():
                results_json = gr.JSON(label="Results")
            
            with gr.Column():
                download_button = gr.Button("Download Results")
                file_output = gr.File(label="Download")
        
        # Define scraping function
        def scrape_website(url, data_types, strategy, use_proxy, output_format):
            if not url:
                return {"error": "Please enter a URL"}, "Error: URL is required"
            
            if not data_types:
                return {"error": "Please select at least one data type to extract"}, "Error: No data types selected"
            
            logs = []
            logs.append(f"Starting scraping process for: {url}")
            logs.append(f"Data types to extract: {', '.join(data_types)}")
            logs.append(f"Strategy: {strategy}")
            logs.append(f"Proxy rotation: {'Enabled' if use_proxy else 'Disabled'}")
            
            # Convert 'auto' to None for auto-selection
            strategy_param = None if strategy == "auto" else strategy
            
            # Perform scraping
            try:
                logs.append("Executing scraping operation...")
                result = agent.scrape(url, data_types, use_proxy, strategy_param)
                
                if "error" in result:
                    logs.append(f"Error: {result['error']}")
                else:
                    logs.append("Scraping completed successfully!")
                    for data_type in data_types:
                        count = len(result.get(data_type, []))
                        logs.append(f"Found {count} {data_type}")
                
                return result, "\n".join(logs)
            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                logs.append(error_msg)
                return {"error": error_msg}, "\n".join(logs)
        
        # Define download function
        def prepare_download(results, output_format):
            if "error" in results:
                return None
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if output_format == "json":
                filename = f"scraping_results_{timestamp}.json"
                with open(filename, "w") as f:
                    json.dump(results, f, indent=2)
                return filename
            else:  # CSV
                filename = f"scraping_results_{timestamp}.csv"
                
                # Flatten the results for CSV format
                flattened_data = []
                for data_type, items in results.items():
                    if data_type != "metadata":
                        for item in items:
                            flattened_data.append({
                                "data_type": data_type,
                                "value": item
                            })
                
                df = pd.DataFrame(flattened_data)
                df.to_csv(filename, index=False)
                return filename
        
        # Connect components
        scrape_button.click(
            scrape_website,
            inputs=[url_input, data_types, strategy, use_proxy, output_format],
            outputs=[results_json, log_output]
        )
        
        download_button.click(
            prepare_download,
            inputs=[results_json, output_format],
            outputs=[file_output]
        )
        
        return interface

# For Hugging Face Spaces compatibility
interface = create_interface()

# Only use launch() during local development, not in Spaces
if __name__ == "__main__":
    interface.launch()
else:
    # This is what Hugging Face Spaces will use
    app = interface
