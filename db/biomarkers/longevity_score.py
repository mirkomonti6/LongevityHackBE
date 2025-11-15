#!/usr/bin/env python3
"""
🌟 LONGEVITY SCORE CALCULATOR 🌟
=================================
Positive, playful framing of biomarker health.

Instead of "You'll die 23 years early!"
We say: "Level up your health score and unlock bonus years! 🎮"
"""

import json
import math
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class BiomarkerMeasurement:
    """A single biomarker measurement"""
    name: str
    value: float
    unit: str
    source: str


@dataclass
class LongevityImpact:
    """The impact of one biomarker on longevity"""
    biomarker_name: str
    user_value: float
    optimal_range: str
    is_optimal: bool
    
    # REAL data from studies
    hazard_ratio: float
    study_survival_rate_optimal: float  # % who survived in optimal group
    study_survival_rate_user: float      # % who survived in user's group
    study_follow_up_years: float         # How long the study lasted
    
    # Positive scores
    health_score: int  # 0-100 (100 = optimal)
    potential_gain_years: float  # How many years you could gain
    
    category: str


class LongevityScoreCalculator:
    """
    Calculates POSITIVE longevity scores with REAL data from studies.
    """
    
    # Biomarker groups (correlated markers - don't sum independently)
    BIOMARKER_GROUPS = {
        'body_composition': [
            'body mass index', 'bmi', 'body fat', 'waist', 'waist circumference',
            'waist-to-hip', 'body weight', 'obesity'
        ],
        'lipids': [
            'cholesterol', 'ldl', 'hdl', 'triglyceride', 'apolipoprotein',
            'lipoprotein'
        ],
        'glucose_metabolism': [
            'glucose', 'hba1c', 'hemoglobin a1c', 'glycated', 'insulin',
            'diabetes'
        ],
        'inflammation': [
            'c-reactive protein', 'crp', 'white blood cell', 'wbc',
            'inflammation', 'interleukin'
        ],
        'blood_cells': [
            'hemoglobin', 'hematocrit', 'red blood cell', 'lymphocyte',
            'platelet', 'mean corpuscular'
        ],
        'cardiovascular': [
            'blood pressure', 'heart rate', 'pulse', 'systolic', 'diastolic'
        ],
        'kidney': [
            'creatinine', 'urea', 'egfr', 'albumin', 'protein'
        ],
        'liver': [
            'alt', 'ast', 'gamma-glutamyl', 'ggt', 'bilirubin', 'alkaline phosphatase'
        ],
        'fitness': [
            'vo2', 'exercise capacity', 'mets', 'grip strength', 'gait speed',
            'physical', 'peak expiratory'
        ],
        'hormones': [
            'testosterone', 'estrogen', 'vitamin d', 'thyroid', 'cortisol'
        ]
    }
    
    def __init__(self, database_path: str = "data/biomarkers_database.json"):
        with open(database_path, 'r') as f:
            self.db = json.load(f)
        print(f"✨ Loaded {self.db['metadata']['total_biomarkers']} biomarkers")
    
    def _normalize_name(self, name: str) -> Optional[str]:
        """
        Smart word-based biomarker matching.
        Prevents false matches like 'ph' in 'lymphocyte'.
        """
        name_lower = name.lower().strip()
        
        # Try exact match first
        for db_name in self.db['biomarkers'].keys():
            if name_lower == db_name.lower():
                return db_name
        
        # Word-based matching
        name_words = set(name_lower.split())
        best_match = None
        best_score = 0
        
        for db_name in self.db['biomarkers'].keys():
            db_words = set(db_name.lower().split())
            
            # Count overlapping words
            overlap = len(name_words & db_words)
            if overlap == 0:
                continue
            
            # Score: overlap / total unique words
            score = overlap / len(name_words | db_words)
            
            if score > best_score and score >= 0.5:  # At least 50% word overlap
                best_score = score
                best_match = db_name
        
        return best_match
    
    def _find_biomarker_group(self, biomarker_name: str) -> str:
        """Find which group this biomarker belongs to (for correlation handling)"""
        name_lower = biomarker_name.lower()
        
        for group_name, keywords in self.BIOMARKER_GROUPS.items():
            for keyword in keywords:
                if keyword in name_lower:
                    return group_name
        
        # If not in any group, treat as independent
        return f"independent_{biomarker_name}"
    
    def _get_best_realistic_study(self, biomarker_data: Dict) -> Optional[Dict]:
        """
        Get best study that is realistic (not composite, not extreme HR).
        Filters out confounded studies with multiple biomarkers combined.
        """
        all_studies = biomarker_data.get('all_studies', [])
        
        # Filter 1: Single biomarker only (no composites)
        single_biomarker_studies = []
        for study in all_studies:
            name = study['biomarker_name']
            # Exclude if has comma or + (indicates multiple biomarkers)
            if ',' not in name and '+' not in name and ' and ' not in name.lower():
                single_biomarker_studies.append(study)
        
        if not single_biomarker_studies:
            # Fallback to best_study if no singles found
            return biomarker_data.get('best_study')
        
        # Filter 2: Reasonable hazard ratios (0.3 to 3.0)
        # Extreme HRs often indicate confounding or extreme populations
        reasonable_studies = []
        for study in single_biomarker_studies:
            hr = study['hazard_ratio']
            if 0.3 <= hr <= 3.0:
                reasonable_studies.append(study)
        
        if not reasonable_studies:
            # If all HRs are extreme, use the least extreme
            reasonable_studies = sorted(single_biomarker_studies, 
                                       key=lambda s: abs(math.log(s['hazard_ratio'])))[:1]
        
        # Filter 3: Has required data
        valid_studies = []
        for study in reasonable_studies:
            pop = study.get('population', {})
            if pop.get('n_subjects') and pop.get('n_deaths') and pop.get('follow_up_years'):
                valid_studies.append(study)
        
        if not valid_studies:
            return biomarker_data.get('best_study')
        
        # Filter 4: Prefer studies with range or threshold data over "direction_only"
        # direction_only studies can't properly score extreme values
        studies_with_ranges = []
        for study in valid_studies:
            opt_type = study.get('optimal_value', {}).get('type')
            if opt_type in ['range', 'threshold']:
                studies_with_ranges.append(study)
        
        # Use range-based studies if available, otherwise use all valid studies
        selection_pool = studies_with_ranges if studies_with_ranges else valid_studies
        
        # Select median by effect magnitude (not most extreme)
        selection_pool.sort(key=lambda s: s['effect_magnitude'])
        median_idx = len(selection_pool) // 2
        
        return selection_pool[median_idx]
    
    def _calculate_survival_rates(self, study_data: Dict) -> tuple:
        """
        Calculate REAL survival rates from study data.
        
        Returns: (survival_rate_optimal, survival_rate_user, follow_up_years)
        """
        pop = study_data['population']
        
        n_subjects = pop.get('n_subjects')
        n_deaths = pop.get('n_deaths')
        follow_up_years = pop.get('follow_up_years')
        
        # Need all three values to calculate
        if not n_subjects or not n_deaths or not follow_up_years:
            return None, None, follow_up_years or 10
        
        # Overall survival rate in the study
        overall_survival_rate = (n_subjects - n_deaths) / n_subjects
        
        # Calculate survival for optimal vs user's group using HR
        hr = study_data['hazard_ratio']
        
        # If HR < 1 (protective), optimal group has BETTER survival
        # If HR > 1 (risk), optimal group has WORSE survival
        
        # Use exponential survival model: S(t) = e^(-hazard * time)
        # For comparative group, hazard_ratio tells us the multiplier
        
        if study_data['effect_direction'] == 'protective':
            # Being in optimal group reduces hazard
            # Baseline hazard (suboptimal group)
            baseline_annual_mortality = -math.log(overall_survival_rate) / follow_up_years
            
            # Optimal group has lower hazard
            optimal_annual_mortality = baseline_annual_mortality * hr
            user_annual_mortality = baseline_annual_mortality
            
            survival_optimal = math.exp(-optimal_annual_mortality * follow_up_years)
            survival_user = math.exp(-user_annual_mortality * follow_up_years)
        else:
            # Risk factor: being suboptimal increases hazard
            baseline_annual_mortality = -math.log(overall_survival_rate) / follow_up_years
            
            optimal_annual_mortality = baseline_annual_mortality
            user_annual_mortality = baseline_annual_mortality * hr
            
            survival_optimal = math.exp(-optimal_annual_mortality * follow_up_years)
            survival_user = math.exp(-user_annual_mortality * follow_up_years)
        
        return survival_optimal, survival_user, follow_up_years
    
    def _calculate_health_score(self, user_value: float, optimal_data: Dict, hr: float, direction: str) -> tuple:
        """
        Calculate health score (0-100) and whether user is optimal.
        Returns: (health_score, is_optimal)
        """
        opt_type = optimal_data['type']
        
        # Range optimal
        if opt_type == 'range':
            range_low = optimal_data.get('range_low')
            range_high = optimal_data.get('range_high')
            
            # Handle case where range values are None
            if range_low is None or range_high is None:
                return 80, False  # Can't calculate without range values
            
            if range_low <= user_value <= range_high:
                return 100, True
            
            # Calculate distance from range
            if user_value < range_low:
                distance = range_low - user_value
                range_width = range_high - range_low
            else:
                distance = user_value - range_high
                range_width = range_high - range_low
            
            # Score decreases with distance (normalized)
            distance_normalized = min(distance / range_width, 2.0)  # Cap at 2x range width
            score = max(0, 100 - (distance_normalized * 40))  # Lose up to 80 points
            
            return int(score), False
        
        # Threshold
        elif opt_type == 'threshold':
            threshold = optimal_data.get('value')
            direction = optimal_data.get('direction', 'higher_is_better')
            
            # Handle case where threshold value is None
            if threshold is None:
                return 80, False  # Can't calculate without threshold value
            
            if direction == 'higher_is_better':
                if user_value >= threshold:
                    return 100, True
                distance_pct = (threshold - user_value) / threshold
            else:
                if user_value <= threshold:
                    return 100, True
                distance_pct = (user_value - threshold) / threshold
            
            score = max(0, 100 - (distance_pct * 80))
            return int(score), False
        
        # For other types, use HR to estimate
        else:
            # Can't calculate exact score without knowing user's position
            return 80, False  # Assume moderate
    
    def _estimate_years_gain(self, survival_optimal: float, survival_user: float, 
                            follow_up_years: float, user_age: int = 50) -> float:
        """
        Estimate years you could GAIN by optimizing this biomarker.
        Uses REAL survival data from studies with conservative caps.
        """
        if survival_optimal is None or survival_user is None:
            return 0.0
        
        # Calculate annual mortality rates
        annual_mortality_optimal = 1 - math.pow(survival_optimal, 1/follow_up_years)
        annual_mortality_user = 1 - math.pow(survival_user, 1/follow_up_years)
        
        # Cap extreme mortality rates (indicates confounded study)
        annual_mortality_optimal = min(annual_mortality_optimal, 0.10)  # Max 10% per year
        annual_mortality_user = min(annual_mortality_user, 0.20)  # Max 20% per year
        
        # Expected remaining lifespan
        remaining_years = 85 - user_age  # Target lifespan 85
        
        # Expected years lived with each mortality rate
        if annual_mortality_user >= 1 or annual_mortality_user <= 0:
            expected_years_user = 0
        else:
            expected_years_user = (1 - math.pow(1 - annual_mortality_user, remaining_years)) / annual_mortality_user
        
        if annual_mortality_optimal >= 1 or annual_mortality_optimal <= 0:
            expected_years_optimal = 0
        else:
            expected_years_optimal = (1 - math.pow(1 - annual_mortality_optimal, remaining_years)) / annual_mortality_optimal
        
        years_gain = expected_years_optimal - expected_years_user
        
        # Cap individual biomarker bonus at 10 years (no single biomarker is worth more)
        years_gain = min(max(0, years_gain), 10.0)
        
        return years_gain
    
    def calculate_biomarker_impact(self, measurement: BiomarkerMeasurement, 
                                   user_age: int = 50) -> Optional[LongevityImpact]:
        """Calculate the longevity impact of one biomarker"""
        
        db_name = self._normalize_name(measurement.name)
        if not db_name:
            print(f"⚠️  Biomarker not found: {measurement.name}")
            return None
        
        biomarker_data = self.db['biomarkers'][db_name]
        
        # Use realistic study (filtered for composites and extreme HRs)
        best_study = self._get_best_realistic_study(biomarker_data)
        if not best_study:
            print(f"⚠️  No realistic study found for: {measurement.name}")
            return None
        
        # Calculate REAL survival rates from study data
        survival_optimal, survival_user, follow_up_years = self._calculate_survival_rates(best_study)
        
        # Calculate health score
        health_score, is_optimal = self._calculate_health_score(
            measurement.value,
            best_study['optimal_value'],
            best_study['hazard_ratio'],
            best_study['effect_direction']
        )
        
        # Calculate potential years gain (REAL calculation!)
        if survival_optimal and survival_user:
            years_gain = self._estimate_years_gain(survival_optimal, survival_user, 
                                                   follow_up_years, user_age)
        else:
            years_gain = 0
        
        # Format optimal range
        opt = best_study['optimal_value']
        if opt['type'] == 'range':
            optimal_range = f"{opt['range_low']}-{opt['range_high']} {opt.get('unit', '')}"
        elif opt['type'] == 'threshold':
            direction = opt.get('direction', 'higher_is_better')
            symbol = '>' if direction == 'higher_is_better' else '<'
            optimal_range = f"{symbol}{opt.get('value')} {opt.get('unit', '')}"
        else:
            optimal_range = opt['type']
        
        return LongevityImpact(
            biomarker_name=db_name,
            user_value=measurement.value,
            optimal_range=optimal_range,
            is_optimal=is_optimal,
            hazard_ratio=best_study['hazard_ratio'],
            study_survival_rate_optimal=survival_optimal or 0,
            study_survival_rate_user=survival_user or 0,
            study_follow_up_years=follow_up_years or 0,
            health_score=health_score,
            potential_gain_years=years_gain,
            category=biomarker_data['category']
        )
    
    def calculate_overall_score(self, impacts: List[LongevityImpact], user_age: int = 50) -> Dict:
        """
        Calculate overall longevity score (0-100).
        
        This is POSITIVE and PLAYFUL! 🎮
        """
        
        if not impacts:
            return {
                "overall_score": 100,
                "score_level": "🏆 LEGENDARY",
                "total_bonus_years": 0,
                "top_opportunity": None,
                "optimized_count": 0,
                "opportunities_count": 0
            }
        
        # Calculate weighted average health score
        total_weight = 0
        weighted_score = 0
        
        for impact in impacts:
            # Weight by effect magnitude (from database)
            biomarker_data = self.db['biomarkers'][impact.biomarker_name]
            weight = biomarker_data['max_effect_magnitude']
            
            weighted_score += impact.health_score * weight
            total_weight += weight
        
        overall_score = int(weighted_score / total_weight) if total_weight > 0 else 100
        
        # Calculate total bonus years available (accounting for correlations)
        non_optimal = [i for i in impacts if not i.is_optimal]
        
        # Group biomarkers by correlation
        grouped_bonuses = {}
        for impact in non_optimal:
            group = self._find_biomarker_group(impact.biomarker_name)
            if group not in grouped_bonuses:
                grouped_bonuses[group] = []
            grouped_bonuses[group].append(impact.potential_gain_years)
        
        # Take max from each group (correlated markers don't add independently)
        total_bonus_years = sum(max(years) for years in grouped_bonuses.values())
        
        # Find top opportunity (biggest gain)
        top_opportunity = None
        if non_optimal:
            top_opportunity = max(non_optimal, key=lambda i: i.potential_gain_years)
        
        # Score level (gamified!)
        if overall_score >= 90:
            level = "🏆 LEGENDARY"
        elif overall_score >= 80:
            level = "💎 DIAMOND"
        elif overall_score >= 70:
            level = "🥇 GOLD"
        elif overall_score >= 60:
            level = "🥈 SILVER"
        elif overall_score >= 50:
            level = "🥉 BRONZE"
        else:
            level = "🌱 ROOKIE (huge potential!)"
        
        optimized_count = sum(1 for i in impacts if i.is_optimal)
        
        return {
            "overall_score": overall_score,
            "score_level": level,
            "total_bonus_years": round(total_bonus_years, 1),
            "top_opportunity": {
                "biomarker": top_opportunity.biomarker_name,
                "current_score": top_opportunity.health_score,
                "bonus_years": round(top_opportunity.potential_gain_years, 1),
                "your_value": top_opportunity.user_value,
                "target": top_opportunity.optimal_range
            } if top_opportunity else None,
            "optimized_count": optimized_count,
            "opportunities_count": len(non_optimal),
            "user_age": user_age
        }


# ============================================================================
# SAMPLE DATA
# ============================================================================

def get_sample_measurements():
    """
    Sample biomarker data - realistic mix of blood tests and wearables.
    Some values are optimal, some need improvement.
    """
    return [
        # Blood lipids
        BiomarkerMeasurement("Cholesterol", 220, "mg/dL", "blood_test"),  # Slightly high
        BiomarkerMeasurement("Triglycerides", 180, "mg/dL", "blood_test"),  # High
        
        # Glucose metabolism
        BiomarkerMeasurement("Glucose", 105, "mg/dL", "blood_test"),  # Prediabetic range
        BiomarkerMeasurement("Hemoglobin", 16.5, "g/dL", "blood_test"),  # Normal
        
        # Inflammation
        BiomarkerMeasurement("C-reactive protein", 3.5, "mg/L", "blood_test"),  # Elevated
        
        # Blood cells
        BiomarkerMeasurement("Lymphocyte percentage", 25.0, "%", "blood_test"),  # Low
        BiomarkerMeasurement("Mean corpuscular volume", 95.5, "fL", "blood_test"),  # High
        
        # Physical measurements
        BiomarkerMeasurement("Body mass index", 28.5, "kg/m^2", "wearable"),  # Overweight
        BiomarkerMeasurement("Body fat percentage", 28.0, "%", "body_scan"),  # High
        BiomarkerMeasurement("Waist circumference", 95, "cm", "measurement"),  # High
        
        # Cardiovascular
        BiomarkerMeasurement("Resting heart rate", 75, "bpm", "wearable"),  # Slightly high
        BiomarkerMeasurement("Blood pressure", 135, "mmHg", "wearable"),  # Systolic, elevated
        
        # Fitness & function
        BiomarkerMeasurement("Exercise capacity", 5.5, "METs", "cardio_test"),  # Good
        BiomarkerMeasurement("Peak expiratory flow", 350, "L/min", "spirometry"),  # Low
        BiomarkerMeasurement("Lean mass index", 16.0, "kg/m^2", "body_scan"),  # Good
        
        # Vitamins & hormones
        BiomarkerMeasurement("25-hydroxyvitamin D", 22, "ng/mL", "blood_test"),  # Low
        BiomarkerMeasurement("Testosterone", 450, "ng/dL", "blood_test"),  # Normal for age
    ]


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("="*80)
    print("🌟 LONGEVITY SCORE CALCULATOR 🌟")
    print("="*80)
    print("Level up your health and unlock bonus years!\n")
    
    calculator = LongevityScoreCalculator()
    
    measurements = get_sample_measurements()
    user_age = 50
    
    print(f"📊 Analyzing {len(measurements)} biomarkers for age {user_age}...\n")
    
    # Calculate impacts
    impacts = []
    for m in measurements:
        impact = calculator.calculate_biomarker_impact(m, user_age)
        if impact:
            impacts.append(impact)
    
    # Display individual scores
    print("="*80)
    print("🎯 YOUR BIOMARKER HEALTH SCORES")
    print("="*80)
    
    impacts.sort(key=lambda i: i.health_score)
    
    for i, impact in enumerate(impacts, 1):
        status = "✅" if impact.is_optimal else "🎯"
        bar_length = int(impact.health_score / 5)
        bar = "█" * bar_length + "░" * (20 - bar_length)
        
        print(f"\n{i}. {impact.biomarker_name} {status}")
        print(f"   Score: {impact.health_score}/100 [{bar}]")
        print(f"   Your value: {impact.user_value}")
        print(f"   Target: {impact.optimal_range}")
        
        if not impact.is_optimal and impact.potential_gain_years > 0:
            print(f"   💚 Bonus potential: +{impact.potential_gain_years:.1f} years if optimized!")
    
    # Overall score
    print("\n" + "="*80)
    print("🏆 YOUR OVERALL LONGEVITY SCORE")
    print("="*80)
    
    overall = calculator.calculate_overall_score(impacts, user_age)
    
    print(f"\n   🎮 Score: {overall['overall_score']}/100")
    print(f"   🏅 Level: {overall['score_level']}")
    print(f"   ✅ Optimized: {overall['optimized_count']} biomarkers")
    print(f"   🎯 Opportunities: {overall['opportunities_count']} biomarkers")
    
    if overall['total_bonus_years'] > 0:
        print(f"\n   ✨ TOTAL BONUS AVAILABLE: +{overall['total_bonus_years']:.1f} YEARS! ✨")
    
    # Top opportunity
    if overall['top_opportunity']:
        print("\n" + "="*80)
        print("🚀 #1 OPPORTUNITY TO LEVEL UP")
        print("="*80)
        
        top = overall['top_opportunity']
        print(f"\n   ⚡ {top['biomarker']}")
        print(f"   Current score: {top['current_score']}/100")
        print(f"   Your value: {top['your_value']}")
        print(f"   Target: {top['target']}")
        print(f"\n   💎 UNLOCK: +{top['bonus_years']:.1f} BONUS YEARS")
        print(f"\n   💡 This is your biggest opportunity! Optimizing this")
        print(f"      biomarker alone could add {top['bonus_years']:.1f} years to your life!")
    
    print("\n" + "="*80)
    print("✨ Every point you improve = more years unlocked! ✨")
    print("="*80)


if __name__ == "__main__":
    main()
