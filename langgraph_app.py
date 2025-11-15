"""
LangGraph application with suggestion and critic nodes.

This module defines the graph structure and orchestrates the workflow.
All node implementations are in the nodes/ package.
"""

from langgraph.graph import StateGraph, END
from nodes import (
    GraphState,
    suggestion_node,
    critic_node,
    interviewNode,
    guardrailsNode,
)


def should_retry(state: GraphState) -> str:
    """
    Decide if we should retry suggestion or end based on critic's decision.
    
    Args:
        state: Current graph state with finalSuggestion and retryCount
        
    Returns:
        "retry" if rejected and retries < 2, otherwise "end"
    """
    final_approved = state.get("finalSuggestion", False)
    retry_count = state.get("retryCount", 0)
    
    if final_approved:
        # Approved - end immediately
        return "end"
    elif retry_count < 2:
        # Rejected but still have retries left (max 2 retries = 3 total attempts)
        return "retry"
    else:
        # Max retries reached - end with rejection
        return "end"


def create_graph():
    """
    Creates and compiles the LangGraph with all nodes.
    
    Returns:
        Compiled LangGraph ready for execution
    """
    # Create a new StateGraph with GraphState as the state schema
    workflow = StateGraph(GraphState)
    
    # Add nodes to the graph
    workflow.add_node("interviewNode", interviewNode) #MOCK
    workflow.add_node("guardrailsNode", guardrailsNode) #MOCK
    workflow.add_node("suggestion", suggestion_node)
    workflow.add_node("critic", critic_node)
    
    # Set the entry point
    workflow.set_entry_point("interviewNode")
    
    # Define the edges in sequence: interviewNode → guardrailsNode → suggestion → critic
    workflow.add_edge("interviewNode", "guardrailsNode")
    workflow.add_edge("guardrailsNode", "suggestion")
    workflow.add_edge("suggestion", "critic")
    
    # Add conditional routing from critic: retry suggestion if rejected (max 2 retries), otherwise end
    workflow.add_conditional_edges(
        "critic",
        should_retry,
        {
            "retry": "suggestion",  # Loop back to suggestion for retry
            "end": END              # End the graph
        }
    )
    
    # Compile the graph
    app = workflow.compile()
    
    return app


def main():
    """
    Main execution function for the LangGraph application.
    
    Creates the graph, initializes it with an empty state,
    executes it, and displays the results.
    """
    print("Creating LangGraph...")
    app = create_graph()
    
    print("Initializing graph with empty state...")
    initial_state: GraphState = {}
    
    print("Executing graph...")
    print("-" * 60)
    
    # Execute the graph
    final_state = app.invoke(initial_state)
    
    print("-" * 60)
    print("\nExecution complete!\n")
    print("Results:")
    print("-" * 60)
    
    if "suggestion" in final_state:
        print(f"Suggestion: {final_state['suggestion']}\n")
    else:
        print("Suggestion: (not generated)\n")
    
    if "critique" in final_state:
        print(f"Critique: {final_state['critique']}\n")
    else:
        print("Critique: (not generated)\n")
    
    print("-" * 60)
    
    return final_state


if __name__ == "__main__":
    main()