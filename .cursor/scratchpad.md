# Project Scratchpad

## Background and Motivation

The user wants to build a LangGraph application with 2 nodes: "suggestion" and "critic". LangGraph is a library for building stateful, multi-actor applications with LLMs. This appears to be a simple graph where:
- The "suggestion" node generates suggestions
- The "critic" node evaluates/critiques those suggestions

This is a foundational setup that can be extended for more complex workflows.

## Key Challenges and Analysis

1. **Dependencies**: Need to install `langgraph` and potentially `langchain` or `langchain-core` for the graph framework
2. **State Management**: LangGraph requires a state schema to pass data between nodes
3. **Node Implementation**: Each node needs to be a function that takes state and returns updated state
4. **Graph Construction**: Need to define edges/connections between nodes (suggestion → critic)
5. **LLM Integration**: Nodes likely need LLM calls, requiring API keys and model configuration
6. **Testing**: Need to verify nodes execute correctly and state flows properly

## High-level Task Breakdown

### Task 1: Set up project dependencies
**Success Criteria:**
- Create `requirements.txt` with necessary packages (langgraph, langchain-core, langchain-openai or similar)
- Install dependencies successfully
- Verify imports work

### Task 2: Define state schema
**Success Criteria:**
- Create a TypedDict or Pydantic model for the graph state
- State should include fields for suggestions and critiques
- State schema is properly typed and documented

### Task 3: Implement "suggestion" node
**Success Criteria:**
- Create a function that takes state and returns updated state
- Node generates a suggestion (can be a simple placeholder or use LLM)
- Function follows LangGraph node signature pattern
- Node can be tested independently

### Task 4: Implement "critic" node
**Success Criteria:**
- Create a function that takes state and returns updated state
- Node critiques/evaluates the suggestion from state
- Function follows LangGraph node signature pattern
- Node can be tested independently

### Task 5: Build and compile the graph
**Success Criteria:**
- Create graph using LangGraph's StateGraph
- Add both nodes to the graph
- Define edge from "suggestion" to "critic"
- Compile the graph successfully
- Graph can be instantiated without errors

### Task 6: Create main execution script
**Success Criteria:**
- Create a main function or script entry point
- Initialize graph with initial state
- Execute the graph and verify both nodes run
- Output shows suggestion and critique

### Task 7: Add basic error handling and logging
**Success Criteria:**
- Add try-catch blocks for graph execution
- Add logging for node execution
- Handle missing API keys gracefully if using LLMs
- Error messages are informative

### Task 8: Test the complete workflow
**Success Criteria:**
- Run the graph with test input
- Verify suggestion node executes
- Verify critic node executes
- Verify final state contains both suggestion and critique
- Manual testing confirms expected behavior

### Task 9: Expose LangGraph as FastAPI application
**Success Criteria:**
- Add FastAPI and uvicorn to requirements.txt
- Create FastAPI wrapper that imports and uses the LangGraph
- Create REST API endpoints (POST /execute, GET /health, GET /)
- Graph initializes on server startup
- API can execute graph via HTTP requests
- Error handling for API endpoints
- FastAPI app can be run with uvicorn

### Task 10: Update API to match new input/output schema
**Success Criteria:**
- Update GraphState to include userInput, messages, pdf, response, finalSuggestion
- Create mock PDF extraction function
- Update suggestion_node to use userInput, messages, and PDF content
- Update critic_node to populate both critique and response fields
- Create new Pydantic models (Message, PdfInput, ApiInput, ApiOutput, ApiRequest, ApiResponse)
- Update /execute endpoint to accept new schema and map to/from GraphState

## Project Status Board

- [x] Task 1: Set up project dependencies
- [x] Task 2: Define state schema
- [x] Task 3: Implement "suggestion" node
- [x] Task 4: Implement "critic" node
- [x] Task 5: Build and compile the graph
- [x] Task 6: Create main execution script
- [ ] Task 7: Add basic error handling and logging
- [ ] Task 8: Test the complete workflow
- [x] Task 9: Expose LangGraph as FastAPI application
- [x] Task 10: Update API to match new input/output schema

## Current Status / Progress Tracking

**Status**: Task 10 completed. API updated to match new input/output schema with userInput, messages, PDF support.

**Last Updated**: Task 10 completed - API schema updated with new models and endpoint mappings

**Completed:**
- Created virtual environment (`venv/`)
- Created `requirements.txt` with langgraph, langchain-core, langchain-openai, python-dotenv
- Installed all dependencies successfully
- Verified imports work correctly
- Created `langgraph_app.py` with `GraphState` TypedDict
- State schema includes `suggestion` and `critique` fields (both NotRequired[str])
- Verified state can be instantiated and used correctly
- Implemented `suggestion_node()` function that takes state and returns updated state
- Node generates a suggestion and updates the state
- Tested node independently - works correctly
- Implemented `critic_node()` function that takes state and returns updated state
- Node reads suggestion from state and generates a critique
- Handles edge case when suggestion is missing
- Tested node independently - works correctly
- Tested both nodes in sequence - suggestion → critic flow works
- Created `create_graph()` function that builds the LangGraph
- Added both nodes to the graph ("suggestion" and "critic")
- Set entry point to "suggestion" node
- Defined edge from "suggestion" to "critic"
- Added edge from "critic" to END
- Graph compiled successfully without errors
- Verified graph can be instantiated and has correct node structure
- Created `main()` function that orchestrates graph execution
- Function creates graph, initializes with empty state, executes, and displays results
- Added `if __name__ == "__main__"` block for script execution
- Script runs successfully and shows both suggestion and critique in output
- Verified both nodes execute when running the script
- Added FastAPI and uvicorn to requirements.txt
- Created `fastapi_app.py` with FastAPI wrapper
- Implemented POST /execute endpoint to run the graph workflow
- Implemented GET /health endpoint for health checks
- Implemented GET / endpoint with API information
- Graph initializes on server startup using startup event
- Created Pydantic models (GraphRequest, GraphResponse) for API requests/responses
- Added error handling for API endpoints (503 for uninitialized graph, 500 for execution errors)
- Installed FastAPI and uvicorn dependencies successfully
- FastAPI app can be run with `python fastapi_app.py` or `uvicorn fastapi_app:app`
- Created comprehensive README.md with installation and execution instructions
- README includes project overview, prerequisites, installation steps, execution options, API usage examples, project structure, and troubleshooting guide
- **Updated GraphState** to include: userInput, messages, pdf, response, finalSuggestion fields
- **Created extract_pdf_content()** mock function that simulates PDF extraction for base64, url, and file_id types
- **Updated suggestion_node()** to:
  - Extract userInput, messages, and pdf from state
  - Call extract_pdf_content() for PDF processing
  - Build context from conversation messages
  - Generate suggestions based on all inputs
  - Populate both suggestion and finalSuggestion fields
- **Updated critic_node()** to populate both critique and response fields (same value)
- **Created new Pydantic models** in fastapi_app.py:
  - Message (role: Literal["user", "assistant", "system"], content: str)
  - PdfInput (type: Optional[Literal["base64", "url", "file_id"]], data: Optional[str])
  - ApiInput (userInput: str, messages: list[Message], pdf: PdfInput)
  - ApiOutput (response: str, finalSuggestion: str)
  - ApiRequest (input: ApiInput)
  - ApiResponse (output: ApiOutput)
- **Updated /execute endpoint** to:
  - Accept ApiRequest instead of GraphRequest
  - Map input fields to GraphState (userInput, messages, pdf)
  - Execute graph with mapped state
  - Map final state response and finalSuggestion to ApiResponse output
- Verified all imports work correctly
- No linting errors in both files

**Next Step**: Test the updated API endpoints with new schema or proceed with Task 7 - Add basic error handling and logging

## Executor's Feedback or Assistance Requests

Task 10 completed successfully. API has been updated to match the new input/output schema:

**New API Schema:**
```json
{
  "input": {
    "userInput": "string",
    "messages": [{"role": "user|assistant|system", "content": "string"}],
    "pdf": {"type": "base64|url|file_id|null", "data": "string or null"}
  },
  "output": {
    "response": "string",
    "finalSuggestion": "string"
  }
}
```

**Changes Made:**
1. **langgraph_app.py:**
   - Updated GraphState TypedDict with new fields (userInput, messages, pdf, response, finalSuggestion)
   - Added extract_pdf_content() mock function for PDF simulation
   - Updated suggestion_node to process userInput, messages, and PDF content
   - Updated critic_node to populate both critique and response fields

2. **fastapi_app.py:**
   - Created new Pydantic models matching the API schema (Message, PdfInput, ApiInput, ApiOutput, ApiRequest, ApiResponse)
   - Updated /execute endpoint to accept ApiRequest and return ApiResponse
   - Added mapping logic to convert between API schema and GraphState

**To Test the API:**
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

All imports verified and no linting errors. Ready for user testing.

## Lessons

_No lessons recorded yet_

