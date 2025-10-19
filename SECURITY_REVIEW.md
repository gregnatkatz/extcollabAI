# AdventHealth Research Platform - Security Review

## Executive Summary

This document reviews the current implementation against the security requirements from the specification, with special focus on the **security enclave aspect** and ensuring **no data leaves AdventHealth**.

## Critical Security Requirements from Specification

### 1. Network Isolation - **MISSING IN CURRENT IMPLEMENTATION**

**Specification Requirements (Page 1, Section 1.4):**
```
VNet Configuration:
  Address Space: 10.100.0.0/16
  
  Subnets:
    - snet-fabric: 10.100.1.0/24 (Microsoft Fabric)
    - snet-ml: 10.100.2.0/24 (Azure ML)
    - snet-api: 10.100.3.0/24 (Backend API)
    - snet-pe: 10.100.4.0/24 (Private Endpoints)

Network Security Groups:
  - NO outbound internet access
  - Allow Azure service tags only (Microsoft.Fabric, AzureMachineLearning)
  - Private endpoints for OneLake, ML Studio
```

**Current Status:** ❌ **NOT IMPLEMENTED**
- Backend is deployed to public Fly.io (https://app-tiouegnz.fly.dev)
- Frontend is deployed to public Devin Apps (https://research-portal-2fbfvjbt.devinapps.com)
- No VNet isolation
- No private endpoints
- Full internet access

**Required Changes:**
1. Deploy backend to Azure App Service within VNet
2. Configure NSGs to block all outbound internet traffic
3. Use Private Endpoints for Fabric and ML Studio
4. Deploy frontend to Azure Static Web Apps with VNet integration
5. Use Azure Front Door with WAF for external access only to portal UI

### 2. Data Residency - **CRITICAL ISSUE**

**Specification Requirements (Page 2, Section 2.1):**
- All data must remain within AdventHealth Azure tenant
- PHI data never leaves the secure enclave
- Export workflow requires PI approval with time-limited SAS URLs
- Audit logging for all data access (7-year retention)

**Current Status:** ⚠️ **PARTIALLY IMPLEMENTED**
- ✅ Export approval workflow exists
- ✅ Time-limited download URLs (24 hours)
- ✅ Audit logging structure in place
- ❌ Data is currently mock/in-memory (no real PHI protection)
- ❌ No actual Azure Blob Storage with SAS tokens
- ❌ No 7-year retention policy configured

**Required Changes:**
1. Store all data in Azure Storage within AdventHealth tenant
2. Implement real SAS token generation with 24-hour expiry
3. Configure Azure Blob Storage with immutable storage for audit logs (7-year retention)
4. Implement data classification tags (PHI, PII, Public)
5. Enable Azure Storage encryption at rest (AES-256)

### 3. Authentication & Authorization - **MISSING REAL IMPLEMENTATION**

**Specification Requirements (Page 3, Section 3.1):**
- Entra ID B2B authentication for all users
- MFA enforced for staff and guests
- Conditional Access policies
- Token validation on every API request
- Guest access with time-limited invitations

**Current Status:** ⚠️ **MOCK IMPLEMENTATION ONLY**
- ✅ API endpoints for Entra ID login exist
- ✅ B2B guest invitation endpoint exists
- ❌ No real Entra ID integration
- ❌ No token validation middleware
- ❌ No MFA enforcement
- ❌ No Conditional Access policies
- ❌ All API endpoints are currently public (no auth required)

**Required Changes:**
1. Integrate Microsoft.Identity.Web for token validation
2. Add authentication middleware to all API endpoints
3. Configure Entra ID Conditional Access policies
4. Enforce MFA for all users
5. Implement guest user lifecycle management (auto-expire after 6 months)

### 4. RBAC & Policies - **STRUCTURE EXISTS, NOT ENFORCED**

**Specification Requirements (Page 2, Section 2.1):**
```sql
CREATE TABLE ProjectMembers (
    Role NVARCHAR(50) CHECK (Role IN ('Contributor', 'Viewer')),
    CanExport BIT DEFAULT 0,
    AccessExpiresAt DATETIME2 NOT NULL
)
```

**Current Status:** ⚠️ **MOCK DATA ONLY**
- ✅ Policy endpoints exist (PHI Data Access, Export Approval, Model Deployment)
- ✅ Policy rules structure defined
- ❌ Policies are not enforced in code
- ❌ No database to store project members
- ❌ No role-based access control on API endpoints
- ❌ No access expiration checks

**Required Changes:**
1. Implement Azure SQL Database with ProjectMembers table
2. Add role-based authorization decorators to API endpoints
3. Check CanExport flag before allowing export requests
4. Implement access expiration checks (auto-revoke expired users)
5. Enforce PI-only approval for exports

### 5. Audit Logging - **STRUCTURE EXISTS, NOT PERSISTED**

**Specification Requirements (Page 2, Section 2.1):**
```sql
CREATE TABLE ActivityLog (
    ActivityType NVARCHAR(100) NOT NULL,
    IPAddress NVARCHAR(50),
    UserAgent NVARCHAR(500),
    CreatedAt DATETIME2 DEFAULT GETUTCDATE()
)
```

**Current Status:** ⚠️ **MOCK DATA ONLY**
- ✅ Activity log endpoint exists
- ✅ Audit log endpoint exists
- ❌ No real logging to database
- ❌ No IP address or user agent capture
- ❌ No 7-year retention policy
- ❌ No immutable storage for compliance

**Required Changes:**
1. Implement Azure SQL Database with ActivityLog table
2. Add middleware to capture IP address and user agent on every request
3. Log all data access, exports, model invocations
4. Configure 7-year retention policy
5. Use Azure Blob Storage with immutable storage for long-term audit logs

### 6. Data Export Controls - **WORKFLOW EXISTS, NOT SECURE**

**Specification Requirements (Page 3, Section 3.4):**
- PI approval required for all exports
- Time-limited SAS URLs (24 hours)
- Export data packaged as encrypted ZIP
- Email notifications to PI and requestor
- Audit trail of all export activities

**Current Status:** ⚠️ **PARTIALLY IMPLEMENTED**
- ✅ Export request workflow exists
- ✅ PI approval workflow exists
- ✅ 24-hour expiration concept exists
- ❌ No real Azure Blob Storage SAS URLs
- ❌ No encrypted ZIP packaging
- ❌ No email notifications
- ❌ Mock download URLs only

**Required Changes:**
1. Implement Azure Blob Storage for export staging
2. Generate real SAS tokens with 24-hour expiry
3. Package exports as encrypted ZIP files
4. Integrate SendGrid or Azure Communication Services for email
5. Delete export files after 24 hours (auto-cleanup)

### 7. Microsoft Fabric Integration - **MOCK ONLY**

**Specification Requirements (Page 3, Section 3.2):**
- Access Fabric workspaces via REST API
- Generate SSO URLs for notebook launch
- No data download to local machines
- All compute happens in Fabric (within VNet)

**Current Status:** ❌ **NOT IMPLEMENTED**
- ✅ API endpoints for Fabric workspaces exist
- ✅ Lakehouse endpoints exist
- ✅ Notebook execution endpoint exists
- ❌ No real Fabric API integration
- ❌ No SSO URL generation
- ❌ Mock URLs only

**Required Changes:**
1. Integrate Fabric REST API with DefaultAzureCredential
2. Generate real SSO URLs for notebook launch
3. Ensure Fabric workspace is in same VNet as backend
4. Configure Private Endpoints for OneLake access
5. Disable notebook export/download features

### 8. Azure ML Studio Integration - **MOCK ONLY**

**Specification Requirements (Page 3, Section 3.3):**
- H100 GPU cluster for model training
- Model deployment with managed endpoints
- No model download (inference only via API)
- All compute within VNet

**Current Status:** ❌ **NOT IMPLEMENTED**
- ✅ API endpoints for ML Studio exist
- ✅ H100 compute status endpoint exists
- ✅ Model endpoint invocation exists
- ❌ No real Azure ML integration
- ❌ No H100 cluster provisioned
- ❌ Mock inference results only

**Required Changes:**
1. Integrate Azure ML SDK (azure-ai-ml)
2. Provision H100 GPU cluster (Standard_NC96ads_A100_v4)
3. Deploy models to managed endpoints
4. Configure Private Endpoints for ML Studio
5. Disable model download (inference only)

### 9. Azure AI Foundry Integration - **MOCK ONLY**

**Specification Requirements (Page 3, Section 3.3):**
- Fine-tuned GPT-4o and Phi-3 models
- Model deployment to Azure OpenAI endpoints
- Model evaluation metrics
- No model export

**Current Status:** ❌ **NOT IMPLEMENTED**
- ✅ API endpoints for Foundry exist
- ✅ Model deployment endpoint exists
- ✅ Evaluation endpoint exists
- ❌ No real Foundry integration
- ❌ Mock models only

**Required Changes:**
1. Integrate Azure AI Projects SDK
2. Deploy real GPT-4o and Phi-3 models
3. Configure Azure OpenAI endpoints within VNet
4. Implement model evaluation pipeline
5. Disable model export features

### 10. Security Checklist from Specification (Page 4, Section 4.5)

**Pre-Launch Security Review:**

- [ ] ❌ Entra ID Conditional Access policies configured
- [ ] ❌ MFA enforced for all users (staff + guests)
- [ ] ❌ VNet with no internet gateway deployed
- [ ] ❌ NSGs deny all outbound internet traffic
- [ ] ❌ Private endpoints for Fabric and ML Studio
- [ ] ❌ Azure SQL firewall rules (allow Azure services only)
- [ ] ⚠️ API authentication validated (bearer token required) - **MOCK ONLY**
- [ ] ❌ CORS configured (only research.adventhealth.com) - **Currently allows all origins**
- [ ] ✅ Export approval workflow tested
- [ ] ⚠️ Audit logging enabled (7-year retention) - **STRUCTURE ONLY**
- [ ] ❌ Data encryption at rest verified (AES-256)
- [ ] ❌ SSL/TLS enforced (minimum TLS 1.2)
- [ ] ❌ DDoS protection enabled on Front Door
- [ ] ❌ Penetration testing completed
- [ ] ❌ HIPAA compliance attestation signed

**Score: 1/15 Complete, 2/15 Partial, 12/15 Missing**

## Critical Security Gaps

### 1. **NO NETWORK ISOLATION** (Highest Priority)
The entire application is deployed to public cloud services (Fly.io, Devin Apps) with full internet access. This violates the core security enclave requirement.

**Impact:** PHI data could potentially be exfiltrated via internet connections.

**Remediation:**
1. Redeploy to Azure App Service within VNet
2. Configure NSGs to block all outbound internet
3. Use Private Endpoints for all Azure services
4. Deploy Azure Front Door with WAF for controlled external access

### 2. **NO AUTHENTICATION ENFORCEMENT** (Highest Priority)
All API endpoints are currently public with no token validation.

**Impact:** Anyone with the API URL can access all data and functionality.

**Remediation:**
1. Add authentication middleware to validate Entra ID tokens
2. Implement role-based authorization on all endpoints
3. Enforce MFA for all users

### 3. **NO DATA PERSISTENCE** (High Priority)
All data is in-memory and will be lost on restart. No real PHI protection.

**Impact:** Cannot enforce data residency, audit logging, or compliance requirements.

**Remediation:**
1. Deploy Azure SQL Database for metadata
2. Deploy Azure Blob Storage for PHI data
3. Configure encryption at rest and in transit
4. Implement 7-year audit log retention

### 4. **CORS ALLOWS ALL ORIGINS** (High Priority)
Current CORS configuration allows any website to call the API.

**Impact:** Cross-site request forgery (CSRF) attacks possible.

**Remediation:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://research.adventhealth.com"],  # Only AdventHealth domain
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
)
```

### 5. **NO REAL SERVICE INTEGRATION** (Medium Priority)
All Fabric, ML Studio, and Foundry integrations are mock data only.

**Impact:** Cannot actually use the platform for research.

**Remediation:**
1. Follow INTEGRATION_GUIDE.md to connect real services
2. Ensure all services are within VNet
3. Use Private Endpoints for all connections

## Compliance Requirements

### HIPAA Compliance
- [ ] ❌ Business Associate Agreement (BAA) with Microsoft
- [ ] ❌ Encryption at rest (AES-256)
- [ ] ❌ Encryption in transit (TLS 1.2+)
- [ ] ❌ Access controls (RBAC)
- [ ] ❌ Audit logging (7-year retention)
- [ ] ❌ Data breach notification procedures
- [ ] ❌ Risk assessment completed

### Data Residency
- [ ] ❌ All data stored in AdventHealth Azure tenant
- [ ] ❌ No data replication outside US East region
- [ ] ❌ No third-party data processors
- [ ] ❌ Data sovereignty verified

## Recommended Implementation Priority

### Phase 1: Critical Security (Week 1-2)
1. Deploy to Azure App Service with VNet
2. Implement Entra ID authentication with token validation
3. Configure CORS to allow only AdventHealth domain
4. Deploy Azure SQL Database for metadata
5. Add authentication middleware to all endpoints

### Phase 2: Network Isolation (Week 3-4)
1. Configure NSGs to block outbound internet
2. Deploy Private Endpoints for Fabric and ML Studio
3. Configure Azure Front Door with WAF
4. Implement DDoS protection

### Phase 3: Data Protection (Week 5-6)
1. Deploy Azure Blob Storage for PHI data
2. Implement encryption at rest and in transit
3. Configure 7-year audit log retention
4. Implement real export workflow with SAS tokens

### Phase 4: Service Integration (Week 7-8)
1. Integrate real Fabric API
2. Integrate real Azure ML Studio
3. Integrate real Azure AI Foundry
4. Provision H100 GPU cluster

### Phase 5: Compliance & Testing (Week 9)
1. Complete HIPAA compliance checklist
2. Penetration testing
3. Security audit
4. Sign BAA with Microsoft

## Conclusion

The current implementation provides a **functional UI and API structure** but **does not meet the security enclave requirements**. The most critical gaps are:

1. **No network isolation** - Application is on public internet
2. **No authentication enforcement** - All endpoints are public
3. **No data persistence** - Cannot enforce compliance requirements
4. **CORS allows all origins** - CSRF vulnerability

**Recommendation:** Do not deploy this to production with real PHI data until Phase 1-3 security controls are implemented. The current deployment is suitable for **demo/prototype purposes only** with mock data.

## Next Steps

1. Review this security assessment with AdventHealth security team
2. Obtain approval for Azure infrastructure deployment
3. Provision Azure resources (VNet, App Service, SQL Database, Storage)
4. Implement Phase 1 critical security controls
5. Conduct security testing before handling real PHI data
