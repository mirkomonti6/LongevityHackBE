"""
Interview node for the LangGraph application.

This node conducts an interview to gather more information from the user.
"""

from .state import GraphState


def interviewNode(state: GraphState) -> GraphState:
    """
    Node that conducts an interview to gather more information.
    
    This node analyzes the user input and conversation history to determine
    what additional information is needed and formulates follow-up questions.
    
    Args:
        state: The current graph state
        
    Returns:
        Updated state with interview questions or additional context
    """
    # Extract input data from state
    user_input = state.get("userInput", "")
    messages = state.get("messages", [])
    
    # Analyze what information might be missing
    # In a real implementation, this would use an LLM to determine follow-up questions
    interview_notes = []
    
    if user_input:
        # Check if we need more context about the user's goals
        if "longevity" in user_input.lower() or "health" in user_input.lower():
            interview_notes.append("Consider asking about specific health goals, current lifestyle, and any existing conditions.")
        
        # Check if we need more specific information
        if len(user_input.split()) < 5:
            interview_notes.append("User input is brief - may need clarification on specific areas of interest.")
    
    # Check conversation depth
    if len(messages) < 2:
        interview_notes.append("Limited conversation history - consider building rapport and understanding context.")
    
    # Generate interview summary
    if interview_notes:
        interview_summary = "Interview Analysis: " + " ".join(interview_notes)
    else:
        interview_summary = "Interview Analysis: Sufficient information provided. Ready to proceed with recommendations."
    
    # Return updated state
    # In a real system, this might add follow-up questions to the messages or set a flag
    return {
        "interviewSummary": interview_summary
    }

