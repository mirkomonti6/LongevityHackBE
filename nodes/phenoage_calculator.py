"""
PhenoAge Biological Age Calculator

Implements the Phenotypic Age (PhenoAge) model by Levine et al. (2018)
to calculate biological age from biomarkers and estimate years gainable
through optimization.
"""

import math
import json
from copy import deepcopy
from typing import Dict, Any, List, Tuple


# ============================
# 1. CONFIGURAZIONE DI BASE
# ============================

# Biomarcatori richiesti dal modello PhenoAge (Levine)
REQUIRED_BIOMARKERS = [
    "age_years",               # anni cronologici
    "albumin_g_dl",            # g/dL
    "creatinine_mg_dl",        # mg/dL
    "glucose_mg_dl",           # mg/dL (a digiuno)
    "crp_mg_l",                # mg/L (C-reactive protein)
    "lymphocyte_percent",      # %
    "mcv_fl",                  # fL
    "rdw_percent",             # %
    "alp_u_l",                 # U/L (alkaline phosphatase)
    "wbc_10e3_per_uL",         # 10^3 cellule/µL
]

# Valori TARGET "ottimali" (scelta ingegneristica, non verità clinica)
OPTIMAL_TARGETS = {
    "albumin_g_dl": 4.7,
    "creatinine_mg_dl": 0.8,
    "glucose_mg_dl": 85.0,
    "crp_mg_l": 0.3,
    "lymphocyte_percent": 35.0,
    "mcv_fl": 90.0,
    "rdw_percent": 12.5,
    "alp_u_l": 60.0,
    "wbc_10e3_per_uL": 5.5,
    # age_years NON si ottimizza: è la cronologica
}


# ============================
# 2. FUNZIONI DI SUPPORTO
# ============================

class BiomarkerError(Exception):
    """Exception raised for biomarker-related errors."""
    pass


def validate_biomarkers(b: Dict[str, float]) -> None:
    """Verifica che tutti i biomarcatori richiesti siano presenti."""
    missing = [k for k in REQUIRED_BIOMARKERS if k not in b]
    if missing:
        raise BiomarkerError(f"Missing biomarkers: {', '.join(missing)}")


def fill_missing_biomarkers(b: Dict[str, float]) -> Dict[str, float]:
    """
    Fill missing biomarkers with optimal values.
    
    If a biomarker is missing (or None), it will be set to its optimal target value.
    age_years must be provided and cannot be filled.
    
    Args:
        b: Dictionary with available biomarker values (may be incomplete)
    
    Returns:
        Dictionary with all required biomarkers filled (missing ones set to optimal values)
    
    Raises:
        BiomarkerError: If age_years is missing (required for calculation)
    """
    filled = deepcopy(b)
    
    # age_years is required - cannot assume it
    if "age_years" not in filled or filled["age_years"] is None:
        raise BiomarkerError("age_years is required and cannot be assumed")
    
    # Fill missing biomarkers with optimal values
    for biomarker in REQUIRED_BIOMARKERS:
        if biomarker == "age_years":
            continue  # Already checked above
        
        if biomarker not in filled or filled[biomarker] is None:
            # Use optimal target value for missing biomarker
            if biomarker in OPTIMAL_TARGETS:
                filled[biomarker] = OPTIMAL_TARGETS[biomarker]
            else:
                # Should not happen, but handle gracefully
                raise BiomarkerError(f"Optimal target not defined for {biomarker}")
    
    return filled


# ============================
# 3. CALCOLO PHENOAGE (Levine)
# ============================

def compute_phenoage(b: Dict[str, float]) -> float:
    """
    Calcola l'età fenotipica (biologica) secondo il modello PhenoAge di Levine.

    Units attese:
        - age_years: anni
        - albumin_g_dl: g/dL
        - creatinine_mg_dl: mg/dL
        - glucose_mg_dl: mg/dL
        - crp_mg_l: mg/L
        - lymphocyte_percent: %
        - mcv_fl: fL
        - rdw_percent: %
        - alp_u_l: U/L
        - wbc_10e3_per_uL: 10^3 cellule/µL

    Args:
        b: Dictionary with biomarker values (missing biomarkers will be filled with optimal values)

    Returns:
        Phenotypic age in years (float)

    Raises:
        BiomarkerError: If age_years is missing (required)
    """
    # Fill missing biomarkers with optimal values
    b = fill_missing_biomarkers(b)

    # Estrai variabili
    age = float(b["age_years"])
    albumin = float(b["albumin_g_dl"])
    creatinine = float(b["creatinine_mg_dl"])
    glucose = float(b["glucose_mg_dl"])
    crp = float(b["crp_mg_l"])
    lymph = float(b["lymphocyte_percent"])
    mcv = float(b["mcv_fl"])
    rdw = float(b["rdw_percent"])
    alp = float(b["alp_u_l"])
    wbc = float(b["wbc_10e3_per_uL"])

    # Coefficienti (Levine) - fonte formula omux.dev (Levine 2018)
    b0 = -19.9067
    b_albumin = -0.0336
    b_creatinine = 0.0095
    b_glucose = 0.1953
    b_crp = 0.0954
    b_lymph = -0.0120
    b_mcv = 0.0268
    b_rdw = 0.3306
    b_alp = 0.00188
    b_wbc = 0.0554
    b_age = 0.0804

    # Conversioni unità per la formula originale
    albumin_conv = albumin * 10.0        # g/dL -> g/L
    creatinine_conv = creatinine * 88.401  # mg/dL -> µmol/L
    glucose_conv = glucose * 0.0555      # mg/dL -> mmol/L
    crp_conv = crp * 0.1                 # mg/L -> mg/dL

    # Calcolo xb (linear predictor)
    xb = (
        b0
        + b_albumin * albumin_conv
        + b_creatinine * creatinine_conv
        + b_glucose * glucose_conv
        + b_crp * math.log(crp_conv)
        + b_lymph * lymph
        + b_mcv * mcv
        + b_rdw * rdw
        + b_alp * alp
        + b_wbc * wbc
        + b_age * age
    )

    # Parametri della funzione di rischio
    gamma = -1.51714
    lambda_ = 0.0076927
    alpha = 141.50225
    beta = -0.00553

    # Calcolo M con un po' di protezione numerica
    M = 1.0 - math.exp((gamma * math.exp(xb)) / lambda_)

    # Clamp per evitare problemi di log (M deve stare in (0,1))
    M = min(max(M, 1e-9), 1.0 - 1e-9)

    # Phenotypic Age
    inner = beta * math.log(1.0 - M)  # inner > 0 perché log(1-M) < 0, beta < 0
    phenotypic_age = alpha + (math.log(inner) / 0.09165)

    return float(phenotypic_age)


# ============================
# 4. SCENARIO MIGLIORATO
# ============================

def build_improved_biomarkers(b: Dict[str, float]) -> Dict[str, float]:
    """
    Crea una copia dei biomarcatori dove ogni valore viene portato a un target 'ottimale'.

    age_years NON viene modificato.

    Args:
        b: Dictionary with current biomarker values

    Returns:
        Dictionary with optimized biomarker values
    """
    improved = deepcopy(b)

    for key, target in OPTIMAL_TARGETS.items():
        if key in improved:
            improved[key] = float(target)

    return improved


def compute_years_gained(b: Dict[str, float]) -> Dict[str, Any]:
    """
    Calcola gli anni biologici guadagnabili ottimizzando i biomarcatori.

    Ritorna:
        - biological_age_now
        - biological_age_target
        - years_biological_gained (>= 0)
        - per_biomarker_contributions: lista ordinata per impatto

    Args:
        b: Dictionary with biomarker values (missing biomarkers will be filled with optimal values)

    Returns:
        Dictionary with biological age analysis results

    Raises:
        BiomarkerError: If age_years is missing (required)
    """
    # Track which biomarkers were originally provided (before filling)
    originally_provided = set(b.keys())
    
    # Fill missing biomarkers with optimal values
    b = fill_missing_biomarkers(b)

    # Età biologica attuale
    ba_now = compute_phenoage(b)

    # Età biologica con tutti i biomarkers portati a target
    b_target = build_improved_biomarkers(b)
    ba_target = compute_phenoage(b_target)

    years_gained_total = max(0.0, ba_now - ba_target)

    # Calcolo contributo di ogni singolo biomarcatore
    # Only calculate contributions for biomarkers that were originally provided
    contributions: List[Tuple[str, float]] = []

    for biom in OPTIMAL_TARGETS.keys():
        # Only calculate contribution if this biomarker was originally provided
        if biom not in originally_provided:
            continue
        
        # Skip if biomarker is already at optimal (no contribution)
        if biom in b and b[biom] == OPTIMAL_TARGETS[biom]:
            continue

        b_single = deepcopy(b)
        b_single[biom] = OPTIMAL_TARGETS[biom]

        ba_single = compute_phenoage(b_single)

        delta = max(0.0, ba_now - ba_single)

        contributions.append((biom, delta))

    # Ordina per impatto decrescente
    contributions.sort(key=lambda x: x[1], reverse=True)

    per_biomarker = [
        {"biomarker": biom, "years_gained_if_optimized": round(delta, 2)}
        for biom, delta in contributions
        if delta > 0.0
    ]

    return {
        "biological_age_now": round(ba_now, 2),
        "biological_age_target": round(ba_target, 2),
        "years_biological_gained": round(years_gained_total, 2),
        "per_biomarker_contributions": per_biomarker,
    }


# ============================
# 5. WRAPPER PER JSON / API
# ============================

def compute_from_json(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrapper per calcolare PhenoAge da un payload JSON.

    Atteso:
        {
          "biomarkers": {
            "age_years": 38,
            "albumin_g_dl": 4.3,
            "creatinine_mg_dl": 0.9,
            "glucose_mg_dl": 92,
            "crp_mg_l": 0.8,
            "lymphocyte_percent": 28,
            "mcv_fl": 88,
            "rdw_percent": 13.2,
            "alp_u_l": 70,
            "wbc_10e3_per_uL": 6.1
          }
        }

    Args:
        payload: Dictionary with "biomarkers" key containing biomarker values

    Returns:
        Dictionary with analysis results including input, optimized biomarkers, and analysis

    Raises:
        BiomarkerError: If payload structure is invalid or biomarkers are missing
    """
    if "biomarkers" not in payload:
        raise BiomarkerError("Payload must contain 'biomarkers' field")

    biomarkers = payload["biomarkers"]

    result = compute_years_gained(biomarkers)

    return {
        "input_biomarkers": biomarkers,
        "optimized_biomarkers": build_improved_biomarkers(biomarkers),
        "analysis": result,
        "disclaimer": (
            "This is an educational longevity model based on published biological age formulas. "
            "It is NOT a medical device and does NOT replace medical advice."
        ),
    }


# ============================
# 6. ESEMPIO USO CLI
# ============================

if __name__ == "__main__":
    # Esempio fittizio
    example_biomarkers = {
        "age_years": 40,
        "albumin_g_dl": 4.2,
        "creatinine_mg_dl": 1.0,
        "glucose_mg_dl": 96,
        "crp_mg_l": 1.2,
        "lymphocyte_percent": 27,
        "mcv_fl": 88,
        "rdw_percent": 13.5,
        "alp_u_l": 80,
        "wbc_10e3_per_uL": 6.8,
    }

    payload = {"biomarkers": example_biomarkers}

    output = compute_from_json(payload)
    print(json.dumps(output, indent=2))

