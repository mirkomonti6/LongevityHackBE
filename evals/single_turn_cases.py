"""
Hard-coded single turn scenarios for evaluating the LangGraph workflow.

Each case pre-populates the GraphState with user profile, biomarker data,
and conversational context so the workflow can run without external inputs.
"""

from __future__ import annotations

from typing import List, TypedDict

from nodes import GraphState


class SingleTurnCase(TypedDict):
    """Container describing a deterministic LangGraph evaluation scenario."""

    name: str
    description: str
    initial_state: GraphState
    expected_outcome: str


SINGLE_TURN_CASES: List[SingleTurnCase] = [
    {
        "name": "metabolic-reset",
        "description": (
            "38-year-old product manager wants metabolic help after high LDL, "
            "elevated CRP, low HDL, and low active minutes per smartwatch."
        ),
        "initial_state": {
            "userInput": "I want to get my cholesterol and metabolic health under control.",
            "messages": [
                {"role": "user", "content": "I feel sluggish and my doctor warned me about LDL."},
                {"role": "assistant", "content": "Sure, let's review your biomarkers before planning."},
            ],
            "userProfile": {
                "age": 38,
                "gender": "male",
                "job": "product manager",
                "height_cm": 182,
                "weight_kg": 94,
                "sleep_hours_per_night": 6.2,
                "movement_days_per_week": 2,
                "work_activity_level": "sedentary",
                "stress_level_1_to_10": 7,
            },
            "bloodData": {
                "glucose": 102,
                "hba1c": 5.8,
                "ldl": 168,
                "hdl": 34,
                "triglycerides": 210,
                "crp": 4.1,
                "vitamin_d": 24,
            },
            "smartwatchData": {
                "hrv": 32,
                "vo2_max": 31,
                "resting_heart_rate": 76,
                "active_minutes_per_day": 18,
                "daily_steps_average": 4200,
            },
        },
        "expected_outcome": (
            "Should recommend an intervention that addresses metabolic health concerns "
            "(e.g., Mediterranean diet, omega-3, resistance training, or HIIT) "
            "and reference the elevated LDL (168), triglycerides (210), and low HDL (34) "
            "along with low activity levels from smartwatch (18 active minutes, 4200 steps)."
        ),
    },
    {
        "name": "stress-recovery",
        "description": (
            "45-year-old design lead dealing with chronic stress, low HRV, "
            "and vitamin D deficiency wants calmer routines."
        ),
        "initial_state": {
            "userInput": "How can I calm my stress hormones without meds?",
            "messages": [
                {"role": "user", "content": "Too many deadlines lately and I barely sleep."},
                {"role": "assistant", "content": "Let's see what biomarkers stand out."},
            ],
            "userProfile": {
                "age": 45,
                "gender": "female",
                "job": "design lead",
                "height_cm": 168,
                "weight_kg": 68,
                "sleep_hours_per_night": 5.5,
                "movement_days_per_week": 1,
                "work_activity_level": "high stress",
                "stress_level_1_to_10": 9,
            },
            "bloodData": {
                "glucose": 95,
                "ldl": 130,
                "hdl": 42,
                "triglycerides": 160,
                "crp": 3.2,
                "vitamin_d": 18,
                "insulin": 18,
            },
            "smartwatchData": {
                "hrv": 28,
                "vo2_max": 28,
                "resting_heart_rate": 82,
                "active_minutes_per_day": 12,
                "daily_steps_average": 3200,
            },
        },
        "expected_outcome": (
            "Should recommend an intervention that helps reduce stress and improve recovery "
            "(e.g., sleep optimization, meditation, walking, or stress management) "
            "and explicitly reference low HRV (28ms) as a stress/recovery indicator. "
            "Should acknowledge severe sleep deprivation (5.5 hours) and high stress level (9/10)."
        ),
    },
    {
        "name": "inflammation-athlete",
        "description": (
            "32-year-old fitness instructor with high CRP inflammation markers "
            "despite high activity, needs anti-inflammatory intervention."
        ),
        "initial_state": {
            "userInput": "I train hard but my inflammation markers are high. What gives?",
            "messages": [
                {"role": "user", "content": "I work out 6 days a week but my CRP is elevated."},
                {"role": "assistant", "content": "Let's analyze your biomarkers and recovery metrics."},
            ],
            "userProfile": {
                "age": 32,
                "gender": "female",
                "job": "fitness instructor",
                "height_cm": 170,
                "weight_kg": 62,
                "sleep_hours_per_night": 6.0,
                "movement_days_per_week": 6,
                "work_activity_level": "very active",
                "stress_level_1_to_10": 6,
            },
            "bloodData": {
                "glucose": 88,
                "hba1c": 5.1,
                "ldl": 95,
                "hdl": 65,
                "triglycerides": 82,
                "crp": 5.8,
                "vitamin_d": 32,
            },
            "smartwatchData": {
                "hrv": 38,
                "vo2_max": 45,
                "resting_heart_rate": 58,
                "active_minutes_per_day": 95,
                "daily_steps_average": 12500,
            },
        },
        "expected_outcome": (
            "Should recommend an intervention that addresses inflammation (CRP 5.8) "
            "(e.g., omega-3, Mediterranean diet, stress management, or recovery-focused approach). "
            "Should recognize the paradox of high activity (95 active min, 12500 steps, VO2 max 45) "
            "but elevated CRP and relatively low HRV (38ms) suggesting overtraining or insufficient recovery."
        ),
    },
    {
        "name": "prediabetic-diet",
        "description": (
            "52-year-old accountant with elevated HbA1c and insulin resistance, "
            "sedentary lifestyle needs dietary intervention."
        ),
        "initial_state": {
            "userInput": "My doctor said I'm prediabetic. I need to reverse this fast.",
            "messages": [
                {"role": "user", "content": "I sit all day and my blood sugar is creeping up."},
                {"role": "assistant", "content": "Let's look at your metabolic markers together."},
            ],
            "userProfile": {
                "age": 52,
                "gender": "male",
                "job": "accountant",
                "height_cm": 175,
                "weight_kg": 88,
                "sleep_hours_per_night": 7.0,
                "movement_days_per_week": 1,
                "work_activity_level": "sedentary",
                "stress_level_1_to_10": 5,
            },
            "bloodData": {
                "glucose": 118,
                "hba1c": 6.2,
                "ldl": 145,
                "hdl": 38,
                "triglycerides": 195,
                "crp": 3.8,
                "vitamin_d": 22,
                "insulin": 22,
            },
            "smartwatchData": {
                "hrv": 30,
                "vo2_max": 26,
                "resting_heart_rate": 78,
                "active_minutes_per_day": 8,
                "daily_steps_average": 2800,
            },
        },
        "expected_outcome": (
            "Should recommend an intervention for prediabetes and insulin resistance "
            "(e.g., Mediterranean diet, intermittent fasting, berberine, walking, or resistance training) "
            "and explicitly reference elevated HbA1c (6.2), glucose (118), and insulin (22) levels. "
            "Should mention the extremely low activity from smartwatch (8 active min, 2800 steps) as a contributing factor."
        ),
    },
    {
        "name": "vitamin-d-bone-health",
        "description": (
            "58-year-old woman with severe vitamin D deficiency and concerns about "
            "bone health approaching menopause."
        ),
        "initial_state": {
            "userInput": "I'm worried about osteoporosis. My vitamin D is really low.",
            "messages": [
                {"role": "user", "content": "I'm 58 and barely go outside. Should I worry about my bones?"},
                {"role": "assistant", "content": "Let's check your vitamin D and other markers."},
            ],
            "userProfile": {
                "age": 58,
                "gender": "female",
                "job": "software engineer",
                "height_cm": 163,
                "weight_kg": 58,
                "sleep_hours_per_night": 6.5,
                "movement_days_per_week": 2,
                "work_activity_level": "sedentary",
                "stress_level_1_to_10": 4,
            },
            "bloodData": {
                "glucose": 92,
                "hba1c": 5.3,
                "ldl": 125,
                "hdl": 52,
                "triglycerides": 110,
                "crp": 2.1,
                "vitamin_d": 12,
            },
            "smartwatchData": {
                "hrv": 35,
                "vo2_max": 30,
                "resting_heart_rate": 72,
                "active_minutes_per_day": 22,
                "daily_steps_average": 4500,
            },
        },
        "expected_outcome": (
            "Should recommend vitamin D supplementation and/or sun exposure protocol, "
            "with emphasis on bone health for post-menopausal women. May also suggest "
            "weight-bearing exercise referencing low activity levels from smartwatch. "
            "Should mention the critically low vitamin D value (12 ng/mL)."
        ),
    },
]


