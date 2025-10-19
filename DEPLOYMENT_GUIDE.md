## AdventHealth Research Platform - Production Deployment Guide

This guide provides step-by-step instructions for deploying the secure research platform to Azure with full network isolation and compliance controls.

## Prerequisites

1. **Azure Subscription** with Owner or Contributor access
2. **Azure CLI** installed and authenticated
3. **Entra ID** tenant with admin access
4. **GitHub repository** for CI/CD (optional)
5. **Domain name** (research.adventhealth.com) configured in Azure DNS

## Phase 1: Azure Infrastructure Deployment (Week 1-2)

### Step 1: Prepare Environment Variables

Create a `parameters.json` file:

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "environment": {
      "value": "prod"
    },
    "location": {
      "value": "eastus"
    },
    "entraIdTenantId": {
      "value": "YOUR_TENANT_ID"
    },
    "entraIdClientId": {
      "value": "YOUR_CLIENT_ID"
    },
    "adminEmail": {
      "value": "admin@adventhealth.com"
    }
  }
}
```

### Step 2: Deploy Azure Infrastructure

```bash
# Login to Azure
az login --tenant YOUR_TENANT_ID

# Set subscription
az account set --subscription YOUR_SUBSCRIPTION_ID

# Create resource group
az group create \
  --name rg-research-prod \
  --location eastus

# Deploy Bicep template
az deployment group create \
  --resource-group rg-research-prod \
  --template-file infrastructure/main.bicep \
  --parameters @parameters.json \
  --mode Incremental

# Get deployment outputs
az deployment group show \
  --resource-group rg-research-prod \
  --name main \
  --query properties.outputs
```

### Step 3: Configure Secrets in Azure Key Vault

```bash
# Get Key Vault name from deployment outputs
KEY_VAULT_NAME=$(az deployment group show \
  --resource-group rg-research-prod \
  --name main \
  --query properties.outputs.keyVaultName.value \
  --output tsv)

# Set SQL admin password
az keyvault secret set \
  --vault-name $KEY_VAULT_NAME \
  --name sql-admin-password \
  --value "YOUR_STRONG_PASSWORD"

# Set Entra ID client secret
az keyvault secret set \
  --vault-name $KEY_VAULT_NAME \
  --name entra-client-secret \
  --value "YOUR_ENTRA_CLIENT_SECRET"

# Set storage connection string
STORAGE_ACCOUNT_NAME=$(az deployment group show \
  --resource-group rg-research-prod \
  --name main \
  --query properties.outputs.storageAccountName.value \
  --output tsv)

STORAGE_CONNECTION_STRING=$(az storage account show-connection-string \
  --name $STORAGE_ACCOUNT_NAME \
  --resource-group rg-research-prod \
  --query connectionString \
  --output tsv)

az keyvault secret set \
  --vault-name $KEY_VAULT_NAME \
  --name storage-connection-string \
  --value "$STORAGE_CONNECTION_STRING"
```

### Step 4: Grant App Service Access to Key Vault

```bash
# Get App Service principal ID
APP_SERVICE_PRINCIPAL_ID=$(az webapp identity show \
  --name ah-research-prod-api \
  --resource-group rg-research-prod \
  --query principalId \
  --output tsv)

# Grant Key Vault Secrets User role
az role assignment create \
  --role "Key Vault Secrets User" \
  --assignee $APP_SERVICE_PRINCIPAL_ID \
  --scope "/subscriptions/YOUR_SUBSCRIPTION_ID/resourceGroups/rg-research-prod/providers/Microsoft.KeyVault/vaults/$KEY_VAULT_NAME"
```

## Phase 2: Entra ID Configuration (Week 2)

### Step 1: Register Backend API Application

```bash
# Create app registration
az ad app create \
  --display-name "AdventHealth Research Platform API" \
  --sign-in-audience AzureADMyOrg \
  --web-redirect-uris "https://ah-research-prod-api.azurewebsites.net/.auth/login/aad/callback" \
  --enable-id-token-issuance true \
  --enable-access-token-issuance true

# Get application ID
API_APP_ID=$(az ad app list \
  --display-name "AdventHealth Research Platform API" \
  --query [0].appId \
  --output tsv)

# Create service principal
az ad sp create --id $API_APP_ID

# Create client secret
az ad app credential reset \
  --id $API_APP_ID \
  --append \
  --display-name "Production Secret"
```

### Step 2: Configure API Permissions

```bash
# Add Microsoft Graph permissions
az ad app permission add \
  --id $API_APP_ID \
  --api 00000003-0000-0000-c000-000000000000 \
  --api-permissions e1fe6dd8-ba31-4d61-89e7-88639da4683d=Scope # User.Read

# Grant admin consent
az ad app permission admin-consent --id $API_APP_ID
```

### Step 3: Configure Conditional Access Policies

1. Go to Azure Portal → Entra ID → Security → Conditional Access
2. Create new policy: "Research Platform - Require MFA"
   - Users: All users accessing Research Platform
   - Cloud apps: AdventHealth Research Platform API
   - Grant: Require multi-factor authentication
   - Session: Sign-in frequency = 8 hours
3. Enable policy

### Step 4: Configure B2B Guest Settings

1. Go to Azure Portal → Entra ID → External Identities → External collaboration settings
2. Configure:
   - Guest user access: Limited access
   - Guest invite settings: Only admins and users in the guest inviter role can invite
   - Collaboration restrictions: Allow invitations only to specified domains (add partner institutions)
   - Guest user lifecycle: Enable automatic guest user expiration (180 days)

## Phase 3: Database Setup (Week 3)

### Step 1: Connect to Azure SQL Database

```bash
# Get SQL Server FQDN
SQL_SERVER_FQDN=$(az deployment group show \
  --resource-group rg-research-prod \
  --name main \
  --query properties.outputs.sqlServerFqdn.value \
  --output tsv)

# Connect via Azure Cloud Shell (has access to VNet)
sqlcmd -S $SQL_SERVER_FQDN -d research-db -U sqladmin -P "YOUR_PASSWORD"
```

### Step 2: Create Database Schema

Run the SQL script from the specification (Page 2, Section 2.1):

```sql
-- Projects Table
CREATE TABLE Projects (
    ProjectId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    Name NVARCHAR(255) NOT NULL,
    PIUserId NVARCHAR(255) NOT NULL,
    PIName NVARCHAR(255) NOT NULL,
    PIEmail NVARCHAR(255) NOT NULL,
    FabricWorkspaceId NVARCHAR(255) NOT NULL,
    FabricWorkspaceUrl NVARCHAR(500),
    MLWorkspaceId NVARCHAR(255),
    MLWorkspaceUrl NVARCHAR(500),
    Status NVARCHAR(50) DEFAULT 'Active',
    CreatedAt DATETIME2 DEFAULT GETUTCDATE(),
    UpdatedAt DATETIME2 DEFAULT GETUTCDATE()
);

-- Project Members (B2B Access Control)
CREATE TABLE ProjectMembers (
    MemberId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    ProjectId UNIQUEIDENTIFIER FOREIGN KEY REFERENCES Projects(ProjectId),
    UserId NVARCHAR(255) NOT NULL,
    UserEmail NVARCHAR(255) NOT NULL,
    UserName NVARCHAR(255),
    Institution NVARCHAR(255),
    Role NVARCHAR(50) CHECK (Role IN ('Contributor', 'Viewer')),
    AccessGrantedAt DATETIME2 DEFAULT GETUTCDATE(),
    AccessExpiresAt DATETIME2 NOT NULL,
    CanExport BIT DEFAULT 0,
    IsActive BIT DEFAULT 1,
    CreatedBy NVARCHAR(255) NOT NULL,
    INDEX IX_UserId (UserId),
    INDEX IX_ProjectId (ProjectId)
);

-- Export Requests
CREATE TABLE ExportRequests (
    RequestId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    RequestNumber NVARCHAR(50) UNIQUE NOT NULL,
    ProjectId UNIQUEIDENTIFIER FOREIGN KEY REFERENCES Projects(ProjectId),
    RequestorUserId NVARCHAR(255) NOT NULL,
    RequestorEmail NVARCHAR(255) NOT NULL,
    DatasetName NVARCHAR(255) NOT NULL,
    RowCount INT,
    Justification NVARCHAR(MAX) NOT NULL,
    Status NVARCHAR(50) DEFAULT 'Pending' CHECK (Status IN ('Pending', 'Approved', 'Rejected', 'Completed', 'Expired')),
    PIReviewerId NVARCHAR(255),
    PIReviewerEmail NVARCHAR(255),
    ReviewedAt DATETIME2,
    ReviewNotes NVARCHAR(MAX),
    DownloadUrl NVARCHAR(500),
    DownloadExpiresAt DATETIME2,
    RequestedAt DATETIME2 DEFAULT GETUTCDATE(),
    CompletedAt DATETIME2,
    INDEX IX_RequestorUserId (RequestorUserId),
    INDEX IX_Status (Status)
);

-- Activity Log (Audit Trail)
CREATE TABLE ActivityLog (
    ActivityId BIGINT PRIMARY KEY IDENTITY(1,1),
    UserId NVARCHAR(255) NOT NULL,
    UserEmail NVARCHAR(255),
    ProjectId UNIQUEIDENTIFIER,
    ActivityType NVARCHAR(100) NOT NULL,
    ActivityDetails NVARCHAR(MAX),
    ResourceId NVARCHAR(255),
    IPAddress NVARCHAR(50),
    UserAgent NVARCHAR(500),
    CreatedAt DATETIME2 DEFAULT GETUTCDATE(),
    INDEX IX_UserId_CreatedAt (UserId, CreatedAt DESC),
    INDEX IX_ActivityType (ActivityType)
);

-- Notifications
CREATE TABLE Notifications (
    NotificationId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    UserId NVARCHAR(255) NOT NULL,
    Type NVARCHAR(50) CHECK (Type IN ('Info', 'Success', 'Warning', 'Error')),
    Message NVARCHAR(MAX) NOT NULL,
    IsRead BIT DEFAULT 0,
    RelatedEntityType NVARCHAR(50),
    RelatedEntityId NVARCHAR(255),
    CreatedAt DATETIME2 DEFAULT GETUTCDATE(),
    INDEX IX_UserId_IsRead (UserId, IsRead)
);
```

## Phase 4: Backend Deployment (Week 4)

### Step 1: Prepare Backend Code

```bash
cd backend

# Update pyproject.toml with all dependencies
poetry install

# Run tests
poetry run pytest

# Build deployment package
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

### Step 2: Deploy to App Service

```bash
# Deploy via Azure CLI
az webapp up \
  --name ah-research-prod-api \
  --resource-group rg-research-prod \
  --runtime "PYTHON:3.11" \
  --sku P1V3

# Or deploy via GitHub Actions (recommended)
# See .github/workflows/deploy-backend.yml
```

### Step 3: Configure App Service Settings

```bash
# Enable VNet integration
az webapp vnet-integration add \
  --name ah-research-prod-api \
  --resource-group rg-research-prod \
  --vnet ah-research-prod-vnet \
  --subnet snet-api

# Enable managed identity
az webapp identity assign \
  --name ah-research-prod-api \
  --resource-group rg-research-prod

# Configure startup command
az webapp config set \
  --name ah-research-prod-api \
  --resource-group rg-research-prod \
  --startup-file "gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app"
```

## Phase 5: Frontend Deployment (Week 4)

### Step 1: Build Frontend

```bash
cd frontend

# Update .env.production
cat > .env.production << EOF
VITE_API_URL=https://ah-research-prod-api.azurewebsites.net
VITE_ENTRA_CLIENT_ID=$API_APP_ID
VITE_ENTRA_TENANT_ID=YOUR_TENANT_ID
VITE_ENVIRONMENT=production
EOF

# Install dependencies
npm install

# Build
npm run build
```

### Step 2: Deploy to Static Web Apps

```bash
# Deploy via Azure CLI
az staticwebapp create \
  --name ah-research-prod-portal \
  --resource-group rg-research-prod \
  --source frontend \
  --location eastus \
  --branch main \
  --app-location "/" \
  --output-location "dist"

# Or deploy manually
az staticwebapp deploy \
  --name ah-research-prod-portal \
  --resource-group rg-research-prod \
  --app-location frontend/dist
```

## Phase 6: Microsoft Fabric Integration (Week 5)

### Step 1: Provision Fabric Capacity

```bash
# Create Fabric capacity (F64)
az fabric capacity create \
  --name ah-research-fabric \
  --resource-group rg-research-prod \
  --location eastus \
  --sku F64 \
  --admin-members "admin@adventhealth.com"
```

### Step 2: Create Fabric Workspaces

1. Go to https://fabric.microsoft.com
2. Create workspace: "Cardiac Research Workspace"
3. Settings → Network security:
   - Enable VNet integration
   - Select VNet: ah-research-prod-vnet
   - Subnet: snet-fabric
4. Settings → Security:
   - Disable "Allow public internet access"
   - Enable "Require Private Endpoint"

### Step 3: Configure Private Endpoint for Fabric

```bash
# Create private endpoint for OneLake
az network private-endpoint create \
  --name ah-research-prod-pe-fabric \
  --resource-group rg-research-prod \
  --vnet-name ah-research-prod-vnet \
  --subnet snet-pe \
  --private-connection-resource-id "/subscriptions/YOUR_SUBSCRIPTION_ID/resourceGroups/rg-research-prod/providers/Microsoft.Fabric/capacities/ah-research-fabric" \
  --group-id "fabric" \
  --connection-name "fabric-connection"
```

## Phase 7: Azure ML Studio Integration (Week 6)

### Step 1: Create ML Workspace

```bash
# Create ML workspace
az ml workspace create \
  --name ah-research-ml \
  --resource-group rg-research-prod \
  --location eastus \
  --public-network-access Disabled

# Configure VNet integration
az ml workspace update \
  --name ah-research-ml \
  --resource-group rg-research-prod \
  --image-build-compute "cpu-cluster"
```

### Step 2: Provision H100 GPU Cluster

```bash
# Create H100 compute cluster
az ml compute create \
  --name h100-cluster \
  --resource-group rg-research-prod \
  --workspace-name ah-research-ml \
  --type amlcompute \
  --vm-size Standard_NC96ads_A100_v4 \
  --min-instances 0 \
  --max-instances 8 \
  --idle-time-before-scale-down 1800 \
  --vnet-name ah-research-prod-vnet \
  --subnet snet-ml
```

### Step 3: Configure Private Endpoint for ML Studio

```bash
# Create private endpoint
az network private-endpoint create \
  --name ah-research-prod-pe-ml \
  --resource-group rg-research-prod \
  --vnet-name ah-research-prod-vnet \
  --subnet snet-pe \
  --private-connection-resource-id "/subscriptions/YOUR_SUBSCRIPTION_ID/resourceGroups/rg-research-prod/providers/Microsoft.MachineLearningServices/workspaces/ah-research-ml" \
  --group-id "amlworkspace" \
  --connection-name "ml-connection"
```

## Phase 8: Security Testing (Week 7-8)

### Step 1: Verify Network Isolation

```bash
# Test that backend cannot access internet
az webapp ssh --name ah-research-prod-api --resource-group rg-research-prod
# Inside SSH session:
curl https://www.google.com  # Should fail

# Test that Fabric cannot access internet
# Connect to Fabric notebook and run:
import requests
requests.get("https://www.google.com")  # Should fail
```

### Step 2: Verify Authentication

```bash
# Test unauthenticated request (should fail)
curl https://ah-research-prod-api.azurewebsites.net/api/v1/user/profile
# Expected: 401 Unauthorized

# Test with invalid token (should fail)
curl -H "Authorization: Bearer invalid_token" \
  https://ah-research-prod-api.azurewebsites.net/api/v1/user/profile
# Expected: 401 Unauthorized

# Test with valid token (should succeed)
# Get token from Entra ID first, then:
curl -H "Authorization: Bearer $VALID_TOKEN" \
  https://ah-research-prod-api.azurewebsites.net/api/v1/user/profile
# Expected: 200 OK with user profile
```

### Step 3: Verify RBAC

```bash
# Test PI-only endpoint as non-PI user (should fail)
curl -H "Authorization: Bearer $NON_PI_TOKEN" \
  -X POST https://ah-research-prod-api.azurewebsites.net/api/v1/exports/exp-001/review \
  -d '{"decision": "Approved", "notes": "Test"}'
# Expected: 403 Forbidden

# Test PI-only endpoint as PI user (should succeed)
curl -H "Authorization: Bearer $PI_TOKEN" \
  -X POST https://ah-research-prod-api.azurewebsites.net/api/v1/exports/exp-001/review \
  -d '{"decision": "Approved", "notes": "Test"}'
# Expected: 200 OK
```

### Step 4: Verify Audit Logging

```bash
# Check audit logs in database
sqlcmd -S $SQL_SERVER_FQDN -d research-db -U sqladmin -P "YOUR_PASSWORD"
SELECT TOP 10 * FROM ActivityLog ORDER BY CreatedAt DESC;

# Check audit logs in Blob Storage
az storage blob list \
  --account-name $STORAGE_ACCOUNT_NAME \
  --container-name audit-logs \
  --prefix "$(date +%Y/%m/%d)/"
```

### Step 5: Penetration Testing

Engage a third-party security firm to conduct:
1. Network penetration testing
2. Application security testing
3. Social engineering testing
4. Physical security assessment

## Phase 9: Compliance & Documentation (Week 9)

### Step 1: HIPAA Compliance Checklist

- [ ] Business Associate Agreement signed with Microsoft
- [ ] Encryption at rest enabled (AES-256)
- [ ] Encryption in transit enabled (TLS 1.2+)
- [ ] Access controls implemented (RBAC)
- [ ] Audit logging enabled (7-year retention)
- [ ] Data breach notification procedures documented
- [ ] Risk assessment completed
- [ ] Security incident response plan documented
- [ ] Employee training completed

### Step 2: Sign Business Associate Agreement

1. Contact Microsoft Azure support
2. Request HIPAA BAA for subscription
3. Sign and return BAA
4. Store signed copy in secure location

### Step 3: Document Security Controls

Create documentation for:
1. Network architecture diagram
2. Data flow diagrams
3. Access control matrix
4. Incident response procedures
5. Disaster recovery plan
6. User training materials

## Phase 10: Production Launch (Week 9)

### Step 1: Pilot Launch

1. Select 5 pilot users (2 PIs, 3 researchers)
2. Provide training on platform usage
3. Monitor for 1 week
4. Collect feedback
5. Address any issues

### Step 2: Full Production Launch

1. Announce launch to all researchers
2. Provide training sessions
3. Distribute user guides
4. Set up support channels (email, Slack)
5. Monitor system performance

### Step 3: Ongoing Monitoring

```bash
# Set up Azure Monitor alerts
az monitor metrics alert create \
  --name "High CPU Usage" \
  --resource-group rg-research-prod \
  --scopes "/subscriptions/YOUR_SUBSCRIPTION_ID/resourceGroups/rg-research-prod/providers/Microsoft.Web/sites/ah-research-prod-api" \
  --condition "avg Percentage CPU > 80" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --action-group "admin-alerts"

# Set up log analytics
az monitor log-analytics workspace create \
  --resource-group rg-research-prod \
  --workspace-name ah-research-logs \
  --location eastus
```

## Troubleshooting

### Issue: Backend cannot connect to SQL Database

**Solution**: Verify Private Endpoint DNS resolution

```bash
# Check DNS resolution
nslookup $SQL_SERVER_FQDN

# Should resolve to private IP (10.100.4.x)
# If resolves to public IP, check Private DNS Zone configuration
```

### Issue: Frontend cannot call backend API

**Solution**: Verify CORS configuration

```bash
# Check CORS headers
curl -H "Origin: https://research.adventhealth.com" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: Authorization" \
  -X OPTIONS \
  https://ah-research-prod-api.azurewebsites.net/api/v1/user/profile

# Should return:
# Access-Control-Allow-Origin: https://research.adventhealth.com
# Access-Control-Allow-Methods: GET, POST, PATCH, DELETE
# Access-Control-Allow-Headers: Authorization, Content-Type
```

### Issue: Entra ID authentication fails

**Solution**: Verify app registration configuration

```bash
# Check redirect URIs
az ad app show --id $API_APP_ID --query web.redirectUris

# Check token configuration
az ad app show --id $API_APP_ID --query "oauth2AllowIdTokenImplicitFlow,oauth2AllowImplicitFlow"
```

## Support

For deployment issues, contact:
- **Azure Support**: https://portal.azure.com/#blade/Microsoft_Azure_Support/HelpAndSupportBlade
- **AdventHealth IT**: it-support@adventhealth.com
- **Platform Team**: research-platform@adventhealth.com

## Cost Monitoring

```bash
# View current month costs
az consumption usage list \
  --start-date $(date -d "$(date +%Y-%m-01)" +%Y-%m-%d) \
  --end-date $(date +%Y-%m-%d) \
  --query "[?contains(instanceName, 'ah-research')].{Name:instanceName, Cost:pretaxCost}" \
  --output table

# Set up budget alert
az consumption budget create \
  --budget-name research-platform-budget \
  --amount 25000 \
  --time-grain Monthly \
  --start-date $(date +%Y-%m-01) \
  --end-date $(date -d "+1 year" +%Y-%m-01) \
  --resource-group rg-research-prod
```

## Estimated Monthly Cost

| Service | SKU | Monthly Cost |
|---------|-----|--------------|
| Microsoft Fabric | F64 | $5,000 |
| Azure ML H100 Cluster | 8x NC96ads | $15,000 |
| Azure SQL Database | S2 | $150 |
| Azure Blob Storage | 5 TB | $100 |
| Azure App Service | P1V3 | $100 |
| Azure Static Web Apps | Standard | $9 |
| Azure Front Door | Standard | $35 |
| Private Endpoints | 5 endpoints | $50 |
| Azure Key Vault | Standard | $5 |
| Application Insights | Pay-as-you-go | $50 |
| **Total** | | **$20,499/month** |

## Next Steps

After successful deployment:
1. Schedule quarterly security audits
2. Review and update access controls monthly
3. Monitor costs and optimize resources
4. Collect user feedback and iterate
5. Plan for additional features (Phase 2)
