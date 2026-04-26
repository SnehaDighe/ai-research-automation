# AI Research & Task Automation Agent

An intelligent automation tool that simplifies research by aggregating information from the web and generating concise summaries. Break down complex queries into manageable steps and leverage LLM APIs for intelligent response generation.

## Product Case Study

📖 **[Read the full product case study](PRODUCT_CASE_STUDY.md)** - Learn about the problem this solves, technical implementation, and business impact.

## Features

- **Web Scraping**: Extract information from multiple web sources
- **Query Decomposition**: Break down complex queries into simpler steps
- **Smart Summarization**: Generate concise, structured summaries
- **Semantic Search**: Retrieve relevant information efficiently
- **FastAPI Backend**: High-performance async REST API
- **Docker Support**: Easy containerization and deployment

## Tech Stack

- **Backend**: Python (FastAPI)
- **LLM & APIs**: OpenAI API
- **Web Scraping**: BeautifulSoup, Requests
- **Search**: Semantic search with vector embeddings
- **Containerization**: Docker
- **API Documentation**: Swagger/OpenAPI

## Project Structure

```
ai-research-automation/
├── src/
│   ├── main.py
│   ├── query_processor.py
│   ├── web_scraper.py
│   ├── semantic_search.py
│   └── utils.py
├── backend/
│   ├── app.py (FastAPI)
│   ├── models.py
│   └── services/
├── config/
│   └── config.py
├── requirements.txt
├── Dockerfile
├── .env.example
└── README.md
```

## Installation

### Prerequisites

- Python 3.9+
- Docker (optional)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-research-automation.git
cd ai-research-automation
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your API keys
```

## Usage

### Run FastAPI Server

```bash
cd backend
python -m uvicorn app:app --reload
```

Access API documentation at: `http://localhost:8000/docs`

### Run as CLI Tool

```bash
python src/main.py --query "What are the latest developments in AI?"
```

## Docker

Build and run with Docker:

```bash
docker build -t ai-research-agent .
docker run -p 8000:8000 --env-file .env ai-research-agent
```

## API Endpoints

- `POST /search` - Search and summarize information
- `POST /decompose` - Break down complex queries
- `GET /status` - System status
- `POST /research` - Full research workflow

## Contributing

Contributions welcome! Please create a pull request with your changes.

## License

MIT License
