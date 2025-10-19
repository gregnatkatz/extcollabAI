# AdventHealth Research Platform - Secure Architecture Design

## Security Enclave Architecture

This document describes the **secure enclave architecture** required to ensure no data leaves AdventHealth.

## Network Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        INTERNET (Public)                            │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │         Azure Front Door + WAF (DDoS Protection)             │ │
│  │         - SSL/TLS Termination                                │ │
│  │         - Only allows HTTPS traffic                          │ │
│  │         - Rate limiting                                      │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                              ↓                                      │
└─────────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    ADVENTHEALTH AZURE TENANT                        │
│                    (Security Enclave Boundary)                      │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │              Azure Static Web Apps (Frontend)                │ │
│  │              VNet Integration: 10.100.5.0/24                 │ │
│  │              - React Portal (Dark Theme)                     │ │
│  │              - No data storage                               │ │
│  │              - API calls via Private Endpoint                │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                              ↓                                      │
│                    (Private Endpoint)                               │
│                              ↓                                      │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │         Azure VNet: 10.100.0.0/16 (NO INTERNET GATEWAY)     │ │
│  │                                                              │ │
│  │  ┌────────────────────────────────────────────────────────┐ │ │
│  │  │  Subnet: snet-api (10.100.3.0/24)                      │ │ │
│  │  │  ┌──────────────────────────────────────────────────┐  │ │ │
│  │  │  │  Azure App Service (Backend API)                 │  │ │ │
│  │  │  │  - FastAPI application                           │  │ │ │
│  │  │  │  - Entra ID authentication                       │  │ │ │
│  │  │  │  - RBAC enforcement                              │  │ │ │
│  │  │  │  - Audit logging                                 │  │ │ │
│  │  │  │  - NO outbound internet access                   │  │ │ │
│  │  │  └──────────────────────────────────────────────────┘  │ │ │
│  │  └────────────────────────────────────────────────────────┘ │ │
│  │                              ↓                                │ │
│  │                    (Private Endpoints)                        │ │
│  │                              ↓                                │ │
│  │  ┌────────────────────────────────────────────────────────┐ │ │
│  │  │  Subnet: snet-pe (10.100.4.0/24)                       │ │ │
│  │  │  ┌──────────────────────────────────────────────────┐  │ │ │
│  │  │  │  Private Endpoints:                              │  │ │ │
│  │  │  │  - Azure SQL Database                            │  │ │ │
│  │  │  │  - Azure Blob Storage                            │  │ │ │
│  │  │  │  - Microsoft Fabric OneLake                      │  │ │ │
│  │  │  │  - Azure ML Studio                               │  │ │ │
│  │  │  │  - Azure OpenAI (Foundry)                        │  │ │ │
│  │  │  └──────────────────────────────────────────────────┘  │ │ │
│  │  └────────────────────────────────────────────────────────┘ │ │
│  │                              ↓                                │ │
│  │  ┌────────────────────────────────────────────────────────┐ │ │
│  │  │  Subnet: snet-fabric (10.100.1.0/24)                   │ │ │
│  │  │  ┌──────────────────────────────────────────────────┐  │ │ │
│  │  │  │  Microsoft Fabric Workspace                      │  │ │ │
│  │  │  │  - Lakehouse (PHI Data)                          │  │ │ │
│  │  │  │  - Notebooks (Python/SQL)                        │  │ │ │
│  │  │  │  - Spark Compute                                 │  │ │ │
│  │  │  │  - NO internet access                            │  │ │ │
│  │  │  │  - NO data export enabled                        │  │ │ │
│  │  │  └──────────────────────────────────────────────────┘  │ │ │
│  │  └────────────────────────────────────────────────────────┘ │ │
│  │                              ↓                                │ │
│  │  ┌────────────────────────────────────────────────────────┐ │ │
│  │  │  Subnet: snet-ml (10.100.2.0/24)                       │ │ │
│  │  │  ┌──────────────────────────────────────────────────┐  │ │ │
│  │  │  │  Azure ML Studio Workspace                       │  │ │ │
│  │  │  │  - H100 GPU Cluster (8x H100)                    │  │ │ │
│  │  │  │  - Model Registry                                │  │ │ │
│  │  │  │  - Managed Endpoints                             │  │ │ │
│  │  │  │  - NO internet access                            │  │ │ │
│  │  │  │  - NO model download enabled                     │  │ │ │
│  │  │  └──────────────────────────────────────────────────┘  │ │ │
│  │  └────────────────────────────────────────────────────────┘ │ │
│  │                                                              │ │
│  │  ┌────────────────────────────────────────────────────────┐ │ │
│  │  │  Azure SQL Database (Metadata)                         │ │ │
│  │  │  - Projects, Users, Policies                           │ │ │
│  │  │  - Audit Logs (7-year retention)                       │ │ │
│  │  │  - Encryption at rest (AES-256)                        │ │ │
│  │  │  - Firewall: Allow Azure services only                │ │ │
│  │  └────────────────────────────────────────────────────────┘ │ │
│  │                                                              │ │
│  │  ┌────────────────────────────────────────────────────────┐ │ │
│  │  │  Azure Blob Storage (PHI Data)                         │ │ │
│  │  │  - Export staging area                                 │ │ │
│  │  │  - Encrypted ZIP files                                 │ │ │
│  │  │  - Time-limited SAS tokens (24h)                       │ │ │
│  │  │  - Auto-delete after expiry                            │ │ │
│  │  │  - Immutable storage for audit logs                    │ │ │
│  │  └────────────────────────────────────────────────────────┘ │ │
│  │                                                              │ │
│  │  ┌────────────────────────────────────────────────────────┐ │ │
│  │  │  Azure Key Vault                                       │ │ │
│  │  │  - Entra ID client secrets                             │ │ │
│  │  │  - Database connection strings                         │ │ │
│  │  │  - Storage account keys                                │ │ │
│  │  │  - Encryption keys                                     │ │ │
│  │  └────────────────────────────────────────────────────────┘ │ │
│  │                                                              │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │              Entra ID (Identity & Access)                    │ │
│  │              - B2B Guest Users                               │ │
│  │              - MFA Enforcement                               │ │
│  │              - Conditional Access Policies                   │ │
│  │              - Token Validation                              │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

                    ❌ NO INTERNET ACCESS ❌
                    ❌ NO DATA EXPORT ❌
                    ❌ NO VPN TUNNELS ❌
```

## Security Enclave Principles

### 1. Network Isolation
- **VNet with NO internet gateway** - No outbound internet access
- **Private Endpoints only** - All Azure services accessed via private IPs
- **NSG rules** - Deny all outbound traffic except Azure service tags
- **No VPN tunnels** - No external network connections

### 2. Data Residency
- **All data in AdventHealth tenant** - No third-party data processors
- **US East region only** - No cross-region replication
- **Encryption at rest** - AES-256 for all storage
- **Encryption in transit** - TLS 1.2+ for all connections

### 3. Access Control
- **Entra ID authentication** - All users authenticated via Entra ID
- **MFA enforced** - Multi-factor authentication required
- **RBAC** - Role-based access control (PI, Contributor, Viewer)
- **Time-limited access** - Guest users auto-expire after 6 months

### 4. Data Export Controls
- **PI approval required** - All exports require PI review
- **Time-limited SAS tokens** - 24-hour expiry
- **Encrypted exports** - ZIP files with password protection
- **Auto-deletion** - Export files deleted after 24 hours
- **Audit trail** - All exports logged with 7-year retention

### 5. Compute Isolation
- **Fabric notebooks** - Execute within VNet, no internet access
- **ML Studio training** - H100 GPUs within VNet, no model download
- **Foundry inference** - API-only access, no model export
- **No local compute** - All processing happens in Azure

## Data Flow

### 1. User Authentication
```
User → Azure Front Door → Static Web App → Entra ID
                                              ↓
                                         JWT Token
                                              ↓
                                    Backend API validates token
```

### 2. Notebook Execution
```
User clicks "Open Notebook" → Backend API → Fabric API (Private Endpoint)
                                              ↓
                                    Generate SSO URL
                                              ↓
                            User redirected to Fabric (within VNet)
                                              ↓
                            Notebook executes on Spark cluster (no internet)
                                              ↓
                            Results saved to Lakehouse (within VNet)
```

### 3. Model Training
```
User submits training job → Backend API → ML Studio API (Private Endpoint)
                                              ↓
                                    Job queued on H100 cluster
                                              ↓
                            Training data loaded from Lakehouse (Private Endpoint)
                                              ↓
                            Model trained on H100 GPUs (no internet)
                                              ↓
                            Model saved to Model Registry (within VNet)
```

### 4. Data Export (Controlled)
```
User requests export → Backend API → Create export request in database
                                              ↓
                                    Email notification to PI
                                              ↓
                            PI reviews and approves
                                              ↓
                            Backend API generates encrypted ZIP
                                              ↓
                            Upload to Blob Storage (Private Endpoint)
                                              ↓
                            Generate SAS token (24-hour expiry)
                                              ↓
                            Email download link to user
                                              ↓
                            User downloads via SAS URL
                                              ↓
                            File auto-deleted after 24 hours
```

## Network Security Groups (NSG) Rules

### snet-api (Backend API)
```
Inbound:
  - Allow HTTPS (443) from Azure Front Door
  - Allow HTTPS (443) from Static Web App
  - Deny all other inbound

Outbound:
  - Allow HTTPS (443) to Azure SQL Database (Private Endpoint)
  - Allow HTTPS (443) to Azure Blob Storage (Private Endpoint)
  - Allow HTTPS (443) to Microsoft Fabric (Private Endpoint)
  - Allow HTTPS (443) to Azure ML Studio (Private Endpoint)
  - Allow HTTPS (443) to Azure OpenAI (Private Endpoint)
  - Allow HTTPS (443) to Entra ID (Service Tag: AzureActiveDirectory)
  - Deny all other outbound (including internet)
```

### snet-fabric (Microsoft Fabric)
```
Inbound:
  - Allow HTTPS (443) from snet-api
  - Allow HTTPS (443) from snet-pe (Private Endpoints)
  - Deny all other inbound

Outbound:
  - Allow HTTPS (443) to Azure Blob Storage (Private Endpoint)
  - Allow HTTPS (443) to Azure SQL Database (Private Endpoint)
  - Deny all other outbound (including internet)
```

### snet-ml (Azure ML Studio)
```
Inbound:
  - Allow HTTPS (443) from snet-api
  - Allow HTTPS (443) from snet-pe (Private Endpoints)
  - Deny all other inbound

Outbound:
  - Allow HTTPS (443) to Azure Blob Storage (Private Endpoint)
  - Allow HTTPS (443) to Microsoft Fabric (Private Endpoint)
  - Deny all other outbound (including internet)
```

### snet-pe (Private Endpoints)
```
Inbound:
  - Allow HTTPS (443) from snet-api
  - Allow HTTPS (443) from snet-fabric
  - Allow HTTPS (443) from snet-ml
  - Deny all other inbound

Outbound:
  - Allow HTTPS (443) to Azure services (Service Tags)
  - Deny all other outbound (including internet)
```

## Compliance Controls

### HIPAA Compliance
1. **Encryption at rest** - AES-256 for all storage (SQL, Blob, Fabric)
2. **Encryption in transit** - TLS 1.2+ for all connections
3. **Access controls** - RBAC with MFA enforcement
4. **Audit logging** - 7-year retention with immutable storage
5. **Data breach notification** - Automated alerts for suspicious activity
6. **Business Associate Agreement** - Signed with Microsoft

### Data Sovereignty
1. **US East region only** - No cross-region replication
2. **AdventHealth tenant only** - No third-party processors
3. **No data export** - Controlled export workflow only
4. **Network isolation** - No internet access from VNet

## Monitoring & Alerting

### Azure Monitor Alerts
1. **Outbound internet attempt** - Alert if any resource tries to access internet
2. **Failed authentication** - Alert on 5+ failed login attempts
3. **Export request** - Alert PI when export is requested
4. **Access expiration** - Alert when guest user access expires in 30 days
5. **Suspicious activity** - Alert on unusual data access patterns

### Application Insights
1. **API performance** - Track response times and errors
2. **User activity** - Track notebook opens, model invocations, exports
3. **Dependency tracking** - Monitor calls to Fabric, ML Studio, Foundry
4. **Exception tracking** - Log all errors with stack traces

## Disaster Recovery

### Backup Strategy
1. **Azure SQL Database** - Automated backups with 35-day retention
2. **Azure Blob Storage** - Geo-redundant storage (GRS) within US
3. **Fabric Lakehouse** - OneLake automatic versioning
4. **ML Studio models** - Model Registry with versioning

### Recovery Procedures
1. **Database restore** - Point-in-time restore from automated backups
2. **Blob restore** - Restore from GRS replica
3. **Fabric restore** - Restore from OneLake version history
4. **Model restore** - Redeploy from Model Registry

## Cost Estimate (Monthly)

| Service | SKU | Cost |
|---------|-----|------|
| Microsoft Fabric | F64 Capacity | $5,000 |
| Azure ML Studio | Standard + H100 (8x NC96ads) | $15,000 |
| Azure SQL Database | S2 (50 DTU) | $150 |
| Azure Blob Storage | Standard LRS (5 TB) | $100 |
| Azure App Service | P1V3 | $100 |
| Azure Static Web Apps | Standard | $9 |
| Azure Front Door | Standard | $35 |
| Private Endpoints | 5 endpoints | $50 |
| Azure Key Vault | Standard | $5 |
| Application Insights | Pay-as-you-go | $50 |
| **Total** | | **$20,499/month** |

## Implementation Checklist

### Phase 1: Infrastructure (Week 1-2)
- [ ] Create Azure VNet (10.100.0.0/16)
- [ ] Create subnets (snet-api, snet-fabric, snet-ml, snet-pe)
- [ ] Configure NSG rules (deny all outbound internet)
- [ ] Deploy Azure SQL Database
- [ ] Deploy Azure Blob Storage
- [ ] Deploy Azure Key Vault
- [ ] Deploy Azure App Service (Backend)
- [ ] Deploy Azure Static Web Apps (Frontend)
- [ ] Deploy Azure Front Door with WAF

### Phase 2: Private Endpoints (Week 3)
- [ ] Create Private Endpoint for Azure SQL Database
- [ ] Create Private Endpoint for Azure Blob Storage
- [ ] Create Private Endpoint for Microsoft Fabric
- [ ] Create Private Endpoint for Azure ML Studio
- [ ] Create Private Endpoint for Azure OpenAI
- [ ] Configure DNS for Private Endpoints

### Phase 3: Authentication (Week 4)
- [ ] Configure Entra ID app registration
- [ ] Implement token validation middleware
- [ ] Configure MFA enforcement
- [ ] Configure Conditional Access policies
- [ ] Implement B2B guest user invitations

### Phase 4: Service Integration (Week 5-6)
- [ ] Integrate Fabric REST API
- [ ] Integrate Azure ML SDK
- [ ] Integrate Azure AI Projects SDK
- [ ] Provision H100 GPU cluster
- [ ] Deploy models to managed endpoints

### Phase 5: Security Testing (Week 7-8)
- [ ] Penetration testing
- [ ] Security audit
- [ ] HIPAA compliance review
- [ ] Sign BAA with Microsoft
- [ ] User acceptance testing

### Phase 6: Production Launch (Week 9)
- [ ] Migrate pilot users
- [ ] Monitor for 1 week
- [ ] Full production launch
- [ ] Training for researchers

## Conclusion

This secure architecture ensures **no data leaves AdventHealth** by:

1. **Network isolation** - VNet with no internet gateway
2. **Private Endpoints** - All Azure services accessed privately
3. **Controlled exports** - PI approval with time-limited SAS tokens
4. **Audit logging** - 7-year retention for compliance
5. **Encryption** - At rest and in transit

The current implementation (Fly.io + Devin Apps) is **NOT suitable for production** with real PHI data. It must be redeployed to Azure with the secure architecture described above.
