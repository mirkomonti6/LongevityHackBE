#!/usr/bin/env python3
"""
Script to extract unique biomarker names from the biomarkers database.
"""

import json
from pathlib import Path
from collections import Counter

def extract_biomarker_names(json_file_path):
    """
    Extract all unique biomarker names from the biomarkers database.
    
    Args:
        json_file_path: Path to the biomarkers_database.json file
    
    Returns:
        A sorted list of unique biomarker names and statistics
    """
    print(f"Reading database from: {json_file_path}")
    
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # The structure is: {"metadata": {...}, "biomarkers": {biomarker_name: {...}, ...}}
    biomarkers_dict = data.get('biomarkers', {})
    metadata = data.get('metadata', {})
    
    print(f"\nMetadata from database:")
    print(f"  Total studies: {metadata.get('total_studies', 'N/A')}")
    print(f"  Total biomarkers: {metadata.get('total_biomarkers', 'N/A')}")
    print(f"  Generation date: {metadata.get('generation_date', 'N/A')}")
    
    # Extract biomarker names (they are the keys)
    biomarker_names = list(biomarkers_dict.keys())
    
    # Get unique names and sort
    unique_names = sorted(set(biomarker_names))
    
    # Create statistics: count how many studies each biomarker has
    biomarker_stats = {}
    for name, info in biomarkers_dict.items():
        studies = info.get('studies', [])
        biomarker_stats[name] = {
            'study_count': len(studies),
            'category': info.get('category', 'Unknown'),
            'rank': info.get('rank', None)
        }
    
    print(f"\nTotal biomarker names found: {len(biomarker_names)}")
    print(f"Unique biomarker names: {len(unique_names)}")
    
    return unique_names, biomarker_stats

def main():
    # Path to the biomarkers database
    db_path = Path(__file__).parent / "db" / "biomarkers" / "data" / "biomarkers_database.json"
    
    if not db_path.exists():
        print(f"Error: Database file not found at {db_path}")
        return
    
    # Extract biomarker names
    unique_names, biomarker_stats = extract_biomarker_names(db_path)
    
    # Save to output files
    output_dir = Path(__file__).parent
    
    # Save unique names (sorted alphabetically)
    unique_output = output_dir / "biomarker_names_unique.txt"
    with open(unique_output, 'w', encoding='utf-8') as f:
        for name in unique_names:
            f.write(f"{name}\n")
    print(f"\n✓ Saved unique biomarker names to: {unique_output}")
    
    # Save with detailed statistics (sorted by rank)
    stats_output = output_dir / "biomarker_names_with_stats.txt"
    with open(stats_output, 'w', encoding='utf-8') as f:
        f.write(f"Total unique biomarkers: {len(unique_names)}\n")
        f.write("\n" + "="*100 + "\n")
        f.write("Biomarker names with statistics (sorted by rank):\n")
        f.write("="*100 + "\n")
        f.write(f"{'Rank':<8} {'Studies':<10} {'Category':<25} {'Biomarker Name'}\n")
        f.write("-"*100 + "\n")
        
        # Sort by rank
        sorted_biomarkers = sorted(
            biomarker_stats.items(),
            key=lambda x: (x[1]['rank'] if x[1]['rank'] is not None else float('inf'))
        )
        
        for name, stats in sorted_biomarkers:
            rank = stats['rank'] if stats['rank'] is not None else 'N/A'
            study_count = stats['study_count']
            category = stats['category']
            f.write(f"{str(rank):<8} {study_count:<10} {category:<25} {name}\n")
    
    print(f"✓ Saved biomarker names with statistics to: {stats_output}")
    
    # Save by category
    category_output = output_dir / "biomarker_names_by_category.txt"
    categories = {}
    for name, stats in biomarker_stats.items():
        cat = stats['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(name)
    
    with open(category_output, 'w', encoding='utf-8') as f:
        f.write("Biomarkers grouped by category:\n")
        f.write("="*80 + "\n\n")
        for cat in sorted(categories.keys()):
            f.write(f"\n{cat} ({len(categories[cat])} biomarkers)\n")
            f.write("-"*80 + "\n")
            for name in sorted(categories[cat]):
                f.write(f"  {name}\n")
    
    print(f"✓ Saved biomarkers by category to: {category_output}")
    
    # Display top 20 by rank
    print("\n" + "="*100)
    print("Top 20 biomarkers by rank:")
    print("="*100)
    print(f"{'Rank':<8} {'Studies':<10} {'Category':<25} {'Biomarker Name'}")
    print("-"*100)
    
    sorted_biomarkers = sorted(
        biomarker_stats.items(),
        key=lambda x: (x[1]['rank'] if x[1]['rank'] is not None else float('inf'))
    )
    
    for name, stats in sorted_biomarkers[:20]:
        rank = stats['rank'] if stats['rank'] is not None else 'N/A'
        study_count = stats['study_count']
        category = stats['category']
        print(f"{str(rank):<8} {study_count:<10} {category:<25} {name}")
    
    # Display category summary
    print("\n" + "="*100)
    print("Biomarkers by category:")
    print("="*100)
    for cat in sorted(categories.keys()):
        print(f"  {cat:<30} {len(categories[cat]):>4} biomarkers")
    
    print("\n" + "="*100)
    print(f"Complete results saved to output files.")
    print("="*100)

if __name__ == "__main__":
    main()

