# AI Geometry Tutor Backend

A Vietnamese geometry tutoring system powered by AI, built with FastAPI, LangGraph, and Google Gemini.

## Architecture Overview

The backend follows a clean, modular architecture:

```
backend/
├── src/                          # Source code root
│   ├── api/                      # FastAPI application layer
│   │   ├── routes/              # API route handlers
│   │   ├── models/              # Request/response models
│   │   ├── middleware/          # Cross-cutting concerns
│   │   └── dependencies.py      # Dependency injection
│   ├── geometry_tutor/          # Core tutoring logic
│   │   ├── agents.py            # LangGraph agents
│   │   ├── core.py              # State management
│   │   ├── graph.py             # Workflow definition
│   │   └── llm_utils.py         # LLM integrations
│   ├── services/                # Business logic services
│   │   ├── llm_service.py       # Language model service
│   │   ├── session_service.py   # Session management
│   │   ├── tutor_service.py     # Core tutoring service
│   │   └── visualization_service.py # Asymptote integration
│   └── shared/                  # Shared utilities
│       ├── config.py            # Configuration management
│       ├── logging.py           # Logging setup
│       └── exceptions.py        # Custom exceptions
├── scripts/                     # Utility scripts
├── notebooks/                   # Jupyter notebooks
└── requirements.txt            # Python dependencies
```

## Features

- **Interactive Vietnamese Geometry Tutoring**: AI-powered step-by-step guidance
- **Multiple Input Modes**: Text problems and image-based problem extraction
- **Progressive Hints**: 3-level hint system for scaffolded learning
- **Solution Validation**: AI assessment of student solutions with feedback
- **Geometric Visualizations**: Asymptote-generated diagrams
- **Session Management**: Persistent tutoring sessions with state tracking
- **RESTful API**: Clean REST endpoints for frontend integration

## Quick Start

### Prerequisites

- Python 3.9+
- Google Gemini API key
- Docker (optional, for containerized deployment)

### Local Development

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd Math-tutor-VAS/backend
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   export GOOGLE_API_KEY="your-gemini-api-key"
   ```

4. **Run the server**:
   ```bash
   python scripts/run_api_server.py
   ```

5. **Access the API**:
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Health check: http://localhost:8000/health

### Docker Deployment

```bash
# Build the image
docker build -t geometry-tutor-backend .

# Run with environment variables
docker run -e GOOGLE_API_KEY="your-key" -p 8000:8000 geometry-tutor-backend
```

### Using Docker Compose

```bash
# Set your API key in environment
export GOOGLE_API_KEY="your-key"

# Start services
docker-compose up --build
```

## API Endpoints

### Session Management
- `POST /sessions` - Create new tutoring session
- `GET /status?session_id=<id>` - Get session status
- `DELETE /sessions` - Delete session

### Tutoring Interactions
- `POST /hint` - Request progressive hints
- `POST /validate` - Submit solution for validation
- `GET /solution?session_id=<id>` - Get complete solution

### Visualization
- `GET /illustration?session_id=<id>` - Generate geometric diagram

### Utility
- `GET /health` - Health check
- `GET /test` - Simple connectivity test

## Configuration

The application uses environment-based configuration:

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Gemini API key | **Required** |
| `LLM_MODEL` | Gemini model name | `gemini-2.0-flash-exp` |
| `LLM_TEMPERATURE` | AI creativity level | `0.1` |
| `HOST` | Server host | `127.0.0.1` |
| `PORT` | Server port | `8000` |
| `SESSION_TIMEOUT_HOURS` | Session expiry | `2` |
| `LOG_LEVEL` | Logging level | `INFO` |

## Development

### Code Structure

The codebase follows clean architecture principles:

- **API Layer** (`src/api/`): FastAPI routes, middleware, and models
- **Service Layer** (`src/services/`): Business logic and external integrations
- **Core Layer** (`src/geometry_tutor/`): Domain logic and LangGraph workflows
- **Shared** (`src/shared/`): Cross-cutting utilities and configuration

### Key Components

1. **LangGraph Workflow**: State-driven tutoring process with AI agents
2. **Session Management**: Repository pattern with pluggable storage
3. **Service Abstractions**: Clean interfaces for LLM, visualization, etc.
4. **Configuration Management**: Type-safe settings with validation
5. **Error Handling**: Structured exceptions and proper HTTP responses

### Running Tests

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests (when implemented)
pytest

# Code formatting
black src/
isort src/

# Type checking
mypy src/
```

## Contributing

1. Follow the existing code structure and patterns
2. Use type hints throughout
3. Add docstrings for public methods
4. Test new features thoroughly
5. Update documentation as needed

## License

MIT License - see LICENSE file for details.