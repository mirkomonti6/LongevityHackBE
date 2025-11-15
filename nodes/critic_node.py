"""
Biohacker Critic Node with LLM

This node uses an LLM to intelligently evaluate biohacking suggestions for
safety, scientific accuracy, feasibility, and personalization.
"""

import os
import json
from openai import OpenAI
from .state import GraphState

NETMIND_API_KEY = "6ecc3bdc2980400a8786fd512ad487e7"

def critic_node(state: GraphState) -> GraphState:
    """
    LLM-powered critic that evaluates biohacking suggestions.
    
    This node:
    1. Reviews the suggestion for medical safety
    2. Validates scientific accuracy
    3. Checks for contraindications based on user profile
    4. Assesses feasibility and personalization
    5. Approves or rejects with detailed reasoning
    
    Args:
        state: The current graph state with suggestion and user data
        
    Returns:
        Updated state with critique, response, and finalSuggestion (boolean)
    """
    # Extract data from state
    suggestion = state.get("suggestion", "")
    user_profile = state.get("userProfile", {})
    blood_data = state.get("bloodData", {})
    selected_intervention = state.get("selectedIntervention", {})
    longevity_score = state.get("longevityScore", {})
    
    # Handle missing suggestion
    if not suggestion or "Error:" in suggestion:
        return {
            "critique": "Unable to evaluate: No valid suggestion provided.",
            "response": suggestion if suggestion else "No suggestion generated.",
            "finalSuggestion": False
        }
    
    # Use LLM to evaluate the suggestion
    try:
        client = OpenAI(
            base_url="https://api.netmind.ai/inference-api/openai/v1",
            api_key=NETMIND_API_KEY
        )
        
        # Prepare context for evaluation
        user_context = {
            "age": user_profile.get("age", "unknown"),
            "gender": user_profile.get("gender", "unknown"),
            "job": user_profile.get("job", "unknown"),
            "longevity_score": longevity_score.get("overall_score", "unknown") if longevity_score else "unknown"
        }
        
        intervention_context = {
            "name": selected_intervention.get("name", "unknown"),
            "category": selected_intervention.get("category", "unknown"),
            "contraindications": selected_intervention.get("contraindications", []),
            "target_markers": selected_intervention.get("target_biomarkers", [])
        } if selected_intervention else {}
        
        # Create evaluation prompt
        prompt = f"""You are a medical safety reviewer evaluating a biohacking health recommendation. Your role is to ensure the suggestion is safe, scientifically sound, and appropriate for the specific user.

USER PROFILE:
{json.dumps(user_context, indent=2)}

BLOOD DATA SUMMARY:
{json.dumps(list(blood_data.keys()) if blood_data else [], indent=2)}

RECOMMENDED INTERVENTION:
{json.dumps(intervention_context, indent=2)}

SUGGESTION TO EVALUATE:
{suggestion}

EVALUATION CRITERIA:
1. SAFETY: Are there any contraindications based on the user's age, gender, or health data?
2. SCIENTIFIC VALIDITY: Is the recommendation backed by credible research?
3. APPROPRIATENESS: Is this intervention suitable for the user's specific situation?
4. FEASIBILITY: Is the recommendation practical and achievable?
5. DISCLAIMERS: Does it need medical disclaimers or professional consultation warnings?

DECISION RULES:
- APPROVE if: Safe, evidence-based, appropriate, and includes necessary disclaimers
- REJECT if: Contraindicated, unsafe for the user, or lacks scientific basis
- If age >70 or <18, exercise extra caution
- Always require medical consultation for prescription-level interventions

TASK:
Provide a thorough evaluation and decide whether to APPROVE or REJECT the suggestion.

Respond ONLY with valid JSON in this exact format:
{{
    "decision": "APPROVE" or "REJECT",
    "reasoning": "2-3 sentences explaining your decision",
    "safety_concerns": ["list any safety concerns or empty array"],
    "recommendations": ["any modifications or additional advice"],
    "requires_medical_consultation": true or false
}}"""

        response = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3.2-Exp",
            messages=[
                {"role": "system", "content": "You are a medical safety expert who reviews health recommendations for safety and appropriateness. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Lower temperature for more consistent safety evaluation
            max_tokens=500
        )
        
        # Parse LLM response
        llm_output = response.choices[0].message.content.strip()
        
        # Extract JSON from response (handle potential markdown code blocks)
        if "```json" in llm_output:
            llm_output = llm_output.split("```json")[1].split("```")[0].strip()
        elif "```" in llm_output:
            llm_output = llm_output.split("```")[1].split("```")[0].strip()
        
        evaluation = json.loads(llm_output)
        
        # Extract evaluation results
        decision = evaluation.get("decision", "REJECT").upper()
        reasoning = evaluation.get("reasoning", "Unable to determine safety.")
        safety_concerns = evaluation.get("safety_concerns", [])
        recommendations = evaluation.get("recommendations", [])
        requires_medical = evaluation.get("requires_medical_consultation", False)
        
        # Determine approval
        final_suggestion_approved = (decision == "APPROVE")
        
        # Build critique message
        critique_parts = [f"**Safety Review:** {reasoning}"]
        
        if safety_concerns:
            critique_parts.append(f"\n**Safety Concerns:** {', '.join(safety_concerns)}")
        
        if recommendations:
            critique_parts.append(f"\n**Additional Recommendations:** {', '.join(recommendations)}")
        
        if requires_medical:
            critique_parts.append("\n**⚠️ Important:** Please consult with a healthcare professional before starting this intervention.")
        
        if final_suggestion_approved:
            critique_parts.append(f"\n\n✅ **Status:** APPROVED - This recommendation is safe and appropriate for your profile.")
        else:
            critique_parts.append(f"\n\n❌ **Status:** NOT APPROVED - Please consult a healthcare provider for personalized advice.")
        
        critique = "\n".join(critique_parts)
        
        # Build final response (combines suggestion + critique if approved)
        if final_suggestion_approved:
            # Add medical disclaimer
            disclaimer = "\n\n---\n*Disclaimer: This information is for educational purposes only and is not medical advice. Consult with a qualified healthcare provider before making any changes to your health regimen.*"
            final_response = f"{suggestion}\n\n{critique}{disclaimer}"
        else:
            # If rejected, return only the critique
            final_response = f"{critique}\n\n*Original suggestion was not approved for safety reasons.*"
        
        return {
            "critique": critique,
            "response": final_response,
            "finalSuggestion": final_suggestion_approved
        }
        
    except Exception as e:
        # Fallback if LLM fails - default to cautious approval with warnings
        print(f"LLM Error in critic_node: {str(e)}")
        
        # Basic safety check - reject if user is very young or very old without human review
        age = user_profile.get("age", 30)
        if age < 18 or age > 75:
            fallback_critique = f"⚠️ Due to your age ({age}), this recommendation requires professional medical review before implementation. Please consult with a healthcare provider."
            fallback_approved = False
            fallback_response = f"{fallback_critique}\n\n*Automated safety check: Age-based caution triggered.*"
        else:
            # Cautious approval with disclaimers
            fallback_critique = "✅ Preliminary safety check passed. However, please consult with a healthcare professional before starting any new health intervention, especially if you have existing medical conditions or take medications."
            fallback_approved = True
            disclaimer = "\n\n*Disclaimer: This information is for educational purposes only and is not medical advice. Consult with a qualified healthcare provider before making any changes to your health regimen.*"
            fallback_response = f"{suggestion}\n\n{fallback_critique}{disclaimer}"
        
        return {
            "critique": fallback_critique,
            "response": fallback_response,
            "finalSuggestion": fallback_approved
        }

