#!/usr/bin/env python3
"""
restructure_json.py
===================

Restructures the extraction JSON output into a clear, sequential format
that's easier to review and identify missing details.

Instead of flat JSON, creates a well-organized structure with:
- Logical field grouping
- Clear section organization
- Data completeness indicators
- Source tracking per field
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from collections import OrderedDict


class JSONRestructurer:
    """Restructures extraction JSON into a clear, sequential format."""
    
    # Define the sequential field order by category
    FIELD_CATEGORIES = OrderedDict([
        ("company_information", {
            "label": "Company Information",
            "fields": [
                "location_name",
                "dba",
                "description_of_operations",
                "naics_number",
                "sic_number",
                "corporation_type",
                "fed_tax_id",
                "website"
            ]
        }),
        ("primary_contact", {
            "label": "Primary Contact",
            "fields": [
                "first_name",
                "last_name",
                "title",
                "contact_type",
                "email",
                "phone",
                "cellphone"
            ]
        }),
        ("address_information", {
            "label": "Address Information",
            "fields": [
                "address",
                "city",
                "state",
                "zipcode",
                "county",
                "states_where_operating"
            ]
        }),
        ("coverage_and_carrier", {
            "label": "Coverage & Carrier",
            "fields": [
                "prospect_type",
                "current_carrier_tpa",
                "additional_carrier",
                "carrier",
                "current_pr_peo_provider",
                "renewal_date_of_current_coverage",
                "requested_effective_date"
            ]
        }),
        ("payroll_and_ownership", {
            "label": "Payroll & Ownership",
            "fields": [
                "payroll_frequency",
                "percentage_of_ownership",
                "ownership_option",
                "inc_exc"
            ]
        }),
        ("lead_information", {
            "label": "Lead Information",
            "fields": [
                "lead_source",
                "share_file_client_folder_link"
            ]
        })
    ])
    
    def __init__(self, schema_path: str = None):
        """Initialize with optional schema for field metadata."""
        self.schema = None
        if schema_path:
            schema_file = Path(schema_path)
            if schema_file.exists():
                with open(schema_file, 'r', encoding='utf-8') as f:
                    self.schema = json.load(f)
    
    def restructure(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Restructure extraction JSON into clear, sequential format.
        
        Args:
            input_data: Original extraction result
            
        Returns:
            Restructured JSON with clear organization
        """
        data = input_data.get("data", {})
        field_sources = input_data.get("fieldSources", {})
        conflicts = input_data.get("conflicts", [])
        missing_required = input_data.get("missingRequiredFields", [])
        warnings = input_data.get("warnings", [])
        
        # Build summary
        total_fields = sum(len(cat["fields"]) for cat in self.FIELD_CATEGORIES.values())
        populated_fields = sum(1 for v in data.values() if v and str(v).strip() and str(v) not in ["", "null", "None"])
        empty_fields = total_fields - populated_fields
        
        # Build restructured output
        restructured = OrderedDict()
        
        # 1. Summary section
        restructured["summary"] = {
            "total_fields": total_fields,
            "populated_fields": populated_fields,
            "empty_fields": empty_fields,
            "missing_required_count": len(missing_required),
            "conflicts_count": len(conflicts),
            "warnings_count": len(warnings)
        }
        
        # 2. Metadata
        restructured["metadata"] = {
            "extraction_status": "success" if not missing_required else "incomplete",
            "completeness_percentage": round((populated_fields / total_fields * 100), 1) if total_fields > 0 else 0,
            "requires_attention": len(missing_required) > 0 or len(conflicts) > 0
        }
        
        # 3. Warnings (if any)
        if warnings:
            restructured["warnings"] = warnings
        
        # 4. Missing Required Fields (if any)
        if missing_required:
            restructured["missing_required_fields"] = missing_required
        
        # 5. Conflicts (if any)
        if conflicts:
            restructured["conflicts"] = conflicts
        
        # 6. Organized data by category
        restructured["data_by_category"] = OrderedDict()
        
        for category_key, category_info in self.FIELD_CATEGORIES.items():
            category_label = category_info["label"]
            category_fields = category_info["fields"]
            
            category_data = OrderedDict()
            category_data["_category_label"] = category_label
            category_data["_fields_count"] = len(category_fields)
            
            populated_in_category = 0
            category_data["fields"] = OrderedDict()
            
            for field_name in category_fields:
                value = data.get(field_name)
                source = field_sources.get(field_name)
                
                # Check if field is populated
                is_populated = value is not None and str(value).strip() not in ["", "null", "None"]
                if is_populated:
                    populated_in_category += 1
                
                # Get field metadata from schema
                field_info = self._get_field_info(field_name)
                
                # Build field object
                field_obj = OrderedDict()
                field_obj["value"] = value if value else None
                field_obj["is_populated"] = is_populated
                field_obj["is_required"] = field_info.get("required", False)
                field_obj["source"] = source if source else None
                
                # Add field label from schema
                if field_info.get("label"):
                    field_obj["field_label"] = field_info["label"]
                
                # Add description if field is empty and has description
                if not is_populated and field_info.get("description"):
                    field_obj["description"] = field_info["description"]
                
                category_data["fields"][field_name] = field_obj
            
            category_data["_populated_count"] = populated_in_category
            category_data["_empty_count"] = len(category_fields) - populated_in_category
            
            restructured["data_by_category"][category_key] = category_data
        
        # 7. Flat data (for backward compatibility)
        restructured["data_flat"] = data
        
        return restructured
    
    def _get_field_info(self, field_name: str) -> Dict[str, Any]:
        """Get field metadata from schema."""
        info = {}
        
        if self.schema and "fields" in self.schema:
            field_def = self.schema["fields"].get(field_name, {})
            
            # Get primary label from aliases
            aliases = field_def.get("aliases", [])
            if aliases:
                info["label"] = aliases[0]
            
            # Get other metadata
            info["required"] = field_def.get("required", False)
            info["description"] = field_def.get("description", "")
            info["type"] = field_def.get("type", "string")
        
        return info
    
    def save_restructured(self, input_path: str, output_path: str = None) -> str:
        """
        Load, restructure, and save JSON.
        
        Args:
            input_path: Path to original extraction JSON
            output_path: Path for restructured output (default: input_restructured.json)
            
        Returns:
            Path to output file
        """
        # Load input
        input_file = Path(input_path)
        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            input_data = json.load(f)
        
        # Restructure
        restructured = self.restructure(input_data)
        
        # Determine output path
        if not output_path:
            output_path = input_file.parent / f"{input_file.stem}_restructured.json"
        else:
            output_path = Path(output_path)
        
        # Save
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(restructured, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Restructured JSON saved to: {output_path}")
        print(f"\n📊 Summary:")
        print(f"   Total Fields: {restructured['summary']['total_fields']}")
        print(f"   Populated: {restructured['summary']['populated_fields']}")
        print(f"   Empty: {restructured['summary']['empty_fields']}")
        print(f"   Completeness: {restructured['metadata']['completeness_percentage']}%")
        
        if restructured['summary']['missing_required_count'] > 0:
            print(f"   ⚠️  Missing Required: {restructured['summary']['missing_required_count']}")
        
        if restructured['summary']['conflicts_count'] > 0:
            print(f"   ⚠️  Conflicts: {restructured['summary']['conflicts_count']}")
        
        return str(output_path)


def restructure_json(input_path: str, output_path: str = None, schema_path: str = None):
    """
    Convenience function to restructure extraction JSON.
    
    Args:
        input_path: Path to original extraction JSON
        output_path: Path for restructured output
        schema_path: Path to schema file for metadata
    """
    # Find schema if not provided
    if not schema_path:
        possible_schema = Path(input_path).parent / "prospect_schema.json"
        if possible_schema.exists():
            schema_path = str(possible_schema)
    
    restructurer = JSONRestructurer(schema_path)
    return restructurer.save_restructured(input_path, output_path)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python restructure_json.py <input.json> [output.json]")
        print("\nRestructures extraction JSON into clear, sequential format.")
        print("Makes it easier to review and identify missing details.")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    restructure_json(input_file, output_file)
