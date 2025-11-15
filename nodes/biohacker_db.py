"""
Biohacker Interventions Database

Mock database containing evidence-based health interventions with scientific references.
Each intervention targets specific biomarkers and includes actionable recommendations.
"""

INTERVENTIONS_DB = [
    {
        "id": "vitamin-d-supplementation",
        "category": "supplements",
        "name": "Vitamin D3 Supplementation",
        "target_biomarkers": ["vitamin_d"],
        "description": "Optimize vitamin D levels for immune function, bone health, and longevity",
        "scientific_references": [
            {
                "study": "Vitamin D and mortality: meta-analysis of individual participant data",
                "authors": "Schöttker et al.",
                "year": 2013,
                "journal": "American Journal of Clinical Nutrition",
                "pmid": "23783290",
                "key_findings": "Higher vitamin D levels associated with reduced all-cause mortality"
            }
        ],
        "dosage": "2000-4000 IU daily, adjust based on blood levels",
        "expected_improvement": "Increase vitamin D to optimal range (40-60 ng/mL) within 8-12 weeks",
        "contraindications": ["hypercalcemia", "kidney disease"],
        "priority_score": 8
    },
    {
        "id": "omega-3-supplementation",
        "category": "supplements",
        "name": "Omega-3 Fatty Acids (EPA/DHA)",
        "target_biomarkers": ["triglycerides", "hdl", "crp"],
        "description": "Reduce inflammation and improve cardiovascular markers",
        "scientific_references": [
            {
                "study": "Omega-3 fatty acids and cardiovascular disease",
                "authors": "Mozaffarian & Wu",
                "year": 2011,
                "journal": "Journal of the American College of Cardiology",
                "pmid": "22115647",
                "key_findings": "Omega-3s reduce triglycerides by 25-30% and lower cardiovascular risk"
            }
        ],
        "dosage": "2-4g EPA+DHA daily with meals",
        "expected_improvement": "Reduce triglycerides 15-30%, improve HDL/LDL ratio within 8 weeks",
        "contraindications": ["bleeding disorders", "fish allergy"],
        "priority_score": 7
    },
    {
        "id": "berberine-glucose",
        "category": "supplements",
        "name": "Berberine for Glucose Control",
        "target_biomarkers": ["glucose", "hba1c", "insulin"],
        "description": "Natural compound that improves insulin sensitivity and glucose metabolism",
        "scientific_references": [
            {
                "study": "Efficacy of berberine in patients with type 2 diabetes mellitus",
                "authors": "Yin et al.",
                "year": 2008,
                "journal": "Metabolism",
                "pmid": "18442638",
                "key_findings": "Berberine reduces fasting glucose and HbA1c similar to metformin"
            }
        ],
        "dosage": "500mg three times daily with meals",
        "expected_improvement": "Reduce fasting glucose 10-20%, HbA1c 0.5-1.0% within 12 weeks",
        "contraindications": ["pregnancy", "hypoglycemia"],
        "priority_score": 9
    },
    {
        "id": "hiit-training",
        "category": "exercise",
        "name": "High-Intensity Interval Training (HIIT)",
        "target_biomarkers": ["glucose", "insulin", "triglycerides", "hdl"],
        "description": "Time-efficient exercise protocol for metabolic health",
        "scientific_references": [
            {
                "study": "HIIT improves insulin sensitivity in adults",
                "authors": "Jelleyman et al.",
                "year": 2015,
                "journal": "Journal of Sports Medicine",
                "pmid": "25771785",
                "key_findings": "HIIT significantly improves insulin sensitivity and glucose control"
            }
        ],
        "dosage": "20-30 minutes, 3x per week (30 sec high intensity, 90 sec recovery)",
        "expected_improvement": "Improve insulin sensitivity 15-25%, reduce glucose 10-15% within 8 weeks",
        "contraindications": ["cardiovascular disease", "severe joint problems"],
        "priority_score": 8
    },
    {
        "id": "mediterranean-diet",
        "category": "diet",
        "name": "Mediterranean Diet Pattern",
        "target_biomarkers": ["ldl", "hdl", "triglycerides", "crp", "glucose"],
        "description": "Anti-inflammatory diet rich in olive oil, fish, vegetables, and whole grains",
        "scientific_references": [
            {
                "study": "Mediterranean diet and longevity",
                "authors": "Trichopoulou et al.",
                "year": 2003,
                "journal": "New England Journal of Medicine",
                "pmid": "12944570",
                "key_findings": "Mediterranean diet associated with 25% reduction in mortality"
            }
        ],
        "dosage": "Daily: vegetables, olive oil, fish 3x/week, minimal processed foods",
        "expected_improvement": "Reduce LDL 10-15%, CRP 20-30% within 12 weeks",
        "contraindications": ["none"],
        "priority_score": 9
    },
    {
        "id": "sleep-optimization",
        "category": "sleep",
        "name": "Sleep Hygiene and Duration Optimization",
        "target_biomarkers": ["glucose", "crp", "cortisol"],
        "description": "Optimize sleep quality and duration for metabolic health",
        "scientific_references": [
            {
                "study": "Sleep duration and metabolic syndrome",
                "authors": "Knutson et al.",
                "year": 2010,
                "journal": "Sleep",
                "pmid": "20337191",
                "key_findings": "7-8 hours sleep associated with optimal metabolic health"
            }
        ],
        "dosage": "7-8 hours nightly, consistent schedule, dark/cool environment",
        "expected_improvement": "Improve glucose control 5-10%, reduce inflammation within 4 weeks",
        "contraindications": ["none"],
        "priority_score": 8
    },
    {
        "id": "resistance-training",
        "category": "exercise",
        "name": "Progressive Resistance Training",
        "target_biomarkers": ["glucose", "insulin", "hba1c"],
        "description": "Build muscle mass to improve glucose disposal and insulin sensitivity",
        "scientific_references": [
            {
                "study": "Resistance training improves glycemic control",
                "authors": "Gordon et al.",
                "year": 2009,
                "journal": "Diabetes Care",
                "pmid": "19564476",
                "key_findings": "Resistance training reduces HbA1c by 0.57% independent of weight loss"
            }
        ],
        "dosage": "3x per week, major muscle groups, progressive overload",
        "expected_improvement": "Reduce HbA1c 0.3-0.6%, improve insulin sensitivity 20-30% within 12 weeks",
        "contraindications": ["acute injuries", "severe osteoporosis"],
        "priority_score": 8
    },
    {
        "id": "magnesium-supplementation",
        "category": "supplements",
        "name": "Magnesium Supplementation",
        "target_biomarkers": ["glucose", "insulin", "blood_pressure"],
        "description": "Essential mineral for glucose metabolism and cardiovascular health",
        "scientific_references": [
            {
                "study": "Magnesium intake and type 2 diabetes",
                "authors": "Larsson & Wolk",
                "year": 2007,
                "journal": "Journal of Internal Medicine",
                "pmid": "17305645",
                "key_findings": "Higher magnesium intake associated with 23% lower diabetes risk"
            }
        ],
        "dosage": "300-400mg elemental magnesium daily (glycinate form preferred)",
        "expected_improvement": "Improve insulin sensitivity 10-15% within 8 weeks",
        "contraindications": ["kidney disease"],
        "priority_score": 7
    },
    {
        "id": "intermittent-fasting",
        "category": "diet",
        "name": "Time-Restricted Eating (16:8)",
        "target_biomarkers": ["glucose", "insulin", "hba1c", "triglycerides"],
        "description": "Limit eating window to improve metabolic flexibility and insulin sensitivity",
        "scientific_references": [
            {
                "study": "Effects of intermittent fasting on health and aging",
                "authors": "de Cabo & Mattson",
                "year": 2019,
                "journal": "New England Journal of Medicine",
                "pmid": "31881139",
                "key_findings": "Time-restricted eating improves multiple metabolic markers and longevity pathways"
            }
        ],
        "dosage": "Daily 16-hour fast, 8-hour eating window (e.g., 12pm-8pm)",
        "expected_improvement": "Reduce fasting glucose 5-15%, improve insulin sensitivity 15-25% within 8 weeks",
        "contraindications": ["eating disorders", "pregnancy", "diabetes on medication"],
        "priority_score": 8
    },
    {
        "id": "coq10-supplementation",
        "category": "supplements",
        "name": "Coenzyme Q10 (CoQ10)",
        "target_biomarkers": ["ldl", "blood_pressure", "crp"],
        "description": "Antioxidant that supports mitochondrial function and cardiovascular health",
        "scientific_references": [
            {
                "study": "CoQ10 and cardiovascular disease",
                "authors": "Mortensen et al.",
                "year": 2014,
                "journal": "Journal of the American College of Cardiology",
                "pmid": "25443696",
                "key_findings": "CoQ10 reduces cardiovascular mortality and improves symptoms"
            }
        ],
        "dosage": "100-200mg daily with fat-containing meal (ubiquinol form preferred)",
        "expected_improvement": "Reduce oxidative stress, improve cardiovascular markers within 12 weeks",
        "contraindications": ["blood thinners (warfarin)"],
        "priority_score": 6
    },
    {
        "id": "stress-reduction-meditation",
        "category": "lifestyle",
        "name": "Mindfulness Meditation and Stress Management",
        "target_biomarkers": ["cortisol", "crp", "blood_pressure"],
        "description": "Evidence-based stress reduction techniques to lower inflammation",
        "scientific_references": [
            {
                "study": "Mindfulness meditation and health outcomes",
                "authors": "Goyal et al.",
                "year": 2014,
                "journal": "JAMA Internal Medicine",
                "pmid": "24395196",
                "key_findings": "Meditation programs reduce anxiety, depression, and pain"
            }
        ],
        "dosage": "10-20 minutes daily meditation, breathwork, or yoga",
        "expected_improvement": "Reduce cortisol 15-25%, lower CRP 10-20% within 8 weeks",
        "contraindications": ["none"],
        "priority_score": 7
    },
    {
        "id": "fiber-supplementation",
        "category": "diet",
        "name": "High-Fiber Diet and Prebiotic Foods",
        "target_biomarkers": ["glucose", "cholesterol", "triglycerides"],
        "description": "Increase soluble fiber intake to improve gut health and metabolic markers",
        "scientific_references": [
            {
                "study": "Dietary fiber and metabolic health",
                "authors": "Reynolds et al.",
                "year": 2019,
                "journal": "The Lancet",
                "pmid": "30638909",
                "key_findings": "High fiber intake reduces mortality, heart disease, and diabetes risk"
            }
        ],
        "dosage": "30-40g fiber daily from vegetables, legumes, whole grains",
        "expected_improvement": "Reduce LDL cholesterol 5-10%, improve glucose control within 8 weeks",
        "contraindications": ["bowel obstruction"],
        "priority_score": 7
    },
    {
        "id": "cold-exposure",
        "category": "lifestyle",
        "name": "Cold Exposure Therapy",
        "target_biomarkers": ["glucose", "triglycerides", "metabolism"],
        "description": "Brief cold exposure to activate brown fat and improve metabolic rate",
        "scientific_references": [
            {
                "study": "Cold-activated brown adipose tissue in humans",
                "authors": "van der Lans et al.",
                "year": 2013,
                "journal": "Diabetes",
                "pmid": "23610060",
                "key_findings": "Regular cold exposure increases brown fat activity and energy expenditure"
            }
        ],
        "dosage": "2-3 minute cold shower daily, or ice bath 1-2x weekly",
        "expected_improvement": "Improve glucose uptake, increase metabolic rate 5-10% within 4 weeks",
        "contraindications": ["Raynaud's disease", "cardiovascular disease"],
        "priority_score": 5
    },
    {
        "id": "walking-routine",
        "category": "exercise",
        "name": "Daily Walking Habit",
        "target_biomarkers": ["glucose", "insulin", "blood_pressure", "triglycerides"],
        "description": "Regular low-intensity walking to improve metabolic health",
        "scientific_references": [
            {
                "study": "Walking and mortality reduction",
                "authors": "Murtagh et al.",
                "year": 2015,
                "journal": "British Journal of Sports Medicine",
                "pmid": "25740891",
                "key_findings": "Brisk walking 30+ minutes daily reduces all-cause mortality by 20%"
            }
        ],
        "dosage": "8,000-10,000 steps daily, including post-meal walks",
        "expected_improvement": "Reduce fasting glucose 5-10%, improve insulin sensitivity within 4 weeks",
        "contraindications": ["severe mobility issues"],
        "priority_score": 9
    },
    {
        "id": "nad-boosting",
        "category": "supplements",
        "name": "NAD+ Precursor Supplementation (NMN/NR)",
        "target_biomarkers": ["metabolism", "cellular_health"],
        "description": "Support cellular energy production and DNA repair",
        "scientific_references": [
            {
                "study": "NAD+ metabolism and aging",
                "authors": "Yoshino et al.",
                "year": 2018,
                "journal": "Cell Metabolism",
                "pmid": "29719225",
                "key_findings": "NAD+ boosting improves mitochondrial function and metabolic health in aging"
            }
        ],
        "dosage": "250-500mg NMN or NR daily, morning on empty stomach",
        "expected_improvement": "Improve energy levels, support healthy aging markers within 8-12 weeks",
        "contraindications": ["none known"],
        "priority_score": 6
    },
    {
        "id": "green-tea-extract",
        "category": "supplements",
        "name": "Green Tea Extract (EGCG)",
        "target_biomarkers": ["glucose", "cholesterol", "crp"],
        "description": "Polyphenol-rich extract for metabolic and cardiovascular support",
        "scientific_references": [
            {
                "study": "Green tea catechins and metabolic syndrome",
                "authors": "Basu et al.",
                "year": 2010,
                "journal": "Nutrition Reviews",
                "pmid": "20384845",
                "key_findings": "Green tea improves glucose metabolism and reduces oxidative stress"
            }
        ],
        "dosage": "400-500mg EGCG daily (or 3-4 cups green tea)",
        "expected_improvement": "Reduce LDL 5-10%, improve glucose metabolism within 8 weeks",
        "contraindications": ["liver disease", "high caffeine sensitivity"],
        "priority_score": 6
    },
    {
        "id": "strength-flexibility-combo",
        "category": "exercise",
        "name": "Combined Strength and Flexibility Training",
        "target_biomarkers": ["glucose", "crp", "mobility_markers"],
        "description": "Balanced program combining resistance training with yoga or stretching",
        "scientific_references": [
            {
                "study": "Yoga and metabolic syndrome",
                "authors": "Chu et al.",
                "year": 2016,
                "journal": "European Journal of Preventive Cardiology",
                "pmid": "26238434",
                "key_findings": "Yoga improves cardiovascular risk factors comparable to conventional exercise"
            }
        ],
        "dosage": "3x weekly: 20 min strength + 15 min flexibility work",
        "expected_improvement": "Improve insulin sensitivity, reduce inflammation within 8 weeks",
        "contraindications": ["acute injuries"],
        "priority_score": 7
    },
    {
        "id": "hydration-optimization",
        "category": "lifestyle",
        "name": "Optimal Hydration Protocol",
        "target_biomarkers": ["kidney_function", "blood_pressure", "metabolism"],
        "description": "Strategic water intake for metabolic and kidney health",
        "scientific_references": [
            {
                "study": "Water intake and chronic disease",
                "authors": "Popkin et al.",
                "year": 2010,
                "journal": "Nutrition Reviews",
                "pmid": "20646222",
                "key_findings": "Adequate hydration supports metabolic function and reduces disease risk"
            }
        ],
        "dosage": "2-3 liters daily, front-loaded in morning, electrolyte balance",
        "expected_improvement": "Improve kidney function markers, support metabolism within 4 weeks",
        "contraindications": ["heart failure", "kidney disease"],
        "priority_score": 6
    }
]


def get_all_interventions():
    """Return all available interventions."""
    return INTERVENTIONS_DB


def get_interventions_by_biomarker(biomarker):
    """
    Get interventions that target a specific biomarker.
    
    Args:
        biomarker: The biomarker to filter by (e.g., 'glucose', 'cholesterol')
    
    Returns:
        List of interventions targeting that biomarker, sorted by priority
    """
    matching = [
        intervention for intervention in INTERVENTIONS_DB
        if biomarker.lower() in [bm.lower() for bm in intervention['target_biomarkers']]
    ]
    return sorted(matching, key=lambda x: x['priority_score'], reverse=True)


def get_intervention_by_id(intervention_id):
    """
    Get a specific intervention by its ID.
    
    Args:
        intervention_id: The unique ID of the intervention
    
    Returns:
        Intervention dict or None if not found
    """
    for intervention in INTERVENTIONS_DB:
        if intervention['id'] == intervention_id:
            return intervention
    return None


def get_interventions_by_category(category):
    """
    Get all interventions in a specific category.
    
    Args:
        category: Category name (e.g., 'supplements', 'exercise', 'diet')
    
    Returns:
        List of interventions in that category
    """
    return [
        intervention for intervention in INTERVENTIONS_DB
        if intervention['category'].lower() == category.lower()
    ]

