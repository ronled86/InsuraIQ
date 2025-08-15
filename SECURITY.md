# Security Guidelines for InsuraIQ

## 🔒 Security Features

### Authentication & Authorization
- JWT-based authentication with Supabase integration
- User-based data isolation (all policies scoped to authenticated user)
- Rate limiting (240 requests/minute per IP)
- CORS protection with configurable allowed origins

### File Upload Security
- File type validation (only .pdf and .csv allowed)
- File size limits (configurable, default 10MB)
- Filename sanitization to prevent path traversal attacks
- Secure temporary file handling

### Database Security
- SQLAlchemy ORM prevents SQL injection
- Parameterized queries throughout
- Environment-based database credentials

### Error Handling
- Generic error messages in production mode
- Detailed logging for debugging (in LOCAL_DEV mode only)
- Secure exception handling

## 🛡️ Production Security Checklist

### Before Deployment:

1. **Environment Variables**
   ```bash
   # Set strong database password
   POSTGRES_PASSWORD=YOUR_VERY_STRONG_PASSWORD_HERE
   
   # Configure allowed origins (replace with your domains)
   ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
   
   # Set valid OpenAI API key
   OPENAI_API_KEY=your_real_openai_api_key
   
   # Disable local dev mode
   LOCAL_DEV=false
   ```

2. **HTTPS Configuration**
   - Update `infra/Caddyfile` to use proper TLS certificates
   - Replace `tls internal` with `tls your@email.com` for Let's Encrypt

3. **Database Security**
   - Change default PostgreSQL password
   - Restrict database network access
   - Enable SSL connections

4. **File Storage**
   - Consider encrypting stored PDF files
   - Implement file retention policies
   - Regular backup procedures

### Security Headers

The application should be deployed behind a reverse proxy (Caddy) that adds security headers:

```
Strict-Transport-Security: max-age=31536000
Content-Security-Policy: default-src 'self'
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
```

### Monitoring & Logging

- Monitor rate limiting hits
- Log authentication failures
- Track file upload patterns
- Monitor for suspicious activity

## 🚨 Security Incident Response

If you suspect a security breach:

1. **Immediate Actions**
   - Rotate all API keys and secrets
   - Check logs for suspicious activity
   - Disable affected user accounts if necessary

2. **Investigation**
   - Preserve logs for analysis
   - Document the incident
   - Identify scope of potential data exposure

3. **Recovery**
   - Apply security patches
   - Update authentication tokens
   - Notify users if personal data was potentially accessed

## 📋 Regular Security Maintenance

### Monthly:
- Review and rotate API keys
- Check for dependency vulnerabilities
- Review access logs

### Quarterly:
- Security audit of the application
- Update dependencies
- Review user access patterns

### Annually:
- Penetration testing
- Security architecture review
- Disaster recovery testing

## 🔧 Security Configuration Reference

### File Upload Limits
```python
# In .env
MAX_FILE_SIZE_MB=10  # Maximum file size in MB
```

### CORS Configuration
```python
# In .env
ALLOWED_ORIGINS=https://app.yourdomain.com,https://yourdomain.com
```

### Rate Limiting
```python
# In .env
RATE_LIMIT_PER_MINUTE=240  # Requests per minute per IP
```

## 📞 Contact

For security-related questions or to report vulnerabilities, contact the development team.

**Do not** post security issues in public GitHub issues.
