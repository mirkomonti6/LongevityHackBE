# LangGraph Application with FastAPI

A LangGraph application with suggestion and critic nodes, exposed as a REST API using FastAPI.

## Project Overview

This project implements a simple LangGraph workflow with two nodes:

- **Suggestion Node**: Generates suggestions
- **Critic Node**: Evaluates and critiques the suggestions

The application can be run as a standalone script or exposed as a REST API via FastAPI.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

### 1. Clone or navigate to the project directory

```bash
cd "/Users/mirkomonti/Desktop/AI_Longevity_Hack/Real project"
```

### 2. Create a virtual environment (recommended)

```bash
python3 -m venv venv
```

### 3. Activate the virtual environment

**On macOS/Linux:**

```bash
source venv/bin/activate
```

**On Windows:**

```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

This will install:

- `langgraph` - For building stateful, multi-actor applications
- `langchain-core` - Core LangChain functionality
- `langchain-openai` - OpenAI integration for LangChain
- `python-dotenv` - For environment variable management
- `fastapi` - Web framework for building APIs
- `uvicorn` - ASGI server for running FastAPI

## Execution

### Option 1: Run as Standalone Script

Execute the LangGraph application directly:

```bash
python langgraph_app.py
```

This will:

1. Create the LangGraph workflow
2. Execute the graph (suggestion → critic)
3. Display the results in the terminal

**Expected Output:**

```
Creating LangGraph...
Initializing graph with empty state...
Executing graph...
------------------------------------------------------------
------------------------------------------------------------

Execution complete!

Results:
------------------------------------------------------------
Suggestion: Consider implementing a feature that improves user engagement through personalized recommendations.

Critique: Critique: The suggestion 'Consider implementing a feature that improves user engagement through personalized recommendations.' has merit. However, consider the implementation complexity and resource requirements. It would be beneficial to validate user demand before full implementation.

------------------------------------------------------------
```

### Option 2: Run as FastAPI Server

Start the FastAPI server to expose the LangGraph as a REST API:

```bash
python fastapi_app.py
```

Or using uvicorn directly:

```bash
uvicorn fastapi_app:app --host 0.0.0.0 --port 8000
```

The server will start on `http://0.0.0.0:8000`

**Access the API:**

- **Interactive API Documentation (Swagger UI)**: http://localhost:8000/docs
- **Alternative API Documentation (ReDoc)**: http://localhost:8000/redoc
- **Root endpoint**: http://localhost:8000/
- **Health check**: http://localhost:8000/health

## API Usage

### Execute the Graph Workflow

**Endpoint:** `POST /execute`

**Request:**

```bash
curl -X POST "http://localhost:8000/execute" \
  -H "Content-Type: application/json" \
  -d '{"initial_state": {}}'
```

**Response:**

```json
{
  "suggestion": "Consider implementing a feature that improves user engagement through personalized recommendations.",
  "critique": "Critique: The suggestion 'Consider implementing a feature that improves user engagement through personalized recommendations.' has merit. However, consider the implementation complexity and resource requirements. It would be beneficial to validate user demand before full implementation.",
  "full_state": {
    "suggestion": "Consider implementing a feature that improves user engagement through personalized recommendations.",
    "critique": "Critique: The suggestion 'Consider implementing a feature that improves user engagement through personalized recommendations.' has merit. However, consider the implementation complexity and resource requirements. It would be beneficial to validate user demand before full implementation."
  }
}
```

### Health Check

**Endpoint:** `GET /health`

```bash
curl http://localhost:8000/health
```

**Response:**

```json
{
  "status": "healthy",
  "graph_initialized": true
}
```

### Get API Information

**Endpoint:** `GET /`

```bash
curl http://localhost:8000/
```

## Project Structure

```
.
├── langgraph_app.py      # LangGraph application with nodes and graph definition
├── fastapi_app.py        # FastAPI wrapper exposing the LangGraph as REST API
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── venv/                # Virtual environment (created during installation)
```

## Key Files

- **`langgraph_app.py`**: Contains the core LangGraph implementation:

  - `GraphState`: State schema for the graph
  - `suggestion_node()`: Node that generates suggestions
  - `critic_node()`: Node that critiques suggestions
  - `create_graph()`: Builds and compiles the LangGraph
  - `main()`: Standalone execution function

- **`fastapi_app.py`**: FastAPI application that wraps the LangGraph:
  - `POST /execute`: Executes the graph workflow
  - `GET /health`: Health check endpoint
  - `GET /`: API information endpoint

## Development

### Running Tests

Currently, the project can be tested by:

1. Running the standalone script: `python langgraph_app.py`
2. Starting the FastAPI server and testing endpoints via the Swagger UI at http://localhost:8000/docs

### Running Offline Evaluations

Use the Deepeval harness in `evals/` to sanity-check the single-turn workflow without hitting the FastAPI API.

1. Install dependencies (includes `deepeval`):
   ```bash
   pip install -r requirements.txt
   ```
2. (Optional) Override the NetMind key used for both the workflow nodes and the Deepeval judge:
   ```bash
   export NETMIND_API_KEY=your-netmind-key
   ```
   A throwaway key is already hard-coded, so you can skip this step for local smoke tests.
3. Execute the eval harness:
   ```bash
   python -m evals.run_single_turn_eval
   ```

The harness loads hard-coded `GraphState` payloads from `evals/single_turn_cases.py`, runs the workflow locally, and scores each response with Deepeval's `AnswerRelevancyMetric` plus a lightweight `GEval` correctness check. Both metrics rely on the custom NetMind-backed judge defined in `evals/netmind_llm.py`.

### Environment Variables

If you need to use OpenAI API keys for LLM integration, create a `.env` file:

```bash
OPENAI_API_KEY=your_api_key_here
```

Then load it in your code using `python-dotenv`.

## Troubleshooting

### Import Errors

If you encounter import errors, ensure:

1. Virtual environment is activated
2. All dependencies are installed: `pip install -r requirements.txt`

### Port Already in Use

If port 8000 is already in use, specify a different port:

```bash
uvicorn fastapi_app:app --host 0.0.0.0 --port 8001
```

### Graph Not Initialized Error

If you see a "Graph not initialized" error, wait a moment after starting the server for the startup event to complete.

## Next Steps

- Add LLM integration to the suggestion and critic nodes
- Implement more sophisticated state management
- Add authentication/authorization to the API
- Add logging and monitoring
- Implement additional graph nodes and workflows

## License

[Add your license information here]
