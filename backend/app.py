"""
FastAPI backend for AI Research & Task Automation Agent
"""
import os
import sys
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Add src directory to path to import modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from query_processor import QueryProcessor
from web_scraper import WebScraper
from semantic_search import SemanticSearch

load_dotenv()

app = FastAPI(
    title="AI Research & Task Automation Agent",
    description="Intelligent research and task automation API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger(__name__)

# Initialize services
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    logger.error("OPENAI_API_KEY not found in environment variables")
    raise ValueError("OPENAI_API_KEY environment variable is required")

query_processor = QueryProcessor(api_key)
web_scraper = WebScraper(
    timeout=int(os.getenv('REQUEST_TIMEOUT', 30)),
    max_retries=int(os.getenv('MAX_RETRIES', 3))
)
semantic_search = SemanticSearch(api_key)


class IndexRequest(BaseModel):
    documents: list
    urls: list = []  # Optional URLs to scrape and index


class ScrapeRequest(BaseModel):
    urls: list


# API endpoints
@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Research & Task Automation Agent"
    }


@app.post("/index")
async def index_documents(request: IndexRequest):
    """Index documents for semantic search"""
    try:
        documents = request.documents
        
        # If URLs provided, scrape them first
        if request.urls:
            scraped_docs = []
            for url in request.urls:
                scraped = web_scraper.scrape_url(url)
                if scraped['success']:
                    scraped_docs.append({
                        'title': scraped['title'],
                        'content': scraped['content'],
                        'url': scraped['url'],
                        'source': 'web'
                    })
            documents.extend(scraped_docs)
        
        semantic_search.add_documents(documents)
        
        return {
            "message": f"Indexed {len(documents)} documents",
            "document_count": len(documents)
        }
    except Exception as e:
        logger.error(f"Error indexing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scrape")
async def scrape_urls(request: ScrapeRequest):
    """Scrape URLs and return content"""
    try:
        results = web_scraper.scrape_multiple(request.urls)
        
        return {
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Error scraping URLs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search")
async def search(request: SearchRequest):
    """Search and retrieve relevant information"""
    try:
        if semantic_search.embeddings is None or len(semantic_search.documents) == 0:
            return {
                "query": request.query,
                "results": [],
                "count": 0,
                "message": "No documents indexed. Use /index endpoint to add documents first."
            }
        
        results = semantic_search.search(request.query, request.limit)
        
        return {
            "query": request.query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Error during search: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/decompose")
async def decompose(request: DecomposeRequest):
    """Break down complex query into sub-questions"""
    try:
        sub_questions = query_processor.decompose_query(request.query)
        
        return {
            "original_query": request.query,
            "sub_questions": sub_questions,
            "count": len(sub_questions)
        }
    except Exception as e:
        logger.error(f"Error decomposing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/research")
async def research(request: QueryRequest):
    """Full research workflow"""
    try:
        logger.info(f"Starting research for: {request.query}")
        
        # Step 1: Decompose query
        sub_questions = query_processor.decompose_query(request.query)
        logger.info(f"Decomposed into {len(sub_questions)} sub-questions")
        
        # Step 2: For each sub-question, perform web search and scraping
        # This is a simplified version - in production you'd use actual search APIs
        search_results = []
        
        # For demonstration, we'll use some sample URLs related to AI research
        sample_urls = [
            "https://en.wikipedia.org/wiki/Artificial_intelligence",
            "https://en.wikipedia.org/wiki/Machine_learning",
            "https://en.wikipedia.org/wiki/Deep_learning"
        ]
        
        # Scrape the URLs
        scraped_content = web_scraper.scrape_multiple(sample_urls)
        
        # Convert scraped content to documents for semantic search
        documents = []
        for content in scraped_content:
            if content['success']:
                documents.append({
                    'title': content['title'],
                    'content': content['content'],
                    'url': content['url'],
                    'source': 'web_scraping'
                })
        
        # Index the documents
        if documents:
            semantic_search.add_documents(documents)
        
        # Step 3: Search for relevant information for each sub-question
        all_search_results = []
        for sub_q in sub_questions[:3]:  # Limit to first 3 sub-questions
            if semantic_search.embeddings is not None:
                results = semantic_search.search(sub_q, k=2)
                all_search_results.extend(results)
            else:
                # Fallback if no documents indexed
                all_search_results.append({
                    'query': sub_q,
                    'document': {'content': f'Search results for: {sub_q}', 'source': 'fallback'},
                    'score': 0.5,
                    'rank': 1
                })
        
        # Step 4: Synthesize response
        formatted_results = []
        for result in all_search_results[:5]:  # Limit to top 5 results
            doc = result.get('document', {})
            formatted_results.append({
                'query': result.get('query', ''),
                'source': doc.get('source', 'Unknown'),
                'content': doc.get('content', '')[:500],  # Truncate for summary
                'score': result.get('score', 0)
            })
        
        summary = query_processor.synthesize_response(request.query, formatted_results)
        
        response = {
            "original_query": request.query,
            "sub_questions": sub_questions,
            "search_results": formatted_results,
            "summary": summary,
            "sources_scraped": len(scraped_content),
            "documents_indexed": len(documents)
        }
        
        if request.include_sources:
            response["scraped_content"] = scraped_content
        
        return response
        
    except Exception as e:
        logger.error(f"Error during research: {e}")
        raise HTTPException(status_code=500, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def status():
    """Get system status"""
    return {
        "status": "operational",
        "service": "AI Research Agent",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv('API_PORT', 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
