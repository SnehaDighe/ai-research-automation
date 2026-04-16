"""
Web scraping module for extracting information from websites
"""
import logging
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import os

logger = logging.getLogger(__name__)


class WebScraper:
    """Scrape and extract information from web sources"""

    def __init__(self, timeout: int = 30, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.headers = {
            'User-Agent': os.getenv(
                'USER_AGENT',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
        }

    def fetch_page(self, url: str) -> str:
        """Fetch web page content"""
        logger.info(f"Fetching: {url}")
        
        for attempt in range(self.max_retries):
            try:
                response = requests.get(
                    url,
                    headers=self.headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt == self.max_retries - 1:
                    logger.error(f"Failed to fetch {url} after {self.max_retries} attempts")
                    return ""

    def extract_content(self, html: str, tag: str = 'p') -> List[str]:
        """Extract text content from HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract text from specified tags
            elements = soup.find_all(tag)
            content = [elem.get_text(strip=True) for elem in elements]
            
            return content
        except Exception as e:
            logger.error(f"Error extracting content: {e}")
            return []

    def scrape_url(self, url: str) -> Dict:
        """Scrape a URL and extract structured content"""
        html = self.fetch_page(url)
        
        if not html:
            return {'url': url, 'title': '', 'content': '', 'success': False}
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract title
        title = soup.title.string if soup.title else ''
        
        # Extract main content
        paragraphs = self.extract_content(html, 'p')
        content = ' '.join(paragraphs)[:1000]  # Limit to first 1000 chars
        
        return {
            'url': url,
            'title': title,
            'content': content,
            'success': True
        }

    def scrape_multiple(self, urls: List[str]) -> List[Dict]:
        """Scrape multiple URLs"""
        results = []
        
        for url in urls:
            try:
                result = self.scrape_url(url)
                results.append(result)
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                results.append({
                    'url': url,
                    'error': str(e),
                    'success': False
                })
        
        return results
