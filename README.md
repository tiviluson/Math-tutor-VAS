# AI Geometry Tutor with Advanced Visualization (Math-tutor-VAS)

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-15.3+-black.svg)](https://nextjs.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.5+-purple.svg)](https://langchain-ai.github.io/langgraph/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)

An intelligent AI-powered geometry tutor that combines **LangGraph state management**, **Google Gemini AI**, and **advanced visualization with Asymptote** to provide interactive Vietnamese geometry problem solving with real-time hints, solution validation, and professional geometric figure generation.

## 🌟 Key Features

### 🤖 **AI-Powered Tutoring System**
- **Multi-Modal Input**: Supports both text problems and image uploads for problem extraction
- **Vietnamese Language Support**: Native Vietnamese geometry problem parsing and explanation
- **Progressive Hints**: Intelligent 3-level hint system that guides without giving away answers
- **Solution Validation**: AI-powered scoring and feedback on student solutions
- **Image Recognition**: Extract geometry problems directly from uploaded images

### 📊 **Advanced Visualization Engine**
- **Asymptote Integration**: Professional mathematical diagrams using Asymptote rendering
- **AI-Generated Figures**: Automatic geometric figure creation from problem descriptions
- **Interactive Plots**: Real-time visualization during problem-solving sessions
- **Multiple Geometry Types**: Support for triangles, circles, quadrilaterals, complex constructions

### 🏗️ **Modern Architecture**
- **LangGraph Workflow**: Graph-based state management for complex AI interactions
- **FastAPI Backend**: High-performance REST API with automatic OpenAPI documentation
- **Next.js Frontend**: Modern React-based user interface with TypeScript
- **Containerized Deployment**: Docker-ready for easy development and production deployment

## 🏛️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js       │    │   FastAPI       │    │   LangGraph     │
│   Frontend      │◄──►│   Backend       │◄──►│   Workflow      │
│                 │    │                 │    │                 │
│ • React UI      │    │ • REST API      │    │ • State Mgmt    │
│ • TypeScript    │    │ • CORS Support  │    │ • AI Agents     │
│ • Tailwind CSS  │    │ • File Upload   │    │ • Node Routing  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Google        │
                    │   Gemini AI     │
                    │                 │
                    │ • Problem Parse │
                    │ • Hint Generate │
                    │ • Solution Val. │
                    │ • Image Extract │
                    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- **Docker & Docker Compose** (recommended)
- **Python 3.11+** (for local development)
- **Node.js 18+** (for frontend development)
- **Google API Key** (for Gemini AI access)

### 🐳 Docker Deployment (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/Math-tutor-VAS.git
   cd Math-tutor-VAS
   ```

2. **Configure environment variables:**
   ```bash
   cd backend
   cp .env.template .env
   # Edit .env and add your GOOGLE_API_KEY
   ```

3. **Launch with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

4. **Access the application:**
   - **API Server**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs
   - **Frontend**: Configure separately or use existing Dash app

### 💻 Local Development

#### Backend Setup
```bash
cd backend
pip install -r requirements.txt
export GOOGLE_API_KEY="your-api-key-here"
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup (Next.js)
```bash
cd frontend
npm install
npm run dev
# Available at http://localhost:3000
```

#### Alternative Frontend (Dash)
```bash
cd app
pip install dash dash-bootstrap-components
python app.py
# Available at http://localhost:8050
```

## 📖 Usage Guide

### 🔤 **Text-Based Problem Solving**

1. **Create a new session with a Vietnamese geometry problem:**
   ```json
   POST /sessions
   {
     "problem_text": "Cho tam giác ABC có AB = 3, BC = 4, CA = 5. Chứng minh rằng tam giác ABC vuông tại B.",
     "is_img": false
   }
   
   Response:
   {
     "session_id": "uuid-string",
     "message": "Session created successfully",
     "total_questions": 1
   }
   ```

2. **Get progressive hints:**
   ```json
   POST /hint
   {
     "session_id": "uuid-string"
   }
   
   Response:
   {
     "success": true,
     "hint_text": "Hãy xem xét mối quan hệ giữa các cạnh của tam giác...",
     "hint_level": 1,
     "max_hints_reached": false
   }
   ```

3. **Submit solution for validation:**
   ```json
   POST /validate
   {
     "session_id": "uuid-string",
     "user_input": "Áp dụng định lý Pythagoras: AB² + BC² = 3² + 4² = 9 + 16 = 25 = 5² = CA²"
   }
   
   Response:
   {
     "success": true,
     "is_correct": true,
     "feedback": "Chính xác! Bạn đã áp dụng đúng định lý Pythagoras...",
     "score": 95,
     "moved_to_next": true,
     "session_complete": true
   }
   ```

4. **Get complete solution:**
   ```json
   GET /solution
   {
     "session_id": "uuid-string"
   }
   
   Response:
   {
     "success": true,
     "solution_text": "Giải chi tiết: Ta có AB = 3, BC = 4, CA = 5...",
     "moved_to_next": true,
     "session_complete": true
   }
   ```

### 🖼️ **Image-Based Problem Extraction**

```json
POST /sessions
{
  "is_img": true,
  "img": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD..."
}

Response:
{
  "session_id": "uuid-string",
  "message": "Session created successfully",
  "total_questions": 2
}
```

### 📊 **Visualization Generation**

```json
GET /illustration
{
  "session_id": "uuid-string"
}

Response:
{
  "success": true,
  "message": "Illustration generated successfully",
  "b64_string_viz": "iVBORw0KGgoAAAANSUhEUgAAAB..."
}
```

### 📋 **Session Management**

```json
# Get session status
GET /status
{
  "session_id": "uuid-string"
}

# List all active sessions
GET /sessions

# Delete a session
DELETE /sessions
{
  "session_id": "uuid-string"
}
```

## 🎯 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/sessions` | Create new problem session (text or image) |
| `GET` | `/status` | Get current session status and progress |
| `POST` | `/hint` | Request progressive hint for current question |
| `POST` | `/validate` | Submit solution for validation and scoring |
| `GET` | `/solution` | Get complete solution for current question |
| `GET` | `/illustration` | Generate geometric visualization |
| `GET` | `/sessions` | List all active sessions (admin) |
| `DELETE` | `/sessions` | Delete a specific session |
| `GET` | `/health` | Health check endpoint |
| `GET` | `/docs` | Interactive API documentation (Swagger UI) |
| `GET` | `/redoc` | Alternative API documentation (ReDoc) |

## 🧠 LangGraph Workflow Architecture

### **Core State Management**
```python
class GraphState(TypedDict):
    # Problem Setup
    original_problem: str
    parsed_elements: Dict[str, Any]
    questions: List[str]
    
    # Dynamic State
    current_question_index: int
    known_facts: List[str]
    ai_discovered_facts: List[str]
    reasoning_chain: List[Dict[str, str]]
    
    # User Interaction
    user_solution_attempt: str
    hint_level: int
    generated_hints: List[str]
    validation_score: int
    
    # Visualization
    illustration_steps: List[str]
    
    # Control Flow
    user_action: str
    session_complete: bool
```

### **AI Agent Nodes**
- **📝 Parsing Agent**: Extracts structured data from Vietnamese geometry problems
- **🎯 Reasoning Agent**: Generates step-by-step solution paths
- **💡 Hint Agent**: Creates progressive educational hints
- **✅ Validation Agent**: Scores and provides feedback on solutions
- **🖼️ Visualization Agent**: Generates geometric figures and diagrams

### **Workflow Graph**
```
[START] → Parse Problem → Generate Solution → Setup Questions
    ↓
Get User Input → Classify Input → Route Action
    ↓               ↓               ↓
Process Hint ← Generate Hint    Validate Solution
    ↓               ↓               ↓
Update State ←  Update State   Update State
    ↓               ↓               ↓
Check Complete → Check Complete → Check Complete
    ↓
[END/NEXT QUESTION]
```

## 🛠️ Technology Stack

### **Backend Technologies**
- **🐍 Python 3.11+**: Core backend language
- **⚡ FastAPI**: Modern, fast web framework for APIs
- **🤖 Google Gemini**: Large language model for AI reasoning
- **📊 LangGraph**: State management and workflow orchestration
- **📈 Matplotlib**: Mathematical plotting and visualization
- **🖼️ Asymptote**: Professional mathematical diagram generation
- **🐳 Docker**: Containerization and deployment

### **Frontend Technologies**
- **⚛️ Next.js 15.3**: React-based frontend framework
- **📘 TypeScript**: Type-safe JavaScript development
- **🎨 Tailwind CSS**: Utility-first CSS framework
- **📊 Dash**: Alternative Python-based web interface
- **🎭 Radix UI**: Accessible component library

### **AI & ML Libraries**
- **🔗 LangChain**: LLM application framework
- **📋 Pydantic**: Data validation and serialization
- **🔢 NumPy**: Numerical computing
- **📊 Matplotlib**: Plotting and visualization

## 📁 Project Structure

```
Math-tutor-VAS/
├── 📁 backend/                 # FastAPI backend server
│   ├── 📁 api/                # REST API endpoints
│   │   ├── main.py           # FastAPI application entry
│   │   ├── tutor.py          # API tutor implementation
│   │   └── 📁 asymptote/      # Visualization engine
│   ├── 📁 geometry_tutor/     # Core LangGraph implementation
│   │   ├── agents.py         # AI agent node implementations
│   │   ├── core.py           # State management & data structures
│   │   ├── graph.py          # LangGraph workflow definition
│   │   ├── prompts.py        # AI prompt templates
│   │   └── llm_utils.py      # LLM initialization & chains
│   ├── requirements.txt      # Python dependencies
│   ├── Dockerfile           # Backend container configuration
│   └── docker-compose.yml   # Multi-service orchestration
├── 📁 frontend/               # Next.js frontend application
│   ├── 📁 src/               # TypeScript source code
│   │   ├── 📁 app/           # Next.js app router
│   │   └── 📁 components/    # React components
│   ├── package.json         # Node.js dependencies
│   └── next.config.ts       # Next.js configuration
├── 📁 app/                   # Alternative Dash frontend
│   ├── app.py              # Dash application entry
│   ├── 📁 pages/            # Dash page components
│   └── 📁 assets/           # Static assets (CSS, JS)
└── 📄 README.md             # Project documentation
```

## 🔧 Configuration

### **Environment Variables**

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GOOGLE_API_KEY` | Google Gemini API key | - | ✅ |
| `LLM_TEMPERATURE` | AI response creativity (0.0-1.0) | 0.1 | ❌ |
| `MAX_OUTPUT_TOKENS` | Maximum AI response length | 2048 | ❌ |
| `ASYMPTOTE_TEXPATH` | LaTeX binary path | /usr/bin | ❌ |
| `ASYMPTOTE_MAGICKPATH` | ImageMagick path | /usr/bin | ❌ |

### **Docker Configuration**
```yaml
# docker-compose.yml
services:
  geometry-tutor:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    volumes:
      - asymptote_temp:/tmp/asymptote
```

## 🧪 Development

### **Running Tests**
```bash
# Backend tests
cd backend
python -m pytest tests/

# Frontend tests  
cd frontend
npm run test
```

### **Code Quality**
```bash
# Python formatting
black backend/
flake8 backend/

# TypeScript formatting
cd frontend
npm run lint
npm run format
```

### **Development Workflow**
1. **Backend**: FastAPI auto-reload on file changes
2. **Frontend**: Next.js hot module replacement
3. **Docker**: Multi-stage builds for optimization

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open Pull Request**

### **Development Guidelines**
- Follow PEP 8 for Python code
- Use TypeScript for all frontend code
- Write comprehensive docstrings
- Add tests for new features
- Update documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini**: Advanced AI language model
- **LangGraph**: State management framework
- **FastAPI**: High-performance web framework
- **Next.js**: React-based frontend framework
- **Asymptote**: Mathematical diagram generation

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-username/Math-tutor-VAS/issues)
- **Documentation**: [API Docs](http://localhost:8000/docs)
- **Community**: [Discussions](https://github.com/your-username/Math-tutor-VAS/discussions)

---

**Built with ❤️ for Vietnamese geometry education**