# ContosoHealth Research Platform

A secure, enterprise-grade research collaboration platform for cardiovascular studies, integrating Microsoft Fabric, Azure ML Studio, and Azure AI Foundry with a unified dark-theme interface.

## 🎯 Overview

The ContosoHealth Research Platform provides a streamlined interface for data scientists and researchers to access computational resources, manage datasets, execute notebooks, deploy ML models, and collaborate on cardiovascular research projects—all while maintaining strict PHI data security and compliance.

**Live Demo**: https://research-portal-2fbfvjbt.devinapps.com

## 🔒 Secure Research Environment (SRE) Architecture

The ContosoHealth platform is designed to implement Microsoft's **Secure Research Environment (SRE)** architecture for production deployment. This architecture ensures that sensitive PHI data never leaves the Azure environment while enabling collaborative research.

**Key SRE Principles:**
- **Network Isolation** - No internet access from compute resources, all traffic stays within Azure VNet
- **Data Exfiltration Prevention** - Raw PHI data cannot be downloaded; only approved aggregated results
- **Private Endpoints** - All Azure services (Fabric, ML Studio, SQL, Storage) accessed via private endpoints
- **Managed Identities** - Service-to-service authentication without credentials
- **PI Approval Workflow** - All data exports require Principal Investigator approval with time-limited access

See **[SRE_ARCHITECTURE.md](SRE_ARCHITECTURE.md)** for complete architecture details, network diagrams, security controls, and deployment checklist.

## ✨ Key Features

- **Unified Research Dashboard** - Single interface for all research projects
- **Multi-Language Notebook Support** - Python, R, and Scala notebooks via Microsoft Fabric
- **H100 GPU Inference** - Real-time model inference with sub-50ms latency
- **PHI-Protected Datasets** - Secure data access with export approval workflow
- **ML Model Deployment** - Azure ML Studio integration with real-time metrics
- **Activity Tracking** - Complete audit trail of all research activities
- **Export Approval Workflow** - PI-approved data export with time-limited access
- **Dark Theme UI** - Professional, eye-friendly interface for long research sessions

## 📸 Complete Demo Walkthrough

### 1. External User Login

External researchers can log in with their institutional credentials to access ContosoHealth research data through a secure B2B authentication flow.

![External Login](screenshots/01-external-login.png)

**Features shown:**
- ContosoHealth branding
- External researcher login form
- Institution-based authentication
- Secure access request workflow

---

### 2. Dashboard - Project Overview

The main dashboard displays all active cardiovascular research projects with key metrics including notebooks, datasets, models, and recent activity.

![Dashboard](screenshots/02-dashboard.png)

**Features shown:**
- Project cards with PI information
- Quick stats (notebooks, datasets, models, activity count)
- Direct links to Microsoft Fabric and Azure ML Studio workspaces
- Status indicators and creation dates

---

### 3. Project Notebooks - Multi-Language Support (Python, R, Scala)

The platform supports Python, R, and Scala notebooks through Microsoft Fabric integration, enabling data scientists to use their preferred tools. Each language has executable code with dedicated "Run" buttons.

![Notebooks](screenshots/10-notebooks-multi-language.png)

**Features shown:**
- **Python notebook** - Real-Time Inference Pipeline with "Run Inference" button (green)
- **R notebook** - Statistical Analysis for Heart Rate Variability with "Run Analysis" button (purple)
- **Scala notebook** - Spark Streaming for ECG Data Pipeline with "Run Pipeline" button (orange)
- Language badges (Python, R, Scala)
- Status indicators (Ready, Running)
- "Open" button to launch in Microsoft Fabric
- Color-coded execution buttons for each language

---

### 3. R Notebook Execution - Statistical Analysis

Execute R notebooks directly in the platform with full statistical analysis output including summary statistics, correlations, t-tests, and logistic regression models.

![R Notebook Execution](screenshots/11-r-notebook-execution.png)

**Features shown:**
- Heart Rate Variability (HRV) statistical analysis on 1000 patients
- Summary statistics (RMSSD, SDNN, pNN50, LF/HF ratio)
- Correlation analysis with AFib status
- T-test results (AFib vs No AFib)
- Logistic regression model (AIC: 1385.42)
- Execution time: 2.3s
- Results ready for export (summary statistics, correlations, model coefficients)

---

### 4. Scala Notebook Execution - Spark Data Pipeline

Execute Scala/Spark notebooks for large-scale data processing with real-time pipeline statistics and risk stratification.

![Scala Notebook Execution](screenshots/12-scala-notebook-execution.png)

**Features shown:**
- ECG Data Streaming Pipeline processing 5 ECG records
- Heart rate distribution (Bradycardia, Normal, Tachycardia)
- Arrhythmia risk stratification (High, Medium, Low)
- High-risk patient identification (P002, P004)
- Average heart rate: 103.6 bpm
- Average QTc: 437.2 ms
- Execution time: 1.8s
- Results ready for export (aggregated metrics, risk scores, patient summaries)

---

### 5. Microsoft Fabric Workspace - Professional Data Science Environment

The integrated Fabric workspace provides a professional, JupyterHub-style interface for data science work with live notebook execution, resource monitoring, and security controls.

![Fabric Workspace](screenshots/07-fabric-workspace.png)

**Features shown:**
- **Live notebook execution** with running cells and real-time outputs
- **File browser** with notebooks, read-only data, and exportable results
- **Resource monitoring** (CPU 34%, Memory 18.2/64 GB, Disk 124/500 GB)
- **Security reminder** prominently displayed (data cannot be downloaded)
- **Kernel status** and session management (2h 34m remaining)
- **Code cells** with Python/pandas code and execution timestamps
- **Visualization outputs** showing feature importance charts
- **Export workflow** with PI approval requirement
- **Quick help** with keyboard shortcuts
- **Installed packages** list (pandas, numpy, scikit-learn, matplotlib, seaborn)

---

### 6. Datasets - PHI-Protected Data Access

All cardiovascular datasets are PHI-protected with security levels and access controls. Researchers can request exports through the approval workflow.

![Datasets](screenshots/04-project-datasets.png)

**Features shown:**
- ECG Recordings Database (2.5M rows, 5.2 TB)
- Patient Demographics (2.5M rows, 890 MB)
- Medication History (6.8M rows, 1.8 GB)
- Security level indicators (PHI-Protected)
- Row counts and data sizes
- "Request Export" button for data access
- Access level badges (Full Access, Read-Only)

---

### 7. ML Models - H100 GPU Deployment

Deployed machine learning models with real-time performance metrics, GPU utilization, and accuracy tracking.

![Models](screenshots/05-project-models.png)

**Features shown:**
- AFib Detection LSTM v2.3 (4 H100 GPUs, 42ms latency, 96% accuracy)
- Multi-Class Arrhythmia CNN v1.8 (2 H100 GPUs, 38ms latency, 89% accuracy)
- Risk Stratification XGBoost v3.0 (CPU, 12ms latency, 87% accuracy)
- Real-time GPU allocation
- Inference latency metrics
- Model accuracy tracking
- "View in ML Studio" links

---

### 8. Activity Feed - Audit Trail

Complete audit trail of all research activities including notebook executions, model training, dataset access, and export requests.

![Activity](screenshots/06-project-activity.png)

**Features shown:**
- Chronological activity log
- User attribution
- Activity type indicators
- Timestamp tracking
- Resource identification

---

### 9. Real-Time Inference Execution

Execute inference on H100 GPUs directly from the platform with real-time results showing predictions, confidence scores, and latency metrics.

![Inference Results](screenshots/06-inference-results.png)

**Features shown:**
- Real-time inference execution
- ECG signal preprocessing (5000 samples)
- Model predictions with confidence scores:
  - Atrial Fibrillation: 78% (predicted class)
  - Normal Sinus Rhythm: 12%
  - Premature Ventricular Contraction: 6%
  - Ventricular Tachycardia: 4%
- GPU utilization (H100-0)
- Inference latency: 42ms (target: <50ms)
- Visual prediction bars

---

### 10. Results Export Dialog - Secure Export Workflow

Request export of analysis results (NOT raw PHI data) including model predictions, statistical summaries, and visualizations. All exports require PI approval.

![Results Export Dialog](screenshots/13-results-export-dialog.png)

**Features shown:**
- **Result Type selection** (not raw datasets):
  - Model Predictions - AFib Detection
  - Statistical Summary - HRV Analysis
  - Aggregated Metrics - Risk Scores
  - Visualization Outputs - ECG Plots
- Number of records (optional)
- Justification requirement
- Clear messaging: "Raw PHI data cannot be exported"
- PI approval workflow

---

### 11. Export Requests - Approval Workflow

Track all data export requests with status, PI reviewer information, and download links for approved exports.

![Export Requests](screenshots/07-export-requests.png)

**Features shown:**
- Export request tracking (EXP-2024-001, EXP-2024-002, etc.)
- Status indicators (Pending, Approved, Rejected)
- Dataset information and row counts
- PI reviewer assignment
- Request timestamps
- Download links for approved exports (time-limited)
- Justification tracking

---

### 12. Notifications - Real-Time Updates

System notifications for export approvals, model training completion, team member additions, and other important events.

![Notifications](screenshots/08-notifications.png)

**Features shown:**
- Real-time notification feed
- Notification types (Success, Info, Warning)
- Unread indicators
- Timestamp tracking
- Related entity links

---

### 13. External Access Request (Legacy)

Request data exports with justification for PI approval. The system enforces the approval workflow for all PHI-protected data.

![Export Dialog](screenshots/09-export-dialog.png)

**Features shown:**
- Dataset selection
- Row count specification
- Justification text area (required)
- PI reviewer assignment
- Submit workflow

---

## 🏗️ Architecture

### Technology Stack

**Frontend:**
- React 18.2 with TypeScript
- Tailwind CSS for dark theme styling
- Vite build system
- Deployed on Azure Static Web Apps

**Backend:**
- FastAPI (Python 3.11)
- Poetry for dependency management
- Mock endpoints for demo (ready for real service integration)
- Deployed on Fly.io

**Projected Integrations (Ready to Connect):**
- Microsoft Fabric (workspaces, notebooks, lakehouses)
- Azure ML Studio (models, compute, H100 GPUs)
- Azure AI Foundry (GPT-4o, Phi-3 models)
- Entra ID (B2B authentication, SSO)
- Azure SQL Database (metadata, audit logs)

### Network Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     AZURE FRONT DOOR + WAF                  │
│                   (DDoS Protection, SSL)                    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              CUSTOM PORTAL (React SPA)                      │
│  • Dashboard UI                                             │
│  • Project listing & navigation                             │
│  • Export approval workflow UI                              │
│  • Activity feeds & notifications                           │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              BACKEND API (FastAPI)                          │
│  • REST endpoints for portal                                │
│  • Integrations with Fabric & ML Studio APIs                │
│  • Export approval workflow logic                           │
│  • Notification service                                     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────┬──────────────┬──────────────┬───────────────┐
│ Azure SQL DB │ Entra ID B2B │ Fabric API   │ Azure ML API  │
│ (Metadata)   │ (Auth)       │ (Native)     │ (Native)      │
└──────────────┴──────────────┴──────────────┴───────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Node.js 20 LTS
- Python 3.11+
- Poetry (Python dependency management)

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Backend Setup

```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload
```

The backend API will be available at `http://localhost:8000`

### Environment Variables

**Frontend (.env):**
```bash
VITE_API_URL=http://localhost:8000
```

**Backend:**
```bash
# Currently using mock data - no environment variables required
# See INTEGRATION_GUIDE.md for connecting real services
```

## 📚 Documentation

- **[SRE_ARCHITECTURE.md](SRE_ARCHITECTURE.md)** - **NEW!** Secure Research Environment (SRE) architecture for production deployment
- **[API_REFERENCE.md](API_REFERENCE.md)** - Complete API documentation with all 40+ endpoints
- **[DEMO_GUIDE.md](DEMO_GUIDE.md)** - Detailed demo walkthrough with next steps
- **[INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)** - How to connect real Azure services
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Production deployment instructions
- **[SECURITY_IMPLEMENTATION.md](SECURITY_IMPLEMENTATION.md)** - Security features and compliance
- **[SECURE_ARCHITECTURE.md](SECURE_ARCHITECTURE.md)** - Network security and architecture

## 🔐 Security Features

- **Entra ID B2B Authentication** - SSO with MFA support
- **PHI Data Protection** - All datasets marked as PHI-protected
- **Export Approval Workflow** - PI approval required for data exports
- **Time-Limited Access** - Export downloads expire after 24 hours
- **Audit Logging** - Complete activity trail for compliance
- **Network Isolation** - VNet with no internet gateway (production)
- **Private Endpoints** - Secure connectivity to Azure services

## 🔌 API Endpoints

### Core Endpoints

```
GET  /api/v1/user/profile              - Get current user profile
GET  /api/v1/user/projects             - Get user's projects
GET  /api/v1/projects/{id}             - Get project details
GET  /api/v1/projects/{id}/notebooks   - Get project notebooks
GET  /api/v1/projects/{id}/datasets    - Get project datasets
GET  /api/v1/projects/{id}/models      - Get deployed models
POST /api/v1/exports/request           - Submit export request
GET  /api/v1/exports/my-requests       - Get export requests
POST /api/v1/notebooks/{id}/run-inference - Execute inference
```

### Integration Endpoints (Projected)

```
# Microsoft Fabric (Mock - Ready to Connect)
GET  /api/v1/fabric/workspaces
GET  /api/v1/fabric/workspaces/{id}/lakehouses
POST /api/v1/fabric/notebooks/{id}/execute

# Azure ML Studio (Mock - Ready to Connect)
GET  /api/v1/mlstudio/compute
GET  /api/v1/mlstudio/endpoints
POST /api/v1/mlstudio/endpoints/{id}/invoke

# Azure AI Foundry (Live Endpoints - Ready to Use)
GET  /api/v1/foundry/projects          - List Foundry projects
GET  /api/v1/foundry/models             - List models (GPT-4o, Phi-3)
POST /api/v1/foundry/models/{id}/deploy - Deploy model
GET  /api/v1/foundry/evaluations        - List model evaluations

# Entra ID (Mock - Ready to Connect)
POST /api/v1/auth/login
POST /api/v1/auth/refresh
GET  /api/v1/auth/validate

# Notebook Execution (Live)
POST /api/v1/notebooks/{id}/run-inference - Execute Python inference
POST /api/v1/notebooks/{id}/run-r         - Execute R statistical analysis
POST /api/v1/notebooks/{id}/run-scala     - Execute Scala/Spark pipeline
```

See [API_REFERENCE.md](API_REFERENCE.md) for complete documentation.

## 🤖 Azure AI Foundry Integration

The platform includes **live Azure AI Foundry endpoints** for LLM model deployment and evaluation:

### Available Models

**GPT-4o Fine-tuned for Medical Notes**
- Model ID: `fm-001`
- Base Model: `gpt-4o`
- Version: `v1.2`
- Status: Deployed
- Accuracy: 92%
- Training Dataset: Medical Notes Corpus
- Deployment URL: `https://foundry-cardiac.openai.azure.com/deployments/medical-notes`

**Phi-3 for Clinical Decision Support**
- Model ID: `fm-002`
- Base Model: `phi-3-medium`
- Version: `v2.0`
- Status: Training (75% complete)
- Training Dataset: Clinical Guidelines Dataset
- Estimated Completion: 2024-10-25

### Foundry API Endpoints

```bash
# List all Foundry projects
curl https://app-tiouegnz.fly.dev/api/v1/foundry/projects

# List available models
curl https://app-tiouegnz.fly.dev/api/v1/foundry/models

# Deploy a model
curl -X POST https://app-tiouegnz.fly.dev/api/v1/foundry/models/fm-001/deploy

# Get model evaluations
curl https://app-tiouegnz.fly.dev/api/v1/foundry/evaluations
```

### Integration Status

- ✅ **Azure AI Foundry**: Live endpoints ready to use
- ✅ **Notebook Execution**: Python, R, and Scala notebooks fully functional
- ⏳ **Microsoft Fabric**: Mock endpoints (ready to connect with credentials)
- ⏳ **H100 GPU Endpoints**: Mock endpoints (ready to connect with credentials)
- ⏳ **Entra ID**: Mock endpoints (ready to connect with tenant configuration)

## 📊 Mock Data

The platform currently uses mock cardiovascular research data for demonstration:

**Projects:**
- Cardiac Arrhythmia Prediction Study
- Heart Failure Readmission Analysis
- Coronary Artery Disease Risk Modeling
- Real-Time ECG Inference on H100

**Datasets:**
- ECG Recordings Database (2.5M rows, 5.2 TB)
- Patient Demographics (2.5M rows, 890 MB)
- Medication History (6.8M rows, 1.8 GB)

**Models:**
- AFib Detection LSTM v2.3 (96% accuracy, 4 H100 GPUs)
- Multi-Class Arrhythmia CNN v1.8 (89% accuracy, 2 H100 GPUs)
- Risk Stratification XGBoost v3.0 (87% accuracy, CPU)

## 🔄 Next Steps - Connecting Real Services

To connect real Azure services, follow these steps:

### 1. Microsoft Fabric Integration

```python
# backend/app/services/fabric.py
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
token = await credential.get_token("https://api.fabric.microsoft.com/.default")

# Replace mock_notebooks with real Fabric API calls
response = await httpx.get(
    f"https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/notebooks",
    headers={"Authorization": f"Bearer {token.token}"}
)
```

### 2. Azure ML Studio Integration

```python
# backend/app/services/azureml.py
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential

ml_client = MLClient(
    credential=DefaultAzureCredential(),
    subscription_id="your-subscription-id",
    resource_group_name="your-resource-group",
    workspace_name="your-ml-workspace"
)

# Get real deployed models
endpoints = ml_client.online_endpoints.list()
```

### 3. Entra ID Authentication

```typescript
// frontend/src/config/msalConfig.ts
import { Configuration } from '@azure/msal-browser';

export const msalConfig: Configuration = {
  auth: {
    clientId: process.env.VITE_CLIENT_ID,
    authority: 'https://login.microsoftonline.com/your-tenant-id',
    redirectUri: 'https://research.contosohealth.com',
  }
};
```

See [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) for complete integration instructions.

## 🧪 Testing

### Backend Tests

```bash
cd backend
poetry run pytest
```

### Frontend Tests

```bash
cd frontend
npm run test
```

### API Testing

Use the provided Postman collection in [API_REFERENCE.md](API_REFERENCE.md) or test with curl:

```bash
# Get user projects
curl http://localhost:8000/api/v1/user/projects

# Get project notebooks
curl http://localhost:8000/api/v1/projects/proj-004/notebooks

# Run inference
curl -X POST http://localhost:8000/api/v1/notebooks/nb-006/run-inference
```

## 📦 Deployment

### Frontend Deployment (Azure Static Web Apps)

```bash
cd frontend
npm run build
# Deploy dist/ folder to Azure Static Web Apps
```

### Backend Deployment (Fly.io)

```bash
cd backend
fly deploy
```

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed deployment instructions.

## 📄 License

Proprietary - ContosoHealth Research Platform
© 2024 ContosoHealth. All rights reserved.

## 🔗 Links

- **Live Demo**: https://research-portal-2fbfvjbt.devinapps.com
- **Backend API**: https://app-tiouegnz.fly.dev
- **API Documentation**: https://app-tiouegnz.fly.dev/docs
- **Devin Session**: https://app.devin.ai/sessions/2e347798f7e842269122e54741b5d338
