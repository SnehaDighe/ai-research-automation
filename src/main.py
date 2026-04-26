"""
Main entry point for AI Research & Task Automation Agent
"""
import os
import logging
from dotenv import load_dotenv
from query_processor import QueryProcessor
from web_scraper import WebScraper
from semantic_search import SemanticSearch

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class ResearchAgent:
    """AI-powered research automation agent"""

    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.query_processor = QueryProcessor(self.api_key)
        self.web_scraper = WebScraper(
            timeout=int(os.getenv('REQUEST_TIMEOUT', 30)),
            max_retries=int(os.getenv('MAX_RETRIES', 3))
        )
        self.search_engine = SemanticSearch(self.api_key)

    def research(self, query: str, urls: list = None) -> dict:
        """Perform complete research workflow"""
        logger.info(f"Starting research for: {query}")
        
        # Step 1: Decompose query
        sub_questions = self.query_processor.decompose_query(query)
        logger.info(f"Decomposed into {len(sub_questions)} sub-questions")
        
        # Step 2: Scrape web content
        if urls is None:
            # Default URLs for AI/ML research
            urls = [
                "https://en.wikipedia.org/wiki/Artificial_intelligence",
                "https://en.wikipedia.org/wiki/Machine_learning",
                "https://en.wikipedia.org/wiki/Deep_learning"
            ]
        
        logger.info(f"Scraping {len(urls)} URLs")
        scraped_content = self.web_scraper.scrape_multiple(urls)
        
        # Step 3: Convert scraped content to documents and index them
        documents = []
        for content in scraped_content:
            if content['success']:
                documents.append({
                    'title': content['title'],
                    'content': content['content'],
                    'url': content['url'],
                    'source': 'web_scraping'
                })
        
        if documents:
            self.search_engine.add_documents(documents)
            logger.info(f"Indexed {len(documents)} documents")
        
        # Step 4: Search for relevant information for each sub-question
        search_results = []
        for sub_q in sub_questions[:3]:  # Limit to first 3 sub-questions
            if self.search_engine.embeddings is not None:
                results = self.search_engine.search(sub_q, k=2)
                for result in results:
                    search_results.append({
                        'query': sub_q,
                        'source': result['document'].get('source', 'Unknown'),
                        'content': result['document'].get('content', '')[:500],  # Truncate
                        'score': result['score'],
                        'url': result['document'].get('url', '')
                    })
            else:
                # Fallback if no documents indexed
                search_results.append({
                    'query': sub_q,
                    'source': 'Fallback',
                    'content': f'Could not retrieve information for: {sub_q}',
                    'score': 0.0,
                    'url': ''
                })
        
        # Step 5: Synthesize response
        final_response = self.query_processor.synthesize_response(
            query,
            search_results
        )
        
        return {
            'original_query': query,
            'sub_questions': sub_questions,
            'search_results': search_results,
            'summary': final_response,
            'sources_scraped': len(scraped_content),
            'documents_indexed': len(documents)
        }


if __name__ == "__main__":
    agent = ResearchAgent()
    
    # Example research query
    result = agent.research("What are the latest advancements in AI and machine learning?")
    
    print("\n=== Research Results ===")
    print(f"Query: {result['original_query']}")
    print(f"\nSub-questions:")
    for q in result['sub_questions']:
        print(f"  - {q}")
    print(f"\nSummary:\n{result['summary']}")
