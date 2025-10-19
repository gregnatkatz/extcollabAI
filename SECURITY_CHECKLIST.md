# AdventHealth Research Platform - Security Compliance Checklist

## Pre-Production Security Verification

This checklist must be completed and verified before deploying to production with real PHI data.

## 1. Network Security ✓

### VNet Isolation
- [ ] VNet created with address space 10.100.0.0/16
- [ ] Four subnets created (snet-fabric, snet-ml, snet-api, snet-pe)
- [ ] No internet gateway attached to VNet
- [ ] All resources deployed within VNet

### Network Security Groups (NSGs)
- [ ] NSG rules deny all outbound internet traffic
- [ ] NSG rules allow only Azure service tags (Microsoft.Fabric, AzureMachineLearning, Microsoft.Sql, Microsoft.Storage)
- [ ] NSG rules allow HTTPS inbound only from Azure Front Door
- [ ] NSG rules tested and verified

### Private Endpoints
- [ ] Private endpoint created for Azure SQL Database
- [ ] Private endpoint created for Azure Blob Storage
- [ ] Private endpoint created for Microsoft Fabric (OneLake)
- [ ] Private endpoint created for Azure ML Studio
- [ ] Private endpoint created for Azure OpenAI (Foundry)
- [ ] Private DNS zones configured for all private endpoints
- [ ] DNS resolution tested from within VNet

### Verification Tests
```bash
# Test 1: Backend cannot access internet
az webapp ssh --name ah-research-prod-api --resource-group rg-research-prod
curl https://www.google.com  # Should timeout/fail

# Test 2: SQL Database not accessible from internet
nslookup ah-research-prod-sql.database.windows.net
# Should resolve to private IP (10.100.4.x)

# Test 3: Storage account not accessible from internet
curl https://ahresearchprodstorage.blob.core.windows.net/exports/
# Should return 403 Forbidden or connection timeout
```

## 2. Authentication & Authorization ✓

### Entra ID Configuration
- [ ] App registration created for backend API
- [ ] Client secret generated and stored in Key Vault
- [ ] Redirect URIs configured correctly
- [ ] API permissions configured (User.Read, offline_access)
- [ ] Admin consent granted for API permissions
- [ ] Token configuration enabled (ID tokens, access tokens)

### Conditional Access Policies
- [ ] Policy created: "Research Platform - Require MFA"
- [ ] MFA enforced for all users (staff and guests)
- [ ] Session timeout set to 8 hours
- [ ] Sign-in frequency configured
- [ ] Device compliance required (optional)
- [ ] Trusted locations configured (optional)

### B2B Guest User Management
- [ ] Guest user access set to "Limited access"
- [ ] Guest invite settings restricted to admins only
- [ ] Collaboration restrictions configured (allowed domains)
- [ ] Guest user lifecycle management enabled (180-day expiration)
- [ ] Guest user review process documented

### RBAC Implementation
- [ ] Role definitions created (PI, Contributor, Viewer, Admin)
- [ ] Role assignments tested for each role
- [ ] PI-only endpoints protected (export approval)
- [ ] Admin-only endpoints protected (user management, audit logs)
- [ ] Project-level access control implemented

### Verification Tests
```bash
# Test 1: Unauthenticated request fails
curl https://ah-research-prod-api.azurewebsites.net/api/v1/user/profile
# Expected: 401 Unauthorized

# Test 2: Invalid token fails
curl -H "Authorization: Bearer invalid_token" \
  https://ah-research-prod-api.azurewebsites.net/api/v1/user/profile
# Expected: 401 Unauthorized

# Test 3: Valid token succeeds
curl -H "Authorization: Bearer $VALID_TOKEN" \
  https://ah-research-prod-api.azurewebsites.net/api/v1/user/profile
# Expected: 200 OK

# Test 4: Non-PI cannot approve exports
curl -H "Authorization: Bearer $NON_PI_TOKEN" \
  -X POST https://ah-research-prod-api.azurewebsites.net/api/v1/exports/exp-001/review
# Expected: 403 Forbidden

# Test 5: PI can approve exports
curl -H "Authorization: Bearer $PI_TOKEN" \
  -X POST https://ah-research-prod-api.azurewebsites.net/api/v1/exports/exp-001/review
# Expected: 200 OK
```

## 3. Data Encryption ✓

### Encryption at Rest
- [ ] Azure SQL Database encryption enabled (TDE)
- [ ] Azure Blob Storage encryption enabled (AES-256)
- [ ] Azure Key Vault encryption enabled
- [ ] Fabric workspace encryption enabled
- [ ] ML Studio workspace encryption enabled
- [ ] Encryption keys managed by Azure (or customer-managed keys)

### Encryption in Transit
- [ ] TLS 1.2 minimum enforced on all services
- [ ] HTTPS enforced on App Service (no HTTP)
- [ ] HTTPS enforced on Static Web Apps
- [ ] HTTPS enforced on Azure Front Door
- [ ] Certificate validation enabled
- [ ] Strong cipher suites configured

### Verification Tests
```bash
# Test 1: HTTP redirects to HTTPS
curl -I http://ah-research-prod-api.azurewebsites.net
# Expected: 301 Moved Permanently, Location: https://...

# Test 2: TLS version check
openssl s_client -connect ah-research-prod-api.azurewebsites.net:443 -tls1_1
# Expected: Connection refused (TLS 1.1 not supported)

openssl s_client -connect ah-research-prod-api.azurewebsites.net:443 -tls1_2
# Expected: Connection successful

# Test 3: SQL Database encryption
az sql db show \
  --name research-db \
  --server ah-research-prod-sql \
  --resource-group rg-research-prod \
  --query "transparentDataEncryption"
# Expected: "Enabled"
```

## 4. Audit Logging ✓

### Audit Log Implementation
- [ ] Audit logging middleware implemented
- [ ] All API requests logged (user, timestamp, action, result)
- [ ] Audit logs written to Azure SQL Database
- [ ] Audit logs written to Azure Blob Storage (immutable)
- [ ] Audit logs include: user ID, email, IP address, user agent, activity type, resource ID
- [ ] Failed authentication attempts logged
- [ ] Failed authorization attempts logged
- [ ] Data access logged (dataset views, exports)

### Audit Log Retention
- [ ] Database retention policy set to 7 years
- [ ] Blob Storage immutable storage enabled
- [ ] Blob Storage lifecycle policy configured (7-year retention)
- [ ] Audit logs cannot be deleted or modified
- [ ] Backup and restore procedures documented

### Verification Tests
```bash
# Test 1: Audit logs created for API requests
sqlcmd -S ah-research-prod-sql.database.windows.net -d research-db -U sqladmin
SELECT TOP 10 * FROM ActivityLog ORDER BY CreatedAt DESC;
# Expected: Recent API requests logged

# Test 2: Audit logs in Blob Storage
az storage blob list \
  --account-name ahresearchprodstorage \
  --container-name audit-logs \
  --prefix "$(date +%Y/%m/%d)/"
# Expected: Today's audit log files

# Test 3: Immutable storage enabled
az storage container immutability-policy show \
  --account-name ahresearchprodstorage \
  --container-name audit-logs
# Expected: Immutability policy enabled
```

## 5. Export Controls ✓

### Export Workflow
- [ ] Export request requires justification
- [ ] Export request requires PI approval
- [ ] Export approval workflow implemented
- [ ] Export approval notifications sent to PI
- [ ] Approved exports generate time-limited SAS URLs (24 hours)
- [ ] Exported data encrypted (ZIP with password or encrypted container)
- [ ] Export downloads logged in audit trail
- [ ] Exports auto-deleted after 24 hours

### Export Security
- [ ] SAS tokens have minimal permissions (read-only)
- [ ] SAS tokens expire after 24 hours
- [ ] Export files stored in secure container (no public access)
- [ ] Export files encrypted at rest
- [ ] Export download requires authentication
- [ ] Export download IP address logged

### Verification Tests
```bash
# Test 1: Export request requires authentication
curl -X POST https://ah-research-prod-api.azurewebsites.net/api/v1/exports/request
# Expected: 401 Unauthorized

# Test 2: Export approval requires PI role
curl -H "Authorization: Bearer $NON_PI_TOKEN" \
  -X POST https://ah-research-prod-api.azurewebsites.net/api/v1/exports/exp-001/review
# Expected: 403 Forbidden

# Test 3: SAS token expires
# Generate SAS token, wait 25 hours, try to download
curl "https://ahresearchprodstorage.blob.core.windows.net/exports/EXP-2024-001.zip?sas=expired_token"
# Expected: 403 Forbidden
```

## 6. CORS Configuration ✓

### CORS Settings
- [ ] CORS configured to allow only AdventHealth domain
- [ ] CORS allows only required methods (GET, POST, PATCH, DELETE)
- [ ] CORS allows only required headers (Authorization, Content-Type)
- [ ] CORS credentials enabled (allow cookies)
- [ ] CORS preflight requests handled correctly

### Verification Tests
```bash
# Test 1: CORS allows AdventHealth domain
curl -H "Origin: https://research.adventhealth.com" \
  -H "Access-Control-Request-Method: GET" \
  -X OPTIONS \
  https://ah-research-prod-api.azurewebsites.net/api/v1/user/profile
# Expected: Access-Control-Allow-Origin: https://research.adventhealth.com

# Test 2: CORS denies other domains
curl -H "Origin: https://evil.com" \
  -H "Access-Control-Request-Method: GET" \
  -X OPTIONS \
  https://ah-research-prod-api.azurewebsites.net/api/v1/user/profile
# Expected: No Access-Control-Allow-Origin header
```

## 7. Secrets Management ✓

### Azure Key Vault
- [ ] Key Vault created with RBAC enabled
- [ ] Key Vault network access restricted to VNet
- [ ] Soft delete enabled (90-day retention)
- [ ] Purge protection enabled
- [ ] All secrets stored in Key Vault (no hardcoded secrets)
- [ ] App Service uses managed identity to access Key Vault
- [ ] Key Vault access logged

### Secret Rotation
- [ ] SQL admin password stored in Key Vault
- [ ] Entra ID client secret stored in Key Vault
- [ ] Storage connection string stored in Key Vault
- [ ] SendGrid API key stored in Key Vault (if used)
- [ ] Secret rotation policy documented (90 days)
- [ ] Secret expiration alerts configured

### Verification Tests
```bash
# Test 1: Key Vault accessible from App Service
az webapp config appsettings list \
  --name ah-research-prod-api \
  --resource-group rg-research-prod \
  --query "[?name=='ENTRA_CLIENT_SECRET'].value"
# Expected: @Microsoft.KeyVault(SecretUri=...)

# Test 2: Key Vault not accessible from internet
curl https://ah-research-prod-kv.vault.azure.net/secrets/sql-admin-password
# Expected: Connection timeout or 403 Forbidden
```

## 8. DDoS Protection & WAF ✓

### Azure Front Door
- [ ] Azure Front Door deployed
- [ ] WAF policy configured
- [ ] DDoS protection enabled (Standard tier)
- [ ] Rate limiting configured (60 requests/minute per IP)
- [ ] Geo-filtering configured (US only, optional)
- [ ] Custom rules for SQL injection prevention
- [ ] Custom rules for XSS prevention

### Verification Tests
```bash
# Test 1: Rate limiting works
for i in {1..100}; do
  curl https://research.adventhealth.com/api/v1/user/profile
done
# Expected: 429 Too Many Requests after 60 requests

# Test 2: SQL injection blocked
curl "https://research.adventhealth.com/api/v1/projects?id=1' OR '1'='1"
# Expected: 403 Forbidden (WAF blocked)
```

## 9. Monitoring & Alerting ✓

### Application Insights
- [ ] Application Insights configured
- [ ] Performance monitoring enabled
- [ ] Exception tracking enabled
- [ ] Custom events tracked (export requests, approvals)
- [ ] Availability tests configured
- [ ] Alert rules configured (high CPU, high memory, errors)

### Log Analytics
- [ ] Log Analytics workspace created
- [ ] Diagnostic settings enabled for all resources
- [ ] Logs retained for 7 years
- [ ] Custom queries saved (failed logins, export approvals)
- [ ] Dashboards created (security, performance, usage)

### Alerts
- [ ] Alert: High CPU usage (>80% for 5 minutes)
- [ ] Alert: High memory usage (>80% for 5 minutes)
- [ ] Alert: HTTP 5xx errors (>10 in 5 minutes)
- [ ] Alert: Failed authentication attempts (>5 in 1 minute)
- [ ] Alert: Export approval pending >24 hours
- [ ] Alert: Budget exceeded (>$25,000/month)

## 10. HIPAA Compliance ✓

### Business Associate Agreement
- [ ] BAA signed with Microsoft Azure
- [ ] BAA covers all Azure services used
- [ ] BAA stored in secure location
- [ ] BAA reviewed annually

### Technical Safeguards
- [ ] Access controls implemented (RBAC)
- [ ] Audit controls implemented (audit logging)
- [ ] Integrity controls implemented (encryption, checksums)
- [ ] Transmission security implemented (TLS 1.2+)
- [ ] Automatic logoff implemented (8-hour session timeout)
- [ ] Encryption and decryption implemented (AES-256)

### Administrative Safeguards
- [ ] Security management process documented
- [ ] Workforce security policies documented
- [ ] Information access management policies documented
- [ ] Security awareness training completed
- [ ] Security incident procedures documented
- [ ] Contingency plan documented (disaster recovery)
- [ ] Business associate contracts signed

### Physical Safeguards
- [ ] Facility access controls documented (Azure data centers)
- [ ] Workstation use policies documented
- [ ] Workstation security policies documented
- [ ] Device and media controls documented

### Verification
- [ ] Risk assessment completed
- [ ] Security audit completed
- [ ] Penetration testing completed
- [ ] Vulnerability scanning completed
- [ ] Compliance attestation signed

## 11. Incident Response ✓

### Incident Response Plan
- [ ] Incident response plan documented
- [ ] Incident response team identified
- [ ] Incident escalation procedures documented
- [ ] Data breach notification procedures documented (72-hour requirement)
- [ ] Incident response playbooks created
- [ ] Incident response drills conducted

### Breach Notification
- [ ] Breach notification template created
- [ ] Breach notification contacts identified
- [ ] Breach notification timeline documented (72 hours)
- [ ] Breach notification procedures tested

## 12. Disaster Recovery ✓

### Backup & Recovery
- [ ] Azure SQL Database automated backups enabled (7-day retention)
- [ ] Azure SQL Database geo-replication enabled (optional)
- [ ] Azure Blob Storage geo-redundant storage enabled (GRS)
- [ ] Backup and restore procedures documented
- [ ] Recovery Time Objective (RTO) defined (4 hours)
- [ ] Recovery Point Objective (RPO) defined (1 hour)
- [ ] Disaster recovery drills conducted

### Business Continuity
- [ ] Business continuity plan documented
- [ ] Failover procedures documented
- [ ] Communication plan documented
- [ ] Alternative work arrangements documented

## 13. User Training ✓

### Training Materials
- [ ] User guide created
- [ ] Video tutorials created
- [ ] Security awareness training created
- [ ] HIPAA training completed by all users
- [ ] Phishing awareness training completed

### Training Completion
- [ ] PI training completed
- [ ] Researcher training completed
- [ ] Admin training completed
- [ ] IT support training completed

## 14. Documentation ✓

### Technical Documentation
- [ ] Architecture diagram created
- [ ] Data flow diagram created
- [ ] Network diagram created
- [ ] API documentation created
- [ ] Database schema documented
- [ ] Deployment guide created
- [ ] Operations runbook created

### Compliance Documentation
- [ ] Security policies documented
- [ ] Privacy policies documented
- [ ] Acceptable use policy documented
- [ ] Data retention policy documented
- [ ] Data disposal policy documented
- [ ] Access control policy documented

## 15. Final Pre-Launch Checklist ✓

### Security Testing
- [ ] Penetration testing completed (third-party)
- [ ] Vulnerability scanning completed
- [ ] Security code review completed
- [ ] OWASP Top 10 vulnerabilities addressed
- [ ] Security findings remediated

### Performance Testing
- [ ] Load testing completed (100 concurrent users)
- [ ] Stress testing completed
- [ ] Performance benchmarks met
- [ ] Scalability tested

### User Acceptance Testing
- [ ] Pilot users identified (5 users)
- [ ] Pilot testing completed (1 week)
- [ ] User feedback collected
- [ ] Critical issues resolved

### Go-Live Approval
- [ ] Security team approval
- [ ] Compliance team approval
- [ ] IT operations approval
- [ ] Executive sponsor approval
- [ ] Go-live date scheduled

## Sign-Off

### Security Team
- Name: ___________________________
- Title: ___________________________
- Signature: ___________________________
- Date: ___________________________

### Compliance Team
- Name: ___________________________
- Title: ___________________________
- Signature: ___________________________
- Date: ___________________________

### IT Operations
- Name: ___________________________
- Title: ___________________________
- Signature: ___________________________
- Date: ___________________________

### Executive Sponsor
- Name: ___________________________
- Title: ___________________________
- Signature: ___________________________
- Date: ___________________________

## Post-Launch Monitoring

### First 24 Hours
- [ ] Monitor error rates
- [ ] Monitor performance metrics
- [ ] Monitor security alerts
- [ ] Monitor user feedback
- [ ] On-call support available

### First Week
- [ ] Daily security reviews
- [ ] Daily performance reviews
- [ ] User feedback collection
- [ ] Issue tracking and resolution

### First Month
- [ ] Weekly security audits
- [ ] Weekly performance reviews
- [ ] Monthly user survey
- [ ] Quarterly compliance review

## Continuous Improvement

### Quarterly Reviews
- [ ] Security audit (Q1, Q2, Q3, Q4)
- [ ] Compliance review (Q1, Q2, Q3, Q4)
- [ ] Performance optimization (Q1, Q2, Q3, Q4)
- [ ] User feedback analysis (Q1, Q2, Q3, Q4)

### Annual Reviews
- [ ] Penetration testing (annual)
- [ ] Risk assessment (annual)
- [ ] BAA renewal (annual)
- [ ] Security training (annual)
- [ ] Disaster recovery drill (annual)
