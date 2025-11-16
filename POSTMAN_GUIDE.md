# Postman Guide - HTTPS Setup

This guide explains how to test the FastAPI application with HTTPS in Postman.

## Prerequisites

1. Make sure the server is running with HTTPS (port 8443)
2. SSL certificates should be generated (run `bash generate_ssl_cert.sh` if needed)

## Step 1: Configure Postman for Self-Signed Certificates

Since we're using self-signed certificates, Postman will show a security warning. Here's how to handle it:

### Option A: Disable SSL Verification (Development Only)

1. Open Postman
2. Go to **Settings** (gear icon) → **General** tab
3. Scroll down to **SSL certificate verification**
4. Toggle it **OFF** (for development/testing only)

⚠️ **Warning**: Only disable SSL verification in development. Never do this in production!

### Option B: Add Certificate to Postman (Recommended)

1. Go to **Settings** → **Certificates** tab
2. Click **Add Certificate**
3. Enter host: `localhost` or `127.0.0.1`
4. Upload your certificate file: `ssl/cert.pem`
5. Upload your key file: `ssl/key.pem`
6. Click **Add**

## Step 2: Create a New Request

### Health Check (GET)

1. **Method**: `GET`
2. **URL**: `https://localhost:8443/health`
3. Click **Send**

**Expected Response**:
```json
{
  "status": "healthy",
  "graph_initialized": true
}
```

### Root Endpoint (GET)

1. **Method**: `GET`
2. **URL**: `https://localhost:8443/`
3. Click **Send**

**Expected Response**:
```json
{
  "message": "LangGraph API",
  "version": "1.0.0",
  "endpoints": {
    "POST /execute": "Execute the LangGraph workflow",
    "GET /health": "Health check endpoint"
  }
}
```

## Step 3: Execute Endpoint (POST)

### Basic Request Setup

1. **Method**: `POST`
2. **URL**: `https://localhost:8443/execute`
3. **Headers**:
   - Key: `Content-Type`
   - Value: `application/json`
4. **Body**: Select **raw** and **JSON** format

### Example 1: High Blood Sugar

**Request Body**:
```json
{
  "input": {
    "userInput": "My doctor said my blood sugar is too high. I want to prevent diabetes.",
    "userProfile": {
      "age": 45,
      "gender": "male",
      "job": "software engineer"
    },
    "bloodData": {
      "glucose": 115,
      "hba1c": 5.9,
      "ldl": 120,
      "hdl": 55,
      "triglycerides": 140,
      "crp": 2.5,
      "vitamin_d": 25,
      "insulin": 12
    },
    "pastMessages": []
  }
}
```

### Example 2: High Cholesterol

**Request Body**:
```json
{
  "input": {
    "userInput": "I have high cholesterol and my doctor wants me to improve it naturally before considering medication.",
    "userProfile": {
      "age": 52,
      "gender": "female",
      "job": "accountant"
    },
    "bloodData": {
      "glucose": 88,
      "hba1c": 5.2,
      "ldl": 145,
      "hdl": 45,
      "triglycerides": 180,
      "crp": 3.5,
      "vitamin_d": 30
    },
    "pastMessages": []
  }
}
```

### Example 3: With Conversation History

**Request Body**:
```json
{
  "input": {
    "userInput": "I tried walking more but still struggle with consistency. What else can I do?",
    "userProfile": {
      "age": 45,
      "gender": "male",
      "job": "software engineer"
    },
    "bloodData": {
      "glucose": 115,
      "hba1c": 5.9,
      "triglycerides": 140
    },
    "pastMessages": [
      {
        "role": "user",
        "content": "I want to improve my blood sugar"
      },
      {
        "role": "assistant",
        "content": "I recommend starting with a daily walking routine..."
      }
    ]
  }
}
```

### Example 4: With Lab PDF (Base64)

**Request Body**:
```json
{
  "input": {
    "userInput": "Here are my latest lab results. What should I focus on?",
    "userProfile": {
      "age": 40,
      "gender": "male",
      "job": "engineer"
    },
    "lab_pdf": {
      "filename": "lab_results.pdf",
      "mime_type": "application/pdf",
      "base64": "JVBERi0xLjQKJdPr6eEKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKPD4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovTWVkaWFCb3ggWzAgMCA2MTIgNzkyXQovUmVzb3VyY2VzIDw8Ci9Gb250IDw8Ci9GMSA0IDAgUgo+Pgo+PgovQ29udGVudHMgNSAwIFIKPj4KZW5kb2JqCjQgMCBvYmoKPDwKL1R5cGUgL0ZvbnQKL1N1YnR5cGUgL1R5cGUxCi9CYXNlRm9udCAvSGVsdmV0aWNhCj4+CmVuZG9iagoxIDAgb2JqCjw8Ci9UeXBlIC9DYXRhbG9nCi9QYWdlcyAyIDAgUgo+PgplbmRvYmoKNSAwIG9iago8PAovTGVuZ3RoIDQ0Cj4+CnN0cmVhbQpCVAovRjEgMTIgVGYKNzAgNzAwIFRkCihIZWxsbyBXb3JsZCkgVGoKRVQKZW5kc3RyZWFtCmVuZG9iagp4cmVmCjAgNgowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA1NCAwMDAwMCBuIAowMDAwMDAwMTA3IDAwMDAwIG4gCjAwMDAwMDAyODMgMDAwMDAgbiAKMDAwMDAwMDMzNyAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDYKL1Jvb3QgMSAwIFIKPj4Kc3RhcnR4cmVmCjQyMQolJUVPRgo="
    },
    "pastMessages": []
  }
}
```

## Expected Response Format

```json
{
  "output": {
    "response": "Complete personalized message with longevity score, recommendations, and safety review...",
    "intervention_name": "Berberine Supplementation",
    "topOpportunityBiomarker": "glucose",
    "potentialBonusYears": 2.5,
    "challenge": {
      "intervention_name": "Berberine Supplementation",
      "duration_days": 10,
      "description": "..."
    }
  }
}
```

## Troubleshooting

### Error: "SSL certificate problem"

**Solution**: 
- Make sure SSL verification is disabled in Postman settings (for development)
- Or add the certificate manually in Postman settings

### Error: "Connection refused" or "ECONNREFUSED"

**Solution**:
- Verify the server is running: `ps aux | grep fastapi_app.py`
- Check the port: Should be 8443 for HTTPS
- Verify certificates exist: `ls -la ssl/`

### Error: "503 - Graph not initialized"

**Solution**:
- Wait a few seconds after server startup
- Check server logs: `tail -f fastapi.log`
- The graph needs time to initialize on first startup

### Error: "500 - Execution Error"

**Solution**:
- Check that all required fields are provided
- Verify JSON format is valid
- Check server logs for detailed error messages

## Postman Collection

You can create a Postman Collection with these requests:

1. Click **New** → **Collection**
2. Name it "LangGraph API"
3. Add the requests above as collection items
4. Set collection variables:
   - `base_url`: `https://localhost:8443`
   - Use `{{base_url}}/health` in your requests

## Environment Variables

Create a Postman Environment for easy switching:

**Variables**:
- `base_url`: `https://localhost:8443`
- `port`: `8443`

Then use `{{base_url}}/execute` in your requests.

## Quick Test Checklist

- [ ] Server is running on HTTPS (port 8443)
- [ ] SSL certificates exist in `ssl/` directory
- [ ] Postman SSL verification is disabled (or certificate added)
- [ ] Health check endpoint returns 200 OK
- [ ] Execute endpoint accepts JSON payload
- [ ] Response contains `output.response` field

## Security Notes

⚠️ **Important**: 
- Self-signed certificates are for **development only**
- For production, use certificates from a trusted CA (e.g., Let's Encrypt)
- Never disable SSL verification in production environments
- Keep your private key (`ssl/key.pem`) secure and never commit it to version control

