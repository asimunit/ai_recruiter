# 🔄 AI Recruitr - Workflow & Architecture

This document provides a comprehensive overview of AI Recruitr's architecture, workflows, and component interactions using visual diagrams.

## 📋 Table of Contents

- [System Architecture](#system-architecture)
- [Component Overview](#component-overview)
- [Resume Processing Workflow](#resume-processing-workflow)
- [Job Matching Workflow](#job-matching-workflow)
- [API Request Flow](#api-request-flow)
- [Data Flow Architecture](#data-flow-architecture)
- [User Journey Flow](#user-journey-flow)
- [Service Dependencies](#service-dependencies)
- [Database Schema](#database-schema)
- [Deployment Architecture](#deployment-architecture)

---

## 🏗️ System Architecture

### High-Level Architecture Overview

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[Streamlit UI]
        COMP[UI Components]
        PAGES[Pages]
    end
    
    subgraph "Backend Layer"
        API[FastAPI Server]
        ROUTES[API Routes]
        MIDDLEWARE[Middleware]
    end
    
    subgraph "Service Layer"
        ES[Embedding Service]
        FS[FAISS Service]
        GS[Gemini Service]
        PS[Parser Service]
    end
    
    subgraph "AI/ML Layer"
        MXBAI[mxbai Embeddings]
        GEMINI[Google Gemini]
        FAISS[FAISS Vector DB]
    end
    
    subgraph "Storage Layer"
        FILES[File Storage]
        INDEX[FAISS Index]
        META[Metadata JSON]
        LOGS[Logs]
    end
    
    subgraph "External Services"
        HF[Hugging Face]
        GOOGLE[Google AI]
    end
    
    %% Frontend connections
    UI --> COMP
    UI --> PAGES
    UI --> API
    
    %% Backend connections
    API --> ROUTES
    API --> MIDDLEWARE
    ROUTES --> ES
    ROUTES --> FS
    ROUTES --> GS
    ROUTES --> PS
    
    %% Service connections
    ES --> MXBAI
    ES --> HF
    GS --> GEMINI
    GS --> GOOGLE
    FS --> FAISS
    PS --> FILES
    
    %% Storage connections
    FS --> INDEX
    FS --> META
    PS --> FILES
    API --> LOGS
    
    %% Styling
    classDef frontend fill:#e1f5fe
    classDef backend fill:#f3e5f5
    classDef service fill:#e8f5e8
    classDef ai fill:#fff3e0
    classDef storage fill:#fce4ec
    classDef external fill:#f1f8e9
    
    class UI,COMP,PAGES frontend
    class API,ROUTES,MIDDLEWARE backend
    class ES,FS,GS,PS service
    class MXBAI,GEMINI,FAISS ai
    class FILES,INDEX,META,LOGS storage
    class HF,GOOGLE external
```

---

## 🧩 Component Overview

### Core Components & Responsibilities

```mermaid
graph LR
    subgraph "Frontend Components"
        APP[app.py<br/>Main Application]
        UPLOAD[upload_resume.py<br/>File Upload UI]
        MATCH[job_matching.py<br/>Matching Interface]
        RESULTS[results.py<br/>Analytics Dashboard]
        UI_COMP[ui_components.py<br/>Reusable Components]
    end
    
    subgraph "Backend Components"
        MAIN[main.py<br/>FastAPI Server]
        ROUTES_API[routes.py<br/>API Endpoints]
        SCHEMAS[schemas.py<br/>Data Models]
    end
    
    subgraph "Service Components"
        EMBED[embedding_service.py<br/>Vector Generation]
        FAISS_SVC[faiss_service.py<br/>Vector Search]
        GEMINI_SVC[gemini_service.py<br/>AI Explanations]
        PARSER[resume_parser.py<br/>Text Extraction]
    end
    
    subgraph "Configuration"
        SETTINGS[settings.py<br/>App Configuration]
        ENV[.env<br/>Environment Variables]
    end
    
    subgraph "Utilities"
        HELPERS[helpers.py<br/>Utility Functions]
    end
    
    %% Frontend flow
    APP --> UPLOAD
    APP --> MATCH
    APP --> RESULTS
    APP --> UI_COMP
    
    %% Backend flow
    MAIN --> ROUTES_API
    ROUTES_API --> SCHEMAS
    
    %% Service interactions
    ROUTES_API --> EMBED
    ROUTES_API --> FAISS_SVC
    ROUTES_API --> GEMINI_SVC
    ROUTES_API --> PARSER
    
    %% Configuration
    MAIN --> SETTINGS
    SETTINGS --> ENV
    
    %% Utilities
    PARSER --> HELPERS
    EMBED --> HELPERS
    
    %% Cross-layer connections
    APP -.->|HTTP Requests| ROUTES_API
    UPLOAD -.->|File Upload| ROUTES_API
    MATCH -.->|Job Matching| ROUTES_API
    RESULTS -.->|Analytics| ROUTES_API
```

---

## 📄 Resume Processing Workflow

### Complete Resume Upload & Processing Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend as Streamlit UI
    participant API as FastAPI
    participant Parser as Resume Parser
    participant Embedder as Embedding Service
    participant FAISS as FAISS Service
    participant Storage as File Storage
    
    User->>Frontend: Upload Resume File(s)
    Frontend->>Frontend: Validate File Type & Size
    
    alt File Valid
        Frontend->>API: POST /upload-resume
        API->>Storage: Save Temporary File
        API->>Parser: Parse Resume Content
        
        Parser->>Parser: Extract Text (PDF/DOCX)
        Parser->>Parser: Identify Sections
        Parser->>Parser: Extract Skills & Info
        Parser->>API: Return Parsed Data
        
        API->>Embedder: Generate Embedding
        Embedder->>Embedder: Load mxbai Model
        Embedder->>Embedder: Process Text to Vector
        Embedder->>API: Return Embedding Vector
        
        API->>FAISS: Store Vector & Metadata
        FAISS->>FAISS: Add to Index
        FAISS->>FAISS: Save Metadata
        FAISS->>API: Confirm Storage
        
        API->>Storage: Clean Temporary File
        API->>Frontend: Success Response
        Frontend->>User: Show Success Message
        
    else File Invalid
        Frontend->>User: Show Error Message
    end
    
    Note over User,Storage: Resume is now searchable in the system
```

### Resume Parsing Detail Flow

```mermaid
flowchart TD
    START([Upload Resume]) --> VALIDATE{Validate File}
    VALIDATE -->|Invalid| ERROR[Show Error]
    VALIDATE -->|Valid| DETECT{Detect File Type}
    
    DETECT -->|PDF| PDF_EXTRACT[PyMuPDF Extract]
    DETECT -->|DOCX| DOCX_EXTRACT[python-docx Extract]
    DETECT -->|TXT| TXT_EXTRACT[Plain Text Read]
    
    PDF_EXTRACT --> CLEAN[Clean Text]
    DOCX_EXTRACT --> CLEAN
    TXT_EXTRACT --> CLEAN
    
    CLEAN --> SECTIONS[Extract Sections]
    SECTIONS --> SKILLS[Extract Skills]
    SKILLS --> CONTACT[Extract Contact Info]
    CONTACT --> EXPERIENCE[Extract Experience Years]
    EXPERIENCE --> EDUCATION[Extract Education]
    EDUCATION --> GENERATE_ID[Generate Resume ID]
    
    GENERATE_ID --> CREATE_METADATA[Create Metadata Object]
    CREATE_METADATA --> EMBEDDING[Generate Embedding]
    
    EMBEDDING --> STORE_FAISS[Store in FAISS]
    STORE_FAISS --> SUCCESS[Processing Complete]
    
    %% Error handling
    PDF_EXTRACT -->|Fails| FALLBACK[Try Alternative Parser]
    DOCX_EXTRACT -->|Fails| FALLBACK
    FALLBACK --> CLEAN
    
    %% Styling
    classDef process fill:#e3f2fd
    classDef decision fill:#fff3e0
    classDef error fill:#ffebee
    classDef success fill:#e8f5e8
    
    class PDF_EXTRACT,DOCX_EXTRACT,TXT_EXTRACT,CLEAN,SECTIONS,SKILLS,CONTACT,EXPERIENCE,EDUCATION,GENERATE_ID,CREATE_METADATA,EMBEDDING,STORE_FAISS process
    class VALIDATE,DETECT decision
    class ERROR error
    class SUCCESS success
```

---

## 🎯 Job Matching Workflow

### Complete Job Matching Process

```mermaid
sequenceDiagram
    participant User
    participant Frontend as Streamlit UI
    participant API as FastAPI
    participant Embedder as Embedding Service
    participant FAISS as FAISS Service
    participant Gemini as Gemini Service
    participant Results as Results Processor
    
    User->>Frontend: Enter Job Description
    Frontend->>Frontend: Validate Form Data
    Frontend->>API: POST /match-job
    
    API->>API: Parse Job Description
    API->>Embedder: Generate Job Embedding
    
    Embedder->>Embedder: Process Job Text
    Embedder->>API: Return Job Vector
    
    API->>FAISS: Search Similar Resumes
    FAISS->>FAISS: Vector Similarity Search
    FAISS->>FAISS: Apply Threshold Filter
    FAISS->>FAISS: Rank by Similarity
    FAISS->>API: Return Top K Matches
    
    loop For Each Match
        API->>Results: Extract Resume Content
        API->>Gemini: Generate Match Explanation
        Gemini->>Gemini: Analyze Job vs Resume
        Gemini->>API: Return Explanation
        API->>Results: Compile Match Result
    end
    
    API->>API: Aggregate All Results
    API->>Frontend: Return Match Response
    
    Frontend->>Frontend: Process Results
    Frontend->>User: Display Matching Candidates
    
    Note over User,Results: User can now review matches and explanations
```

### Detailed Matching Algorithm

```mermaid
flowchart TD
    START([Job Description Input]) --> PREPROCESS[Preprocess Job Text]
    PREPROCESS --> EMBED_JOB[Generate Job Embedding]
    
    EMBED_JOB --> LOAD_INDEX[Load FAISS Index]
    LOAD_INDEX --> SEARCH[Vector Similarity Search]
    
    SEARCH --> THRESHOLD{Apply Similarity Threshold}
    THRESHOLD -->|Below Threshold| FILTER_OUT[Filter Out]
    THRESHOLD -->|Above Threshold| KEEP[Keep Candidate]
    
    KEEP --> RANK[Rank by Similarity Score]
    RANK --> TOP_K[Select Top K Results]
    
    TOP_K --> LOOP_START{For Each Match}
    LOOP_START --> EXTRACT_CONTENT[Extract Resume Content]
    EXTRACT_CONTENT --> SKILL_MATCH[Find Matching Skills]
    SKILL_MATCH --> GENERATE_EXPLANATION[Generate AI Explanation]
    
    GENERATE_EXPLANATION --> COMPILE_RESULT[Compile Match Result]
    COMPILE_RESULT --> LOOP_END{More Matches?}
    LOOP_END -->|Yes| LOOP_START
    LOOP_END -->|No| AGGREGATE[Aggregate All Results]
    
    AGGREGATE --> SORT[Sort by Score]
    SORT --> RETURN[Return to Frontend]
    
    FILTER_OUT --> LOOP_END
    
    %% Styling
    classDef process fill:#e3f2fd
    classDef decision fill:#fff3e0
    classDef output fill:#e8f5e8
    
    class PREPROCESS,EMBED_JOB,LOAD_INDEX,SEARCH,KEEP,RANK,TOP_K,EXTRACT_CONTENT,SKILL_MATCH,GENERATE_EXPLANATION,COMPILE_RESULT,AGGREGATE,SORT process
    class THRESHOLD,LOOP_START,LOOP_END decision
    class RETURN output
```

---

## 🔗 API Request Flow

### REST API Endpoints & Flow

```mermaid
graph TD
    subgraph "Client Requests"
        UPLOAD_REQ[POST /upload-resume]
        MATCH_REQ[POST /match-job]
        COUNT_REQ[GET /resumes/count]
        STATUS_REQ[GET /]
        HEALTH_REQ[GET /health]
    end
    
    subgraph "API Gateway"
        FASTAPI[FastAPI Server<br/>Port 8000]
        CORS[CORS Middleware]
        LOGGING[Request Logging]
        ERROR_HANDLER[Error Handler]
    end
    
    subgraph "Route Handlers"
        UPLOAD_HANDLER[upload_resume()]
        MATCH_HANDLER[match_job_to_resumes()]
        COUNT_HANDLER[get_resume_count()]
        STATUS_HANDLER[get_status()]
        HEALTH_HANDLER[health_check()]
    end
    
    subgraph "Service Layer"
        PARSER_SVC[Resume Parser]
        EMBED_SVC[Embedding Service]
        FAISS_SVC[FAISS Service]
        GEMINI_SVC[Gemini Service]
    end
    
    subgraph "Responses"
        SUCCESS_RESP[200 Success]
        ERROR_RESP[400/500 Error]
        JSON_RESP[JSON Response]
    end
    
    %% Request flow
    UPLOAD_REQ --> FASTAPI
    MATCH_REQ --> FASTAPI
    COUNT_REQ --> FASTAPI
    STATUS_REQ --> FASTAPI
    HEALTH_REQ --> FASTAPI
    
    %% Middleware
    FASTAPI --> CORS
    CORS --> LOGGING
    LOGGING --> ERROR_HANDLER
    
    %% Route handling
    ERROR_HANDLER --> UPLOAD_HANDLER
    ERROR_HANDLER --> MATCH_HANDLER
    ERROR_HANDLER --> COUNT_HANDLER
    ERROR_HANDLER --> STATUS_HANDLER
    ERROR_HANDLER --> HEALTH_HANDLER
    
    %% Service calls
    UPLOAD_HANDLER --> PARSER_SVC
    UPLOAD_HANDLER --> EMBED_SVC
    UPLOAD_HANDLER --> FAISS_SVC
    
    MATCH_HANDLER --> EMBED_SVC
    MATCH_HANDLER --> FAISS_SVC
    MATCH_HANDLER --> GEMINI_SVC
    
    COUNT_HANDLER --> FAISS_SVC
    
    %% Responses
    UPLOAD_HANDLER --> SUCCESS_RESP
    MATCH_HANDLER --> SUCCESS_RESP
    COUNT_HANDLER --> SUCCESS_RESP
    STATUS_HANDLER --> SUCCESS_RESP
    HEALTH_HANDLER --> SUCCESS_RESP
    
    ERROR_HANDLER --> ERROR_RESP
    
    SUCCESS_RESP --> JSON_RESP
    ERROR_RESP --> JSON_RESP
```

### API Response Structure

```mermaid
classDiagram
    class UploadResponse {
        +string message
        +string resume_id
        +string filename
        +int skills_found
        +int sections_found
    }
    
    class MatchResponse {
        +string job_title
        +int total_resumes
        +int matches_found
        +MatchResult[] matches
        +float processing_time
    }
    
    class MatchResult {
        +string resume_id
        +string filename
        +float similarity_score
        +string match_explanation
        +string[] matching_skills
        +string experience_match
    }
    
    class StatusResponse {
        +string status
        +string version
        +int total_resumes
        +string embedding_model
        +string llm_model
    }
    
    class ErrorResponse {
        +string error
        +string detail
        +int code
    }
    
    MatchResponse --> MatchResult
```

---

## 📊 Data Flow Architecture

### System Data Flow

```mermaid
flowchart LR
    subgraph "Input Sources"
        RESUMES[Resume Files<br/>PDF, DOCX, TXT]
        JOBS[Job Descriptions<br/>Text Input]
    end
    
    subgraph "Processing Pipeline"
        PARSER[Text Extraction<br/>& Parsing]
        NLP[NLP Processing<br/>Skills, Sections]
        EMBEDDING[Embedding Generation<br/>mxbai Model]
    end
    
    subgraph "Storage Systems"
        FAISS_DB[(FAISS Vector DB<br/>Embeddings)]
        METADATA[(JSON Metadata<br/>Resume Info)]
        FILE_STORE[(File Storage<br/>Temp Files)]
    end
    
    subgraph "AI Processing"
        SIMILARITY[Similarity Search<br/>Cosine Distance]
        GEMINI_AI[Gemini AI<br/>Match Explanation]
    end
    
    subgraph "Output Systems"
        API_RESP[API Responses<br/>JSON Format]
        UI_DISPLAY[UI Display<br/>Streamlit]
        ANALYTICS[Analytics<br/>Insights]
    end
    
    %% Data flow
    RESUMES --> PARSER
    PARSER --> NLP
    NLP --> EMBEDDING
    EMBEDDING --> FAISS_DB
    NLP --> METADATA
    RESUMES --> FILE_STORE
    
    JOBS --> EMBEDDING
    EMBEDDING --> SIMILARITY
    FAISS_DB --> SIMILARITY
    SIMILARITY --> GEMINI_AI
    METADATA --> GEMINI_AI
    
    GEMINI_AI --> API_RESP
    API_RESP --> UI_DISPLAY
    API_RESP --> ANALYTICS
    
    %% Styling
    classDef input fill:#e3f2fd
    classDef process fill:#f3e5f5
    classDef storage fill:#e8f5e8
    classDef ai fill:#fff3e0
    classDef output fill:#fce4ec
    
    class RESUMES,JOBS input
    class PARSER,NLP,EMBEDDING process
    class FAISS_DB,METADATA,FILE_STORE storage
    class SIMILARITY,GEMINI_AI ai
    class API_RESP,UI_DISPLAY,ANALYTICS output
```

### Vector Processing Pipeline

```mermaid
graph TD
    TEXT_INPUT[Text Input] --> TOKENIZE[Tokenization]
    TOKENIZE --> NORMALIZE[Text Normalization]
    NORMALIZE --> TRUNCATE[Truncate to Max Length]
    TRUNCATE --> MXBAI[mxbai Model Processing]
    
    MXBAI --> HIDDEN_STATES[Hidden States]
    HIDDEN_STATES --> POOLING[Mean Pooling]
    POOLING --> L2_NORM[L2 Normalization]
    L2_NORM --> VECTOR[1024-dim Vector]
    
    VECTOR --> FAISS_ADD[Add to FAISS Index]
    VECTOR --> SIMILARITY[Compute Similarities]
    
    subgraph "FAISS Operations"
        FAISS_ADD --> INDEX_UPDATE[Update Index]
        INDEX_UPDATE --> METADATA_STORE[Store Metadata]
    end
    
    subgraph "Search Operations"
        SIMILARITY --> TOP_K[Get Top-K Results]
        TOP_K --> THRESHOLD[Apply Threshold]
        THRESHOLD --> RESULTS[Return Results]
    end
```

---

## 👤 User Journey Flow

### Complete User Experience Flow

```mermaid
journey
    title AI Recruitr User Journey
    
    section Setup
        Visit Application: 5: User
        Check API Status: 3: System
        View Dashboard: 4: User
    
    section Upload Resumes
        Navigate to Upload: 5: User
        Select Files: 4: User
        Drag & Drop: 5: User
        Process Files: 3: System
        View Results: 4: User
        Check Statistics: 3: User
    
    section Job Matching
        Navigate to Matching: 5: User
        Enter Job Details: 4: User
        Set Parameters: 3: User
        Submit Search: 5: User
        Process Matching: 2: System
        Generate Explanations: 2: System
        View Results: 5: User
    
    section Review Results
        Analyze Matches: 5: User
        Read Explanations: 4: User
        Check Similarity Scores: 4: User
        Export Results: 3: User
    
    section Analytics
        View Dashboard: 4: User
        Check Trends: 3: User
        Generate Reports: 2: User
        Export Data: 3: User
```

### User Interface Navigation Flow

```mermaid
stateDiagram-v2
    [*] --> Landing: Application Start
    
    Landing --> Upload: Navigate to Upload
    Landing --> Matching: Navigate to Matching
    Landing --> Results: Navigate to Results
    
    state Upload {
        [*] --> FileSelection: Select Files
        FileSelection --> Processing: Submit Upload
        Processing --> Success: Files Processed
        Processing --> Error: Processing Failed
        Success --> FileSelection: Upload More
        Error --> FileSelection: Try Again
    }
    
    state Matching {
        [*] --> JobForm: Enter Job Details
        JobForm --> Search: Submit Search
        Search --> MatchResults: Results Found
        Search --> NoResults: No Matches
        MatchResults --> JobForm: New Search
        NoResults --> JobForm: Refine Search
    }
    
    state Results {
        [*] --> CurrentResults: View Current
        CurrentResults --> Analytics: View Analytics
        Analytics --> Export: Export Data
        Export --> CurrentResults: Back to Results
    }
    
    Upload --> Matching: Continue to Matching
    Matching --> Results: View Results
    Results --> Upload: Upload More Resumes
```

---

## 🔧 Service Dependencies

### Service Dependency Graph

```mermaid
graph TD
    subgraph "Core Services"
        EMBEDDING[Embedding Service<br/>sentence-transformers]
        FAISS[FAISS Service<br/>faiss-cpu]
        GEMINI[Gemini Service<br/>google-generativeai]
        PARSER[Resume Parser<br/>PyMuPDF, python-docx]
    end
    
    subgraph "External Dependencies"
        HF_API[Hugging Face API<br/>Model Downloads]
        GOOGLE_API[Google AI API<br/>Gemini Access]
        TORCH[PyTorch<br/>ML Framework]
        NUMPY[NumPy<br/>Array Operations]
    end
    
    subgraph "System Dependencies"
        PYTHON[Python 3.9+<br/>Runtime]
        FASTAPI_DEP[FastAPI<br/>Web Framework]
        STREAMLIT_DEP[Streamlit<br/>UI Framework]
        UVICORN[Uvicorn<br/>ASGI Server]
    end
    
    subgraph "Optional Dependencies"
        REDIS[Redis<br/>Caching]
        POSTGRES[PostgreSQL<br/>Metadata DB]
        DOCKER[Docker<br/>Containerization]
    end
    
    %% Core service dependencies
    EMBEDDING --> HF_API
    EMBEDDING --> TORCH
    EMBEDDING --> NUMPY
    GEMINI --> GOOGLE_API
    FAISS --> NUMPY
    PARSER --> PYTHON
    
    %% System dependencies
    FASTAPI_DEP --> UVICORN
    FASTAPI_DEP --> PYTHON
    STREAMLIT_DEP --> PYTHON
    
    %% Service interconnections
    FAISS -.-> EMBEDDING
    GEMINI -.-> FAISS
    PARSER -.-> EMBEDDING
    
    %% Optional connections
    EMBEDDING -.-> REDIS
    FAISS -.-> POSTGRES
    
    %% Styling
    classDef core fill:#e3f2fd
    classDef external fill:#fff3e0
    classDef system fill:#e8f5e8
    classDef optional fill:#f3e5f5
    
    class EMBEDDING,FAISS,GEMINI,PARSER core
    class HF_API,GOOGLE_API,TORCH,NUMPY external
    class PYTHON,FASTAPI_DEP,STREAMLIT_DEP,UVICORN system
    class REDIS,POSTGRES,DOCKER optional
```

### Initialization Sequence

```mermaid
sequenceDiagram
    participant App as Application
    participant Config as Configuration
    participant Embed as Embedding Service
    participant FAISS as FAISS Service
    participant Gemini as Gemini Service
    participant API as FastAPI Server
    participant UI as Streamlit UI
    
    App->>Config: Load Configuration
    Config->>Config: Validate Settings
    Config->>Config: Check API Keys
    
    App->>Embed: Initialize Embedding Service
    Embed->>Embed: Load mxbai Model
    Embed->>Embed: Test Model Loading
    
    App->>FAISS: Initialize FAISS Service
    FAISS->>FAISS: Load/Create Index
    FAISS->>FAISS: Load Metadata
    
    App->>Gemini: Initialize Gemini Service
    Gemini->>Gemini: Configure API Client
    Gemini->>Gemini: Test Connection
    
    App->>API: Start FastAPI Server
    API->>API: Setup Routes
    API->>API: Configure Middleware
    
    App->>UI: Start Streamlit UI
    UI->>UI: Initialize Session State
    UI->>API: Test API Connection
    
    Note over App,UI: System Ready for Use
```

---

## 🗄️ Database Schema

### FAISS Index Structure

```mermaid
erDiagram
    FAISS_INDEX {
        int vector_id PK
        float[1024] embedding_vector
        datetime created_at
        string index_type
    }
    
    RESUME_METADATA {
        string resume_id PK
        int vector_id FK
        string filename
        string raw_content
        json sections
        json skills
        int experience_years
        json education
        json certifications
        json contact_info
        datetime created_at
        boolean embedding_generated
    }
    
    JOB_SEARCHES {
        string search_id PK
        string job_title
        string job_description
        json requirements
        float similarity_threshold
        int top_k
        datetime search_time
        float processing_time
        int matches_found
    }
    
    SEARCH_RESULTS {
        string result_id PK
        string search_id FK
        string resume_id FK
        float similarity_score
        string match_explanation
        json matching_skills
        int rank_position
    }
    
    FAISS_INDEX ||--|| RESUME_METADATA : "vector_id"
    JOB_SEARCHES ||--o{ SEARCH_RESULTS : "search_id"
    RESUME_METADATA ||--o{ SEARCH_RESULTS : "resume_id"
```

### Data Storage Architecture

```mermaid
graph TB
    subgraph "File System Storage"
        UPLOADS[/uploads/<br/>Temporary Files]
        FAISS_FILES[/data/faiss_index/<br/>Index Files]
        METADATA_JSON[/data/faiss_index/<br/>metadata.json]
        LOGS[/logs/<br/>Application Logs]
    end
    
    subgraph "In-Memory Storage"
        SESSION[Streamlit Session State]
        CACHE[Model Cache]
        INDEX_CACHE[FAISS Index Cache]
    end
    
    subgraph "Optional External Storage"
        REDIS_CACHE[(Redis Cache)]
        POSTGRES_DB[(PostgreSQL)]
        S3_STORAGE[(AWS S3)]
    end
    
    %% File system connections
    UPLOADS --> METADATA_JSON
    FAISS_FILES --> INDEX_CACHE
    METADATA_JSON --> SESSION
    
    %% Optional connections
    CACHE -.-> REDIS_CACHE
    METADATA_JSON -.-> POSTGRES_DB
    UPLOADS -.-> S3_STORAGE
    
    %% Styling
    classDef filesystem fill:#e3f2fd
    classDef memory fill:#e8f5e8
    classDef external fill:#fff3e0
    
    class UPLOADS,FAISS_FILES,METADATA_JSON,LOGS filesystem
    class SESSION,CACHE,INDEX_CACHE memory
    class REDIS_CACHE,POSTGRES_DB,S3_STORAGE external
```

---

## 🚀 Deployment Architecture

### Container Architecture

```mermaid
graph TB
    subgraph "Docker Containers"
        subgraph "Frontend Container"
            STREAMLIT[Streamlit App<br/>Port 8501]
            UI_FILES[UI Components]
        end
        
        subgraph "Backend Container"
            FASTAPI[FastAPI Server<br/>Port 8000]
            SERVICES[AI Services]
        end
        
        subgraph "Cache Container"
            REDIS_CONT[Redis Cache<br/>Port 6379]
        end
        
        subgraph "Reverse Proxy"
            NGINX[Nginx<br/>Port 80/443]
        end
    end
    
    subgraph "External Services"
        HF_MODELS[Hugging Face<br/>Models]
        GEMINI_API[Google Gemini<br/>API]
    end
    
    subgraph "Storage Volumes"
        DATA_VOL[/data Volume<br/>FAISS Index]
        LOGS_VOL[/logs Volume<br/>Application Logs]
    end
    
    %% Container connections
    NGINX --> STREAMLIT
    NGINX --> FASTAPI
    STREAMLIT -.->|API Calls| FASTAPI
    FASTAPI --> REDIS_CONT
    
    %% External connections
    SERVICES --> HF_MODELS
    SERVICES --> GEMINI_API
    
    %% Volume connections
    FASTAPI --> DATA_VOL
    FASTAPI --> LOGS_VOL
    STREAMLIT --> LOGS_VOL
    
    %% Styling
    classDef container fill:#e3f2fd
    classDef external fill:#fff3e0
    classDef storage fill:#e8f5e8
    
    class STREAMLIT,UI_FILES,FASTAPI,SERVICES,REDIS_CONT,NGINX container
    class HF_MODELS,GEMINI_API external
    class DATA_VOL,LOGS_VOL storage
```

### Production Deployment Flow

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant Git as Git Repository
    participant CI as CI/CD Pipeline
    participant Registry as Container Registry
    participant Server as Production Server
    participant Monitor as Monitoring
    
    Dev->>Git: Push Code Changes
    Git->>CI: Trigger Build Pipeline
    
    CI->>CI: Run Tests
    CI->>CI: Build Docker Images
    CI->>Registry: Push Images
    
    CI->>Server: Deploy to Production
    Server->>Registry: Pull Latest Images
    Server->>Server: Update Containers
    Server->>Server: Run Health Checks
    
    Server->>Monitor: Send Metrics
    Monitor->>Monitor: Check System Health
    Monitor->>Dev: Alert if Issues
    
    Note over Dev,Monitor: Continuous Deployment & Monitoring
```

---

## 📈 Performance & Scaling

### Performance Optimization Points

```mermaid
mindmap
    root((Performance))
        Embedding Generation
            Model Caching
            Batch Processing
            GPU Acceleration
            Quantization
        
        Vector Search
            Index Optimization
            Parallel Search
            Memory Mapping
            Compression
        
        API Response
            Response Caching
            Connection Pooling
            Async Processing
            Load Balancing
        
        Storage I/O
            SSD Storage
            Index Partitioning
            Metadata Caching
            File Compression
        
        Frontend
            Component Caching
            Lazy Loading
            Progressive Loading
            CDN Assets
```

### Scaling Architecture

```mermaid
graph TB
    subgraph "Load Balancer Layer"
        LB[Load Balancer<br/>Nginx/HAProxy]
    end
    
    subgraph "API Layer (Horizontal Scaling)"
        API1[FastAPI Instance 1]
        API2[FastAPI Instance 2]
        API3[FastAPI Instance N]
    end
    
    subgraph "Service Layer (Distributed)"
        EMBED_CLUSTER[Embedding Service<br/>GPU Cluster]
        FAISS_CLUSTER[FAISS Service<br/>Distributed Index]
        GEMINI_POOL[Gemini Service<br/>Connection Pool]
    end
    
    subgraph "Storage Layer (Distributed)"
        FAISS_SHARDS[(FAISS Shards<br/>Partitioned Index)]
        METADATA_DB[(Metadata Database<br/>PostgreSQL Cluster)]
        REDIS_CLUSTER[(Redis Cluster<br/>Distributed Cache)]
    end
    
    subgraph "Monitoring & Logging"
        METRICS[Metrics Collection<br/>Prometheus]
        LOGS_AGG[Log Aggregation<br/>ELK Stack]
        ALERTS[Alerting<br/>Grafana]
    end
    
    %% Load balancing
    LB --> API1
    LB --> API2
    LB --> API3
    
    %% Service connections
    API1 --> EMBED_CLUSTER
    API2 --> FAISS_CLUSTER
    API3 --> GEMINI_POOL
    
    %% Storage connections
    FAISS_CLUSTER --> FAISS_SHARDS
    API1 --> METADATA_DB
    API2 --> REDIS_CLUSTER
    
    %% Monitoring
    API1 --> METRICS
    API2 --> LOGS_AGG
    METRICS --> ALERTS
    
    %% Styling
    classDef balancer fill:#e3f2fd
    classDef api fill:#e8f5e8
    classDef service fill:#fff3e0
    classDef storage fill:#fce4ec
    classDef monitoring fill:#f3e5f5
    
    class LB balancer
    class API1,API2,API3 api
    class EMBED_CLUSTER,FAISS_CLUSTER,GEMINI_POOL service
    class FAISS_SHARDS,METADATA_DB,REDIS_CLUSTER storage
    class METRICS,LOGS_AGG,ALERTS monitoring
```

---

## 🔄 Development Workflow

### Development & Testing Flow

```mermaid
gitgraph
    commit id: "Initial Setup"
    
    branch feature/embedding-service
    checkout feature/embedding-service
    commit id: "Add mxbai model"
    commit id: "Add fallback models"
    commit id: "Unit tests"
    
    checkout main
    merge feature/embedding-service
    
    branch feature/faiss-integration
    checkout feature/faiss-integration
    commit id: "FAISS service"
    commit id: "Vector operations"
    commit id: "Integration tests"
    
    checkout main
    merge feature/faiss-integration
    
    branch feature/streamlit-ui
    checkout feature/streamlit-ui
    commit id: "Upload UI"
    commit id: "Matching UI"
    commit id: "Results UI"
    commit id: "E2E tests"
    
    checkout main
    merge feature/streamlit-ui
    
    commit id: "Production Release v1.0"
```

---

This comprehensive workflow documentation provides a complete understanding of AI Recruitr's architecture, data flows, and operational processes. Each diagram illustrates different aspects of the system to help developers, operators, and stakeholders understand how the components work together to deliver intelligent resume matching capabilities.