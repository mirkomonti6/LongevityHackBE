"""
Biohacker Suggestion Node

This node analyzes user health data and generates personalized biohacking recommendations
using an LLM to intelligently select interventions and create engagement challenges.
"""

import os
import json
from typing import Dict, List, Any
from openai import OpenAI
from .state import GraphState
from .biohacker_db import get_all_interventions, get_interventions_by_biomarker
from .longevity_calculator import calculate_longevity_score, identify_problematic_biomarkers

NETMIND_API_KEY = "6ecc3bdc2980400a8786fd512ad487e7"

def generate_10_day_challenge(intervention: Dict[str, Any], user_profile: Dict) -> Dict:
    """
    Generate a simple 10-day challenge based on the intervention.
    
    Args:
        intervention: The selected intervention from the database
        user_profile: User demographic information
        
    Returns:
        Dict with challenge details
    """
    category = intervention['category']
    name = intervention['name']
    
    # Simple daily tasks based on intervention type
    if category == 'supplements':
        daily_tasks = [f"Take {intervention['dosage']}" for _ in range(10)]
    elif category == 'exercise':
        if 'walking' in name.lower():
            daily_tasks = [
                "Walk 5,000 steps today",
                "Walk 6,000 steps today",
                "Walk 7,000 steps today",
                "Walk 8,000 steps today",
                "Walk 8,000 steps today",
                "Walk 9,000 steps today",
                "Walk 10,000 steps today",
                "Walk 10,000 steps today",
                "Walk 10,000 steps + 5 min stretching",
                "Walk 10,000 steps + reflect on progress"
            ]
        elif 'hiit' in name.lower() or 'interval' in name.lower():
            daily_tasks = [
                "Day 1: 15 min HIIT session",
                "Day 2: Rest/light walking",
                "Day 3: 20 min HIIT session",
                "Day 4: Rest/light activity",
                "Day 5: 20 min HIIT session",
                "Day 6: Rest/stretching",
                "Day 7: 25 min HIIT session",
                "Day 8: Rest/light activity",
                "Day 9: 25 min HIIT session",
                "Day 10: Rest and assess progress"
            ]
        else:
            daily_tasks = [f"Complete {intervention['dosage']}" for _ in range(10)]
    elif category == 'diet':
        daily_tasks = [
            f"Day {i+1}: Follow {name} - {intervention['dosage']}" for i in range(10)
        ]
    elif category == 'sleep':
        daily_tasks = [f"Sleep {intervention['dosage']}" for _ in range(10)]
    elif category == 'lifestyle':
        daily_tasks = [f"{intervention['dosage']}" for _ in range(10)]
    else:
        daily_tasks = [f"Follow {name} protocol - Day {i+1}" for i in range(10)]
    
    return {
        "intervention_name": name,
        "duration_days": 10,
        "daily_tasks": daily_tasks,
        "success_criteria": intervention.get('expected_improvement', 'Complete all 10 days'),
        "category": category
    }


def format_scientific_references(intervention: Dict[str, Any]) -> List[Dict]:
    """
    Format scientific references for the response.
    
    Args:
        intervention: The intervention with references
        
    Returns:
        List of formatted reference dicts
    """
    return intervention.get('scientific_references', [])


def suggestion_node(state: GraphState) -> GraphState:
    """
    Biohacker agent that analyzes health data and generates personalized recommendations.
    
    This node:
    1. Calculates longevity score from blood data
    2. Identifies problematic biomarkers
    3. Queries intervention database
    4. Uses LLM to select best intervention and generate personalized message
    5. Creates 10-day challenge
    
    Args:
        state: The current graph state with userProfile and bloodData
        
    Returns:
        Updated state with suggestion, challenge, references, and longevity score
    """
    # Extract data from state
    user_profile = state.get("userProfile", {})
    blood_data = state.get("bloodData", {})
    user_input = state.get("userInput", "")
    messages = state.get("messages", [])
    
    # Validate required data
    if not user_profile or not blood_data:
        return {
            "suggestion": "Error: User profile and blood data are required for biohacker recommendations.",
            "longevityScore": None
        }
    
    # Extract user demographics
    age = user_profile.get("age", 30)
    gender = user_profile.get("gender", "unknown")
    job = user_profile.get("job", "unknown")
    
    # Calculate longevity score
    longevity_result = calculate_longevity_score(blood_data, age, gender)
    
    # Identify problematic biomarkers
    problematic = longevity_result['problematic_markers']
    
    # If no problematic markers, return general wellness message
    if not problematic:
        return {
            "suggestion": f"Congratulations! Your longevity score is {longevity_result['overall_score']} ({longevity_result['grade']}). All biomarkers are in excellent ranges. Continue your current health practices!",
            "longevityScore": longevity_result,
            "problematicBiomarkers": [],
            "challenge": None
        }
    
    # Get candidate interventions for top problematic biomarkers
    candidate_interventions = []
    processed_ids = set()
    
    for biomarker_name, value, score, priority in problematic[:3]:  # Top 3 problematic
        interventions = get_interventions_by_biomarker(biomarker_name)
        for intervention in interventions[:3]:  # Top 3 interventions per biomarker
            if intervention['id'] not in processed_ids:
                candidate_interventions.append(intervention)
                processed_ids.add(intervention['id'])
    
    # If no interventions found, return general message
    if not candidate_interventions:
        return {
            "suggestion": f"Your longevity score is {longevity_result['overall_score']} ({longevity_result['grade']}). We're analyzing the best interventions for your specific biomarkers.",
            "longevityScore": longevity_result,
            "problematicBiomarkers": problematic
        }
    
    # Use LLM to select best intervention and generate personalized message
    try:
        client = OpenAI(
            base_url="https://api.netmind.ai/inference-api/openai/v1",
            api_key=NETMIND_API_KEY
        )
        
        # Prepare context for LLM
        interventions_summary = []
        for i, intervention in enumerate(candidate_interventions[:5]):  # Limit to top 5
            interventions_summary.append({
                "id": intervention['id'],
                "name": intervention['name'],
                "category": intervention['category'],
                "targets": intervention['target_biomarkers'],
                "description": intervention['description'],
                "dosage": intervention['dosage'],
                "expected_improvement": intervention['expected_improvement'],
                "contraindications": intervention['contraindications'],
                "reference": intervention['scientific_references'][0] if intervention['scientific_references'] else {}
            })
        
        # Build conversation context
        conversation_context = ""
        if messages:
            recent_messages = messages[-3:]
            conversation_context = "\n".join([
                f"{msg.get('role', 'user')}: {msg.get('content', '')}"
                for msg in recent_messages
            ])
        
        # Create LLM prompt
        prompt = f"""You are a biohacking health optimization specialist. Analyze the user's health data and select the BEST intervention from the options provided.

USER PROFILE:
- Age: {age}
- Gender: {gender}
- Occupation: {job}

LONGEVITY SCORE: {longevity_result['overall_score']}/100 (Grade: {longevity_result['grade']})

PROBLEMATIC BIOMARKERS (priority order):
{chr(10).join([f"- {name}: {value} (score: {score:.1f}/100, optimal range)" for name, value, score, priority in problematic[:5]])}

AVAILABLE INTERVENTIONS:
{json.dumps(interventions_summary, indent=2)}

CONVERSATION CONTEXT:
{conversation_context if conversation_context else "No previous conversation"}

USER'S CURRENT CONCERN:
{user_input if user_input else "General health optimization"}

TASK:
1. Select the SINGLE BEST intervention considering:
   - Which biomarker issue is most critical (highest priority)
   - User's age, gender, and lifestyle (job)
   - Feasibility and ease of implementation
   - Scientific evidence strength
   - Any contraindications

2. Generate a personalized, motivating message (200-300 words) that:
   - Addresses the user warmly and personally
   - Explains their longevity score and what it means
   - Highlights the most important biomarker to improve
   - Recommends the selected intervention with confidence
   - Cites the scientific research supporting it (author, year, key finding)
   - Explains expected benefits and timeline
   - Encourages them with a positive, actionable tone

Respond ONLY with valid JSON in this exact format:
{{
    "selected_intervention_id": "the-intervention-id",
    "personalized_message": "Your warm, scientific, motivating message here..."
}}"""

        response = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3.2-Exp",
            messages=[
                {"role": "system", "content": "You are a health optimization specialist who provides evidence-based, personalized biohacking recommendations. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        # Parse LLM response
        llm_output = response.choices[0].message.content.strip()
        
        # Extract JSON from response (handle potential markdown code blocks)
        if "```json" in llm_output:
            llm_output = llm_output.split("```json")[1].split("```")[0].strip()
        elif "```" in llm_output:
            llm_output = llm_output.split("```")[1].split("```")[0].strip()
        
        llm_result = json.loads(llm_output)
        
        selected_id = llm_result.get("selected_intervention_id")
        personalized_message = llm_result.get("personalized_message")
        
        # Find the selected intervention
        selected_intervention = None
        for intervention in candidate_interventions:
            if intervention['id'] == selected_id:
                selected_intervention = intervention
                break
        
        if not selected_intervention:
            selected_intervention = candidate_interventions[0]  # Fallback to first
        
        # Generate 10-day challenge
        challenge = generate_10_day_challenge(selected_intervention, user_profile)
        
        # Format scientific references
        references = format_scientific_references(selected_intervention)
        
        # Add challenge info to message
        full_message = f"{personalized_message}\n\n🎯 **Your 10-Day Challenge:**\nI've created a simple 10-day routine to help you get started with {selected_intervention['name']}. Complete each day's task and track your progress!"
        
        return {
            "suggestion": full_message,
            "longevityScore": longevity_result,
            "problematicBiomarkers": problematic,
            "selectedIntervention": selected_intervention,
            "challenge": challenge,
            "scientificReferences": references
        }
        
    except Exception as e:
        # Fallback if LLM fails
        print(f"LLM Error in suggestion_node: {str(e)}")
        fallback_intervention = candidate_interventions[0]
        challenge = generate_10_day_challenge(fallback_intervention, user_profile)
        references = format_scientific_references(fallback_intervention)
        
        top_biomarker = problematic[0][0]
        
        fallback_message = f"""Your longevity score is {longevity_result['overall_score']}/100 (Grade {longevity_result['grade']}).

Based on your blood work, your {top_biomarker} needs attention. I recommend: **{fallback_intervention['name']}**

{fallback_intervention['description']}

**Protocol:** {fallback_intervention['dosage']}

**Expected Results:** {fallback_intervention['expected_improvement']}

**Scientific Backing:** {references[0]['study'] if references else 'Multiple peer-reviewed studies'} showed significant improvements in {top_biomarker}.

Let's optimize your health together! 🚀"""
        
        return {
            "suggestion": fallback_message,
            "longevityScore": longevity_result,
            "problematicBiomarkers": problematic,
            "selectedIntervention": fallback_intervention,
            "challenge": challenge,
            "scientificReferences": references
        }

