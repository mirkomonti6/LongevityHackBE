"""
Suggestion node for the LangGraph application.

This node generates suggestions based on user input, conversation history, and PDF content.
"""

from .state import GraphState
from .utils import extract_pdf_content


def suggestion_node(state: GraphState) -> GraphState:
    """
    Node that generates a suggestion.
    
    This node takes the current state and generates a suggestion based on:
    - User input
    - Past conversation messages
    - Extracted PDF content
    
    Args:
        state: The current graph state
        
    Returns:
        Updated state with 'suggestion' and 'finalSuggestion' fields populated
    """
    # Extract input data from state
    user_input = state.get("userInput", "")
    messages = state.get("messages", [])
    pdf = state.get("pdf", {})
    
    # Extract PDF content
    pdf_content = extract_pdf_content(pdf) if pdf else ""
    
    # Build context from messages
    message_context = ""
    if messages:
        message_context = "\n".join([
            f"{msg.get('role', 'unknown')}: {msg.get('content', '')}"
            for msg in messages[-3:]  # Use last 3 messages for context
        ])
    
    # Generate suggestion based on inputs
    # In a real implementation, this would use an LLM
    suggestion_parts = []
    
    if user_input:
        suggestion_parts.append(f"Based on your input: '{user_input}'")
    
    if message_context:
        suggestion_parts.append(f"Considering the conversation context")
    
    if pdf_content:
        suggestion_parts.append(f"and the document content: {pdf_content}")
    
    if suggestion_parts:
        suggestion = f"{' '.join(suggestion_parts)}, I suggest focusing on personalized health optimization strategies that integrate the latest research findings."
    else:
        suggestion = "Consider implementing a feature that improves user engagement through personalized recommendations."
    
    # Return updated state
    return {
        "suggestion": suggestion,
        "finalSuggestion": suggestion  # Both fields have the same value
    }

