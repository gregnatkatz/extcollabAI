# AdventHealth Research Platform - API Endpoints

## Base URL
- **Local**: http://localhost:8000
- **Production**: https://app-tiouegnz.fly.dev

## Authentication Endpoints

### POST /api/v1/auth/login
Mock Entra ID authentication
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "dr.smith@adventhealth.com", "password": "password"}'
```

Response:
```json
{
  "accessToken": "mock_token_...",
  "refreshToken": "mock_refresh_...",
  "expiresIn": 3600,
  "tokenType": "Bearer",
  "user": {...}
}
```

### POST /api/v1/auth/refresh
Refresh access token
```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refreshToken": "mock_refresh_..."}'
```

### GET /api/v1/auth/validate
Validate current token
```bash
curl http://localhost:8000/api/v1/auth/validate
```

## Policy Management Endpoints

### GET /api/v1/policies
List all policies (PHI Data Access, Export Approval, Model Deployment)
```bash
curl http://localhost:8000/api/v1/policies
```

Response:
```json
[
  {
    "policyId": "pol-001",
    "name": "PHI Data Access Policy",
    "type": "DataAccess",
    "description": "Controls access to PHI-protected datasets",
    "status": "Active",
    "rules": [...]
  }
]
```

### GET /api/v1/policies/{policy_id}
Get policy details
```bash
curl http://localhost:8000/api/v1/policies/pol-001
```

## Microsoft Fabric Endpoints

### GET /api/v1/fabric/workspaces
List all Fabric workspaces
```bash
curl http://localhost:8000/api/v1/fabric/workspaces
```

Response:
```json
[
  {
    "workspaceId": "ws-001",
    "name": "Cardiac Research Workspace",
    "description": "Primary workspace for cardiac arrhythmia studies",
    "capacityId": "cap-f64-001",
    "region": "East US",
    "status": "Active",
    "owner": "dr.smith@adventhealth.com",
    "members": 5,
    "storageUsed": "2.3 TB",
    "storageLimit": "10 TB"
  }
]
```

### GET /api/v1/fabric/workspaces/{workspace_id}
Get workspace details with items and compute info
```bash
curl http://localhost:8000/api/v1/fabric/workspaces/ws-001
```

### GET /api/v1/fabric/workspaces/{workspace_id}/lakehouses
List lakehouses in workspace
```bash
curl http://localhost:8000/api/v1/fabric/workspaces/ws-001/lakehouses
```

Response:
```json
[
  {
    "lakehouseId": "lh-001",
    "name": "ECG Data Lakehouse",
    "workspaceId": "ws-001",
    "storageUsed": "1.2 TB",
    "tables": 15,
    "files": 2500,
    "status": "Active"
  }
]
```

### POST /api/v1/fabric/notebooks/{notebook_id}/execute
Execute a Fabric notebook
```bash
curl -X POST http://localhost:8000/api/v1/fabric/notebooks/nb-001/execute
```

Response:
```json
{
  "executionId": "exec-...",
  "notebookId": "nb-001",
  "status": "Running",
  "startedAt": "2024-10-19T...",
  "estimatedDuration": "5-10 minutes"
}
```

## Azure ML Studio Endpoints

### GET /api/v1/mlstudio/workspaces
List ML workspaces
```bash
curl http://localhost:8000/api/v1/mlstudio/workspaces
```

### GET /api/v1/mlstudio/compute
List compute targets including H100 GPU cluster
```bash
curl http://localhost:8000/api/v1/mlstudio/compute
```

Response:
```json
[
  {
    "computeId": "compute-h100-001",
    "name": "H100-GPU-Cluster",
    "type": "AmlCompute",
    "vmSize": "Standard_NC96ads_A100_v4",
    "gpuType": "H100",
    "minNodes": 0,
    "maxNodes": 8,
    "currentNodes": 4,
    "idleNodes": 0,
    "status": "Running",
    "location": "East US"
  }
]
```

### POST /api/v1/mlstudio/compute/{compute_id}/scale
Scale compute cluster
```bash
curl -X POST http://localhost:8000/api/v1/mlstudio/compute/compute-h100-001/scale \
  -H "Content-Type: application/json" \
  -d '{"targetNodes": 8}'
```

### GET /api/v1/mlstudio/endpoints
List model endpoints
```bash
curl http://localhost:8000/api/v1/mlstudio/endpoints
```

Response:
```json
[
  {
    "endpointId": "ep-001",
    "name": "afib-detection-endpoint",
    "modelName": "AFib Detection LSTM",
    "modelVersion": "v2.3",
    "status": "Healthy",
    "computeType": "H100",
    "instanceCount": 2,
    "requestsPerMinute": 450,
    "avgLatency": "45ms",
    "errorRate": 0.002,
    "scoringUri": "https://afib-detection.eastus.inference.ml.azure.com/score"
  }
]
```

### POST /api/v1/mlstudio/endpoints/{endpoint_id}/invoke
Invoke model endpoint (H100 inference)
```bash
curl -X POST http://localhost:8000/api/v1/mlstudio/endpoints/ep-001/invoke \
  -H "Content-Type: application/json" \
  -d '{"data": [[0.1, 0.2, 0.3]]}'
```

Response:
```json
{
  "endpointId": "ep-001",
  "prediction": {
    "class": "AFib Detected",
    "confidence": 0.94,
    "probabilities": {
      "Normal": 0.06,
      "AFib": 0.94
    }
  },
  "latency": "43ms",
  "timestamp": "2024-10-19T..."
}
```

### GET /api/v1/compute/h100
Get H100 GPU cluster status
```bash
curl http://localhost:8000/api/v1/compute/h100
```

Response:
```json
{
  "totalGPUs": 8,
  "availableGPUs": 4,
  "activeJobs": [
    {
      "jobId": "job-001",
      "projectName": "Cardiac Arrhythmia Prediction Study",
      "modelName": "Multi-Class Arrhythmia CNN",
      "gpusUsed": 4,
      "status": "Training",
      "progress": 67
    }
  ]
}
```

## Azure AI Foundry Endpoints

### GET /api/v1/foundry/projects
List Foundry projects
```bash
curl http://localhost:8000/api/v1/foundry/projects
```

### GET /api/v1/foundry/models
List Foundry models (GPT-4o, Phi-3, etc.)
```bash
curl http://localhost:8000/api/v1/foundry/models
```

Response:
```json
[
  {
    "modelId": "fm-001",
    "name": "GPT-4o Fine-tuned for Medical Notes",
    "baseModel": "gpt-4o",
    "version": "v1.2",
    "status": "Deployed",
    "accuracy": 0.92,
    "trainingDataset": "Medical Notes Corpus",
    "trainingDate": "2024-09-15T00:00:00Z",
    "deploymentUrl": "https://foundry-cardiac.openai.azure.com/deployments/medical-notes"
  }
]
```

### POST /api/v1/foundry/models/{model_id}/deploy
Deploy Foundry model
```bash
curl -X POST http://localhost:8000/api/v1/foundry/models/fm-001/deploy
```

Response:
```json
{
  "modelId": "fm-001",
  "deploymentId": "deploy-...",
  "status": "Deploying",
  "estimatedTime": "10-15 minutes",
  "endpoint": "https://foundry-cardiac.openai.azure.com/deployments/fm-001"
}
```

### GET /api/v1/foundry/evaluations
List model evaluations
```bash
curl http://localhost:8000/api/v1/foundry/evaluations
```

## Admin Endpoints

### GET /api/v1/admin/users
List all users (staff and B2B guests)
```bash
curl http://localhost:8000/api/v1/admin/users
```

Response:
```json
[
  {
    "userId": "user-001",
    "email": "dr.smith@adventhealth.com",
    "name": "Dr. Sarah Smith",
    "role": "PI",
    "institution": "AdventHealth Orlando",
    "accountType": "Staff",
    "status": "Active",
    "projects": 2,
    "lastLogin": "2024-10-19T14:30:00Z"
  }
]
```

### POST /api/v1/admin/users/invite
Invite B2B guest user
```bash
curl -X POST http://localhost:8000/api/v1/admin/users/invite \
  -H "Content-Type: application/json" \
  -d '{"email": "researcher@external.edu", "role": "Contributor", "projectId": "proj-001"}'
```

Response:
```json
{
  "invitationId": "inv-...",
  "email": "researcher@external.edu",
  "role": "Contributor",
  "projectId": "proj-001",
  "status": "Sent",
  "expiresAt": "2024-10-26T...",
  "invitationUrl": "https://research.adventhealth.com/invite/..."
}
```

### GET /api/v1/admin/audit
Get audit logs
```bash
curl http://localhost:8000/api/v1/admin/audit
```

Response:
```json
[
  {
    "auditId": "audit-001",
    "userId": "user-001",
    "userEmail": "dr.smith@adventhealth.com",
    "action": "DatasetAccessed",
    "resource": "ECG Recordings Database",
    "resourceId": "ds-001",
    "projectId": "proj-001",
    "timestamp": "2024-10-19T14:30:00Z",
    "ipAddress": "10.0.1.25",
    "result": "Success"
  }
]
```

## Project Endpoints (Already Working)

### GET /api/v1/user/profile
Get current user profile
```bash
curl http://localhost:8000/api/v1/user/profile
```

### GET /api/v1/user/projects
Get user's projects
```bash
curl http://localhost:8000/api/v1/user/projects
```

### GET /api/v1/projects/{project_id}
Get project details
```bash
curl http://localhost:8000/api/v1/projects/proj-001
```

### GET /api/v1/projects/{project_id}/activity
Get project activity feed
```bash
curl http://localhost:8000/api/v1/projects/proj-001/activity
```

### GET /api/v1/projects/{project_id}/notebooks
Get project notebooks
```bash
curl http://localhost:8000/api/v1/projects/proj-001/notebooks
```

### GET /api/v1/projects/{project_id}/datasets
Get project datasets
```bash
curl http://localhost:8000/api/v1/projects/proj-001/datasets
```

### GET /api/v1/projects/{project_id}/models
Get project models
```bash
curl http://localhost:8000/api/v1/projects/proj-001/models
```

## Export Endpoints (Already Working)

### GET /api/v1/exports/my-requests
Get user's export requests
```bash
curl http://localhost:8000/api/v1/exports/my-requests
```

### POST /api/v1/exports/request
Create export request
```bash
curl -X POST http://localhost:8000/api/v1/exports/request \
  -H "Content-Type: application/json" \
  -d '{
    "projectId": "proj-001",
    "datasetName": "ECG Recordings Database",
    "rowCount": 1000,
    "justification": "Need data for model training"
  }'
```

### POST /api/v1/exports/{request_id}/review
Review export request (PI only)
```bash
curl -X POST http://localhost:8000/api/v1/exports/exp-12345678/review \
  -H "Content-Type: application/json" \
  -d '{
    "decision": "Approved",
    "notes": "Approved for research purposes"
  }'
```

## Notification Endpoints (Already Working)

### GET /api/v1/notifications
Get notifications
```bash
curl http://localhost:8000/api/v1/notifications?unreadOnly=true
```

### PATCH /api/v1/notifications/{notification_id}/read
Mark notification as read
```bash
curl -X PATCH http://localhost:8000/api/v1/notifications/notif-001/read
```

## Health Check

### GET /healthz
Health check endpoint
```bash
curl http://localhost:8000/healthz
```

Response:
```json
{
  "status": "ok"
}
```

## Notes

- All endpoints currently return mock data
- Authentication is not enforced (mock tokens accepted)
- See `INTEGRATION_GUIDE.md` for instructions on connecting real services
- Frontend is deployed at: https://research-portal-2fbfvjbt.devinapps.com
- Backend is deployed at: https://app-tiouegnz.fly.dev
