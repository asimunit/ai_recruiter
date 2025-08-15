# 🎯 AI Recruitr - Smart Resume Matcher

**AI-powered recruitment system that uses semantic matching to find the best-fit candidates using FAISS vector database and Gemini AI.**

![AI Recruitr Banner](https://img.shields.io/badge/AI%20Recruitr-Smart%20Resume%20Matcher-blue?style=for-the-badge&logo=artificial-intelligence)

## ✨ Features

- 🎯 **Semantic Resume Matching** - Goes beyond keyword matching using AI embeddings
- 🚀 **Fast Vector Search** - Lightning-fast similarity search with FAISS
- 🤖 **AI-Powered Explanations** - Gemini AI generates detailed match explanations
- 📄 **Multi-Format Support** - Process PDF, DOCX, and TXT resume files
- 💡 **Clean Architecture** - Modular microservices design with FastAPI + Streamlit
- 📊 **Analytics Dashboard** - Comprehensive insights and matching analytics
- ⚡ **Real-Time Processing** - Instant resume processing and matching
- 🔍 **Advanced Filtering** - Filter by skills, experience, location, and more

## 🏗️ Architecture

```
ai_recruitr/
├── backend/              # FastAPI microservices
│   ├── services/         # Core business logic
│   ├── api/             # REST API endpoints
│   └── models/          # Pydantic schemas
├── frontend/            # Streamlit UI
│   ├── pages/           # UI pages
│   └── components/      # Reusable components
├── config/              # Configuration
├── data/                # Data storage
└── utils/               # Utilities
```

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | FastAPI + Python 3.9+ |
| **Frontend** | Streamlit |
| **Embeddings** | mxbai-embed-large-v1 (Hugging Face) |
| **Vector DB** | FAISS |
| **LLM** | Google Gemini |
| **Resume Parsing** | PyMuPDF, python-docx |
| **Data Processing** | Pandas, NumPy |

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Git
- Google Gemini API key

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/ai-recruitr.git
cd ai-recruitr
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
# Required: Google Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Customize settings
API_HOST=localhost
API_PORT=8000
STREAMLIT_HOST=localhost
STREAMLIT_PORT=8501
LOG_LEVEL=INFO
```

### 5. Get Your Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy and paste it into your `.env` file

### 6. Run the Application

#### Option A: Run Both Services (Recommended)

```bash
# Terminal 1: Start FastAPI backend
python -m backend.main

# Terminal 2: Start Streamlit frontend
streamlit run frontend/app.py
```

#### Option B: Using Scripts (Windows)

```bash
# Start backend
start_backend.bat

# Start frontend  
start_frontend.bat
```

#### Option C: Using Scripts (macOS/Linux)

```bash
# Start backend
./start_backend.sh

# Start frontend
./start_frontend.sh
```

### 7. Access the Application

- **Streamlit UI**: http://localhost:8501
- **FastAPI Docs**: http://localhost:8000/docs
- **API Health**: http://localhost:8000/health

## 📖 Usage Guide

### 1. Upload Resumes

1. Navigate to **"📄 Upload Resumes"** page
2. Drag and drop PDF/DOCX resume files
3. Click **"🚀 Process All Files"**
4. Wait for processing to complete

### 2. Match Job Descriptions

1. Go to **"🔍 Job Matching"** page
2. Fill in the job description form:
   - Job title
   - Detailed job description
   - Required skills
   - Experience level
3. Click **"🔍 Find Matching Resumes"**
4. Review the matching results

### 3. Analyze Results

1. Visit **"📊 Results & Analytics"** page
2. View current matching results
3. Explore analytics and insights
4. Export data in JSON/CSV format

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | **Required** |
| `API_HOST` | FastAPI host | `localhost` |
| `API_PORT` | FastAPI port | `8000` |
| `STREAMLIT_HOST` | Streamlit host | `localhost` |
| `STREAMLIT_PORT` | Streamlit port | `8501` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `MAX_FILE_SIZE` | Max upload size (bytes) | `10485760` (10MB) |
| `TOP_K_MATCHES` | Default max matches | `10` |
| `SIMILARITY_THRESHOLD` | Default threshold | `0.7` |

### Model Configuration

The system uses:
- **Embedding Model**: `mixedbread-ai/mxbai-embed-large-v1`
- **LLM**: `gemini-pro`
- **Vector Dimension**: 1024
- **Max Sequence Length**: 512 tokens

## 🧪 API Documentation

### Upload Resume

```bash
curl -X POST "http://localhost:8000/api/v1/upload-resume" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@resume.pdf"
```

### Match Job Description

```bash
curl -X POST "http://localhost:8000/api/v1/match-job" \
     -H "Content-Type: application/json" \
     -d '{
       "job_description": {
         "title": "Senior Python Developer",
         "description": "We are looking for...",
         "skills_required": ["Python", "Django", "PostgreSQL"]
       },
       "top_k": 10,
       "similarity_threshold": 0.7
     }'
```

### Get Resume Count

```bash
curl "http://localhost:8000/api/v1/resumes/count"
```

## 📁 Project Structure

```
ai_recruitr/
├── 📁 backend/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── 📁 api/
│   │   ├── __init__.py
│   │   └── routes.py           # API endpoints
│   ├── 📁 models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic models
│   └── 📁 services/
│       ├── __init__.py
│       ├── embedding_service.py # mxbai embeddings
│       ├── faiss_service.py    # Vector database
│       ├── gemini_service.py   # Gemini LLM
│       └── resume_parser.py    # Resume processing
├── 📁 frontend/
│   ├── __init__.py
│   ├── app.py                  # Streamlit main app
│   ├── 📁 pages/
│   │   ├── __init__.py
│   │   ├── upload_resume.py    # Upload interface
│   │   ├── job_matching.py     # Matching interface
│   │   └── results.py          # Analytics dashboard
│   └── 📁 components/
│       ├── __init__.py
│       └── ui_components.py    # Reusable UI components
├── 📁 config/
│   ├── __init__.py
│   └── settings.py             # Configuration
├── 📁 data/
│   ├── 📁 resumes/             # Uploaded resumes
│   ├── 📁 faiss_index/         # FAISS index files
│   └── 📁 processed/           # Processed data
├── 📁 utils/
│   ├── __init__.py
│   └── helpers.py              # Utility functions
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## 🚨 Troubleshooting

### Common Issues

#### 1. "GEMINI_API_KEY is required" Error

**Problem**: Missing or invalid Gemini API key.

**Solution**:
```bash
# Check your .env file
cat .env

# Ensure GEMINI_API_KEY is set
echo $GEMINI_API_KEY
```

#### 2. FAISS Installation Issues

**Problem**: FAISS installation fails on some systems.

**Solution**:
```bash
# Try installing CPU version specifically
pip install faiss-cpu==1.7.4

# On macOS with Apple Silicon:
conda install -c pytorch faiss-cpu
```

#### 3. Resume Text Extraction Fails

**Problem**: PDF text extraction returns empty content.

**Solution**:
- Ensure PDFs are text-based, not scanned images
- Try converting PDFs to text format first
- Check file permissions

#### 4. Streamlit Connection Error

**Problem**: Frontend can't connect to FastAPI backend.

**Solution**:
```bash
# Check if backend is running
curl http://localhost:8000/health

# Verify ports in .env file
grep -E "(API_PORT|STREAMLIT_PORT)" .env
```

#### 5. Slow Embedding Generation

**Problem**: Embedding generation takes too long.

**Solution**:
- Check if you have GPU available
- Reduce batch size in processing
- Consider using smaller embedding model for testing

### Debug Mode

Enable debug logging:

```bash
# Set in .env
LOG_LEVEL=DEBUG

# Or run with debug
python -m backend.main --log-level DEBUG
```

## 🔒 Security Considerations

### Production Deployment

- [ ] Change default ports
- [ ] Set up proper CORS origins
- [ ] Use environment-specific API keys
- [ ] Enable HTTPS
- [ ] Implement rate limiting
- [ ] Add authentication
- [ ] Secure file uploads
- [ ] Monitor API usage

### Data Privacy

- [ ] Implement data retention policies
- [ ] Add resume deletion functionality
- [ ] Encrypt sensitive data
- [ ] Audit API access
- [ ] Comply with GDPR/privacy laws

## 🚀 Advanced Features

### Scaling

- **Database**: Replace FAISS with Pinecone/Weaviate for production
- **Caching**: Add Redis for embedding caching
- **Queue**: Use Celery for async processing
- **Load Balancing**: Deploy with multiple API instances

### Enhancements

- **Multi-language Support**: Add language detection
- **Resume Scoring**: Implement comprehensive scoring
- **Bias Detection**: Add fairness checking
- **Integration**: Connect with LinkedIn, ATS systems
- **Real-time Updates**: WebSocket for live updates

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Format code
black .
isort .

# Lint code
flake8 .
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Hugging Face](https://huggingface.co/) for mxbai embeddings
- [Google](https://ai.google.dev/) for Gemini LLM
- [Facebook Research](https://github.com/facebookresearch/faiss) for FAISS
- [FastAPI](https://fastapi.tiangolo.com/) team
- [Streamlit](https://streamlit.io/) team

## 📞 Support

- 📧 Email: support@ai-recruitr.com
- 💬 Discord: [AI Recruitr Community](https://discord.gg/ai-recruitr)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/ai-recruitr/issues)
- 📖 Documentation: [Full Docs](https://docs.ai-recruitr.com)

---

**Made with ❤️ for smarter recruiting**

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-Latest-red.svg)
![FAISS](https://img.shields.io/badge/FAISS-1.7.4-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)