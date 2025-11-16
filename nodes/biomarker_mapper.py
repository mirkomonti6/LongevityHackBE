"""
Biomarker Mapper for PhenoAge

Maps PDF-extracted test data and blood data to PhenoAge required biomarkers
using LLM for intelligent field matching and unit conversion.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from openai import OpenAI

from .phenoage_calculator import REQUIRED_BIOMARKERS, BiomarkerError

logger = logging.getLogger(__name__)

NETMIND_API_KEY = "6ecc3bdc2980400a8786fd512ad487e7"


def map_to_phenoage_biomarkers_llm(
    pdf_data: Optional[Dict[str, Any]] = None,
    blood_data: Optional[Dict[str, float]] = None,
    user_profile: Optional[Dict[str, Any]] = None,
    client: Optional[OpenAI] = None
) -> Optional[Dict[str, float]]:
    """
    Map PDF-extracted test data and other sources to PhenoAge required biomarkers using LLM.

    Args:
        pdf_data: Dictionary from pdf_parser with structure:
            {
                "tests": [{"name": "...", "result": ..., "unit": "...", ...}, ...],
                "patient": {"age": ..., "gender": ...}
            }
        blood_data: Dictionary of biomarker names to values (existing format)
        user_profile: Dictionary with user profile data (age, gender, etc.)
        client: OpenAI client instance (if None, will create one)

    Returns:
        Dictionary with PhenoAge required biomarkers, or None if insufficient data
    """
    if client is None:
        client = OpenAI(
            base_url="https://api.netmind.ai/inference-api/openai/v1",
            api_key=NETMIND_API_KEY
        )

    # Collect all available test data
    all_tests = []
    
    # Add tests from PDF data
    if pdf_data and "tests" in pdf_data and isinstance(pdf_data["tests"], list):
        for test in pdf_data["tests"]:
            test_name = test.get("name", "")
            test_result = test.get("result")
            test_unit = test.get("unit", "")
            if test_name and test_result is not None:
                all_tests.append({
                    "name": test_name,
                    "result": test_result,
                    "unit": test_unit,
                    "source": "pdf"
                })
    
    # Add tests from blood_data
    if blood_data:
        for name, value in blood_data.items():
            if value is not None:
                all_tests.append({
                    "name": name,
                    "result": value,
                    "unit": "",  # May not have unit info
                    "source": "blood_data"
                })
    
    # Extract age from multiple sources
    age = None
    if user_profile and "age" in user_profile:
        age = user_profile["age"]
    elif pdf_data and "patient" in pdf_data and "age" in pdf_data["patient"]:
        age = pdf_data["patient"]["age"]
    
    if not age:
        logger.warning("Age not found in user_profile or PDF data")
        return None
    
    if not all_tests:
        logger.warning("No test data available for mapping")
        return None
    
    logger.info(f"Mapping {len(all_tests)} tests to PhenoAge biomarkers (age: {age})")
    
    # Prepare LLM prompt
    prompt = f"""You are a medical data specialist. Your task is to map laboratory test results to the specific biomarkers required for the PhenoAge biological age calculation model.

REQUIRED PHENOAGE BIOMARKERS (with exact field names and units):
1. age_years: Chronological age in years (already provided: {age})
2. albumin_g_dl: Albumin in g/dL
3. creatinine_mg_dl: Creatinine in mg/dL
4. glucose_mg_dl: Fasting glucose in mg/dL
5. crp_mg_l: C-reactive protein in mg/L
6. lymphocyte_percent: Lymphocyte percentage (%)
7. mcv_fl: Mean corpuscular volume in fL
8. rdw_percent: Red cell distribution width (%)
9. alp_u_l: Alkaline phosphatase in U/L
10. wbc_10e3_per_uL: White blood cell count in 10^3 cells/µL

AVAILABLE TEST DATA:
{json.dumps(all_tests, indent=2)}

UNIT CONVERSION RULES:
- Albumin: g/L → divide by 10 to get g/dL
- Creatinine: µmol/L → divide by 88.401 to get mg/dL; mg/dL stays as is
- Glucose: mmol/L → multiply by 18.018 to get mg/dL; mg/dL stays as is
- CRP: mg/dL → multiply by 10 to get mg/L; mg/L stays as is
- WBC: cells/µL → divide by 1000 to get 10^3/µL; 10^3/µL stays as is
- MCV: fL stays as is
- Percentages: % stays as is
- ALP: U/L stays as is

COMMON TEST NAME VARIATIONS:
- Albumin: "Albumin", "ALB", "Serum Albumin"
- Creatinine: "Creatinine", "CREA", "Serum Creatinine", "Cr", "Creatine, Serum
- Glucose: "Glucose", "GLU", "Fasting Glucose", "Blood Glucose", "FBG"
- CRP: "C-Reactive Protein", "CRP", "hs-CRP", "hs-CRP"
- Lymphocyte: "Lymphocyte %", "Lymphocytes", "LYM%", "Lymphocyte Percentage"
- MCV: "MCV", "Mean Corpuscular Volume", "Mean Cell Volume"
- RDW: "RDW", "Red Cell Distribution Width", "RDW-CV", "RDW-SD"
- ALP: "Alkaline Phosphatase", "ALP", "ALKP", "Alk Phos"
- WBC: "White Blood Cell Count", "WBC", "Leukocyte Count", "White Cell Count"

INSTRUCTIONS:
1. Match each available test to the corresponding PhenoAge biomarker
2. Perform necessary unit conversions
3. Extract the age from the provided value ({age})
4. If a biomarker cannot be found or mapped, set it to null
5. Return ONLY valid JSON with the exact field names listed above

Respond with valid JSON in this exact format:
{{
    "age_years": {age},
    "albumin_g_dl": <value or null>,
    "creatinine_mg_dl": <value or null>,
    "glucose_mg_dl": <value or null>,
    "crp_mg_l": <value or null>,
    "lymphocyte_percent": <value or null>,
    "mcv_fl": <value or null>,
    "rdw_percent": <value or null>,
    "alp_u_l": <value or null>,
    "wbc_10e3_per_uL": <value or null>
}}

IMPORTANT: Only include biomarkers that can be reliably mapped. If a biomarker is missing, set it to null."""

    try:
        response = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3.2-Exp",
            messages=[
                {
                    "role": "system",
                    "content": "You are a medical data expert who maps laboratory tests to standardized biomarker formats. Always respond with valid JSON only."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1500
        )
        
        llm_output = response.choices[0].message.content.strip()
        
        # Extract JSON from response (handle potential markdown code blocks)
        if "```json" in llm_output:
            llm_output = llm_output.split("```json")[1].split("```")[0].strip()
        elif "```" in llm_output:
            llm_output = llm_output.split("```")[1].split("```")[0].strip()
        
        result = json.loads(llm_output)
        
        # Validate that we have age_years
        if "age_years" not in result or result["age_years"] is None:
            logger.warning("LLM did not return age_years")
            return None
        
        # Convert to float and filter out None values, but keep the structure
        mapped_biomarkers = {}
        for key in REQUIRED_BIOMARKERS:
            value = result.get(key)
            if value is not None:
                try:
                    mapped_biomarkers[key] = float(value)
                except (ValueError, TypeError):
                    logger.warning(f"Could not convert {key} to float: {value}")
                    mapped_biomarkers[key] = None
            else:
                mapped_biomarkers[key] = None
        
        # Check if we have at least age_years (required)
        if mapped_biomarkers.get("age_years") is None:
            logger.warning("Age is missing from mapped biomarkers")
            return None
        
        # Count how many biomarkers we successfully mapped
        mapped_count = sum(1 for v in mapped_biomarkers.values() if v is not None)
        logger.info(f"Successfully mapped {mapped_count}/{len(REQUIRED_BIOMARKERS)} PhenoAge biomarkers")
        
        # Return the mapped biomarkers (may have some None values)
        return mapped_biomarkers
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM JSON response: {e}")
        logger.error(f"LLM output: {llm_output[:500]}")
        return None
    except Exception as e:
        logger.error(f"Failed to map biomarkers with LLM: {e}")
        return None


def map_to_phenoage_biomarkers(
    pdf_data: Optional[Dict[str, Any]] = None,
    blood_data: Optional[Dict[str, float]] = None,
    user_profile: Optional[Dict[str, Any]] = None,
    client: Optional[OpenAI] = None
) -> Optional[Dict[str, float]]:
    """
    Main entry point for mapping to PhenoAge biomarkers.
    
    This is a convenience wrapper that calls the LLM-based mapper.
    
    Args:
        pdf_data: Dictionary from pdf_parser
        blood_data: Dictionary of biomarker names to values
        user_profile: Dictionary with user profile data
        client: OpenAI client instance (optional)
    
    Returns:
        Dictionary with PhenoAge required biomarkers, or None if insufficient data
    """
    return map_to_phenoage_biomarkers_llm(
        pdf_data=pdf_data,
        blood_data=blood_data,
        user_profile=user_profile,
        client=client
    )



