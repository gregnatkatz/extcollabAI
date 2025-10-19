# AdventHealth Research Platform - API Reference

Complete API documentation for all endpoints with request/response examples.

**Base URL**: `https://app-tiouegnz.fly.dev`

---

## Authentication

All endpoints require authentication (mock for demo):

```http
Authorization: Bearer <token>
```

To get a token (mock):
```bash
curl -X POST https://app-tiouegnz.fly.dev/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "dr.smith@adventhealth.com", "password": "mock"}'
```

---

## User & Projects

### Get User Profile

```http
GET /api/v1/user/profile
```

**Response**:
```json
{
  "userId": "user-001",
  "email": "dr.smith@adventhealth.com",
  "name": "Dr. Sarah Smith",
  "institution": "AdventHealth Orlando",
  "accountType": "Staff",
  "accessExpires": "2025-10-19T00:00:00Z",
  "projects": ["proj-001", "proj-002", "proj-004"]
}
```

### Get User's Projects

```http
GET /api/v1/user/projects
```

**Response**:
```json
[
  {
    "projectId": "proj-004",
    "name": "Real-Time ECG Inference on H100",
    "piName": "Dr. Sarah Smith",
    "piEmail": "dr.smith@adventhealth.com",
    "fabricWorkspaceUrl": "https://fabric.microsoft.com/workspace/ecg-inference",
    "mlWorkspaceUrl": "https://ml.azure.com/workspace/ecg-inference-ml",
    "status": "Active",
    "createdAt": "2024-10-01T08:00:00Z",
    "description": "Production inference pipeline for real-time arrhythmia detection using H100 GPUs with sub-50ms latency",
    "stats": {
      "notebooks": 1,
      "datasets": 2,
      "models": 1,
      "recentActivity": 0
    }
  }
]
```

### Get Project Details

```http
GET /api/v1/projects/{project_id}
```

**Example**:
```bash
curl https://app-tiouegnz.fly.dev/api/v1/projects/proj-004
```

**Response**: Same as project object above

---

## Notebooks

### Get Project Notebooks

```http
GET /api/v1/projects/{project_id}/notebooks
```

**Example**:
```bash
curl https://app-tiouegnz.fly.dev/api/v1/projects/proj-004/notebooks
```

**Response**:
```json
[
  {
    "notebookId": "nb-006",
    "name": "Real-Time Inference Pipeline",
    "language": "Python",
    "author": "Dr. Sarah Smith",
    "modified": "2024-10-19T10:00:00Z",
    "status": "Ready",
    "fabricUrl": "https://fabric.microsoft.com/notebook/inference-pipeline",
    "executableCode": "import numpy as np\nimport time\n..."
  }
]
```

### Run Inference (NEW!)

```http
POST /api/v1/notebooks/{notebook_id}/run-inference
```

**Example**:
```bash
curl -X POST https://app-tiouegnz.fly.dev/api/v1/notebooks/nb-006/run-inference
```

**Response**:
```json
{
  "executionId": "exec-12345678-1234-1234-1234-123456789abc",
  "notebookId": "nb-006",
  "status": "Completed",
  "output": "=== Real-Time ECG Inference on H100 GPU ===\n\nInput: ECG signal with 5000 samples\nPreprocessing: Complete (normalized and filtered)\n\nModel: AFib Detection LSTM v2.3\nGPU: H100-0\nInference Time: 42.44ms\n\nPredictions:\n  normal_sinus_rhythm                      12.00% ██████\n  atrial_fibrillation                      78.00% ███████████████████████████████████████\n  premature_ventricular_contraction         6.00% ███\n  ventricular_tachycardia                   4.00% ██\n\n✓ Predicted: ATRIAL_FIBRILLATION (confidence: 78.0%)\n✓ Latency: 42.44ms (target: <50ms)",
  "result": {
    "model": "AFib Detection LSTM v2.3",
    "predictions": {
      "normal_sinus_rhythm": 0.12,
      "atrial_fibrillation": 0.78,
      "premature_ventricular_contraction": 0.06,
      "ventricular_tachycardia": 0.04
    },
    "predicted_class": "atrial_fibrillation",
    "confidence": 0.78,
    "inference_time_ms": 42.44,
    "gpu_used": "H100-0",
    "timestamp": "2024-10-19T15:30:45.123456"
  },
  "startedAt": "2024-10-19T15:30:45.080000",
  "completedAt": "2024-10-19T15:30:45.123456",
  "duration": "42.44ms"
}
```

**Key Features**:
- Executes real Python code with numpy
- Simulates ECG signal processing
- Returns realistic inference results
- Sub-50ms latency on H100 GPU
- Complete console output for demo

---

## Datasets

### Get Project Datasets

```http
GET /api/v1/projects/{project_id}/datasets
```

**Example**:
```bash
curl https://app-tiouegnz.fly.dev/api/v1/projects/proj-004/datasets
```

**Response**:
```json
[
  {
    "datasetId": "ds-006",
    "name": "Real-Time ECG Stream",
    "rows": 2500000,
    "size": "180 GB",
    "tables": 1,
    "security": "PHI Protected",
    "accessLevel": "Contributor"
  },
  {
    "datasetId": "ds-007",
    "name": "Inference Results Archive",
    "rows": 8500000,
    "size": "95 GB",
    "tables": 2,
    "security": "PHI Protected",
    "accessLevel": "Viewer"
  }
]
```

---

## Models

### Get Project Models

```http
GET /api/v1/projects/{project_id}/models
```

**Example**:
```bash
curl https://app-tiouegnz.fly.dev/api/v1/projects/proj-004/models
```

**Response**:
```json
[
  {
    "modelId": "model-004",
    "name": "Production AFib Detector",
    "version": "v3.0",
    "framework": "PyTorch",
    "status": "Deployed",
    "gpus": 4,
    "latency": "42ms",
    "accuracy": 0.96,
    "mlStudioUrl": "https://ml.azure.com/model/production-afib"
  }
]
```

---

## Export Workflow

### Get My Export Requests

```http
GET /api/v1/exports/my-requests?status=Pending
```

**Query Parameters**:
- `status` (optional): Filter by status (Pending, Approved, Rejected, Completed)

**Response**:
```json
[
  {
    "requestId": "exp-001",
    "requestNumber": "EXP-2024-001",
    "projectId": "proj-001",
    "requestorEmail": "researcher@external.edu",
    "datasetName": "ECG Recordings Database",
    "rowCount": 1000,
    "justification": "Need sample data for validation of external arrhythmia detection algorithm",
    "status": "Pending",
    "piReviewer": "Dr. Sarah Smith",
    "requestedAt": "2024-10-17T10:00:00Z"
  }
]
```

### Create Export Request

```http
POST /api/v1/exports/request
```

**Request Body**:
```json
{
  "projectId": "proj-004",
  "datasetName": "Real-Time ECG Stream",
  "rowCount": 1000,
  "justification": "Need to export ECG data for training a new deep learning model to detect atrial fibrillation patterns. The model requires 1000 labeled ECG recordings for validation."
}
```

**Response**:
```json
{
  "requestId": "exp-003",
  "requestNumber": "EXP-2024-003",
  "projectId": "proj-004",
  "requestorEmail": "dr.smith@adventhealth.com",
  "datasetName": "Real-Time ECG Stream",
  "rowCount": 1000,
  "justification": "Need to export ECG data for training...",
  "status": "Pending",
  "piReviewer": "Dr. Sarah Smith",
  "piReviewerEmail": "dr.smith@adventhealth.com",
  "requestedAt": "2024-10-19T15:45:00Z",
  "estimatedApprovalTime": "3-5 business days"
}
```

### Review Export Request (PI Only)

```http
POST /api/v1/exports/{request_id}/review
```

**Request Body**:
```json
{
  "decision": "Approved",
  "notes": "Approved for research purposes. Data is de-identified and limited to 1000 records."
}
```

**Response**:
```json
{
  "requestId": "exp-003",
  "requestNumber": "EXP-2024-003",
  "status": "Approved",
  "reviewedAt": "2024-10-19T16:00:00Z",
  "reviewNotes": "Approved for research purposes...",
  "downloadUrl": "https://storage.blob.core.windows.net/exports/EXP-2024-003.zip?sv=2021-06-08&se=2024-10-20T16%3A00%3A00Z&sr=b&sp=r&sig=...",
  "downloadExpiresAt": "2024-10-20T16:00:00Z"
}
```

---

## Notifications

### Get Notifications

```http
GET /api/v1/notifications?unreadOnly=true
```

**Query Parameters**:
- `unreadOnly` (optional): Only return unread notifications

**Response**:
```json
[
  {
    "notificationId": "notif-001",
    "type": "Success",
    "message": "Your export request EXP-2024-002 has been approved. Download link expires in 24 hours.",
    "isRead": false,
    "relatedEntityType": "Export",
    "relatedEntityId": "exp-002",
    "createdAt": "2024-10-18T14:00:00Z"
  }
]
```

### Mark Notification as Read

```http
PATCH /api/v1/notifications/{notification_id}/read
```

**Response**:
```json
{
  "success": true
}
```

---

## External Access Requests

### Submit Access Request

```http
POST /api/v1/access-requests
```

**Request Body**:
```json
{
  "fullName": "Dr. John Doe",
  "email": "john.doe@external.edu",
  "institution": "External University",
  "position": "Associate Professor",
  "projectInterest": "Real-Time ECG Inference on H100",
  "researchPurpose": "Developing novel deep learning algorithms for arrhythmia detection in real-time clinical settings",
  "dataNeeded": "ECG recordings with labeled arrhythmia events",
  "hipaaTraining": true,
  "irbApproval": true,
  "dataSecurityAgreement": true,
  "noExternalSharing": true,
  "institutionalAgreement": true
}
```

**Response**:
```json
{
  "requestId": "acc-12345678-1234-1234-1234-123456789abc",
  "status": "Pending",
  "message": "Access request submitted successfully. A PI will review within 3-5 business days.",
  "estimatedReviewDate": "2024-10-22T15:45:00Z"
}
```

---

## H100 GPU Status

### Get H100 Cluster Status

```http
GET /api/v1/h100/status
```

**Response**:
```json
{
  "totalGPUs": 8,
  "availableGPUs": 4,
  "activeJobs": [
    {
      "jobId": "job-001",
      "projectId": "proj-004",
      "modelName": "Production AFib Detector",
      "gpusUsed": 4,
      "status": "Running",
      "startedAt": "2024-10-19T15:30:00Z"
    }
  ]
}
```

---

## Microsoft Fabric Integration

### Get Fabric Workspaces

```http
GET /api/v1/fabric/workspaces
```

**Response**:
```json
[
  {
    "workspaceId": "ws-001",
    "name": "Cardiac Research Workspace",
    "description": "Main workspace for cardiovascular research projects",
    "capacityId": "cap-001",
    "region": "East US",
    "status": "Active",
    "lakehouses": 3,
    "notebooks": 12,
    "createdAt": "2024-01-15T00:00:00Z"
  }
]
```

### Get Workspace Details

```http
GET /api/v1/fabric/workspaces/{workspace_id}
```

**Response**:
```json
{
  "workspaceId": "ws-001",
  "name": "Cardiac Research Workspace",
  "description": "Main workspace for cardiovascular research projects",
  "capacityId": "cap-001",
  "region": "East US",
  "status": "Active",
  "lakehouses": 3,
  "notebooks": 12,
  "createdAt": "2024-01-15T00:00:00Z",
  "members": [
    {
      "userId": "user-001",
      "email": "dr.smith@adventhealth.com",
      "role": "Admin"
    }
  ]
}
```

### Get Lakehouses

```http
GET /api/v1/fabric/workspaces/{workspace_id}/lakehouses
```

**Response**:
```json
[
  {
    "lakehouseId": "lh-001",
    "name": "ECG Data Lakehouse",
    "description": "Centralized storage for ECG recordings and analysis results",
    "status": "Active",
    "storageSize": "2.5 TB",
    "tables": 15,
    "files": 125000,
    "createdAt": "2024-01-20T00:00:00Z"
  }
]
```

### Execute Notebook

```http
POST /api/v1/fabric/notebooks/{notebook_id}/execute
```

**Response**:
```json
{
  "executionId": "exec-12345678-1234-1234-1234-123456789abc",
  "notebookId": "nb-006",
  "status": "Running",
  "startedAt": "2024-10-19T15:45:00Z",
  "estimatedDuration": "5-10 minutes"
}
```

---

## Azure ML Studio Integration

### Get ML Workspaces

```http
GET /api/v1/mlstudio/workspaces
```

**Response**:
```json
[
  {
    "workspaceId": "mlws-001",
    "name": "Cardiac ML Workspace",
    "subscriptionId": "sub-001",
    "resourceGroup": "rg-cardiac-research",
    "region": "East US",
    "status": "Active",
    "computeTargets": 3,
    "models": 8,
    "endpoints": 4,
    "createdAt": "2024-01-15T10:00:00Z"
  }
]
```

### Get Compute Targets

```http
GET /api/v1/mlstudio/compute
```

**Response**:
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

### Scale Compute

```http
POST /api/v1/mlstudio/compute/{compute_id}/scale
```

**Request Body**:
```json
{
  "targetNodes": 8
}
```

**Response**:
```json
{
  "computeId": "compute-h100-001",
  "targetNodes": 8,
  "status": "Scaling",
  "estimatedTime": "3-5 minutes"
}
```

### Get ML Endpoints

```http
GET /api/v1/mlstudio/endpoints
```

**Response**:
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
    "deployedAt": "2024-10-10T00:00:00Z",
    "scoringUri": "https://afib-detection.eastus.inference.ml.azure.com/score"
  }
]
```

### Invoke ML Endpoint

```http
POST /api/v1/mlstudio/endpoints/{endpoint_id}/invoke
```

**Request Body**:
```json
{
  "data": {
    "ecg_signal": [0.1, 0.2, 0.15, ...]
  }
}
```

**Response**:
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
  "timestamp": "2024-10-19T15:50:00Z"
}
```

---

## Azure AI Foundry Integration

### Get Foundry Projects

```http
GET /api/v1/foundry/projects
```

**Response**:
```json
[
  {
    "projectId": "foundry-001",
    "name": "Cardiac Research Foundation",
    "description": "Azure AI Foundry project for cardiac research models",
    "status": "Active",
    "models": 5,
    "datasets": 8,
    "experiments": 23,
    "createdAt": "2024-01-15T00:00:00Z"
  }
]
```

### Get Foundry Models

```http
GET /api/v1/foundry/models
```

**Response**:
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

### Deploy Foundry Model

```http
POST /api/v1/foundry/models/{model_id}/deploy
```

**Response**:
```json
{
  "modelId": "fm-001",
  "deploymentId": "deploy-12345678-1234-1234-1234-123456789abc",
  "status": "Deploying",
  "estimatedTime": "10-15 minutes",
  "endpoint": "https://foundry-cardiac.openai.azure.com/deployments/fm-001"
}
```

### Get Model Evaluations

```http
GET /api/v1/foundry/evaluations
```

**Response**:
```json
[
  {
    "evaluationId": "eval-001",
    "modelId": "fm-001",
    "modelName": "GPT-4o Fine-tuned for Medical Notes",
    "metrics": {
      "accuracy": 0.92,
      "precision": 0.91,
      "recall": 0.93,
      "f1Score": 0.92,
      "perplexity": 12.5
    },
    "testDataset": "Medical Notes Test Set",
    "evaluatedAt": "2024-09-20T00:00:00Z"
  }
]
```

---

## Admin Endpoints

### Get Users

```http
GET /api/v1/admin/users
```

**Response**:
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
    "lastLogin": "2024-10-19T14:30:00Z",
    "createdAt": "2024-01-10T00:00:00Z"
  }
]
```

### Invite User

```http
POST /api/v1/admin/users/invite
```

**Request Body**:
```json
{
  "email": "researcher@external.edu",
  "role": "Contributor",
  "projectId": "proj-004"
}
```

**Response**:
```json
{
  "invitationId": "inv-12345678-1234-1234-1234-123456789abc",
  "email": "researcher@external.edu",
  "role": "Contributor",
  "projectId": "proj-004",
  "status": "Sent",
  "expiresAt": "2024-10-26T15:55:00Z",
  "invitationUrl": "https://research.adventhealth.com/invite/12345678-1234-1234-1234-123456789abc"
}
```

### Get Audit Logs

```http
GET /api/v1/admin/audit?startDate=2024-10-01&endDate=2024-10-19
```

**Query Parameters**:
- `startDate` (optional): Start date for audit logs (ISO 8601)
- `endDate` (optional): End date for audit logs (ISO 8601)

**Response**:
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
    "userAgent": "Mozilla/5.0",
    "result": "Success"
  }
]
```

---

## Policies

### Get All Policies

```http
GET /api/v1/policies
```

**Response**:
```json
[
  {
    "policyId": "pol-001",
    "name": "PHI Data Access Policy",
    "description": "Governs access to Protected Health Information in research datasets",
    "category": "Data Access",
    "status": "Active",
    "version": "2.1",
    "effectiveDate": "2024-01-01T00:00:00Z",
    "requirements": [
      "HIPAA training certification",
      "IRB approval for research protocol",
      "Signed data use agreement",
      "Multi-factor authentication enabled",
      "Annual recertification required"
    ]
  }
]
```

### Get Policy Details

```http
GET /api/v1/policies/{policy_id}
```

**Response**: Same as policy object above with additional details

---

## Error Responses

All endpoints return standard error responses:

**400 Bad Request**:
```json
{
  "error": "Bad Request",
  "message": "Missing required field: justification",
  "code": "VALIDATION_ERROR"
}
```

**401 Unauthorized**:
```json
{
  "error": "Unauthorized",
  "message": "Invalid or expired token",
  "code": "AUTH_ERROR"
}
```

**403 Forbidden**:
```json
{
  "error": "Forbidden",
  "message": "Insufficient permissions to access this resource",
  "code": "PERMISSION_DENIED"
}
```

**404 Not Found**:
```json
{
  "error": "Not Found",
  "message": "Project with ID 'proj-999' not found",
  "code": "RESOURCE_NOT_FOUND"
}
```

**500 Internal Server Error**:
```json
{
  "error": "Internal Server Error",
  "message": "An unexpected error occurred",
  "code": "INTERNAL_ERROR"
}
```

---

## Rate Limiting

All endpoints are rate limited:
- **Authenticated requests**: 1000 requests per hour
- **Unauthenticated requests**: 100 requests per hour

Rate limit headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 995
X-RateLimit-Reset: 1697734800
```

---

## Testing with cURL

### Complete Workflow Example

```bash
# 1. Get user profile
curl https://app-tiouegnz.fly.dev/api/v1/user/profile

# 2. Get user's projects
curl https://app-tiouegnz.fly.dev/api/v1/user/projects

# 3. Get inference project details
curl https://app-tiouegnz.fly.dev/api/v1/projects/proj-004

# 4. Get notebooks
curl https://app-tiouegnz.fly.dev/api/v1/projects/proj-004/notebooks

# 5. Run inference
curl -X POST https://app-tiouegnz.fly.dev/api/v1/notebooks/nb-006/run-inference

# 6. Get datasets
curl https://app-tiouegnz.fly.dev/api/v1/projects/proj-004/datasets

# 7. Get models
curl https://app-tiouegnz.fly.dev/api/v1/projects/proj-004/models

# 8. Request data export
curl -X POST https://app-tiouegnz.fly.dev/api/v1/exports/request \
  -H "Content-Type: application/json" \
  -d '{
    "projectId": "proj-004",
    "datasetName": "Real-Time ECG Stream",
    "rowCount": 1000,
    "justification": "Need data for model training"
  }'

# 9. Get export requests
curl https://app-tiouegnz.fly.dev/api/v1/exports/my-requests

# 10. Get H100 status
curl https://app-tiouegnz.fly.dev/api/v1/h100/status
```

---

## Postman Collection

Import this collection into Postman for easy testing:

```json
{
  "info": {
    "name": "AdventHealth Research Platform",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Get User Profile",
      "request": {
        "method": "GET",
        "url": "{{baseUrl}}/api/v1/user/profile"
      }
    },
    {
      "name": "Run Inference",
      "request": {
        "method": "POST",
        "url": "{{baseUrl}}/api/v1/notebooks/nb-006/run-inference"
      }
    }
  ],
  "variable": [
    {
      "key": "baseUrl",
      "value": "https://app-tiouegnz.fly.dev"
    }
  ]
}
```

---

## Next Steps

1. **Test all endpoints** using the cURL examples above
2. **Review DEMO_GUIDE.md** for complete workflow documentation
3. **See INTEGRATION_GUIDE.md** for connecting real Azure services
4. **Check SECURITY_CHECKLIST.md** before production deployment
