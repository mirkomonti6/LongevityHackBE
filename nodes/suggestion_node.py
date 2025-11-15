"""
Biohacker Suggestion Node

This node analyzes user health data and generates personalized biohacking recommendations
using an LLM to intelligently select interventions and create engagement challenges.
"""

import os
import json
import logging
from typing import Dict, List, Any
from openai import OpenAI
from .state import GraphState
from .biohacker_db import get_all_interventions, get_interventions_by_biomarker
from .longevity_calculator import identify_problematic_biomarkers
from .smartwatch_db import (
    get_mock_smartwatch_data, 
    assess_fitness_level, 
    identify_activity_gaps,
    get_smartwatch_insights_summary,
    match_interventions_to_activity_gaps
)
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from db.biomarkers.longevity_score import LongevityScoreCalculator, BiomarkerMeasurement

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

NETMIND_API_KEY = "6ecc3bdc2980400a8786fd512ad487e7"

def format_scientific_references(intervention: Dict[str, Any]) -> List[Dict]:
    """
    Format scientific references for the response.
    
    Args:
        intervention: The intervention with references
        
    Returns:
        List of formatted reference dicts
    """
    return intervention.get('scientific_references', [])


def map_blood_data_to_measurements(blood_data: Dict[str, float], user_profile: Dict[str, Any], client: OpenAI) -> List[BiomarkerMeasurement]:
    """
    Use LLM to map blood data to BiomarkerMeasurement objects with inferred units.
    
    Args:
        blood_data: Dictionary of biomarker names to values
        user_profile: User demographic data for context
        client: OpenAI client for LLM calls
        
    Returns:
        List of BiomarkerMeasurement objects
    """
    if not blood_data:
        return []
    
    logger.info(f"Mapping {len(blood_data)} biomarkers to database format...")
    
    # Prepare prompt for LLM
    biomarkers_list = [{"name": k, "value": v} for k, v in blood_data.items()]
    
    prompt = f"""You are a medical data specialist. Given a list of biomarker measurements, your task is to:
1. Match each biomarker name to the most likely standard biomarker name used in medical databases
2. Infer the appropriate unit of measurement based on the biomarker type and value range

Common biomarker units:
- Cholesterol, LDL, HDL, Triglycerides: mg/dL or mmol/L
- Glucose: mg/dL or mmol/L
- Hemoglobin: g/dL
- C-reactive protein (CRP): mg/L
- Testosterone: ng/dL or nmol/L
- Vitamin D: ng/mL or nmol/L
- BMI: kg/m^2
- Blood pressure: mmHg
- Heart rate: bpm
- Body fat: %
- HbA1c: %
- Creatinine: mg/dL
- Albumin: g/dL
- White blood cell count: cells/μL or 10^9/L
- Platelets: cells/μL or 10^9/L

User context:
- Age: {user_profile.get('age', 'unknown')}
- Gender: {user_profile.get('gender', 'unknown')}

Input biomarkers:
{json.dumps(biomarkers_list, indent=2)}

For each biomarker, provide:
1. The standardized biomarker name (match to common medical terminology)
2. The value (as provided)
3. The most likely unit based on the value range

Respond ONLY with valid JSON in this format:
{{
    "measurements": [
        {{"name": "standardized_name", "value": numeric_value, "unit": "appropriate_unit"}},
        ...
    ]
}}"""

    try:
        response = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3.2-Exp",
            messages=[
                {"role": "system", "content": "You are a medical data expert who standardizes biomarker measurements. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        llm_output = response.choices[0].message.content.strip()
        
        # Extract JSON from response (handle potential markdown code blocks)
        if "```json" in llm_output:
            llm_output = llm_output.split("```json")[1].split("```")[0].strip()
        elif "```" in llm_output:
            llm_output = llm_output.split("```")[1].split("```")[0].strip()
        
        result = json.loads(llm_output)
        measurements = []
        
        for item in result.get("measurements", []):
            try:
                measurement = BiomarkerMeasurement(
                    name=item["name"],
                    value=float(item["value"]),
                    unit=item["unit"],
                    source="blood_test"
                )
                measurements.append(measurement)
                logger.info(f"  Mapped: {item['name']} = {item['value']} {item['unit']}")
            except (KeyError, ValueError) as e:
                logger.warning(f"  Failed to parse measurement: {item} - {e}")
                continue
        
        logger.info(f"Successfully mapped {len(measurements)} biomarkers")
        return measurements
        
    except Exception as e:
        logger.error(f"Failed to map blood data with LLM: {e}")
        return []


def suggestion_node(state: GraphState) -> GraphState:
    """
    Biohacker agent that analyzes health data and generates personalized recommendations.
    
    This node:
    1. Identifies problematic biomarkers
    2. Queries intervention database
    3. Uses LLM to select best intervention and generate personalized message
    4. Creates 10-day challenge
    
    Args:
        state: The current graph state with userProfile and bloodData
        
    Returns:
        Updated state with suggestion, challenge, and references
    """
    logger.info("=== Suggestion Node Started ===")
    
    # Extract data from state
    user_profile = state.get("userProfile", {})
    blood_data = state.get("bloodData", {})
    user_input = state.get("userInput", "")
    messages = state.get("messages", [])
    
    logger.info(f"User profile: Age={user_profile.get('age')}, Gender={user_profile.get('gender')}, Job={user_profile.get('job')}")
    logger.info(f"Blood data biomarkers: {list(blood_data.keys()) if blood_data else 'None'}")
    
    # Get or generate smartwatch data
    smartwatch_data = state.get("smartwatchData")
    if not smartwatch_data and user_profile:
        logger.info("Generating mock smartwatch data based on user profile")
        smartwatch_data = get_mock_smartwatch_data(user_profile)
    
    # Assess fitness and identify gaps from smartwatch data
    fitness_assessment = None
    activity_gaps = []
    smartwatch_insights = None
    
    if smartwatch_data:
        fitness_assessment = assess_fitness_level(smartwatch_data)
        activity_gaps = identify_activity_gaps(smartwatch_data)
        smartwatch_insights = get_smartwatch_insights_summary(smartwatch_data)
        
        logger.info(f"Smartwatch data: HRV={smartwatch_data.get('hrv')}, VO2 Max={smartwatch_data.get('vo2_max')}, " +
                   f"RHR={smartwatch_data.get('resting_heart_rate')}, Active mins={smartwatch_data.get('active_minutes_per_day')}")
        logger.info(f"Fitness level: {fitness_assessment['fitness_level']} ({fitness_assessment['overall_score']}/100)")
        logger.info(f"Identified {len(activity_gaps)} activity gaps")
    
    # Validate required data
    if not user_profile or not blood_data:
        logger.warning("Missing required data: user_profile or blood_data")
        return {
            "suggestion": "Error: User profile and blood data are required for biohacker recommendations."
        }
    
    # Extract user demographics
    age = user_profile.get("age", 30)
    gender = user_profile.get("gender", "unknown")
    job = user_profile.get("job", "unknown")
    
    # ============================================================================
    # LONGEVITY SCORE CALCULATION
    # ============================================================================
    
    # Initialize OpenAI client for LLM calls (needed for mapping and suggestions)
    client = OpenAI(
        base_url="https://api.netmind.ai/inference-api/openai/v1",
        api_key=NETMIND_API_KEY
    )
    
    # Calculate longevity score and identify top opportunity
    top_opportunity = None
    longevity_overall = None
    
    try:
        # Get the database path relative to this file
        current_dir = os.path.dirname(__file__)
        db_path = os.path.join(current_dir, "..", "db", "biomarkers", "data", "biomarkers_database.json")
        
        logger.info("=== Longevity Score Calculation Started ===")
        
        # Initialize calculator
        calculator = LongevityScoreCalculator(database_path=db_path)
        
        # Map blood data to measurements using LLM
        measurements = map_blood_data_to_measurements(blood_data, user_profile, client)
        
        if measurements:
            # Calculate impacts for each biomarker
            impacts = []
            for measurement in measurements:
                impact = calculator.calculate_biomarker_impact(measurement, age)
                if impact:
                    impacts.append(impact)
            
            logger.info(f"Calculated impacts for {len(impacts)} biomarkers")
            
            # Calculate overall longevity score
            if impacts:
                longevity_overall = calculator.calculate_overall_score(impacts, age)
                top_opportunity = longevity_overall.get("top_opportunity")
                
                # Log overall score
                logger.info("="*60)
                logger.info("🌟 LONGEVITY SCORE RESULTS 🌟")
                logger.info("="*60)
                logger.info(f"Overall Score: {longevity_overall['overall_score']}/100")
                logger.info(f"Score Level: {longevity_overall['score_level']}")
                logger.info(f"Optimized Biomarkers: {longevity_overall['optimized_count']}")
                logger.info(f"Improvement Opportunities: {longevity_overall['opportunities_count']}")
                logger.info(f"Total Bonus Years Available: +{longevity_overall['total_bonus_years']} years")
                
                # Log top opportunity
                if top_opportunity:
                    logger.info("="*60)
                    logger.info("🚀 #1 OPPORTUNITY TO LEVEL UP 🚀")
                    logger.info("="*60)
                    logger.info(f"Biomarker: {top_opportunity['biomarker']}")
                    logger.info(f"Current Score: {top_opportunity['current_score']}/100")
                    logger.info(f"Your Value: {top_opportunity['your_value']}")
                    logger.info(f"Target Range: {top_opportunity['target']}")
                    logger.info(f"💎 POTENTIAL GAIN: +{top_opportunity['bonus_years']} BONUS YEARS")
                    logger.info(f"This is your biggest opportunity! Optimizing this biomarker")
                    logger.info(f"alone could add {top_opportunity['bonus_years']} years to your life!")
                    logger.info("="*60)
                else:
                    logger.info("🎉 All biomarkers are optimal! No improvement opportunities.")
                    logger.info("="*60)
        else:
            logger.warning("No measurements could be mapped from blood data")
            
    except FileNotFoundError:
        logger.error(f"Biomarkers database not found at path: {db_path}")
    except Exception as e:
        logger.error(f"Error during longevity score calculation: {e}")
    
    logger.info("=== Longevity Score Calculation Completed ===\n")
    
    # ============================================================================
    # END LONGEVITY SCORE CALCULATION
    # ============================================================================
    
    # Identify problematic biomarkers
    problematic = identify_problematic_biomarkers(blood_data, threshold=80)
    logger.info(f"Identified {len(problematic)} problematic biomarkers")
    
    # If no problematic markers, return general wellness message
    if not problematic:
        logger.info("No problematic biomarkers found - returning wellness message")
        return {
            "suggestion": "🎉 Wow! Your biomarkers are looking amazing! 💪 Everything's in the sweet spot! Keep doing what you're doing - you're absolutely crushing it! 🌟",
            "problematicBiomarkers": [],
            "challenge": None
        }
    
    # Get candidate interventions for top problematic biomarkers
    candidate_interventions = []
    processed_ids = set()
    
    logger.info(f"Searching interventions for top 3 problematic biomarkers: {[b[0] for b in problematic[:3]]}")
    
    for biomarker_name, value, score, priority in problematic[:3]:  # Top 3 problematic
        interventions = get_interventions_by_biomarker(biomarker_name)
        for intervention in interventions[:3]:  # Top 3 interventions per biomarker
            if intervention['id'] not in processed_ids:
                candidate_interventions.append(intervention)
                processed_ids.add(intervention['id'])
    
    logger.info(f"Found {len(candidate_interventions)} candidate interventions")
    
    # If no interventions found, return general message
    if not candidate_interventions:
        logger.warning("No interventions found for problematic biomarkers")
        return {
            "suggestion": "We're analyzing the best interventions for your specific biomarkers.",
            "problematicBiomarkers": problematic
        }
    
    # Use LLM to select best intervention and generate personalized message
    logger.info("Calling LLM to select best intervention...")
    # Note: client already initialized earlier for longevity score calculation
    
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
    
    logger.info(f"Presenting {len(interventions_summary)} interventions to LLM")
    
    # Build conversation context
    conversation_context = ""
    if messages:
        recent_messages = messages[-3:]
        conversation_context = "\n".join([
            f"{msg.get('role', 'user')}: {msg.get('content', '')}"
            for msg in recent_messages
        ])
    
    # Build smartwatch context for LLM
    smartwatch_context = ""
    if smartwatch_data and fitness_assessment:
        gaps_summary = ""
        if activity_gaps:
            top_gaps = activity_gaps[:3]
            gaps_summary = "\n".join([
                f"- {gap['metric']}: {gap['value']} (target: {gap['target']}) - {gap['severity']} priority"
                for gap in top_gaps
            ])
        
        smartwatch_context = f"""
SMARTWATCH DATA (Recent Activity & Recovery):
- Fitness Level: {fitness_assessment['fitness_level'].title()} ({fitness_assessment['overall_score']:.1f}/100)
- VO2 Max: {smartwatch_data['vo2_max']} ml/kg/min (cardiovascular fitness indicator)
- HRV: {smartwatch_data['hrv']} ms (recovery & stress indicator)
- Resting Heart Rate: {smartwatch_data['resting_heart_rate']} bpm
- Daily Active Minutes: {smartwatch_data['active_minutes_per_day']} min (target: 60-150 min)
- Daily Steps: {smartwatch_data['daily_steps_average']} steps

Activity/Recovery Gaps Identified:
{gaps_summary if gaps_summary else "No major gaps - solid baseline!"}
"""
    
    # Build longevity score context
    longevity_context = ""
    if top_opportunity:
        longevity_context = f"""
🎯 TOP LONGEVITY OPPORTUNITY (Backed by Science):
- Biomarker: {top_opportunity['biomarker']}
- Current Score: {top_opportunity['current_score']}/100
- Your Value: {top_opportunity['your_value']}
- Target Range: {top_opportunity['target']}
- 💎 POTENTIAL GAIN: +{top_opportunity['bonus_years']} BONUS YEARS
- This is THE #1 opportunity to maximize lifespan! Optimizing this biomarker alone could add {top_opportunity['bonus_years']} years!
"""
    
    # Create LLM prompt
    prompt = f"""You're a health-savvy friend who gets excited about helping people optimize their wellbeing! 😊 Analyze the user's health data and pick the BEST intervention from the options.

USER PROFILE:
- Age: {age}
- Gender: {gender}
- Occupation: {job}
{longevity_context}
BIOMARKERS THAT NEED SOME LOVE (priority order):
{chr(10).join([f"- {name}: {value} (score: {score:.1f}/100, optimal range)" for name, value, score, priority in problematic[:5]])}
{smartwatch_context}
AVAILABLE INTERVENTIONS:
{json.dumps(interventions_summary, indent=2)}

CONVERSATION CONTEXT:
{conversation_context if conversation_context else "No previous conversation"}

USER'S CURRENT CONCERN:
{user_input if user_input else "General health optimization"}

YOUR MISSION:
1. Pick the SINGLE BEST intervention considering:
   - **HIGHEST PRIORITY**: The TOP LONGEVITY OPPORTUNITY if provided (focus on the biomarker with the biggest potential bonus years!)
   - Which biomarker needs the most attention (highest priority)
   - Their current fitness level and activity patterns from smartwatch data
   - What fits their age, gender, and lifestyle best
   - What's actually doable and not super complicated
   - The science backing it up
   - Any reasons they shouldn't do it
   - How smartwatch metrics suggest they'll benefit (e.g., low HRV → stress management, low VO2 max → cardio)

2. Write THREE sections:

   A) REASONING (150-200 words): Explain WHY you chose this intervention over others:
      - **IF TOP LONGEVITY OPPORTUNITY IS PROVIDED**: Lead with this! Mention the specific bonus years they could gain (e.g., "Your Cholesterol is your #1 opportunity - optimizing it could add 6 bonus years to your life!")
      - Reference SPECIFIC biomarker values (e.g., "Your testosterone is at 320 ng/dL...")
      - Reference SPECIFIC smartwatch metrics with actual values (e.g., "Your HRV is 42ms, well below the 50-70ms target..." or "You're averaging only 3,500 steps/day...")
      - Connect the dots: explain how BOTH biomarkers AND smartwatch data justify this intervention
      - If suggesting exercise/activity: cite their VO2 max value, active minutes, or step count
      - If suggesting stress management: reference their HRV value and what it indicates
      # - If suggesting sleep optimization: mention their deep sleep and REM hours specifically
      - Explain how age, gender, and occupation influenced your choice
      - Why this is the #1 priority right now
      - Keep it friendly and conversational with emojis!

   B) SUGGESTION (200-300 words): The actual recommendation like texting a friend! 📱
      - Use emojis naturally throughout (but don't overdo it!)
      - Keep it conversational and friendly - like "Hey!" not "Dear patient"
      - **IF TOP LONGEVITY OPPORTUNITY**: Mention the exciting potential bonus years gain to motivate them! (e.g., "This could literally add 6 years to your life! 🎉")
      - Weave in SPECIFIC smartwatch data naturally to back up your suggestions (e.g., "Looking at your smartwatch, you're only getting 25 active minutes per day when we need 60+...")
      - When recommending action, justify it with their actual metrics (steps, HRV, VO2 max, active minutes)
      - If suggesting a sedentary person do more activity, reference their low step count or active minutes
      - If suggesting stress management, cite their low HRV value
      # - If suggesting sleep changes, mention their deep/REM sleep hours
      - Explain what they'll do in simple terms
      - Share the science in a friendly way - like "So this cool study from [Author, Year] found that [key result]"
      - Make it relatable with real-world benefits they'll actually care about
      - Get them pumped and ready to start! 💪

   C) CHALLENGE: Create a gamified 10-day challenge with:
      - intervention_name: The intervention name
      - duration_days: 10
      - daily_tasks: Array of 10 strings, each a daily task with emojis and motivational messages
        * Use progression (start easy, build up)
        * Add milestone celebrations (Day 3, Day 5, Day 7, Day 10)
        * Make tasks specific to the intervention type
        * Examples: "💪 Day 1: 15 min HIIT - Beast mode activated!", "✅ Day 5: Take 500mg - 🌟 Halfway hero!"
      - success_criteria: What success looks like (from expected_improvement)
      - category: The intervention category

Remember: Choose ONLY ONE intervention. Justify it with ALL the data (biomarkers + smartwatch + profile). Science-backed BUT make it fun! 😄

Respond ONLY with valid JSON in this exact format:
{{
    "selected_intervention_id": "the-intervention-id",
    "reasoning": "Your detailed reasoning here with emojis...",
    "suggestion": "Your fun, friendly, science-backed recommendation here with emojis...",
    "challenge": {{
        "intervention_name": "Intervention Name",
        "duration_days": 10,
        "daily_tasks": ["Day 1: ...", "Day 2: ...", "Day 3: ...", "Day 4: ...", "Day 5: ...", "Day 6: ...", "Day 7: ...", "Day 8: ...", "Day 9: ...", "Day 10: ..."],
        "success_criteria": "Expected improvement description",
        "category": "category_name"
    }}
}}"""

    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V3.2-Exp",
        messages=[
            {"role": "system", "content": "You are a fun, friendly health enthusiast who loves sharing science-backed health tips. You're casual and conversational but always evidence-based. Use emojis naturally and make health optimization exciting! Always respond with valid JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1500
    )
    
    logger.info("LLM response received")
    
    # Parse LLM response
    llm_output = response.choices[0].message.content.strip()
    
    # Extract JSON from response (handle potential markdown code blocks)
    if "```json" in llm_output:
        llm_output = llm_output.split("```json")[1].split("```")[0].strip()
    elif "```" in llm_output:
        llm_output = llm_output.split("```")[1].split("```")[0].strip()
    
    llm_result = json.loads(llm_output)
    
    selected_id = llm_result.get("selected_intervention_id")
    reasoning = llm_result.get("reasoning")
    suggestion = llm_result.get("suggestion")
    challenge = llm_result.get("challenge")
    
    logger.info(f"LLM selected intervention: {selected_id}")
    
    # Find the selected intervention
    selected_intervention = None
    for intervention in candidate_interventions:
        if intervention['id'] == selected_id:
            selected_intervention = intervention
            break
    
    if not selected_intervention:
        logger.warning(f"Selected intervention {selected_id} not found, using fallback")
        selected_intervention = candidate_interventions[0]  # Fallback to first
    
    # Format scientific references
    references = format_scientific_references(selected_intervention)
    
    # Create structured JSON output
    suggestion_output = {
        "reasoning": reasoning,
        "suggestion": suggestion,
        "challenge": challenge
    }
    
    logger.info("=== Suggestion Node Completed Successfully ===")
    return {
        "suggestion": suggestion_output,
        "problematicBiomarkers": problematic,
        "selectedIntervention": selected_intervention,
        "scientificReferences": references,
        "smartwatchData": smartwatch_data
    }

