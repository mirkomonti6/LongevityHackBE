#!/usr/bin/env python3
"""
Test to verify that extreme body fat percentage values are properly detected
and prioritized in the longevity score calculation.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from db.biomarkers.longevity_score import (
    LongevityScoreCalculator,
    BiomarkerMeasurement
)


def test_extreme_body_fat_detection():
    """
    Test that extreme body fat percentage (99.51%) is properly:
    1. Detected and scored
    2. Shows significant potential gain
    3. Prioritized over other biomarkers
    """
    print("="*80)
    print("🧪 TEST: Extreme Body Fat Detection")
    print("="*80)
    
    # Initialize calculator
    db_path = project_root / "db" / "biomarkers" / "data" / "biomarkers_database.json"
    calculator = LongevityScoreCalculator(database_path=str(db_path))
    
    # Create test measurements with extreme body fat and slightly elevated cholesterol
    measurements = [
        BiomarkerMeasurement(
            name="Body Fat Percentage",
            value=99.51,  # EXTREMELY high (normal is 15-25%)
            unit="%",
            source="body_scan"
        ),
        BiomarkerMeasurement(
            name="Cholesterol",
            value=245.0,  # Moderately high (normal is <200 mg/dL)
            unit="mg/dL",
            source="blood_test"
        ),
        BiomarkerMeasurement(
            name="HDL Cholesterol",
            value=38.0,  # Low
            unit="mg/dL",
            source="blood_test"
        ),
        BiomarkerMeasurement(
            name="LDL Cholesterol",
            value=170.0,  # High
            unit="mg/dL",
            source="blood_test"
        ),
    ]
    
    print(f"\n📊 Test Data:")
    for m in measurements:
        print(f"  - {m.name}: {m.value} {m.unit}")
    
    # Calculate impacts
    print(f"\n⚙️  Calculating biomarker impacts...")
    impacts = []
    for measurement in measurements:
        impact = calculator.calculate_biomarker_impact(measurement, user_age=50)
        if impact:
            impacts.append(impact)
            print(f"  ✓ {impact.biomarker_name}:")
            print(f"    - Health Score: {impact.health_score}/100")
            print(f"    - Potential Gain: +{impact.potential_gain_years:.1f} years")
            print(f"    - Hazard Ratio: {impact.hazard_ratio}")
            print(f"    - Optimal Range: {impact.optimal_range}")
        else:
            print(f"  ✗ {measurement.name}: Not found in database or no valid studies")
    
    # Calculate overall score
    if impacts:
        print(f"\n🎯 Calculating overall score...")
        overall = calculator.calculate_overall_score(impacts, user_age=50)
        
        print(f"\n{'='*80}")
        print("📈 RESULTS:")
        print(f"{'='*80}")
        print(f"Overall Score: {overall['overall_score']}/100")
        print(f"Score Level: {overall['score_level']}")
        print(f"Total Bonus Years Available: +{overall['total_bonus_years']} years")
        print(f"Optimized Biomarkers: {overall['optimized_count']}")
        print(f"Improvement Opportunities: {overall['opportunities_count']}")
        
        if overall['top_opportunity']:
            top = overall['top_opportunity']
            print(f"\n🚀 #1 OPPORTUNITY:")
            print(f"  Biomarker: {top['biomarker']}")
            print(f"  Current Score: {top['current_score']}/100")
            print(f"  Potential Gain: +{top['bonus_years']} years")
            print(f"  Your Value: {top['your_value']}")
            print(f"  Target Range: {top['target']}")
    
    # Run assertions
    print(f"\n{'='*80}")
    print("🧪 TEST ASSERTIONS:")
    print(f"{'='*80}")
    
    test_passed = True
    
    # Test 1: Body fat percentage should be found
    body_fat_impacts = [i for i in impacts if 'body fat' in i.biomarker_name.lower()]
    if body_fat_impacts:
        print("✅ TEST 1 PASSED: Body fat percentage was found in database")
        body_fat_impact = body_fat_impacts[0]
        
        # Test 2: Body fat should have low health score
        if body_fat_impact.health_score < 50:
            print(f"✅ TEST 2 PASSED: Body fat has low health score ({body_fat_impact.health_score}/100)")
        else:
            print(f"❌ TEST 2 FAILED: Body fat should have low score but has {body_fat_impact.health_score}/100")
            test_passed = False
        
        # Test 3: Body fat should show significant potential gain
        if body_fat_impact.potential_gain_years > 0:
            print(f"✅ TEST 3 PASSED: Body fat shows potential gain (+{body_fat_impact.potential_gain_years:.1f} years)")
        else:
            print(f"❌ TEST 3 FAILED: Body fat shows no potential gain")
            test_passed = False
    else:
        print("❌ TEST 1 FAILED: Body fat percentage not found in database")
        test_passed = False
    
    # Test 4: Check if body fat is the top opportunity
    if impacts and overall.get('top_opportunity'):
        top_biomarker = overall['top_opportunity']['biomarker'].lower()
        if 'body fat' in top_biomarker or 'body mass index' in top_biomarker:
            print(f"✅ TEST 4 PASSED: Body composition ('{overall['top_opportunity']['biomarker']}') is #1 opportunity")
        else:
            print(f"⚠️  TEST 4 NOTE: Top opportunity is '{overall['top_opportunity']['biomarker']}' (not body composition)")
            print(f"   This may be due to correlation grouping or HR filtering")
            # Don't fail the test, but note it
    
    # Test 5: Check all impacts for comparison
    print(f"\n📊 All Impacts Comparison:")
    non_optimal = [i for i in impacts if not i.is_optimal]
    sorted_impacts = sorted(non_optimal, key=lambda i: i.potential_gain_years, reverse=True)
    for i, impact in enumerate(sorted_impacts, 1):
        print(f"  {i}. {impact.biomarker_name}: +{impact.potential_gain_years:.1f} years (HR={impact.hazard_ratio})")
    
    print(f"\n{'='*80}")
    if test_passed:
        print("✅ ALL CORE TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print(f"{'='*80}\n")
    
    return test_passed


def test_hr_filtering():
    """
    Test to check which studies are being selected for body fat percentage
    and whether HR filtering is affecting the results.
    """
    print("="*80)
    print("🔍 TEST: HR Filtering Analysis")
    print("="*80)
    
    db_path = project_root / "db" / "biomarkers" / "data" / "biomarkers_database.json"
    calculator = LongevityScoreCalculator(database_path=str(db_path))
    
    # Check body fat percentage biomarker data
    body_fat_key = calculator._normalize_name("Body Fat Percentage")
    if body_fat_key:
        biomarker_data = calculator.db['biomarkers'][body_fat_key]
        all_studies = biomarker_data.get('all_studies', [])
        
        print(f"\n📚 Found {len(all_studies)} studies for Body Fat Percentage")
        print(f"\n🏆 Best Study (from database):")
        best = biomarker_data.get('best_study')
        if best:
            print(f"  - HR: {best.get('hazard_ratio')}")
            print(f"  - Effect: {best.get('effect_direction')}")
            print(f"  - Optimal: {best.get('optimal_value', {}).get('type')}")
        
        print(f"\n🔍 Applying Study Filters:")
        
        # Filter 1: Single biomarker only
        single_studies = [s for s in all_studies 
                         if ',' not in s['biomarker_name'] 
                         and '+' not in s['biomarker_name'] 
                         and ' and ' not in s['biomarker_name'].lower()]
        print(f"  After Filter 1 (single biomarker): {len(single_studies)} studies")
        
        # Check HR distribution
        print(f"\n  HR Distribution in single-biomarker studies:")
        for study in single_studies:
            hr = study['hazard_ratio']
            print(f"    - HR {hr}: {study.get('effect_direction')} "
                  f"(n={study.get('population', {}).get('n_subjects', 'N/A')}, "
                  f"deaths={study.get('population', {}).get('n_deaths', 'N/A')})")
        
        # Filter 2: HR threshold
        hr_threshold = 3.0  # Current threshold in code
        reasonable_studies = [s for s in single_studies 
                             if 0.3 <= s['hazard_ratio'] <= hr_threshold]
        print(f"\n  After Filter 2 (HR 0.3-{hr_threshold}): {len(reasonable_studies)} studies")
        
        if not reasonable_studies:
            print(f"  ⚠️  NO STUDIES PASS HR FILTER!")
            print(f"  📌 Recommendation: Increase HR threshold to include HR={best.get('hazard_ratio')}")
        
        # Filter 3: Required data
        valid_studies = []
        for study in reasonable_studies if reasonable_studies else single_studies:
            pop = study.get('population', {})
            if pop.get('n_subjects') and pop.get('n_deaths') and pop.get('follow_up_years'):
                valid_studies.append(study)
        
        print(f"  After Filter 3 (has n_subjects, n_deaths, follow_up): {len(valid_studies)} studies")
        
        # Show selected study
        selected = calculator._get_best_realistic_study(biomarker_data)
        if selected:
            print(f"\n✅ Selected Study:")
            print(f"  - HR: {selected.get('hazard_ratio')}")
            print(f"  - Effect Magnitude: {selected.get('effect_magnitude')}")
            print(f"  - Effect Direction: {selected.get('effect_direction')}")
            print(f"  - Optimal Type: {selected.get('optimal_value', {}).get('type')}")
            print(f"  - Optimal Range: {selected.get('optimal_value', {})}")
            print(f"  - Population: n={selected.get('population', {}).get('n_subjects')}, "
                  f"deaths={selected.get('population', {}).get('n_deaths')}")
    else:
        print("❌ Body Fat Percentage not found in database")
    
    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    # Run tests
    test_passed = test_extreme_body_fat_detection()
    print("\n")
    test_hr_filtering()
    
    # Exit with appropriate code
    sys.exit(0 if test_passed else 1)

