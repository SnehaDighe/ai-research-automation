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

    def research(self, query: str) -> dict:
        """Perform complete research workflow"""
        logger.info(f"Starting research for: {query}")
        
        # Step 1: Decompose query
        sub_questions = self.query_processor.decompose_query(query)
        logger.info(f"Decomposed into {len(sub_questions)} sub-questions")
        
        # Step 2: Search for answers (simulation)
        search_results = []
        for sub_q in sub_questions[:3]:  # Limit to first 3
            # Simulate search results
            search_results.append({
                'query': sub_q,
                'source': 'Research Database',
                'content': f'Information about: {sub_q}'
            })
        
        # Step 3: Synthesize response
        final_response = self.query_processor.synthesize_response(
            query,
            search_results
        )
        
        return {
            'original_query': query,
            'sub_questions': sub_questions,
            'search_results': search_results,
            'summary': final_response
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
