"""
FastAPI application exposing the LangGraph workflow as REST API endpoints.

This module creates a FastAPI server that wraps the LangGraph application,
allowing it to be accessed via HTTP requests.
"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Literal, Dict, Any
from langgraph_app import create_graph
from nodes import GraphState
from nodes.pdf_parser import NetMindLabExtractor

# Load environment variables from .env file
load_dotenv()

# Create FastAPI app instance
app = FastAPI(
    title="LangGraph API",
    description="API for LangGraph suggestion and critique workflow",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=False,  # Cannot be True when allow_origins=["*"]
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
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


class LabPdfInput(BaseModel):
    """Lab PDF input model with filename, mime_type, and base64 data."""
    filename: str
    mime_type: str
    base64: str


class UserProfile(BaseModel):
    """User profile model for biohacker agent."""
    age: int
    gender: Literal["male", "female", "other"]
    job: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    sleep_hours_per_night: Optional[float] = None
    movement_days_per_week: Optional[int] = None
    work_activity_level: Optional[str] = None
    stress_level_1_to_10: Optional[int] = None


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
    sex: Optional[Literal["male", "female", "other"]] = None
    lab_pdf: Optional[LabPdfInput] = None
    # Additional health metrics that can be passed directly (for backward compatibility)
    age: Optional[int] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    sleep_hours_per_night: Optional[float] = None
    movement_days_per_week: Optional[int] = None
    work_activity_level: Optional[str] = None
    stress_level_1_to_10: Optional[int] = None


class ApiOutput(BaseModel):
    """Output model for the API response."""
    response: str
    intervention_name: Optional[str] = None
    topOpportunityBiomarker: Optional[str] = None
    potentialBonusYears: Optional[float] = None
    challenge: Optional[dict] = None


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
async def execute_graph(request: ApiInput):
    """
    Execute the LangGraph workflow.
    
    This endpoint runs the complete graph (suggestion → critic) and returns
    the final response and intervention name based on user input, messages, and PDF content.
    
    Args:
        request: ApiInput containing userInput, messages, pdf, and health data
        
    Returns:
        ApiResponse with output containing response text and intervention_name (if approved)
        
    Raises:
        HTTPException: If graph is not initialized or execution fails
    """
    if graph_app is None:
        raise HTTPException(
            status_code=503,
            detail="Graph not initialized. Please wait for startup to complete."
        )
    
    try:
        # Initialize blood data dictionary
        blood_data_dict: Dict[str, Any] = {}
        
        # Handle lab_pdf parsing if provided
        if request.lab_pdf:
            try:
                # Instantiate the PDF parser
                extractor = NetMindLabExtractor()
                
                # Extract structured data from base64 PDF
                lab_results = extractor.extract_from_base64(
                    base64_string=request.lab_pdf.base64,
                    filename=request.lab_pdf.filename
                )
                
                # Extract biomarkers from the tests array
                if "tests" in lab_results and isinstance(lab_results["tests"], list):
                    for test in lab_results["tests"]:
                        test_name = test.get("name", "").lower().replace(" ", "_")
                        test_result = test.get("result")
                        if test_name and test_result is not None:
                            blood_data_dict[test_name] = test_result
                            
            except Exception as e:
                print(f"Warning: Failed to parse lab PDF: {str(e)}")
                # Continue execution even if PDF parsing fails
        
        # Merge with provided bloodData if any
        if request.bloodData:
            blood_data_dict.update(request.bloodData.to_dict())
        
        # Build userProfile from all available sources
        user_profile_dict: Dict[str, Any] = {}
        
        # Start with existing userProfile if provided
        if request.userProfile:
            user_profile_dict = request.userProfile.model_dump(exclude_none=True)
        
        # Map sex to gender if provided (sex takes precedence)
        if request.sex:
            user_profile_dict["gender"] = request.sex
        
        # Add direct health metrics from top-level fields if provided
        direct_fields = {
            "age": request.age,
            "height_cm": request.height_cm,
            "weight_kg": request.weight_kg,
            "sleep_hours_per_night": request.sleep_hours_per_night,
            "movement_days_per_week": request.movement_days_per_week,
            "work_activity_level": request.work_activity_level,
            "stress_level_1_to_10": request.stress_level_1_to_10,
        }
        
        # Only add non-None values
        for key, value in direct_fields.items():
            if value is not None:
                user_profile_dict[key] = value
        
        # Map ApiInput to GraphState
        initial_state: GraphState = {
            "userInput": request.userInput,
            "messages": [msg.model_dump() for msg in request.pastMessages],
            "pdf": request.pdf.model_dump()
        }
        
        # Add userProfile if we have any data
        if user_profile_dict:
            initial_state["userProfile"] = user_profile_dict
        
        # Add bloodData if we have any data
        if blood_data_dict:
            initial_state["bloodData"] = blood_data_dict
        
        # Execute the graph
        final_state = graph_app.invoke(initial_state)
        
        # Extract suggestion and approval status
        suggestion_dict = final_state.get("suggestion")
        final_suggestion_approved = final_state.get("finalSuggestion", False)
        critique = final_state.get("critique", "")
        
        # Extract longevity opportunity data
        top_opportunity_biomarker = final_state.get("topOpportunityBiomarker")
        potential_bonus_years = final_state.get("potentialBonusYears")
        challenge = final_state.get("challenge", {})
        intervention_name = challenge.get("intervention_name") if challenge else None
        
        # Build response based on approval status
        if final_suggestion_approved and suggestion_dict and isinstance(suggestion_dict, dict):
            # Approved: Return suggestion text and intervention name
            response_text = suggestion_dict.get("suggestion", "No suggestion generated")
            challenge = suggestion_dict.get("challenge", {})
            intervention_name = challenge.get("intervention_name") if challenge else None
            
            response = ApiResponse(
                output=ApiOutput(
                    response=response_text,
                    intervention_name=intervention_name,
                    topOpportunityBiomarker=top_opportunity_biomarker,
                    potentialBonusYears=potential_bonus_years,
                    challenge=challenge
                )
            )
        else:
            # Rejected: Return critic's rejection message
            response_text = critique or "Suggestion was not approved for safety reasons."
            
            response = ApiResponse(
                output=ApiOutput(
                    response=response_text,
                    intervention_name=None,
                    topOpportunityBiomarker=top_opportunity_biomarker,
                    potentialBonusYears=potential_bonus_years
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
    import os
    
    # SSL certificate paths
    ssl_certfile = os.getenv("SSL_CERTFILE", "ssl/cert.pem")
    ssl_keyfile = os.getenv("SSL_KEYFILE", "ssl/key.pem")
    
    # Check if SSL certificates exist
    use_https = os.path.exists(ssl_certfile) and os.path.exists(ssl_keyfile)
    
    if use_https:
        print(f"Starting server with HTTPS on port 8443")
        print(f"Certificate: {ssl_certfile}")
        print(f"Key: {ssl_keyfile}")
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=int(os.getenv("PORT", 8443)),
            ssl_certfile=ssl_certfile,
            ssl_keyfile=ssl_keyfile
        )
    else:
        print("SSL certificates not found. Starting server with HTTP on port 8000")
        print("To enable HTTPS, run: bash generate_ssl_cert.sh")
        uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

