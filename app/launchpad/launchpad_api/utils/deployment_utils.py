"""
Deployment Page Utility Functions

This module provides helper functions for managing deployment page data,
including step validation, progress calculation, and default step initialization.
"""

import json
import logging
from typing import List, Dict, Optional, Tuple


# Default deployment steps
DEFAULT_DEPLOYMENT_STEPS = [
    {
        "id": "hardware_delivery",
        "name": "Hardware Delivery",
        "status": "pending",
        "estimatedHours": 4
    },
    {
        "id": "software_installation",
        "name": "Software Installation",
        "status": "pending",
        "estimatedHours": 8
    },
    {
        "id": "network_setup",
        "name": "Network Setup",
        "status": "pending",
        "estimatedHours": 6
    },
    {
        "id": "system_testing",
        "name": "System Testing",
        "status": "pending",
        "estimatedHours": 4
    }
]

# Step order for validation
STEP_ORDER = ["hardware_delivery", "software_installation", "network_setup", "system_testing"]

# Valid step statuses
VALID_STATUSES = ["pending", "in_progress", "completed", "blocked"]


def get_default_steps() -> List[Dict]:
    """Get default deployment steps."""
    return DEFAULT_DEPLOYMENT_STEPS.copy()


def parse_steps_field(field_value) -> Optional[List[Dict]]:
    """
    Parse the steps field value (can be JSON string or dict/list).
    
    Args:
        field_value: Can be a JSON string, dict, list, or None
        
    Returns:
        List of step dictionaries, or None if invalid
    """
    if field_value is None:
        return []
    
    # If it's already a list, return it
    if isinstance(field_value, list):
        return field_value
    
    # If it's a dict, wrap it in a list (shouldn't happen, but handle it)
    if isinstance(field_value, dict):
        return [field_value]
    
    # If it's a string, try to parse as JSON
    if isinstance(field_value, str):
        if not field_value.strip():
            return []
        try:
            parsed = json.loads(field_value)
            if isinstance(parsed, list):
                return parsed
            elif isinstance(parsed, dict):
                return [parsed]
            else:
                return []
        except json.JSONDecodeError:
            logging.warning(f"[deployment_utils] Invalid JSON in steps field: {field_value}")
            return None
    
    return None


def validate_step(step: Dict) -> Tuple[bool, Optional[str]]:
    """
    Validate a single deployment step.
    
    Args:
        step: Step dictionary
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Required fields
    required_fields = ["id", "name", "status", "estimatedHours"]
    for field in required_fields:
        if field not in step:
            return False, f"Step missing required field: {field}"
    
    # Validate status
    if step["status"] not in VALID_STATUSES:
        return False, f"Invalid status '{step['status']}'. Must be one of: {', '.join(VALID_STATUSES)}"
    
    # Validate estimatedHours
    try:
        estimated_hours = float(step["estimatedHours"])
        if estimated_hours < 0:
            return False, "estimatedHours must be a positive number"
    except (ValueError, TypeError):
        return False, "estimatedHours must be a valid number"
    
    # Validate actualHours if provided
    if "actualHours" in step and step["actualHours"] is not None:
        try:
            actual_hours = float(step["actualHours"])
            if actual_hours < 0:
                return False, "actualHours must be a positive number"
        except (ValueError, TypeError):
            return False, "actualHours must be a valid number"
    
    # Validate completedAt if provided
    if "completedAt" in step and step["completedAt"]:
        if not isinstance(step["completedAt"], str):
            return False, "completedAt must be a valid ISO date string"
    
    # Validate deliveryReceipt if provided
    if "deliveryReceipt" in step and step["deliveryReceipt"]:
        if not isinstance(step["deliveryReceipt"], str):
            return False, "deliveryReceipt must be a valid URL string"
    
    # Special validation: hardware_delivery requires deliveryReceipt when completed
    if step["id"] == "hardware_delivery" and step["status"] == "completed":
        if not step.get("deliveryReceipt"):
            return False, "hardware_delivery step requires deliveryReceipt when status is 'completed'"
    
    return True, None


def validate_step_progression(steps: List[Dict]) -> Tuple[bool, Optional[str]]:
    """
    Validate that steps are completed in the correct order.
    
    Args:
        steps: List of step dictionaries
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Create a map of step_id -> step
    step_map = {step["id"]: step for step in steps}
    
    # Check each step in order
    for i, step_id in enumerate(STEP_ORDER):
        if step_id not in step_map:
            continue  # Step not present, skip
        
        step = step_map[step_id]
        
        # If this step is completed, all previous steps must be completed
        if step["status"] == "completed":
            # Check all previous steps
            for prev_step_id in STEP_ORDER[:i]:
                if prev_step_id in step_map:
                    prev_step = step_map[prev_step_id]
                    if prev_step["status"] != "completed":
                        return False, f"Cannot complete '{step['name']}' before '{prev_step['name']}' is completed"
        
        # If this step is in_progress, previous step should be completed (unless it's the first)
        if step["status"] == "in_progress" and i > 0:
            prev_step_id = STEP_ORDER[i - 1]
            if prev_step_id in step_map:
                prev_step = step_map[prev_step_id]
                if prev_step["status"] != "completed":
                    return False, f"Cannot start '{step['name']}' before '{prev_step['name']}' is completed"
    
    return True, None


def calculate_progress(steps: List[Dict]) -> int:
    """
    Calculate deployment progress percentage based on completed steps.
    
    Args:
        steps: List of step dictionaries
        
    Returns:
        Progress percentage (0-100)
    """
    if not steps:
        return 0
    
    completed_count = sum(1 for step in steps if step.get("status") == "completed")
    total_count = len(steps)
    
    if total_count == 0:
        return 0
    
    progress = int((completed_count / total_count) * 100)
    return min(100, max(0, progress))  # Clamp between 0 and 100


def are_all_steps_completed(steps: List[Dict]) -> bool:
    """
    Check if all deployment steps are completed.
    
    Args:
        steps: List of step dictionaries
        
    Returns:
        True if all steps are completed, False otherwise
    """
    if not steps:
        return False
    
    return all(step.get("status") == "completed" for step in steps)


def validate_notes_field(field_value) -> Tuple[bool, Optional[List[Dict]], Optional[str]]:
    """
    Validate the notes field value.
    
    Args:
        field_value: Can be a JSON string, dict, list, or None
        
    Returns:
        Tuple of (is_valid, parsed_notes, error_message)
    """
    if field_value is None:
        return True, [], None
    
    # If it's already a list, validate it
    if isinstance(field_value, list):
        notes = field_value
    # If it's a dict, wrap it in a list
    elif isinstance(field_value, dict):
        notes = [field_value]
    # If it's a string, try to parse as JSON
    elif isinstance(field_value, str):
        if not field_value.strip():
            return True, [], None
        try:
            parsed = json.loads(field_value)
            if isinstance(parsed, list):
                notes = parsed
            elif isinstance(parsed, dict):
                notes = [parsed]
            else:
                return False, None, "notes field must be a JSON array"
        except json.JSONDecodeError:
            return False, None, "notes field must be valid JSON"
    else:
        return False, None, "notes field must be a JSON array"
    
    # Validate each note
    for note in notes:
        if not isinstance(note, dict):
            return False, None, "Each note must be an object"
        
        required_fields = ["id", "author", "content", "timestamp"]
        for field in required_fields:
            if field not in note:
                return False, None, f"Note missing required field: {field}"
        
        # Validate timestamp
        if not isinstance(note["timestamp"], str):
            return False, None, "Note timestamp must be a valid ISO date string"
    
    return True, notes, None


def validate_installation_fields(fields: Dict) -> Tuple[bool, Optional[str]]:
    """
    Validate installation section fields.
    
    Args:
        fields: Dictionary of field_name -> field_value
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Validate deployment_engineer (optional, max 255 chars)
    if "deployment_engineer" in fields and fields["deployment_engineer"]:
        if not isinstance(fields["deployment_engineer"], str):
            return False, "deployment_engineer must be a string"
        if len(fields["deployment_engineer"]) > 255:
            return False, "deployment_engineer cannot exceed 255 characters"
    
    # Validate start_date (optional, ISO date format)
    if "start_date" in fields and fields["start_date"]:
        if not isinstance(fields["start_date"], str):
            return False, "start_date must be a string"
        # Basic date format validation (YYYY-MM-DD)
        try:
            from datetime import datetime
            datetime.strptime(fields["start_date"], "%Y-%m-%d")
        except ValueError:
            return False, "start_date must be in YYYY-MM-DD format"
    
    # Validate target_date (optional, ISO date format)
    if "target_date" in fields and fields["target_date"]:
        if not isinstance(fields["target_date"], str):
            return False, "target_date must be a string"
        # Basic date format validation (YYYY-MM-DD)
        try:
            from datetime import datetime
            datetime.strptime(fields["target_date"], "%Y-%m-%d")
        except ValueError:
            return False, "target_date must be in YYYY-MM-DD format"
        
        # Validate target_date is after start_date if both provided
        if "start_date" in fields and fields["start_date"]:
            try:
                start = datetime.strptime(fields["start_date"], "%Y-%m-%d")
                target = datetime.strptime(fields["target_date"], "%Y-%m-%d")
                if target < start:
                    return False, "target_date must be after start_date"
            except ValueError:
                pass  # Already validated above
    
    # Validate progress (optional, 0-100)
    if "progress" in fields and fields["progress"]:
        try:
            progress = float(fields["progress"])
            if progress < 0 or progress > 100:
                return False, "progress must be between 0 and 100"
        except (ValueError, TypeError):
            return False, "progress must be a valid number"
    
    return True, None

