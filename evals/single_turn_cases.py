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
            "Should highlight a lipid-focused intervention (e.g., omega-3, fiber, or HIIT) "
            "and tie rationale to LDL/HDL imbalance plus low activity levels."
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
            "Should recommend stress-management or recovery-focused intervention "
            "that references low HRV, sleep deprivation, or mindfulness routines."
        ),
    },
]


