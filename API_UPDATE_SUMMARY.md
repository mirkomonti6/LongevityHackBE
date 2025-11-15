# API Schema Update Summary

## Overview
Updated the LangGraph application and FastAPI to match the new input/output schema with support for user input, conversation messages, and PDF documents.

## New API Schema

### Request Format
```json
{
  "input": {
    "userInput": "string",
    "messages": [
      {
        "role": "user | assistant | system",
        "content": "string"
      }
    ],
    "pdf": {
      "type": "base64 | url | file_id | null",
      "data": "string or null"
    }
  }
}
```

### Response Format
```json
{
  "output": {
    "response": "string",
    "finalSuggestion": "string"
  }
}
```

## Changes Made

### 1. langgraph_app.py

#### Updated GraphState
Added new fields to the state schema:
- `userInput`: User's input text
- `messages`: List of conversation messages with role and content
- `pdf`: PDF document information (type and data)
- `response`: Final response output (critique)
- `finalSuggestion`: Final suggestion output

#### New Function: extract_pdf_content()
- Mock function that simulates PDF content extraction
- Handles three PDF types: `base64`, `url`, `file_id`
- Returns mocked extracted text based on type

#### Updated suggestion_node()
- Extracts `userInput`, `messages`, and `pdf` from state
- Calls `extract_pdf_content()` to process PDF
- Builds context from last 3 conversation messages
- Generates suggestion based on all inputs
- Populates both `suggestion` and `finalSuggestion` fields

#### Updated critic_node()
- Generates critique based on suggestion
- Populates both `critique` and `response` fields with the same value

### 2. fastapi_app.py

#### New Pydantic Models
Created models matching the API schema:
- `Message`: role (Literal["user", "assistant", "system"]), content (str)
- `PdfInput`: type (Optional[Literal["base64", "url", "file_id"]]), data (Optional[str])
- `ApiInput`: userInput (str), messages (list[Message]), pdf (PdfInput)
- `ApiOutput`: response (str), finalSuggestion (str)
- `ApiRequest`: input (ApiInput)
- `ApiResponse`: output (ApiOutput)

#### Updated /execute Endpoint
- Changed signature to accept `ApiRequest` and return `ApiResponse`
- Maps incoming request to GraphState format
- Converts messages and PDF to dict format for state
- Executes the LangGraph workflow
- Maps final state back to ApiResponse format
- Extracts `response` and `finalSuggestion` from state

## Testing the API

### Start the Server
```bash
# Option 1
python fastapi_app.py

# Option 2
uvicorn fastapi_app:app --host 0.0.0.0 --port 8000
```

### Example Request
```bash
curl -X POST "http://localhost:8000/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "userInput": "What are the best longevity practices?",
      "messages": [
        {"role": "user", "content": "Tell me about health"},
        {"role": "assistant", "content": "Health is important"}
      ],
      "pdf": {
        "type": "base64",
        "data": "sample_data"
      }
    }
  }'
```

### Expected Response
```json
{
  "output": {
    "response": "Critique: The suggestion '...' has merit. However, consider the implementation complexity and resource requirements. It would be beneficial to validate user demand before full implementation.",
    "finalSuggestion": "Based on your input: 'What are the best longevity practices?' Considering the conversation context and the document content: [Mocked PDF extraction] Document provided as base64. Content summary: Research findings on longevity and health optimization., I suggest focusing on personalized health optimization strategies that integrate the latest research findings."
  }
}
```

## Interactive API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Files Modified

1. `langgraph_app.py`
   - Updated GraphState TypedDict
   - Added extract_pdf_content() function
   - Updated suggestion_node() function
   - Updated critic_node() function

2. `fastapi_app.py`
   - Added new Pydantic models
   - Updated /execute endpoint
   - Added Literal type import

## Validation

- ✅ All imports verified
- ✅ No linting errors
- ✅ Models match the specified schema
- ✅ Request/response mapping implemented correctly

## Next Steps

1. Test the API with various inputs
2. Replace mock PDF extraction with actual PDF processing library (e.g., PyPDF2, pdfplumber)
3. Integrate real LLM calls (e.g., OpenAI) in suggestion and critic nodes
4. Add authentication/authorization if needed
5. Deploy to production environment

