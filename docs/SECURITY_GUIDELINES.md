# Security Guidelines — Marcus Garvey App WWMD

**Date**: February 8, 2026  
**Version**: 1.0  
**Subject**: API Key Management, Data Protection, and Best Practices

---

## API Key Security

### Where Keys Are Used

| Location | Method | Security |
|----------|--------|----------|
| `.env` file | Read at startup | Should NOT be in repo (in `.gitignore`) |
| Environment variable | Read from `GEMINI_API_KEY` | Platform-managed (Vercel, Render, etc.) |
| User-supplied (frontend) | Sent in POST request body | Transported via HTTPS |
| Generation API | Authorization header | Never in URL query params ✅ |

### Key Handling Best Practices

#### Do ✅
- Store keys in platform environment variables (Vercel, Render, Heroku)
- Use Authorization header for API calls (not URL query params)
- Validate key format before use (32+ chars, alphanumeric+underscore)
- Log presence of keys, NOT the key values themselves
- Enable HTTPS everywhere (URLs should be `https://`)
- Rotate keys regularly
- Use separate keys for staging/production

#### Do NOT ❌
- Commit `.env` file to Git
- Print or log full key values
- Pass keys as URL query parameters
- Send keys over unencrypted HTTP
- Share keys via email or Slack
- Store keys in code comments
- Use same key for multiple environments

---

## Input Validation & Sanitization

### User-Supplied API Keys
- **Validation**: Must be 32+ characters, alphanumeric with `_` and `-`
- **Sanitization**: Whitespace trimmed, invalid format rejected with generic error
- **Error Message**: Never echoes back the invalid key

### User Queries & Situations
- **Max Length**: 
  - WWMD Query: 2,000 characters
  - WWMD Situation: 4,000 characters
- **Type Check**: Must be string, not JSON object or array
- **Sanitization**: Trimmed of whitespace before processing

### Prompt Injection Prevention
- User input is passed to LLM only within defined context sections
- Prompt template structure prevents breaking out of context
- System instructions are separate from user data

---

## Logging & Monitoring

### What to Log ✅
- Request timestamp
- Endpoint called
- Response status (success/error type)
- Latency metrics
- Key presence (true/false), not the key itself

### What NOT to Log ❌
- Full API keys
- User's actual queries (privacy)
- Response content containing sensitive data
- Database connection strings
- Environment variables

### Error Handling
- Generic error messages for users
- Detailed errors only in server logs (not sent to client)
- Never expose stack traces to clients
- HTTP 401: Sanitized "Unauthorized" message only

---

## HTTPS & Transport Security

### Production Requirements
1. **Frontend**: Must be served over HTTPS
   - Vercel, Netlify auto-provide SSL
   - Custom domain: ensure HTTPS certificate installed
2. **Backend API**: Must be served over HTTPS
   - Vercel, Render auto-provide SSL
   - Self-hosted: use Let's Encrypt + nginx/Caddy
3. **CORS Configuration**:
   - Set `CORS_ORIGINS` to exact frontend domain
   - Do NOT use wildcard (`*`) in production
   - Example: `https://app.your-domain.com` (not `http://localhost:3000`)

---

## API Key Precedence (Current Implementation)

When calling the WWMD/RAG system, API keys are checked in this order:

1. **User-supplied key** (from `/api/wwmd` or `/api/chat` request body `apiConfig.geminiApiKey`)
   - If provided and valid format → use this
   - If provided but invalid → error (generic message)
   
2. **Environment variable** (`GEMINI_API_KEY`)
   - If set and valid → use this
   - If set but invalid → error
   
3. **`.env` file** (fallback only)
   - Last resort for local development
   - NEVER in production repo

---

## Diagnostic Endpoint (`/api/key-diagnostic`)

### Purpose
Safe detection of which API key source would be used without exposing secrets.

### Response (Example)
```json
{
  "user_key_present": false,
  "env_key_present": true,
  "using_user_key": false,
  "using_env_key": true,
  "note": "This endpoint will never echo secret values..."
}
```

### Security Notes
- Returns only boolean flags, never key content
- Safe to call from frontend for debugging
- Does NOT reveal which .env file was read
- Does NOT reveal key format or length

### Optional: Restrict Access
Consider adding `DIAGNOSTIC_MODE` or admin token check if you want to disable this endpoint in production.

---

## Environment Variables (Recommended)

### Development (Local)
```bash
# .env file (NOT in Git)
GEMINI_API_KEY="your_dev_key_here"
DIAGNOSTIC_MODE=1
```

### Staging (Vercel/Render)
```bash
# Via platform dashboard environment variables
GEMINI_API_KEY=sk_staging_xxx_xxx_xxx
CORS_ORIGINS=https://staging.your-domain.com
DIAGNOSTIC_MODE=0
```

### Production (Vercel/Render)
```bash
# Via platform dashboard environment variables
GEMINI_API_KEY=sk_prod_xxx_xxx_xxx
CORS_ORIGINS=https://app.your-domain.com
DIAGNOSTIC_MODE=0
```

---

## Secrets Management Checklist

Before deploying to production:

- [ ] GEMINI_API_KEY set in platform environment variables
- [ ] `.env` file NOT in Git history (check `.gitignore`)
- [ ] CORS_ORIGINS set to exact frontend domain
- [ ] HTTPS enabled for both frontend and backend
- [ ] DIAGNOSTIC_MODE unset or set to `0` in production
- [ ] All debug logging removed or muted
- [ ] API key validation enabled (32+ char check)
- [ ] No keys in error messages
- [ ] Review recent Git commits for accidental secret exposure

---

## Incident Response

If an API key is accidentally exposed:

1. **Immediately** rotate the key in your Google Cloud console
2. Delete the key from exposed location (Git, logs, etc.)
3. Generate a new key
4. Update all environment variables
5. Monitor for unauthorized usage

---

## References

- [Google Cloud Security Best Practices](https://cloud.google.com/docs/authentication/application-default-credentials)
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [Vercel Environment Variables](https://vercel.com/docs/concepts/projects/environment-variables)

---

**Last Updated**: February 8, 2026  
**Maintained By**: WWMD Security Team
