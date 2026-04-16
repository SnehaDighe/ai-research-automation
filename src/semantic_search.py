"""
Semantic search module for finding relevant information
"""
import logging
from typing import List, Dict
import numpy as np
import openai

logger = logging.getLogger(__name__)


class SemanticSearch:
    """Perform semantic search on documents"""

    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        self.api_key = api_key
        self.model = model
        openai.api_key = api_key
        self.documents = []
        self.embeddings = None

    def add_documents(self, documents: List[Dict]):
        """Add documents to the search index"""
        self.documents = documents
        logger.info(f"Added {len(documents)} documents")
        
        # Generate embeddings
        texts = [doc.get('content', '') for doc in documents]
        self.embeddings = self._generate_embeddings(texts)

    def _generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for texts"""
        try:
            embeddings = []
            for i, text in enumerate(texts):
                if not text:
                    embeddings.append([0] * 1536)  # Default embedding size
                    continue
                
                response = openai.Embedding.create(
                    input=text[:2000],  # Limit to 2000 chars
                    model=self.model
                )
                embeddings.append(response['data'][0]['embedding'])
                
                if (i + 1) % 10 == 0:
                    logger.info(f"Generated {i + 1}/{len(texts)} embeddings")
            
            return np.array(embeddings)
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return np.array([])

    def search(self, query: str, k: int = 5) -> List[Dict]:
        """Search for relevant documents"""
        if self.embeddings is None or len(self.embeddings) == 0:
            logger.warning("No documents indexed for search")
            return []
        
        try:
            # Generate query embedding
            response = openai.Embedding.create(
                input=query,
                model=self.model
            )
            query_embedding = np.array(response['data'][0]['embedding'])
            
            # Calculate similarities
            similarities = np.dot(self.embeddings, query_embedding)
            top_indices = np.argsort(similarities)[-k:][::-1]
            
            results = []
            for idx in top_indices:
                if idx < len(self.documents):
                    results.append({
                        'document': self.documents[idx],
                        'score': float(similarities[idx]),
                        'rank': len(results) + 1
                    })
            
            return results
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return []
