# AdventHealth Research Platform - Integration Guide

## Overview
This guide explains how to connect the real Microsoft services (Entra ID, Fabric, ML Studio, Azure AI Foundry) to replace the mock endpoints.

## Current Architecture

The platform currently uses mock data and endpoints. All API endpoints are structured and ready for real service integration.

### Backend Structure
- **Location**: `/backend/app/main.py`
- **Mock Data**: Lines 111-416 contain all mock data
- **API Endpoints**: Lines 418-965 contain all endpoints

## Integration Steps

### 1. Entra ID Authentication

**Endpoints to Update:**
- `POST /api/v1/auth/login` (line 554)
- `POST /api/v1/auth/refresh` (line 564)
- `GET /api/v1/auth/validate` (line 571)

**Required Changes:**
```python
# Install required packages
# poetry add msal azure-identity

from msal import ConfidentialClientApplication
from azure.identity import DefaultAzureCredential

# Configuration (add to .env)
ENTRA_TENANT_ID = "your-tenant-id"
ENTRA_CLIENT_ID = "your-client-id"
ENTRA_CLIENT_SECRET = "your-client-secret"

# Replace mock login with real Entra ID
@app.post("/api/v1/auth/login")
async def entra_id_login(email: str, password: str):
    app = ConfidentialClientApplication(
        ENTRA_CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{ENTRA_TENANT_ID}",
        client_credential=ENTRA_CLIENT_SECRET
    )
    
    result = app.acquire_token_by_username_password(
        username=email,
        password=password,
        scopes=["User.Read"]
    )
    
    if "access_token" in result:
        return {
            "accessToken": result["access_token"],
            "refreshToken": result.get("refresh_token"),
            "expiresIn": result["expires_in"],
            "tokenType": "Bearer",
            "user": {
                "userId": result["id_token_claims"]["oid"],
                "email": result["id_token_claims"]["preferred_username"],
                "name": result["id_token_claims"]["name"]
            }
        }
    else:
        raise HTTPException(status_code=401, detail="Authentication failed")
```

### 2. Microsoft Fabric Integration

**Endpoints to Update:**
- `GET /api/v1/fabric/workspaces` (line 630)
- `GET /api/v1/fabric/workspaces/{workspace_id}` (line 663)
- `GET /api/v1/fabric/workspaces/{workspace_id}/lakehouses` (line 684)
- `POST /api/v1/fabric/notebooks/{notebook_id}/execute` (line 709)

**Required Changes:**
```python
# Install required packages
# poetry add azure-identity requests

import requests
from azure.identity import DefaultAzureCredential

# Configuration
FABRIC_API_BASE = "https://api.fabric.microsoft.com/v1"

# Get Azure credential
credential = DefaultAzureCredential()
token = credential.get_token("https://api.fabric.microsoft.com/.default")

# Replace mock workspaces with real Fabric API
@app.get("/api/v1/fabric/workspaces")
async def get_fabric_workspaces():
    headers = {
        "Authorization": f"Bearer {token.token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        f"{FABRIC_API_BASE}/workspaces",
        headers=headers
    )
    
    if response.status_code == 200:
        workspaces = response.json()["value"]
        return workspaces
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch workspaces")
```

**Fabric API Documentation:**
- Workspaces: https://learn.microsoft.com/en-us/rest/api/fabric/core/workspaces
- Notebooks: https://learn.microsoft.com/en-us/rest/api/fabric/notebook
- Lakehouses: https://learn.microsoft.com/en-us/rest/api/fabric/lakehouse

### 3. Azure ML Studio Integration

**Endpoints to Update:**
- `GET /api/v1/mlstudio/workspaces` (line 719)
- `GET /api/v1/mlstudio/compute` (line 736)
- `POST /api/v1/mlstudio/compute/{compute_id}/scale` (line 766)
- `GET /api/v1/mlstudio/endpoints` (line 775)
- `POST /api/v1/mlstudio/endpoints/{endpoint_id}/invoke` (line 808)

**Required Changes:**
```python
# Install required packages
# poetry add azure-ai-ml azure-identity

from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential

# Configuration
SUBSCRIPTION_ID = "your-subscription-id"
RESOURCE_GROUP = "your-resource-group"
WORKSPACE_NAME = "your-workspace-name"

# Create ML Client
credential = DefaultAzureCredential()
ml_client = MLClient(credential, SUBSCRIPTION_ID, RESOURCE_GROUP, WORKSPACE_NAME)

# Replace mock compute with real Azure ML
@app.get("/api/v1/mlstudio/compute")
async def get_ml_compute_targets():
    compute_targets = []
    
    for compute in ml_client.compute.list():
        compute_targets.append({
            "computeId": compute.name,
            "name": compute.name,
            "type": compute.type,
            "vmSize": compute.size,
            "minNodes": compute.scale_settings.min_instances if hasattr(compute, 'scale_settings') else 0,
            "maxNodes": compute.scale_settings.max_instances if hasattr(compute, 'scale_settings') else 0,
            "status": compute.provisioning_state,
            "location": compute.location
        })
    
    return compute_targets

# H100 GPU Endpoint Invocation
@app.post("/api/v1/mlstudio/endpoints/{endpoint_id}/invoke")
async def invoke_ml_endpoint(endpoint_id: str, data: dict):
    endpoint = ml_client.online_endpoints.get(endpoint_id)
    
    result = ml_client.online_endpoints.invoke(
        endpoint_name=endpoint_id,
        request_file=data
    )
    
    return {
        "endpointId": endpoint_id,
        "prediction": result,
        "timestamp": datetime.now().isoformat()
    }
```

**Azure ML Documentation:**
- ML Client: https://learn.microsoft.com/en-us/python/api/azure-ai-ml/azure.ai.ml.mlclient
- Compute: https://learn.microsoft.com/en-us/azure/machine-learning/how-to-create-attach-compute-cluster
- Endpoints: https://learn.microsoft.com/en-us/azure/machine-learning/how-to-deploy-online-endpoints

### 4. Azure AI Foundry Integration

**Endpoints to Update:**
- `GET /api/v1/foundry/projects` (line 824)
- `GET /api/v1/foundry/models` (line 839)
- `POST /api/v1/foundry/models/{model_id}/deploy` (line 865)
- `GET /api/v1/foundry/evaluations` (line 875)

**Required Changes:**
```python
# Install required packages
# poetry add azure-ai-projects azure-identity openai

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

# Configuration
PROJECT_CONNECTION_STRING = "your-project-connection-string"

# Create AI Project Client
credential = DefaultAzureCredential()
project_client = AIProjectClient.from_connection_string(
    credential=credential,
    conn_str=PROJECT_CONNECTION_STRING
)

# Replace mock models with real Foundry models
@app.get("/api/v1/foundry/models")
async def get_foundry_models():
    models = []
    
    for model in project_client.models.list():
        models.append({
            "modelId": model.id,
            "name": model.name,
            "baseModel": model.base_model,
            "version": model.version,
            "status": model.status,
            "trainingDate": model.created_at.isoformat()
        })
    
    return models
```

**Azure AI Foundry Documentation:**
- AI Projects: https://learn.microsoft.com/en-us/azure/ai-studio/
- Model Deployment: https://learn.microsoft.com/en-us/azure/ai-studio/how-to/deploy-models

### 5. Policy Management

**Endpoints to Update:**
- `GET /api/v1/policies` (line 578)
- `GET /api/v1/policies/{policy_id}` (line 622)

**Implementation Options:**

**Option A: Azure Policy**
```python
from azure.mgmt.policyinsights import PolicyInsightsClient

policy_client = PolicyInsightsClient(credential, SUBSCRIPTION_ID)

@app.get("/api/v1/policies")
async def get_policies():
    policies = []
    
    for policy in policy_client.policy_states.list_query_results_for_subscription(
        policy_states_resource="latest",
        subscription_id=SUBSCRIPTION_ID
    ):
        policies.append({
            "policyId": policy.policy_definition_id,
            "name": policy.policy_definition_name,
            "status": policy.compliance_state
        })
    
    return policies
```

**Option B: Custom Policy Engine**
Store policies in Azure SQL Database and implement custom RBAC logic.

### 6. Environment Variables

Create a `.env` file in the backend directory:

```bash
# Entra ID
ENTRA_TENANT_ID=your-tenant-id
ENTRA_CLIENT_ID=your-client-id
ENTRA_CLIENT_SECRET=your-client-secret

# Azure Subscription
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_RESOURCE_GROUP=your-resource-group

# Microsoft Fabric
FABRIC_CAPACITY_ID=your-fabric-capacity-id

# Azure ML
ML_WORKSPACE_NAME=your-ml-workspace
ML_REGION=eastus

# Azure AI Foundry
FOUNDRY_PROJECT_CONNECTION_STRING=your-connection-string

# Database (if using real DB instead of in-memory)
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

Load environment variables in `main.py`:
```python
from dotenv import load_dotenv
import os

load_dotenv()

ENTRA_TENANT_ID = os.getenv("ENTRA_TENANT_ID")
ENTRA_CLIENT_ID = os.getenv("ENTRA_CLIENT_ID")
# ... etc
```

### 7. Database Migration (Optional)

To persist data instead of using in-memory storage:

```python
# Install SQLAlchemy
# poetry add sqlalchemy psycopg2-binary

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Replace mock_projects with database queries
@app.get("/api/v1/user/projects")
async def get_user_projects():
    db = SessionLocal()
    projects = db.query(Project).filter(Project.piEmail == mock_user["email"]).all()
    db.close()
    return projects
```

## Testing Integration

### 1. Test Entra ID Authentication
```bash
curl -X POST https://app-tiouegnz.fly.dev/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "your-email@adventhealth.com", "password": "your-password"}'
```

### 2. Test Fabric Workspaces
```bash
curl -X GET https://app-tiouegnz.fly.dev/api/v1/fabric/workspaces \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Test ML Studio Compute
```bash
curl -X GET https://app-tiouegnz.fly.dev/api/v1/mlstudio/compute \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. Test H100 Endpoint Invocation
```bash
curl -X POST https://app-tiouegnz.fly.dev/api/v1/mlstudio/endpoints/ep-001/invoke \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"data": [[0.1, 0.2, 0.3, ...]]}'
```

## Deployment After Integration

After updating the code with real integrations:

1. **Test locally first:**
```bash
cd backend
poetry run fastapi dev app/main.py
```

2. **Deploy backend:**
```bash
# From project root
deploy backend --dir backend
```

3. **Rebuild and deploy frontend:**
```bash
cd frontend
npm run build
deploy frontend --dir frontend/dist
```

## Security Considerations

1. **Never commit secrets** - Use environment variables and Azure Key Vault
2. **Enable HTTPS only** - Already configured in deployment
3. **Implement rate limiting** - Add middleware for API rate limits
4. **Audit logging** - All endpoints log to `/api/v1/admin/audit`
5. **Token validation** - Validate Entra ID tokens on every request
6. **Network isolation** - Use Azure Private Endpoints for Fabric/ML Studio

## Support

For questions about integration:
- Entra ID: https://learn.microsoft.com/en-us/entra/identity/
- Microsoft Fabric: https://learn.microsoft.com/en-us/fabric/
- Azure ML: https://learn.microsoft.com/en-us/azure/machine-learning/
- Azure AI Foundry: https://learn.microsoft.com/en-us/azure/ai-studio/

## API Endpoint Summary

### Authentication
- `POST /api/v1/auth/login` - Entra ID login
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/validate` - Validate current token

### Policies
- `GET /api/v1/policies` - List all policies
- `GET /api/v1/policies/{policy_id}` - Get policy details

### Microsoft Fabric
- `GET /api/v1/fabric/workspaces` - List workspaces
- `GET /api/v1/fabric/workspaces/{workspace_id}` - Workspace details
- `GET /api/v1/fabric/workspaces/{workspace_id}/lakehouses` - List lakehouses
- `POST /api/v1/fabric/notebooks/{notebook_id}/execute` - Execute notebook

### Azure ML Studio
- `GET /api/v1/mlstudio/workspaces` - List ML workspaces
- `GET /api/v1/mlstudio/compute` - List compute targets (including H100)
- `POST /api/v1/mlstudio/compute/{compute_id}/scale` - Scale compute
- `GET /api/v1/mlstudio/endpoints` - List model endpoints
- `POST /api/v1/mlstudio/endpoints/{endpoint_id}/invoke` - Invoke model

### Azure AI Foundry
- `GET /api/v1/foundry/projects` - List Foundry projects
- `GET /api/v1/foundry/models` - List Foundry models
- `POST /api/v1/foundry/models/{model_id}/deploy` - Deploy model
- `GET /api/v1/foundry/evaluations` - List model evaluations

### Admin
- `GET /api/v1/admin/users` - List all users
- `POST /api/v1/admin/users/invite` - Invite new user
- `GET /api/v1/admin/audit` - Get audit logs

### Projects (Already Working)
- `GET /api/v1/user/projects` - User's projects
- `GET /api/v1/projects/{project_id}` - Project details
- `GET /api/v1/projects/{project_id}/notebooks` - Project notebooks
- `GET /api/v1/projects/{project_id}/datasets` - Project datasets
- `GET /api/v1/projects/{project_id}/models` - Project models
- `GET /api/v1/projects/{project_id}/activity` - Project activity

### Exports (Already Working)
- `GET /api/v1/exports/my-requests` - User's export requests
- `POST /api/v1/exports/request` - Create export request
- `POST /api/v1/exports/{request_id}/review` - Review export request

### Notifications (Already Working)
- `GET /api/v1/notifications` - Get notifications
- `PATCH /api/v1/notifications/{notification_id}/read` - Mark as read

### Compute (Already Working)
- `GET /api/v1/compute/h100` - H100 GPU cluster status
