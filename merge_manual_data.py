"""
Utility to merge extracted JSON data with manual overrides.

This is useful when contact information or other fields are not present in
the GHQ or email documents, but are known from other sources (phone calls,
Salesforce, etc.).

Usage:
    python merge_manual_data.py --input tlw.json --overrides manual_data.json --output tlw_final.json
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
import sys


def load_json(filepath):
    """Load JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data, filepath):
    """Save JSON file with pretty formatting."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def merge_data(extracted_data, overrides):
    """
    Merge extracted data with manual overrides.
    
    Args:
        extracted_data: Original extracted data structure
        overrides: Dictionary of field:value overrides
        
    Returns:
        Merged data structure with tracking of changes
    """
    # Make a deep copy to avoid modifying original
    result = json.loads(json.dumps(extracted_data))
    
    # Track what was changed
    changes = []
    
    # Get the data section (handle both formats)
    if 'data' in result:
        data_section = result['data']
    else:
        data_section = result
        result = {'data': data_section}
    
    # Apply overrides
    for field, new_value in overrides.items():
        if field in data_section:
            old_value = data_section[field]
            if old_value != new_value:
                data_section[field] = new_value
                changes.append({
                    'field': field,
                    'old_value': old_value,
                    'new_value': new_value,
                    'reason': 'Manual override'
                })
        else:
            # Field doesn't exist, add it
            data_section[field] = new_value
            changes.append({
                'field': field,
                'old_value': None,
                'new_value': new_value,
                'reason': 'Manual addition'
            })
    
    # Update field sources if they exist
    if 'fieldSources' in result:
        for field in overrides.keys():
            result['fieldSources'][field] = 'MANUAL'
    
    # Add metadata about the merge
    if 'metadata' not in result:
        result['metadata'] = {}
    
    result['metadata']['mergedAtUtc'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    result['metadata']['manualOverridesApplied'] = len(changes)
    
    # Add changes log
    if changes:
        result['manualChanges'] = changes
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description='Merge extracted JSON data with manual overrides',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Merge with overrides from JSON file
    python merge_manual_data.py --input tlw.json --overrides contact_info.json --output tlw_final.json
    
    # Quick inline override
    python merge_manual_data.py --input tlw.json --field first_name "John" --field last_name "Doe" --output tlw_final.json
        """
    )
    
    parser.add_argument('--input', '-i', required=True,
                        help='Input JSON file (extracted data)')
    parser.add_argument('--overrides', '-o',
                        help='JSON file containing field overrides')
    parser.add_argument('--field', '-f', action='append', nargs=2,
                        metavar=('FIELD', 'VALUE'),
                        help='Inline field override (can be used multiple times)')
    parser.add_argument('--output', '-out', required=True,
                        help='Output JSON file path')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Print detailed changes')
    
    args = parser.parse_args()
    
    # Load input file
    print(f"Loading extracted data from: {args.input}")
    extracted = load_json(args.input)
    
    # Collect overrides
    overrides = {}
    
    # From file if provided
    if args.overrides:
        print(f"Loading overrides from: {args.overrides}")
        override_data = load_json(args.overrides)
        overrides.update(override_data)
    
    # From inline arguments
    if args.field:
        for field_name, field_value in args.field:
            overrides[field_name] = field_value
            if args.verbose:
                print(f"  Inline override: {field_name} = {field_value}")
    
    if not overrides:
        print("ERROR: No overrides provided. Use --overrides FILE or --field NAME VALUE")
        sys.exit(1)
    
    print(f"\nApplying {len(overrides)} override(s)...")
    
    # Merge data
    result = merge_data(extracted, overrides)
    
    # Show changes
    if 'manualChanges' in result and args.verbose:
        print("\nChanges made:")
        for change in result['manualChanges']:
            print(f"  {change['field']}: '{change['old_value']}' → '{change['new_value']}'")
    
    # Save result
    save_json(result, args.output)
    print(f"\n✓ Merged data saved to: {args.output}")
    print(f"  {len(result.get('manualChanges', []))} field(s) modified")


if __name__ == '__main__':
    main()
