"""
Smartwatch Health Data Module

Mock smartwatch data generator that provides realistic advanced health metrics
based on user profile (age, gender, fitness level). Includes HRV, VO2 max,
resting heart rate, activity minutes, and sleep stages.
"""

import random
from typing import Dict, List, Any, Tuple


def get_mock_smartwatch_data(user_profile: Dict) -> Dict[str, Any]:
    """
    Generate realistic mock smartwatch data based on user profile.
    
    Args:
        user_profile: User demographic data with age, gender, job
        
    Returns:
        Dict with smartwatch metrics including HRV, VO2 max, resting HR,
        active minutes, sleep stages, and step averages
    """
    age = user_profile.get("age", 35)
    gender = user_profile.get("gender", "unknown").lower()
    job = user_profile.get("job", "").lower()
    
    # Infer baseline fitness from job type
    sedentary_jobs = ["developer", "programmer", "designer", "accountant", "office", "manager", "analyst"]
    active_jobs = ["trainer", "nurse", "teacher", "construction", "retail", "service"]
    
    is_sedentary = any(keyword in job for keyword in sedentary_jobs)
    is_active = any(keyword in job for keyword in active_jobs)
    
    # Base fitness level on job and age
    if is_sedentary:
        fitness_modifier = -0.15
    elif is_active:
        fitness_modifier = 0.10
    else:
        fitness_modifier = 0.0
    
    # Age-based decline in fitness metrics
    age_factor = max(0.6, 1.0 - (age - 25) * 0.01)
    
    # Gender-specific baselines
    if gender == "male":
        base_vo2_max = 42
        base_hrv = 55
        base_rhr = 65
    elif gender == "female":
        base_vo2_max = 38
        base_hrv = 58
        base_rhr = 68
    else:
        base_vo2_max = 40
        base_hrv = 56
        base_rhr = 66
    
    # Apply modifiers with some randomness
    vo2_max = round(base_vo2_max * age_factor * (1 + fitness_modifier) + random.uniform(-3, 3), 1)
    hrv = round(base_hrv * age_factor * (1 + fitness_modifier) + random.uniform(-8, 8), 1)
    resting_hr = round(base_rhr - (fitness_modifier * 10) + (1 - age_factor) * 5 + random.uniform(-3, 3), 0)
    
    # Activity metrics
    if is_sedentary:
        active_minutes = random.randint(15, 45)
        daily_steps = random.randint(3000, 6000)
    elif is_active:
        active_minutes = random.randint(60, 120)
        daily_steps = random.randint(8000, 12000)
    else:
        active_minutes = random.randint(30, 70)
        daily_steps = random.randint(5000, 8000)
    
    # Sleep metrics (total ~7-8 hours typical)
    # total_sleep = round(6.5 + random.uniform(0, 2), 1)
    # deep_sleep = round(total_sleep * 0.15 + random.uniform(-0.3, 0.3), 1)  # ~13-18% deep
    # rem_sleep = round(total_sleep * 0.22 + random.uniform(-0.4, 0.4), 1)   # ~20-25% REM
    # light_sleep = round(total_sleep - deep_sleep - rem_sleep, 1)
    
    # Ensure realistic bounds
    vo2_max = max(20, min(70, vo2_max))
    hrv = max(20, min(100, hrv))
    resting_hr = max(45, min(90, resting_hr))
    # deep_sleep = max(0.5, min(2.5, deep_sleep))
    # rem_sleep = max(0.8, min(3.0, rem_sleep))
    # light_sleep = max(3.0, light_sleep)
    
    return {
        "hrv": hrv,
        "vo2_max": vo2_max,
        "resting_heart_rate": int(resting_hr),
        "active_minutes_per_day": active_minutes,
        "daily_steps_average": daily_steps,
        # "sleep_deep_hours": deep_sleep,
        # "sleep_rem_hours": rem_sleep,
        # "sleep_light_hours": light_sleep,
        # "sleep_total_hours": round(deep_sleep + rem_sleep + light_sleep, 1)
    }


def assess_fitness_level(smartwatch_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Assess overall fitness level based on smartwatch metrics.
    
    Args:
        smartwatch_data: Dict with smartwatch metrics
        
    Returns:
        Dict with overall fitness level and component scores
    """
    vo2_max = smartwatch_data.get("vo2_max", 35)
    hrv = smartwatch_data.get("hrv", 50)
    resting_hr = smartwatch_data.get("resting_heart_rate", 70)
    active_minutes = smartwatch_data.get("active_minutes_per_day", 30)
    
    # Score each component (0-100)
    # VO2 Max scoring (20-70 range)
    vo2_score = min(100, max(0, (vo2_max - 20) * 2))
    
    # HRV scoring (20-100 range, higher is better)
    hrv_score = min(100, max(0, (hrv - 20) * 1.25))
    
    # Resting HR scoring (45-90 range, lower is better)
    rhr_score = min(100, max(0, 100 - (resting_hr - 45) * 2.2))
    
    # Active minutes scoring (0-150 range, 150+ is ideal)
    activity_score = min(100, (active_minutes / 150) * 100)
    
    # Overall fitness score (weighted average)
    overall_score = (
        vo2_score * 0.30 +
        hrv_score * 0.25 +
        rhr_score * 0.25 +
        activity_score * 0.20
    )
    
    # Categorize fitness level
    if overall_score >= 80:
        fitness_level = "excellent"
        description = "Outstanding fitness metrics! You're in peak condition."
    elif overall_score >= 65:
        fitness_level = "good"
        description = "Solid fitness foundation with room for optimization."
    elif overall_score >= 45:
        fitness_level = "fair"
        description = "Moderate fitness level - significant improvement potential."
    else:
        fitness_level = "needs_improvement"
        description = "Below optimal fitness markers - great opportunity to level up!"
    
    return {
        "overall_score": round(overall_score, 1),
        "fitness_level": fitness_level,
        "description": description,
        "component_scores": {
            "cardiovascular_fitness": round(vo2_score, 1),
            "recovery_capacity": round(hrv_score, 1),
            "heart_efficiency": round(rhr_score, 1),
            "activity_level": round(activity_score, 1)
        }
    }


def identify_activity_gaps(smartwatch_data: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Identify specific areas where activity/recovery metrics need improvement.
    
    Args:
        smartwatch_data: Dict with smartwatch metrics
        
    Returns:
        List of gaps with severity, metric name, and recommendation
    """
    gaps = []
    
    vo2_max = smartwatch_data.get("vo2_max", 35)
    hrv = smartwatch_data.get("hrv", 50)
    resting_hr = smartwatch_data.get("resting_heart_rate", 70)
    active_minutes = smartwatch_data.get("active_minutes_per_day", 30)
    daily_steps = smartwatch_data.get("daily_steps_average", 5000)
    # deep_sleep = smartwatch_data.get("sleep_deep_hours", 1.2)
    # rem_sleep = smartwatch_data.get("sleep_rem_hours", 1.5)
    
    # VO2 Max assessment
    if vo2_max < 30:
        gaps.append({
            "severity": "high",
            "metric": "VO2 Max",
            "value": vo2_max,
            "target": "35-45+",
            "recommendation": "Cardiovascular fitness is low - HIIT or cardio training recommended"
        })
    elif vo2_max < 38:
        gaps.append({
            "severity": "moderate",
            "metric": "VO2 Max",
            "value": vo2_max,
            "target": "38-45+",
            "recommendation": "Room to improve aerobic capacity through regular cardio"
        })
    
    # HRV assessment
    if hrv < 40:
        gaps.append({
            "severity": "high",
            "metric": "HRV",
            "value": hrv,
            "target": "50-70+",
            "recommendation": "Low HRV suggests stress/poor recovery - prioritize sleep and stress management"
        })
    elif hrv < 50:
        gaps.append({
            "severity": "moderate",
            "metric": "HRV",
            "value": hrv,
            "target": "50-70+",
            "recommendation": "HRV could be better - focus on recovery and stress reduction"
        })
    
    # Resting heart rate assessment
    if resting_hr > 75:
        gaps.append({
            "severity": "moderate",
            "metric": "Resting Heart Rate",
            "value": resting_hr,
            "target": "55-65",
            "recommendation": "Elevated resting HR - improve cardiovascular fitness through regular exercise"
        })
    elif resting_hr > 70:
        gaps.append({
            "severity": "low",
            "metric": "Resting Heart Rate",
            "value": resting_hr,
            "target": "55-65",
            "recommendation": "Slight room for improvement in resting heart rate"
        })
    
    # Activity minutes assessment
    if active_minutes < 30:
        gaps.append({
            "severity": "high",
            "metric": "Active Minutes",
            "value": active_minutes,
            "target": "60-150+",
            "recommendation": "Well below recommended activity - need more movement throughout the day"
        })
    elif active_minutes < 60:
        gaps.append({
            "severity": "moderate",
            "metric": "Active Minutes",
            "value": active_minutes,
            "target": "60-150+",
            "recommendation": "Below optimal activity level - aim for 60+ active minutes daily"
        })
    
    # Daily steps assessment
    if daily_steps < 5000:
        gaps.append({
            "severity": "high",
            "metric": "Daily Steps",
            "value": daily_steps,
            "target": "8000-10000",
            "recommendation": "Very sedentary - prioritize walking and general movement"
        })
    elif daily_steps < 7000:
        gaps.append({
            "severity": "moderate",
            "metric": "Daily Steps",
            "value": daily_steps,
            "target": "8000-10000",
            "recommendation": "Below target steps - increase daily walking"
        })
    
    # Deep sleep assessment
    # if deep_sleep < 1.0:
    #     gaps.append({
    #         "severity": "high",
    #         "metric": "Deep Sleep",
    #         "value": f"{deep_sleep}h",
    #         "target": "1.5-2.0h",
    #         "recommendation": "Insufficient deep sleep - optimize sleep hygiene and reduce stress"
    #     })
    # elif deep_sleep < 1.3:
    #     gaps.append({
    #         "severity": "moderate",
    #         "metric": "Deep Sleep",
    #         "value": f"{deep_sleep}h",
    #         "target": "1.5-2.0h",
    #         "recommendation": "Low deep sleep - consider sleep optimization strategies"
    #     })
    
    # REM sleep assessment
    # if rem_sleep < 1.2:
    #     gaps.append({
    #         "severity": "moderate",
    #         "metric": "REM Sleep",
    #         "value": f"{rem_sleep}h",
    #         "target": "1.8-2.5h",
    #         "recommendation": "Low REM sleep - may affect cognitive function and recovery"
    #     })
    
    # Sort by severity (high -> moderate -> low)
    severity_order = {"high": 0, "moderate": 1, "low": 2}
    gaps.sort(key=lambda x: severity_order.get(x["severity"], 3))
    
    return gaps


def get_smartwatch_insights_summary(smartwatch_data: Dict[str, Any]) -> str:
    """
    Generate a human-readable summary of smartwatch insights.
    
    Args:
        smartwatch_data: Dict with smartwatch metrics
        
    Returns:
        String summary of key smartwatch insights
    """
    fitness = assess_fitness_level(smartwatch_data)
    gaps = identify_activity_gaps(smartwatch_data)
    
    summary_lines = [
        f"Fitness Level: {fitness['fitness_level'].title()} ({fitness['overall_score']}/100)",
        f"VO2 Max: {smartwatch_data['vo2_max']} ml/kg/min",
        f"HRV: {smartwatch_data['hrv']} ms",
        f"Resting HR: {smartwatch_data['resting_heart_rate']} bpm",
        f"Daily Active Minutes: {smartwatch_data['active_minutes_per_day']} min",
        f"Daily Steps: {smartwatch_data['daily_steps_average']} steps",
        # f"Sleep: {smartwatch_data['sleep_total_hours']}h (Deep: {smartwatch_data['sleep_deep_hours']}h, REM: {smartwatch_data['sleep_rem_hours']}h)"
    ]
    
    if gaps:
        summary_lines.append(f"\nTop Priorities: {', '.join([g['metric'] for g in gaps[:3]])}")
    
    return "\n".join(summary_lines)


def match_interventions_to_activity_gaps(gaps: List[Dict[str, str]]) -> List[str]:
    """
    Suggest intervention categories based on identified activity gaps.
    
    Args:
        gaps: List of activity gaps from identify_activity_gaps()
        
    Returns:
        List of suggested intervention categories/types
    """
    suggestions = []
    
    for gap in gaps:
        metric = gap["metric"]
        severity = gap["severity"]
        
        if metric == "VO2 Max" and severity in ["high", "moderate"]:
            suggestions.append("cardio_exercise")
        
        if metric == "HRV" and severity in ["high", "moderate"]:
            suggestions.append("stress_management")
            # suggestions.append("sleep_optimization")
        
        if metric in ["Active Minutes", "Daily Steps"] and severity in ["high", "moderate"]:
            suggestions.append("walking_program")
            suggestions.append("general_activity")
        
        # if metric in ["Deep Sleep", "REM Sleep"]:
        #     suggestions.append("sleep_optimization")
        
        if metric == "Resting Heart Rate" and severity in ["high", "moderate"]:
            suggestions.append("cardiovascular_training")
    
    # Remove duplicates while preserving order
    seen = set()
    unique_suggestions = []
    for item in suggestions:
        if item not in seen:
            seen.add(item)
            unique_suggestions.append(item)
    
    return unique_suggestions

