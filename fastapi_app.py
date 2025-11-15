"""
FastAPI application exposing the LangGraph workflow as REST API endpoints.

This module creates a FastAPI server that wraps the LangGraph application,
allowing it to be accessed via HTTP requests.
"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Literal
from langgraph_app import create_graph
from nodes import GraphState

# Load environment variables from .env file
load_dotenv()

# Create FastAPI app instance
app = FastAPI(
    title="LangGraph API",
    description="API for LangGraph suggestion and critique workflow",
    version="1.0.0"
)

# Initialize the graph once at startup
graph_app = None


@app.on_event("startup")
async def startup_event():
    """Initialize the LangGraph application on server startup."""
    global graph_app
    print("Initializing LangGraph...")
    graph_app = create_graph()
    print("LangGraph initialized and ready!")


# Pydantic models matching the new API schema
class Message(BaseModel):
    """Message model with role and content."""
    role: Literal["user", "assistant", "system"]
    content: str


class PdfInput(BaseModel):
    """PDF input model with type and data."""
    type: Optional[Literal["base64", "url", "file_id"]] = None
    data: Optional[str] = None


class UserProfile(BaseModel):
    """User profile model for biohacker agent."""
    age: int
    gender: Literal["male", "female", "other"]
    job: str


class BloodData(BaseModel):
    """Blood biomarker data model - flexible dict of marker names to values."""
    glucose: Optional[float] = None
    hba1c: Optional[float] = None
    ldl: Optional[float] = None
    hdl: Optional[float] = None
    triglycerides: Optional[float] = None
    crp: Optional[float] = None
    vitamin_d: Optional[float] = None
    insulin: Optional[float] = None
    blood_pressure_systolic: Optional[float] = None
    blood_pressure_diastolic: Optional[float] = None
    
    def to_dict(self):
        """Convert to dict, excluding None values."""
        return {k: v for k, v in self.model_dump().items() if v is not None}


class ApiInput(BaseModel):
    """Input model for the API request."""
    userInput: str = ""
    pastMessages: list[Message] = []
    pdf: PdfInput = PdfInput()
    userProfile: Optional[UserProfile] = None
    bloodData: Optional[BloodData] = None


class ApiOutput(BaseModel):
    """Output model for the API response."""
    response: str
    finalSuggestion: bool


class ApiRequest(BaseModel):
    """Request model for the /execute endpoint."""
    input: ApiInput


class ApiResponse(BaseModel):
    """Response model for the /execute endpoint."""
    output: ApiOutput


# Legacy models for backward compatibility (if needed)
class GraphRequest(BaseModel):
    """Request model for graph execution."""
    initial_state: Optional[dict] = {}


class GraphResponse(BaseModel):
    """Response model for graph execution."""
    suggestion: Optional[str] = None
    critique: Optional[str] = None
    full_state: dict


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "LangGraph API",
        "version": "1.0.0",
        "endpoints": {
            "POST /execute": "Execute the LangGraph workflow",
            "GET /health": "Health check endpoint"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "graph_initialized": graph_app is not None
    }


@app.post("/execute", response_model=ApiResponse)
async def execute_graph(request: ApiRequest):
    """
    Execute the LangGraph workflow.
    
    This endpoint runs the complete graph (suggestion → critic) and returns
    the final response and suggestion based on user input, messages, and PDF content.
    
    Args:
        request: ApiRequest containing input with userInput, messages, and pdf
        
    Returns:
        ApiResponse with output containing response and finalSuggestion
        
    Raises:
        HTTPException: If graph is not initialized or execution fails
    """
    if graph_app is None:
        raise HTTPException(
            status_code=503,
            detail="Graph not initialized. Please wait for startup to complete."
        )
    
    try:
        # Map ApiRequest.input to GraphState
        initial_state: GraphState = {
            "userInput": request.input.userInput,
            "messages": [msg.model_dump() for msg in request.input.pastMessages],
            "pdf": request.input.pdf.model_dump()
        }
        
        # Add biohacker fields if provided
        if request.input.userProfile:
            initial_state["userProfile"] = request.input.userProfile.model_dump()
        
        if request.input.bloodData:
            initial_state["bloodData"] = request.input.bloodData.to_dict()
        
        # Execute the graph
        final_state = graph_app.invoke(initial_state)
        
        # Map final state to ApiResponse
        # Use response field (critique) and finalSuggestion field from state
        response_text = final_state.get("response") or final_state.get("critique", "No response generated")
        final_suggestion_approved = final_state.get("finalSuggestion", False)
        
        response = ApiResponse(
            output=ApiOutput(
                response=response_text,
                finalSuggestion=final_suggestion_approved
            )
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error executing graph: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

