"""
Query processor for breaking down complex queries into steps
"""
import logging
from typing import List
import openai

logger = logging.getLogger(__name__)


class QueryProcessor:
    """Break down complex queries into manageable steps"""

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        openai.api_key = api_key

    def decompose_query(self, query: str) -> List[str]:
        """Break down a complex query into sub-questions"""
        logger.info(f"Decomposing query: {query}")
        
        prompt = f"""Break down this complex research query into 3-5 specific, actionable sub-questions:

Query: {query}

Provide only the sub-questions, one per line, without numbering."""
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500
            )
            
            text = response.choices[0].message['content']
            sub_questions = [q.strip() for q in text.split('\n') if q.strip()]
            
            logger.info(f"Generated {len(sub_questions)} sub-questions")
            return sub_questions
        except Exception as e:
            logger.error(f"Error decomposing query: {e}")
            return [query]  # Return original query if decomposition fails

    def synthesize_response(self, query: str, search_results: List[dict]) -> str:
        """Synthesize search results into a coherent response"""
        logger.info("Synthesizing response from search results")
        
        # Format search results
        formatted_results = "\n\n".join([
            f"Source: {result.get('source', 'Unknown')}\nContent: {result.get('content', '')}"
            for result in search_results[:5]
        ])
        
        prompt = f"""Based on these search results, provide a comprehensive, concise answer to the query:

Query: {query}

Search Results:
{formatted_results}

Provide a well-structured answer with key insights."""
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message['content']
        except Exception as e:
            logger.error(f"Error synthesizing response: {e}")
            return "Unable to generate response"
