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
from .phenoage_calculator import compute_years_gained, BiomarkerError
from .biomarker_mapper import map_to_phenoage_biomarkers
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


def map_health_data_to_measurements(blood_data: Dict[str, float], user_profile: Dict[str, Any], client: OpenAI) -> List[BiomarkerMeasurement]:
    """
    Use LLM to map blood and user profile data to BiomarkerMeasurement objects with inferred units.
    
    Args:
        blood_data: Dictionary of biomarker names to values
        user_profile: User demographic data and health metrics (age, gender, weight_kg, height_cm, sleep_hours_per_night, movement_days_per_week)
        client: OpenAI client for LLM calls
        
    Returns:
        List of BiomarkerMeasurement objects
    """
    # Combine blood data with user profile metrics
    all_health_data = {}
    
    # Add blood data
    if blood_data:
        all_health_data.update(blood_data)
    
    # Extract user profile metrics and calculate derived biomarkers
    weight_kg = user_profile.get('weight_kg')
    height_cm = user_profile.get('height_cm')
    age = user_profile.get('age')
    gender = user_profile.get('gender', '').lower()
    sleep_hours = user_profile.get('sleep_hours_per_night')
    movement_days = user_profile.get('movement_days_per_week')
    
    # Calculate BMI if weight and height are available
    if weight_kg and height_cm:
        height_m = height_cm / 100.0
        bmi = weight_kg / (height_m ** 2)
        all_health_data['BMI'] = round(bmi, 2)
        all_health_data['Body weight'] = weight_kg
        logger.info(f"Calculated BMI: {bmi:.2f} kg/m^2")
        
        # Calculate body fat percentage using Deurenberg formula
        # Formula: (1.20 × BMI) + (0.23 × age) - (10.8 × gender_factor) - 5.4
        # gender_factor: 1 for male, 0 for female
        if age:
            gender_factor = 1 if gender in ['male', 'm', 'man'] else 0
            body_fat_pct = (1.20 * bmi) + (0.23 * age) - (10.8 * gender_factor) - 5.4
            all_health_data['Body fat percentage'] = round(body_fat_pct, 2)
            logger.info(f"Estimated body fat percentage: {body_fat_pct:.2f}%")
    
    # Add sleep duration if available
    if sleep_hours is not None:
        all_health_data['Sleep duration'] = sleep_hours
        logger.info(f"Sleep duration: {sleep_hours} hours/night")
    
    # Add movement/exercise frequency if available
    if movement_days is not None:
        all_health_data['Exercise frequency'] = movement_days
        logger.info(f"Exercise frequency: {movement_days} days/week")
    
    if not all_health_data:
        return []
    
    logger.info(f"Mapping {len(all_health_data)} health metrics to database format...")
    
    # Prepare prompt for LLM
    biomarkers_list = [{"name": k, "value": v} for k, v in all_health_data.items()]
    
    prompt = f"""You are a medical data specialist. Given a list of biomarker and health measurements, your task is to:
1. Match each biomarker/metric name to the most likely standard biomarker name used in medical databases
2. Infer the appropriate unit of measurement based on the biomarker type and value range

Common biomarker units:
- Cholesterol, LDL, HDL, Triglycerides: mg/dL or mmol/L
- Glucose: mg/dL or mmol/L
- Hemoglobin: g/dL
- C-reactive protein (CRP): mg/L
- Testosterone: ng/dL or nmol/L
- Vitamin D: ng/mL or nmol/L
- BMI: kg/m^2
- Body weight: kg
- Body fat percentage: %
- Blood pressure: mmHg
- Heart rate: bpm
- HbA1c: %
- Creatinine: mg/dL
- Albumin: g/dL
- White blood cell count: cells/μL or 10^9/L
- Platelets: cells/μL or 10^9/L
- Sleep duration: hours (per night)
- Exercise frequency: days/week or sessions/week

SPECIAL INSTRUCTIONS for user profile metrics:
- "Sleep duration" or "Sleep hours": Map to appropriate sleep-related biomarker in database (e.g., "Sleep duration", "Sleep hours per night")
- "Exercise frequency" or "Movement days": Map to physical activity metrics (e.g., "Exercise frequency", "Physical activity days per week")

User context:
- Age: {user_profile.get('age', 'unknown')}
- Gender: {user_profile.get('gender', 'unknown')}

Input health data (blood tests + user profile metrics):
{json.dumps(biomarkers_list, indent=2)}

For each measurement, provide:
1. The standardized biomarker name (match to common medical terminology or relevant database fields)
2. The value (as provided)
3. The most likely unit based on the value range and measurement type

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
                {"role": "system", "content": "You are a medical data expert who standardizes biomarker and health measurements. Always respond with valid JSON."},
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
                # Determine source based on measurement type
                name_lower = item["name"].lower()
                if any(term in name_lower for term in ['bmi', 'body weight', 'body fat', 'waist']):
                    source = "user_profile"
                elif any(term in name_lower for term in ['sleep', 'exercise', 'activity', 'movement']):
                    source = "user_profile"
                else:
                    source = "blood_test"
                
                measurement = BiomarkerMeasurement(
                    name=item["name"],
                    value=float(item["value"]),
                    unit=item["unit"],
                    source=source
                )
                measurements.append(measurement)
                logger.info(f"  Mapped: {item['name']} = {item['value']} {item['unit']} (source: {source})")
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
    
    # Check for retry/feedback from critic
    critique_feedback = state.get("critiqueFeedback")
    retry_count = state.get("retryCount", 0)
    
    if critique_feedback:
        logger.info(f"=== RETRY ATTEMPT {retry_count} - Processing critique feedback ===")
        logger.info(f"Previous rejection reason: {critique_feedback}")
    
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
        
        # Map blood and user profile data to measurements using LLM
        measurements = map_health_data_to_measurements(blood_data, user_profile, client)
        
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
    
    # ============================================================================
    # PHENOAGE BIOLOGICAL AGE CALCULATION
    # ============================================================================
    
    phenoage_results = None
    pdf_data = state.get("pdf", {})
    
    try:
        logger.info("=== PhenoAge Biological Age Calculation Started ===")
        
        # Map biomarkers to PhenoAge format using LLM
        mapped_biomarkers = map_to_phenoage_biomarkers(
            pdf_data=pdf_data,
            blood_data=blood_data,
            user_profile=user_profile,
            client=client
        )
        
        if mapped_biomarkers:
            # Check if we have at least age (required) and some biomarkers
            required_count = sum(1 for k in mapped_biomarkers.keys() if mapped_biomarkers[k] is not None)
            logger.info(f"Mapped {required_count} PhenoAge biomarkers")
            
            # Try to compute PhenoAge if we have age (required)
            # Missing biomarkers will be filled with optimal values
            if mapped_biomarkers.get("age_years") is not None:
                try:
                    # Filter out None values, but keep structure
                    # Missing biomarkers will be filled with optimal values in compute_years_gained
                    biomarkers_for_calc = {k: v for k, v in mapped_biomarkers.items() if v is not None}
                    
                    # Check which biomarkers are missing (will be filled with optimal values)
                    missing_biomarkers = [k for k in ["albumin_g_dl", "creatinine_mg_dl", 
                                                       "glucose_mg_dl", "crp_mg_l", "lymphocyte_percent",
                                                       "mcv_fl", "rdw_percent", "alp_u_l", "wbc_10e3_per_uL"]
                                         if k not in biomarkers_for_calc]
                    
                    if missing_biomarkers:
                        logger.info(f"Missing {len(missing_biomarkers)} biomarkers - will use optimal values: {', '.join(missing_biomarkers)}")
                    
                    # Calculate PhenoAge (missing biomarkers will be filled with optimal values)
                    phenoage_results = compute_years_gained(biomarkers_for_calc)
                    
                    logger.info("="*60)
                    logger.info("🧬 PHENOAGE BIOLOGICAL AGE RESULTS 🧬")
                    logger.info("="*60)
                    logger.info(f"Current Biological Age: {phenoage_results['biological_age_now']:.2f} years")
                    logger.info(f"Chronological Age: {age} years")
                    logger.info(f"Target Biological Age (optimized): {phenoage_results['biological_age_target']:.2f} years")
                    logger.info(f"Years Gainable: {phenoage_results['years_biological_gained']:.2f} years")
                    
                    if missing_biomarkers:
                        logger.info(f"Note: {len(missing_biomarkers)} biomarkers assumed optimal (not in test data)")
                    
                    if phenoage_results['per_biomarker_contributions']:
                        logger.info("="*60)
                        logger.info("🎯 TOP BIOMARKER OPPORTUNITIES (PhenoAge)")
                        logger.info("="*60)
                        for i, contrib in enumerate(phenoage_results['per_biomarker_contributions'][:5], 1):
                            logger.info(f"{i}. {contrib['biomarker']}: +{contrib['years_gained_if_optimized']:.2f} years")
                        logger.info("="*60)
                        
                except BiomarkerError as e:
                    logger.warning(f"PhenoAge calculation error: {e}")
                except Exception as e:
                    logger.error(f"Error during PhenoAge calculation: {e}")
            else:
                logger.warning("Age not available for PhenoAge calculation")
        else:
            logger.warning("Could not map biomarkers to PhenoAge format")
            
    except Exception as e:
        logger.error(f"Error during PhenoAge biological age calculation: {e}")
    
    logger.info("=== PhenoAge Biological Age Calculation Completed ===\n")
    
    # ============================================================================
    # END PHENOAGE BIOLOGICAL AGE CALCULATION
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
    
    # Build PhenoAge biological age context (PRIMARY SOURCE - use this for intervention selection)
    phenoage_context = ""
    if phenoage_results:
        bio_age = phenoage_results['biological_age_now']
        target_age = phenoage_results['biological_age_target']
        years_gainable = phenoage_results['years_biological_gained']
        age_diff = bio_age - age  # Biological age vs chronological age
        
        age_status = "younger" if age_diff < 0 else "older"
        age_diff_abs = abs(age_diff)
        
        top_pheno_biomarker = None
        if phenoage_results['per_biomarker_contributions']:
            top_pheno_biomarker = phenoage_results['per_biomarker_contributions'][0]
        
        # Build detailed PhenoAge context with all top opportunities
        phenoage_opportunities = ""
        if phenoage_results['per_biomarker_contributions']:
            top_3 = phenoage_results['per_biomarker_contributions'][:3]
            opportunities_list = "\n".join([
                f"  {i+1}. {opp['biomarker']}: +{opp['years_gained_if_optimized']:.2f} years if optimized"
                for i, opp in enumerate(top_3)
            ])
            phenoage_opportunities = f"""
TOP PHENOAGE BIOMARKER OPPORTUNITIES (sorted by impact):
{opportunities_list}
"""
        
        phenoage_context = f"""
🧬 PHENOAGE BIOLOGICAL AGE ANALYSIS (Levine Model) - USE THIS FOR INTERVENTION SELECTION:
- Chronological Age: {age} years
- Current Biological Age: {bio_age:.1f} years ({age_diff_abs:.1f} years {age_status} than chronological)
- Target Biological Age (if all biomarkers optimized): {target_age:.1f} years
- 💎 TOTAL YEARS GAINABLE: +{years_gainable:.1f} biological years through optimization
{phenoage_opportunities}
- This is based on the PhenoAge model which predicts biological age from 9 key biomarkers + age
- Biological age is a better predictor of healthspan and lifespan than chronological age
- **PRIORITIZE interventions that target the top PhenoAge biomarker opportunities listed above**
"""
    
    # Build retry/feedback context if this is a retry
    retry_context = ""
    if critique_feedback:
        retry_context = f"""
⚠️ PREVIOUS ATTEMPT WAS REJECTED BY SAFETY REVIEW (Attempt {retry_count}):
{critique_feedback}

CRITICAL INSTRUCTIONS FOR THIS RETRY:
- You MUST select a DIFFERENT intervention than the previous attempt
- Address ALL safety concerns and recommendations mentioned above
- If age-related concerns were raised, choose age-appropriate interventions
- If contraindications were mentioned, avoid interventions with similar contraindications
- If dosage/timing concerns were raised, adjust accordingly
- Do NOT repeat the same recommendation that was rejected
"""
        logger.info("Added retry context to LLM prompt")
    
    # Create LLM prompt
    prompt = f"""You're a health-savvy friend who gets excited about helping people optimize their wellbeing! 😊 Analyze the user's health data and pick the BEST intervention from the options.
{retry_context}
USER PROFILE:
- Age: {age}
- Gender: {gender}
- Occupation: {job}
{phenoage_context}
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
   - **HIGHEST PRIORITY**: If PhenoAge analysis is provided, prioritize interventions that target the TOP PhenoAge biomarker opportunities (these directly reduce biological age and are the most impactful!)
   - Focus on the biomarker with the highest years gainable from the PhenoAge analysis
   - Which biomarker needs the most attention based on PhenoAge opportunities
   - Their current fitness level and activity patterns from smartwatch data
   - What fits their age, gender, and lifestyle best
   - What's actually doable and not super complicated
   - The science backing it up
   - Any reasons they shouldn't do it
   - How smartwatch metrics suggest they'll benefit (e.g., low HRV → stress management, low VO2 max → cardio)

2. Write THREE sections:

   A) REASONING (150-200 words): Explain WHY you chose this intervention over others:
      - **IF PHENOAGE ANALYSIS IS PROVIDED**: Lead with this! Mention their biological age vs chronological age, and how optimizing the top PhenoAge biomarker could reduce their biological age (e.g., "Your biological age is 40.5 but you're only 35 - optimizing your albumin could reduce it by 9.2 years!")
      - Reference the specific PhenoAge biomarker opportunity and the years gainable
      - Reference SPECIFIC biomarker values from the PhenoAge analysis
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
      - **IF PHENOAGE ANALYSIS IS PROVIDED**: Mention the exciting potential biological age reduction to motivate them! (e.g., "This could literally reduce your biological age by 9 years! 🎉" or "Your biological age is 40.5 but you're only 35 - optimizing this could bring it down!")
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
      - daily_tasks: Array of 10 strings with SPECIFIC, ACTIONABLE tasks (not vague!)
        * Each task must include EXACT details: what to do, how much, when, and how
        * Use progression (start easy, build gradually)
        * Add milestone celebrations (Day 3, Day 5, Day 7, Day 10)
        
        EXAMPLES OF SPECIFIC vs VAGUE TASKS:
        ❌ VAGUE: "Day 1: Take your supplement - Let's go! 💪"
        ✅ SPECIFIC: "Day 1: Take 500mg Omega-3 with breakfast (around 8-9am). Set a phone reminder! 🐟"
        
        ❌ VAGUE: "Day 1: Do some cardio - Beast mode! 🔥"
        ✅ SPECIFIC: "Day 1: 20-min brisk walk after lunch. Keep pace where you can talk but not sing. 🚶‍♂️"
        
        ❌ VAGUE: "Day 3: Keep going with your routine! 🌟"
        ✅ SPECIFIC: "Day 3: 25-min jog or cycle (increase intensity slightly). Aim for 130-140 heart rate. 🎯"
        
        ❌ VAGUE: "Day 5: You're halfway there! 💪"
        ✅ SPECIFIC: "Day 5: Take 500mg Omega-3 with breakfast + log how you feel (energy, focus). Halfway! 🌟"
        
        FOR SUPPLEMENTS: Include exact dosage, timing (breakfast/lunch/dinner), and practical tips
        FOR EXERCISE: Include exact duration, intensity level, type of activity, and heart rate/pace guidance
        FOR DIET: Include specific foods, portion sizes, meal timing, and simple recipes
        FOR LIFESTYLE: Include exact duration, time of day, and step-by-step instructions
        
      - success_criteria: What success looks like (from expected_improvement)
      - category: The intervention category

Remember: Choose ONLY ONE intervention. Justify it with ALL the data (biomarkers + smartwatch + profile). Science-backed BUT make it fun! 😄

Respond ONLY with valid JSON in this exact format:
{{
    "selected_intervention_id": "the-intervention-id",
    "reasoning": "Your detailed reasoning here with emojis...",
    "suggestion": "Your fun, friendly, science-backed recommendation here with emojis...",
    "biomarker": "The primary biomarker name this intervention targets (use PhenoAge biomarker name if available)",
    "bonus_years": 6.5,
    "challenge": {{
        "intervention_name": "Intervention Name",
        "duration_days": 10,
        "daily_tasks": ["Day 1: ...", "Day 2: ...", "Day 3: ...", "Day 4: ...", "Day 5: ...", "Day 6: ...", "Day 7: ...", "Day 8: ...", "Day 9: ...", "Day 10: ..."],
        "success_criteria": "Expected improvement description",
        "category": "category_name"
    }}
}}

IMPORTANT: bonus_years must be a NUMBER (e.g., 6.5), NOT a string. Use the years gainable from the TOP PHENOAGE BIOMARKER OPPORTUNITY if provided above (e.g., if top opportunity is albumin_g_dl with +9.17 years, use 9.17)."""

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
    biomarker = llm_result.get("biomarker")
    bonus_years_raw = llm_result.get("bonus_years")
    
    # Convert bonus_years to float if it's a string (e.g., "6" -> 6.0)
    bonus_years = None
    if bonus_years_raw is not None:
        try:
            bonus_years = float(bonus_years_raw)
        except (ValueError, TypeError):
            logger.warning(f"Could not convert bonus_years to float: {bonus_years_raw}")
            bonus_years = None
    
    logger.info(f"LLM selected intervention: {selected_id}")
    logger.info(f"LLM identified top biomarker: {biomarker} with potential bonus years: {bonus_years}")
    
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
    
    result = {
        "suggestion": suggestion_output,
        "problematicBiomarkers": problematic,
        "selectedIntervention": selected_intervention,
        "scientificReferences": references,
        "smartwatchData": smartwatch_data,
        "topOpportunityBiomarker": biomarker,
        "potentialBonusYears": bonus_years,
        "challenge": challenge
    }
    
    # Add PhenoAge results if available
    if phenoage_results:
        result["biologicalAgeNow"] = phenoage_results["biological_age_now"]
        result["biologicalAgeTarget"] = phenoage_results["biological_age_target"]
        result["yearsBiologicalGained"] = phenoage_results["years_biological_gained"]
        result["phenoageBiomarkerContributions"] = phenoage_results["per_biomarker_contributions"]
    
    # Clear critique feedback after processing (to avoid confusion in next iteration)
    if critique_feedback:
        result["critiqueFeedback"] = None
        logger.info("Cleared critique feedback from state")
    
    return result

