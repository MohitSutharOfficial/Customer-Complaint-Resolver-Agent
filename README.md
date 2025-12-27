# Customer Complaint Resolver Agent

An AI-powered multi-agent system for automated customer complaint resolution, built with FastAPI, LangGraph, and Next.js.

### Demo

[Demo Files](https://drive.google.com/drive/folders/1Mrb9AVW5UmNW1Ashn0A9CxLbZUb3bPww?usp=drive_link)

## Screenshots
### Business Page with Chatbot
![Dashboard Overview](Screenshots/Screenshot%201.png)

### Complaint Inbox
![Complaint Inbox](Screenshots/Screenshot%202.png)

### Complaint Details
![Complaint Detail View](Screenshots/Screenshot%203.png)

### AI Response Generation
![AI Response](Screenshots/Screenshot%204.png)

### Help box
![Help Box](Screenshots/Screenshot%205.png)

### Agent Performance
![Agent Performance Metrics](Screenshots/Screenshot%206.png)

### New Complaint Form
![Submit Complaint](Screenshots/Screenshot%207.png)

### Customer History
![Customer History](Screenshots/Screenshot%208.png)
## 🏗️ Architecture
### Complete Request Flow: ✓ WORKING

```
┌─────────────────────────────────────────────────────┐
│ 1. USER INPUT (Frontend Chatbot)                      │
│    • User types complaint message                   │
│    • Clicks send button                             │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│ 2. FRONTEND API CALL                                │
│    POST http://127.0.0.1:8000/api/v1/complaints/   │
│    Body: {                                          │
│      raw_text: "complaint message",                 │
│      channel: "chat",                               │
│      customer_name: "Guest",                        │
│      customer_email: "guest@example.com"            │
│    }                                                │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│ 3. BACKEND API ENDPOINT                             │
│    File: backend/app/api/complaints.py              │
│    • Receives complaint data                        │
│    • Looks up/creates customer                      │
│    • Retrieves complaint history                    │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│ 4. ORCHESTRATOR INVOCATION                          │
│    File: backend/app/agents/orchestrator.py         │
│    orchestrator.process_complaint(...)              │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│ 5. LANGGRAPH WORKFLOW (Sequential Processing)       │
│                                                     │
│    ┌─────────────────┐                             │
│    │  Intake Agent   │ → Normalize & clean text    │
│    └────────┬────────┘                             │
│             │                                       │
│    ┌────────▼────────┐                             │
│    │ Context Agent   │ → Load customer history     │
│    └────────┬────────┘                             │
│             │                                       │
│    ┌────────▼────────┐                             │
│    │Classifier Agent │ → 8 categories, sentiment   │
│    └────────┬────────┘                             │
│             │                                       │
│    ┌────────▼────────┐                             │
│    │ Priority Agent  │ → Score 1-5, SLA deadline   │
│    └────────┬────────┘                             │
│             │                                       │
│    ┌────────▼────────┐                             │
│    │ Response Agent  │ → Generate empathetic reply │
│    └────────┬────────┘                             │
│             │                                       │
│    ┌────────▼────────┐                             │
│    │Validator Agent  │ → Quality check response    │
│    └────────┬────────┘                             │
│             │                                       │
│    ┌────────▼────────┐                             │
│    │Escalation Agent │ → Determine human review    │
│    └────────┬────────┘                             │
│             │                                       │
│    ┌────────▼────────┐                             │
│    │   Finalize      │ → Set final status          │
│    └─────────────────┘                             │
│                                                     │
│    Each agent:                                      │
│    • Uses Google Gemini 2.0 Flash                   │
│    • Has fallback rule-based logic                  │
│    • Creates audit log entry                        │
│    • Adds to state for next agent                   │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│ 6. DATABASE PERSISTENCE                             │
│    • Save Complaint record with all metadata        │
│    • Update Customer complaint count                │
│    • Create AuditLog entries for each agent         │
│    • SQLite: complaints.db                          │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│ 7. API RESPONSE TO FRONTEND                         │
│    Returns: {                                       │
│      external_id: "C-ABC12345",                     │
│      ai_response: "I understand your concern...",   │
│      categories: ["Billing"],                       │
│      priority_level: "HIGH",                        │
│      sentiment: "frustrated",                       │
│      status: "pending_review",                      │
│      escalated: false                               │
│    }                                                │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│ 8. FRONTEND DISPLAYS RESULT                         │
│    • Shows AI response in chat                      │
│    • Displays category badge                        │
│    • Shows priority level (color-coded)             │
│    • Displays ETA                                   │
│    • Smooth animations                              │
└─────────────────────────────────────────────────────┘
```


## 🚀 Features

### AI Agents
- **Intake Agent**: Normalizes complaints from various channels (email, chat, social media, phone)
- **Classifier Agent**: Multi-label categorization and sentiment analysis
- **Priority Agent**: Rule-based urgency scoring (1-5 scale)
- **Context Agent**: Customer history retrieval and churn risk assessment
- **Response Agent**: Personalized response generation with tone matching
- **Validator Agent**: Quality checks, policy compliance, completeness verification
- **Escalation Agent**: Intelligent routing and SLA management

### Platform Features
- Multi-channel complaint intake
- Real-time complaint processing
- Draft response generation with human-in-the-loop editing
- Analytics dashboard with AI performance metrics
- Customer sentiment tracking
- Audit logging for compliance

## 📋 Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+ (optional, for caching)
- Gemni API key

## 🛠️ Installation

### Backend Setup

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment:**
```bash
cp .env.example .env
```

Edit `.env` with your settings:
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/complaints_db
OPENAI_API_KEY=your-openai-api-key
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key-for-jwt
```

5. **Set up the database:**
```bash
# Create PostgreSQL database
createdb complaints_db

# The tables will be created automatically on first run
```

6. **Run the backend:**
```bash
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Configure environment:**
Create `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

4. **Run the frontend:**
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## 📁 Project Structure

```
GDG/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── base_agent.py       # Abstract base class
│   │   │   ├── intake_agent.py     # Channel normalization
│   │   │   ├── classifier_agent.py # Categorization & sentiment
│   │   │   ├── priority_agent.py   # Urgency scoring
│   │   │   ├── context_agent.py    # Customer history
│   │   │   ├── response_agent.py   # Response generation
│   │   │   ├── validator_agent.py  # Quality checks
│   │   │   ├── escalation_agent.py # Human routing
│   │   │   └── orchestrator.py     # LangGraph workflow
│   │   ├── api/
│   │   │   ├── complaints.py       # Complaint endpoints
│   │   │   └── analytics.py        # Analytics endpoints
│   │   ├── core/
│   │   │   ├── config.py           # Settings
│   │   │   └── database.py         # DB connection
│   │   ├── models/
│   │   │   ├── database.py         # SQLAlchemy models
│   │   │   └── schemas.py          # Pydantic schemas
│   │   └── main.py                 # FastAPI app
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx               # Dashboard
│   │   ├── inbox/page.tsx         # Complaint inbox
│   │   ├── analytics/page.tsx     # Analytics view
│   │   └── layout.tsx             # Root layout
│   ├── components/
│   │   ├── ui/                    # shadcn/ui components
│   │   ├── sidebar.tsx            # Navigation
│   │   ├── header.tsx             # Top bar
│   │   ├── complaint-list.tsx     # List view
│   │   ├── complaint-detail.tsx   # Detail panel
│   │   └── new-complaint-form.tsx # Submit form
│   ├── lib/
│   │   ├── api.ts                 # API client
│   │   └── store.ts               # Zustand store
│   ├── package.json
│   └── tailwind.config.js
│
└── README.md
```

## 🔌 API Endpoints

### Complaints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/complaints/` | Create new complaint |
| GET | `/api/v1/complaints/` | List all complaints |
| GET | `/api/v1/complaints/{id}` | Get complaint by ID |
| PATCH | `/api/v1/complaints/{id}` | Update complaint |
| POST | `/api/v1/complaints/{id}/process` | Process through AI pipeline |
| PATCH | `/api/v1/complaints/{id}/response` | Update draft response |
| POST | `/api/v1/complaints/{id}/send` | Send response to customer |
| POST | `/api/v1/complaints/{id}/escalate` | Escalate to human agent |

### Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/analytics/dashboard` | Dashboard metrics |
| GET | `/api/v1/analytics/agent-performance` | AI agent stats |

## 🎯 How It Works

1. **Complaint Submission**: Customer submits complaint via any channel (email, chat, social, phone)

2. **Intake Processing**: Intake Agent normalizes the complaint into a standard format

3. **Classification**: Classifier Agent categorizes the complaint (billing, technical, product, etc.) and analyzes sentiment

4. **Priority Assessment**: Priority Agent calculates urgency score based on keywords, sentiment, and customer status

5. **Context Enrichment**: Context Agent retrieves customer history, previous interactions, and calculates churn risk

6. **Response Generation**: Response Agent creates a personalized response using templates and AI generation

7. **Validation**: Validator Agent checks response quality, policy compliance, and completeness

8. **Resolution/Escalation**: 
   - If validation passes → Auto-send or queue for human review
   - If validation fails → Escalate to human agent with context


## 🔧 Configuration

### Agent Configuration

Each agent can be customized in their respective files under `backend/app/agents/`:

- Adjust classification categories in `classifier_agent.py`
- Modify priority rules in `priority_agent.py`
- Customize response templates in `response_agent.py`
- Update validation rules in `validator_agent.py`
- Configure escalation thresholds in `escalation_agent.py`

### LangGraph Workflow

The agent orchestration flow is defined in `backend/app/agents/orchestrator.py`. You can modify:
- Agent execution order
- Conditional routing logic
- Retry/feedback loops
- Memory persistence

## 📊 Performance Metrics

The system tracks:
- **Classification Accuracy**: How often AI correctly categorizes complaints
- **Response Quality Score**: Validator ratings of generated responses
- **Auto-Resolution Rate**: Percentage of complaints resolved without human intervention
- **Average Response Time**: Time from complaint receipt to response
- **Escalation Rate**: Percentage of complaints requiring human review
- **Customer Satisfaction**: Post-resolution feedback scores

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [LangChain](https://langchain.com/) and [LangGraph](https://github.com/langchain-ai/langgraph)
- UI components from [shadcn/ui](https://ui.shadcn.com/)
- Powered by [Gemini Api](https://gemini.com/)
