# llm_parser.py
"""
Production-grade LLM parser for mortality predictors database.
Creates clean, standardized data structure with all metadata.
"""

import pandas as pd
import json
import math
from typing import Dict, List, Optional, Literal
from pydantic import BaseModel, Field
import openai
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import time
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
# Look in current directory first, then parent directories
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    # Try project root
    load_dotenv()


# ============================================================================
# STRICT DATA SCHEMA (Pydantic for validation)
# ============================================================================

class OptimalValue(BaseModel):
    """Optimal/reference value for a biomarker"""
    type: Literal["range", "threshold", "direction_only", "percentile", "unparseable"]
    value: Optional[float] = Field(None, description="Single optimal value (if applicable)")
    range_low: Optional[float] = Field(None, description="Lower bound of optimal range")
    range_high: Optional[float] = Field(None, description="Upper bound of optimal range")
    unit: Optional[str] = Field(None, description="Unit of measurement")
    direction: Optional[Literal["higher_is_better", "lower_is_better"]] = Field(None)
    percentile: Optional[int] = Field(None, description="Optimal percentile (0-100)")
    
    # For per-unit changes
    per_unit_change: Optional[float] = Field(None, description="HR change per X units")
    per_unit_amount: Optional[float] = Field(None, description="The X in 'per X units'")


class ComparisonGroups(BaseModel):
    """The two groups being compared in the study"""
    group1_description: str = Field(..., description="First group (usually optimal/reference)")
    group1_value_low: Optional[float] = None
    group1_value_high: Optional[float] = None
    
    group2_description: str = Field(..., description="Second group (usually at-risk)")
    group2_value_low: Optional[float] = None
    group2_value_high: Optional[float] = None
    
    which_is_optimal: Literal["group1", "group2", "unclear"]


class PopulationCharacteristics(BaseModel):
    """Study population characteristics"""
    sex: Optional[Literal["males", "females", "both", "unknown"]] = "unknown"
    age_min: Optional[int] = None
    age_max: Optional[int] = None
    age_mean: Optional[float] = None
    n_subjects: Optional[int] = None
    n_deaths: Optional[int] = None
    follow_up_years: Optional[float] = None
    ethnicity: Optional[str] = None
    health_status: Optional[str] = Field(None, description="e.g., healthy, diabetic, etc.")


class StudyQuality(BaseModel):
    """Study quality metrics"""
    p_value: Optional[float] = None
    confidence_interval_low: Optional[float] = None
    confidence_interval_high: Optional[float] = None
    n_subjects: Optional[int] = None
    study_design: Optional[str] = Field(None, description="e.g., prospective, retrospective")
    adjustments: Optional[str] = Field(None, description="Variables adjusted for")


class BiomarkerStudy(BaseModel):
    """Complete standardized biomarker study"""
    # Core identification
    biomarker_name: str
    biomarker_category: str  # Blood, Physical parameter, etc.
    biomarker_detail: Optional[str] = None
    
    # Effect size (CRITICAL for importance)
    hazard_ratio: float
    effect_magnitude: float = Field(..., description="abs(log(HR)) - importance score")
    effect_direction: Literal["protective", "harmful"]
    
    # Optimal values (CRITICAL for calculation)
    optimal_value: OptimalValue
    comparison_groups: ComparisonGroups
    
    # Population characteristics
    population: PopulationCharacteristics
    
    # Study quality
    quality: StudyQuality
    
    # Metadata
    pmid: Optional[int] = None
    cohort_name: Optional[str] = None
    
    # Raw data (for reference only)
    raw_groups_compared: str
    
    # Calculation instructions
    calculation_method: str = Field(..., description="How to calculate user's risk from their value")


# ============================================================================
# LLM PARSING FUNCTIONS
# ============================================================================

class LLMBiomarkerParser:
    """Parse biomarker studies using OpenAI"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        
    def create_parsing_prompt(self, row: pd.Series) -> str:
        """Create prompt for parsing a single study"""
        
        prompt = f"""Parse this biomarker study into structured JSON. Be PRECISE and extract ALL numerical values.

STUDY DATA:
- Biomarker: {row.get('Biomarker', 'N/A')}
- Category: {row.get('Category', 'N/A')}
- Detail: {row.get('Detail', 'N/A')}
- Groups Compared: {row.get('Groups compared', 'N/A')}
- Hazard Ratio: {row.get('Effect Size', 'N/A')}
- Effect Size Type: {row.get('Effect Size Type', 'N/A')}
- Unit: {row.get('Unit', 'N/A')}
- P-value: {row.get('P value', 'N/A')}
- Sex: {row.get('Sex', 'N/A')}
- Follow-up: {row.get('Follow-up', 'N/A')}
- # Subjects: {row.get('# Subjects', 'N/A')}
- # Deaths: {row.get('# Deaths', 'N/A')}
- Population: {row.get('Population', 'N/A')}
- Cohort: {row.get('Cohort', 'N/A')}

INSTRUCTIONS:
1. Parse "Groups Compared" carefully to extract:
   - What are the two groups? (e.g., "BMI >30" vs "BMI 18.5-25")
   - What are the exact numerical values?
   - Which group is optimal (lower mortality)? If HR < 1, group1 is better. If HR > 1, group2 is better.

2. Determine optimal value type:
   - "range": if optimal is a range (e.g., 18.5-25 kg/m²)
   - "threshold": if optimal is above/below a value (e.g., >60 mg/dL)
   - "direction_only": if "per unit increase/decrease" with no specific target
   - "percentile": if comparison is by percentile/quartile
   - "unparseable": if truly cannot parse

3. Extract population characteristics:
   - Parse sex: "males", "females", "both", or "unknown"
   - Extract age range if mentioned
   - Parse follow-up duration (convert to years)

4. Create calculation method (be SPECIFIC):
   - If range: "Compare user's value to optimal range [X, Y]. Calculate RR = HR^((distance)/unit)"
   - If per-unit: "Calculate RR = HR^((user_value - baseline_value) / per_unit_amount)"
   - Be specific about the formula

RETURN VALID JSON matching this schema (no markdown, just JSON):
{{
  "biomarker_name": "string",
  "biomarker_category": "string",
  "biomarker_detail": "string or null",
  "hazard_ratio": float,
  "effect_magnitude": float (abs(log(HR))),
  "effect_direction": "protective" or "harmful",
  "optimal_value": {{
    "type": "range" | "threshold" | "direction_only" | "percentile" | "unparseable",
    "value": float or null,
    "range_low": float or null,
    "range_high": float or null,
    "unit": "string or null",
    "direction": "higher_is_better" | "lower_is_better" | null,
    "percentile": int or null,
    "per_unit_change": float or null,
    "per_unit_amount": float or null
  }},
  "comparison_groups": {{
    "group1_description": "string",
    "group1_value_low": float or null,
    "group1_value_high": float or null,
    "group2_description": "string",
    "group2_value_low": float or null,
    "group2_value_high": float or null,
    "which_is_optimal": "group1" | "group2" | "unclear"
  }},
  "population": {{
    "sex": "males" | "females" | "both" | "unknown",
    "age_min": int or null,
    "age_max": int or null,
    "age_mean": float or null,
    "n_subjects": int or null,
    "n_deaths": int or null,
    "follow_up_years": float or null,
    "ethnicity": "string or null",
    "health_status": "string or null"
  }},
  "quality": {{
    "p_value": float or null,
    "confidence_interval_low": float or null,
    "confidence_interval_high": float or null,
    "n_subjects": int or null,
    "study_design": "string or null",
    "adjustments": "string or null"
  }},
  "pmid": int or null,
  "cohort_name": "string or null",
  "raw_groups_compared": "string",
  "calculation_method": "string (detailed formula)"
}}"""
        
        return prompt
    
    def parse_single_study(self, row: pd.Series, retry_count: int = 3) -> Optional[BiomarkerStudy]:
        """Parse a single study with retries"""
        
        for attempt in range(retry_count):
            try:
                prompt = self.create_parsing_prompt(row)
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a precise medical data parser. Return ONLY valid JSON, no markdown."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0,  # Deterministic
                    response_format={"type": "json_object"}
                )
                
                # Parse JSON response
                result_json = json.loads(response.choices[0].message.content)
                
                # Calculate effect magnitude if not provided
                hr = result_json.get('hazard_ratio', 1.0)
                if hr > 0:
                    result_json['effect_magnitude'] = abs(math.log(hr))
                else:
                    result_json['effect_magnitude'] = 0
                
                # Validate with Pydantic
                study = BiomarkerStudy(**result_json)
                return study
                
            except Exception as e:
                if attempt == retry_count - 1:
                    print(f"Failed to parse after {retry_count} attempts: {e}")
                    return None
                time.sleep(1)  # Wait before retry
        
        return None
    
    def parse_all_studies(self, results_df: pd.DataFrame, 
                         max_workers: int = 10,
                         limit: Optional[int] = None) -> List[BiomarkerStudy]:
        """Parse all studies in parallel"""
        
        rows_to_process = results_df.head(limit) if limit else results_df
        total = len(rows_to_process)
        
        print(f"Parsing {total} studies with {max_workers} parallel workers...")
        print(f"Estimated cost: ${total * 0.0001:.2f} (using {self.model})")
        print(f"Estimated time: {total / max_workers * 0.7 / 60:.1f} minutes\n")
        
        parsed_studies = []
        failed_count = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_row = {
                executor.submit(self.parse_single_study, row): idx 
                for idx, row in rows_to_process.iterrows()
            }
            
            # Process completed tasks with progress bar
            with tqdm(total=total, desc="Parsing studies") as pbar:
                for future in as_completed(future_to_row):
                    result = future.result()
                    if result:
                        parsed_studies.append(result)
                    else:
                        failed_count += 1
                    pbar.update(1)
        
        print(f"\n✅ Successfully parsed: {len(parsed_studies)}/{total}")
        print(f"❌ Failed: {failed_count}/{total}")
        
        return parsed_studies


# ============================================================================
# DATABASE BUILDING & EXPORT
# ============================================================================

def build_complete_database(parsed_studies: List[BiomarkerStudy]) -> Dict:
    """Build ONE complete database with everything"""
    
    # Group studies by biomarker
    biomarkers = {}
    
    for study in parsed_studies:
        biomarker = study.biomarker_name
        
        if biomarker not in biomarkers:
            biomarkers[biomarker] = {
                "biomarker_name": biomarker,
                "category": study.biomarker_category,
                "studies": [],
                "best_study": None,
                "max_effect_magnitude": 0
            }
        
        # Add study
        study_dict = study.model_dump()
        biomarkers[biomarker]["studies"].append(study_dict)
        
        # Track best study (highest effect magnitude)
        if study.effect_magnitude > biomarkers[biomarker]["max_effect_magnitude"]:
            biomarkers[biomarker]["max_effect_magnitude"] = study.effect_magnitude
            biomarkers[biomarker]["best_study"] = study_dict
    
    # Build final database structure
    database = {
        "metadata": {
            "total_studies": len(parsed_studies),
            "total_biomarkers": len(biomarkers),
            "categories": list(set(s.biomarker_category for s in parsed_studies)),
            "parseable_count": sum(1 for s in parsed_studies if s.optimal_value.type != "unparseable"),
            "generation_date": time.strftime("%Y-%m-%d %H:%M:%S")
        },
        "biomarkers": {}
    }
    
    # Add all biomarkers sorted by importance (effect magnitude)
    sorted_biomarkers = sorted(
        biomarkers.items(),
        key=lambda x: x[1]["max_effect_magnitude"],
        reverse=True
    )
    
    for rank, (name, data) in enumerate(sorted_biomarkers, 1):
        database["biomarkers"][name] = {
            "rank": rank,  # Importance rank
            "biomarker_name": name,
            "category": data["category"],
            "max_effect_magnitude": round(data["max_effect_magnitude"], 3),
            "best_study": data["best_study"],  # Most important study for this biomarker
            "all_studies": data["studies"],  # All studies for reference
            "study_count": len(data["studies"])
        }
    
    return database


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution"""
    
    # Get API key from .env file
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not found!")
        print("Please create a .env file in db/biomarkers/ with:")
        print("OPENAI_API_KEY=your-api-key-here")
        return
    
    # Load data
    print("Loading mortality predictors database...")
    results_df = pd.read_csv("data/results.csv")
    print(f"Loaded {len(results_df)} studies\n")
    
    # Initialize parser
    parser = LLMBiomarkerParser(api_key=api_key, model="gpt-4o-mini")
    
    # FOR TESTING: Start with just 10 studies
    # Remove limit=10 to process all 1587
    parsed_studies = parser.parse_all_studies(results_df, max_workers=10)
    
    if not parsed_studies:
        print("No studies parsed successfully!")
        return
    
    # Build complete database (ONE file with everything)
    print("\nBuilding complete database...")
    database = build_complete_database(parsed_studies)
    
    # Export ONE database file
    print("\nExporting database...")
    output_file = "data/biomarkers_database.json"
    with open(output_file, 'w') as f:
        json.dump(database, f, indent=2)
    print(f"✅ Exported: {output_file}")
    
    # Display summary
    print("\n" + "="*80)
    print("DATABASE SUMMARY")
    print("="*80)
    print(f"Total Studies Parsed: {database['metadata']['total_studies']}")
    print(f"Unique Biomarkers: {database['metadata']['total_biomarkers']}")
    print(f"Parseable Optimal Values: {database['metadata']['parseable_count']}")
    print(f"Categories: {', '.join(database['metadata']['categories'])}")
    
    # Display top 10 biomarkers
    print("\n" + "="*80)
    print("TOP 10 MOST IMPORTANT BIOMARKERS (by effect magnitude)")
    print("="*80)
    
    top_10 = list(database['biomarkers'].items())[:10]
    for name, data in top_10:
        best = data['best_study']
        print(f"\n{data['rank']}. {name} ({data['category']})")
        print(f"   Effect Magnitude: {data['max_effect_magnitude']}")
        print(f"   Hazard Ratio: {best['hazard_ratio']:.2f} ({best['effect_direction']})")
        print(f"   Optimal: {best['optimal_value']['type']}")
        if best['optimal_value'].get('range_low'):
            print(f"   Range: {best['optimal_value']['range_low']}-{best['optimal_value']['range_high']} {best['optimal_value'].get('unit', '')}")
        print(f"   Studies: {data['study_count']}")
    
    print("\n" + "="*80)
    print(f"✅ COMPLETE! All data in: {output_file}")
    print(f"📊 Database ready for production use")
    print("="*80)


if __name__ == "__main__":
    main()
