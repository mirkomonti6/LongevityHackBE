"""
Longevity Score Calculator

Calculates a health/longevity score based on blood biomarkers, age, and gender.
Uses weighted formula with optimal ranges for key markers.
"""

import math
from typing import Dict, Optional, Tuple


# Optimal ranges for key biomarkers (lower, optimal_low, optimal_high, upper)
BIOMARKER_RANGES = {
    "glucose": {
        "unit": "mg/dL",
        "optimal_low": 70,
        "optimal_high": 85,
        "acceptable_low": 65,
        "acceptable_high": 100,
        "weight": 10,
        "description": "Fasting glucose"
    },
    "hba1c": {
        "unit": "%",
        "optimal_low": 4.5,
        "optimal_high": 5.4,
        "acceptable_low": 4.0,
        "acceptable_high": 5.7,
        "weight": 12,
        "description": "Hemoglobin A1c (3-month glucose average)"
    },
    "ldl": {
        "unit": "mg/dL",
        "optimal_low": 50,
        "optimal_high": 100,
        "acceptable_low": 40,
        "acceptable_high": 130,
        "weight": 10,
        "description": "LDL cholesterol"
    },
    "hdl": {
        "unit": "mg/dL",
        "optimal_low": 60,
        "optimal_high": 90,
        "acceptable_low": 40,
        "acceptable_high": 100,
        "weight": 8,
        "description": "HDL cholesterol",
        "higher_better": True
    },
    "triglycerides": {
        "unit": "mg/dL",
        "optimal_low": 50,
        "optimal_high": 100,
        "acceptable_low": 40,
        "acceptable_high": 150,
        "weight": 8,
        "description": "Triglycerides"
    },
    "crp": {
        "unit": "mg/L",
        "optimal_low": 0.0,
        "optimal_high": 1.0,
        "acceptable_low": 0.0,
        "acceptable_high": 3.0,
        "weight": 9,
        "description": "C-reactive protein (inflammation marker)"
    },
    "vitamin_d": {
        "unit": "ng/mL",
        "optimal_low": 40,
        "optimal_high": 60,
        "acceptable_low": 30,
        "acceptable_high": 80,
        "weight": 7,
        "description": "Vitamin D (25-OH)",
        "higher_better": True
    },
    "insulin": {
        "unit": "μIU/mL",
        "optimal_low": 2,
        "optimal_high": 5,
        "acceptable_low": 1,
        "acceptable_high": 10,
        "weight": 9,
        "description": "Fasting insulin"
    },
    "blood_pressure_systolic": {
        "unit": "mmHg",
        "optimal_low": 110,
        "optimal_high": 120,
        "acceptable_low": 100,
        "acceptable_high": 130,
        "weight": 7,
        "description": "Systolic blood pressure"
    },
    "blood_pressure_diastolic": {
        "unit": "mmHg",
        "optimal_low": 70,
        "optimal_high": 80,
        "acceptable_low": 60,
        "acceptable_high": 85,
        "weight": 7,
        "description": "Diastolic blood pressure"
    }
}


def calculate_biomarker_score(value: float, biomarker: str) -> float:
    """
    Calculate a 0-100 score for a single biomarker value.
    
    100 = optimal range
    50-99 = acceptable but suboptimal
    <50 = outside healthy ranges
    
    Args:
        value: The biomarker value
        biomarker: The biomarker name (must be in BIOMARKER_RANGES)
    
    Returns:
        Score from 0-100
    """
    if biomarker not in BIOMARKER_RANGES:
        return 50  # Unknown biomarker, neutral score
    
    ranges = BIOMARKER_RANGES[biomarker]
    opt_low = ranges["optimal_low"]
    opt_high = ranges["optimal_high"]
    acc_low = ranges["acceptable_low"]
    acc_high = ranges["acceptable_high"]
    higher_better = ranges.get("higher_better", False)
    
    # In optimal range = 100
    if opt_low <= value <= opt_high:
        return 100.0
    
    # Below optimal
    if value < opt_low:
        if value >= acc_low:
            # In acceptable range below optimal
            range_size = opt_low - acc_low
            distance = opt_low - value
            score = 100 - (distance / range_size) * 30  # Scale 100-70
            return max(score, 70)
        else:
            # Below acceptable range
            distance = acc_low - value
            penalty = min(distance / acc_low * 50, 70)  # Cap penalty at 70 points
            return max(30 - penalty, 0)
    
    # Above optimal
    if value > opt_high:
        if value <= acc_high:
            # In acceptable range above optimal
            range_size = acc_high - opt_high
            distance = value - opt_high
            score = 100 - (distance / range_size) * 30  # Scale 100-70
            return max(score, 70)
        else:
            # Above acceptable range
            distance = value - acc_high
            penalty = min(distance / acc_high * 50, 70)
            return max(30 - penalty, 0)
    
    return 50  # Fallback


def calculate_age_adjustment(age: int, gender: str) -> float:
    """
    Calculate age-based adjustment factor.
    
    Younger ages get slight bonus, middle age is neutral, older ages expect
    slightly different ranges but we don't penalize healthy aging.
    
    Args:
        age: Age in years
        gender: 'male' or 'female'
    
    Returns:
        Adjustment multiplier (0.95-1.05)
    """
    if age < 30:
        return 1.02  # Slight bonus for youth
    elif age < 50:
        return 1.0  # Neutral
    elif age < 65:
        return 0.98  # Slight adjustment for middle age
    else:
        return 0.97  # Minimal adjustment for older adults


def identify_problematic_biomarkers(blood_data: Dict[str, float], threshold: float = 80) -> list:
    """
    Identify biomarkers that are below the threshold score.
    
    Args:
        blood_data: Dict of biomarker names to values
        threshold: Score threshold below which a marker is considered problematic
    
    Returns:
        List of tuples (biomarker_name, current_value, score, priority)
    """
    problematic = []
    
    for biomarker, value in blood_data.items():
        if biomarker in BIOMARKER_RANGES:
            score = calculate_biomarker_score(value, biomarker)
            if score < threshold:
                weight = BIOMARKER_RANGES[biomarker]["weight"]
                priority = weight * (100 - score) / 100  # Higher weight and worse score = higher priority
                problematic.append((biomarker, value, score, priority))
    
    # Sort by priority (highest first)
    problematic.sort(key=lambda x: x[3], reverse=True)
    return problematic


def calculate_longevity_score(
    blood_data: Dict[str, float],
    age: int,
    gender: str
) -> Dict[str, any]:
    """
    Calculate overall longevity/health score from blood data and demographics.
    
    Args:
        blood_data: Dict mapping biomarker names to values
        age: Age in years
        gender: 'male' or 'female'
    
    Returns:
        Dict containing:
            - overall_score: 0-100 score
            - component_scores: Individual biomarker scores
            - problematic_markers: List of markers needing attention
            - grade: Letter grade (A+, A, B, C, D, F)
    """
    component_scores = {}
    total_weight = 0
    weighted_score = 0
    
    # Calculate score for each available biomarker
    for biomarker, value in blood_data.items():
        if biomarker in BIOMARKER_RANGES:
            score = calculate_biomarker_score(value, biomarker)
            weight = BIOMARKER_RANGES[biomarker]["weight"]
            
            component_scores[biomarker] = {
                "value": value,
                "score": score,
                "unit": BIOMARKER_RANGES[biomarker]["unit"],
                "optimal_range": f"{BIOMARKER_RANGES[biomarker]['optimal_low']}-{BIOMARKER_RANGES[biomarker]['optimal_high']}",
                "description": BIOMARKER_RANGES[biomarker]["description"]
            }
            
            weighted_score += score * weight
            total_weight += weight
    
    # Calculate base score
    if total_weight > 0:
        base_score = weighted_score / total_weight
    else:
        base_score = 50  # No data available
    
    # Apply age adjustment
    age_adjustment = calculate_age_adjustment(age, gender)
    overall_score = min(base_score * age_adjustment, 100)
    
    # Determine grade
    if overall_score >= 95:
        grade = "A+"
    elif overall_score >= 90:
        grade = "A"
    elif overall_score >= 85:
        grade = "A-"
    elif overall_score >= 80:
        grade = "B+"
    elif overall_score >= 75:
        grade = "B"
    elif overall_score >= 70:
        grade = "C+"
    elif overall_score >= 65:
        grade = "C"
    elif overall_score >= 60:
        grade = "D"
    else:
        grade = "F"
    
    # Identify problematic markers
    problematic = identify_problematic_biomarkers(blood_data, threshold=80)
    
    return {
        "overall_score": round(overall_score, 1),
        "grade": grade,
        "component_scores": component_scores,
        "problematic_markers": problematic,
        "age": age,
        "gender": gender,
        "total_markers_analyzed": len(component_scores)
    }


def get_score_interpretation(score: float) -> str:
    """
    Get human-readable interpretation of longevity score.
    
    Args:
        score: Overall longevity score (0-100)
    
    Returns:
        Interpretation string
    """
    if score >= 90:
        return "Exceptional - You're in the top tier for health optimization"
    elif score >= 80:
        return "Very Good - Most markers are in optimal ranges"
    elif score >= 70:
        return "Good - Generally healthy with room for improvement"
    elif score >= 60:
        return "Fair - Several markers could be optimized"
    else:
        return "Needs Attention - Multiple markers require intervention"

