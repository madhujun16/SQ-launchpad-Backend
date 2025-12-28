import connexion
from flask import jsonify, request
import logging
import traceback
from datetime import datetime, date
from sqlalchemy.exc import IntegrityError
from ..utils.messages import generic_message
from ..db import db
from ..db_models.procurement_data import ProcurementData
from ..db_models.site import Site
from ..db_models.user import User

# Role constants - matching scoping_approval_controller
ADMIN_ROLE = 1
OPS_MANAGER_ROLE = 2
DEPLOYMENT_ENGINEER_ROLE = 3


def get_current_user():
    """Get current user from session/authentication - placeholder for actual auth implementation."""
    # TODO: Implement actual authentication logic
    # For now, return a mock user or get from session
    # This should be replaced with actual authentication
    user_id = request.headers.get('X-User-Id')  # Placeholder
    if user_id:
        try:
            return User.get_by_id(int(user_id))
        except:
            return None
    return None


def check_role(user, allowed_roles):
    """Check if user has one of the allowed roles."""
    if not user:
        return False
    return user.role in allowed_roles


def validate_date(date_string):
    """Validate date string format (YYYY-MM-DD) and check if it's within reasonable range."""
    if not date_string:
        return None, None
    
    try:
        parsed_date = datetime.strptime(date_string, '%Y-%m-%d').date()
        # Check if date is not more than 1 year in the future
        max_future_date = date.today().replace(year=date.today().year + 1)
        if parsed_date > max_future_date:
            return None, "Delivery date cannot be more than 1 year in the future"
        return parsed_date, None
    except ValueError:
        return None, "Invalid date format. Expected YYYY-MM-DD"


def validate_url(url_string):
    """Validate URL format."""
    if not url_string:
        return None, None
    
    if not isinstance(url_string, str) or len(url_string) > 500:
        return None, "Invalid URL format or URL too long (max 500 characters)"
    
    # Basic URL validation
    if not (url_string.startswith('http://') or url_string.startswith('https://')):
        return None, "URL must start with http:// or https://"
    
    return url_string, None


def site_procurement_get(site_id):  # noqa: E501
    """Get procurement data for a site

    :param site_id: Site ID
    :type site_id: int

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 404
    payload = {"message": generic_message}

    try:
        logging.info(f"[site_procurement_get] Fetching procurement data for site_id={site_id}")
        
        # Get current user
        current_user = get_current_user()
        if not current_user:
            payload = {
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": "Authentication required"
                }
            }
            return jsonify(payload), 401

        # Validate site_id
        try:
            site_id_int = int(site_id)
        except (TypeError, ValueError):
            payload = {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid site ID"
                }
            }
            return jsonify(payload), 400

        # Check if site exists
        site = Site.get_by_id(site_id_int)
        if not site:
            payload = {
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Site not found"
                }
            }
            return jsonify(payload), 404

        # Get procurement data
        procurement = ProcurementData.get_by_site_id(site_id_int)
        
        if not procurement:
            payload = {
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Procurement data not found for this site"
                }
            }
            return jsonify(payload), 404

        payload = {
            "message": "Successfully fetched procurement data",
            "data": procurement.to_dict()
        }
        result = 200

    except Exception as error:
        logging.error(
            f"[site_procurement_get] Error fetching procurement data for site_id={site_id}: {str(error)}\n"
            f"{traceback.format_exc()}"
        )
        payload = {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": generic_message
            }
        }
        result = 500

    return jsonify(payload), result


def site_procurement_put(site_id, body):  # noqa: E501
    """Update procurement data (save as draft)

    :param site_id: Site ID
    :type site_id: int
    :param body: Procurement data
    :type body: dict | bytes

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 400
    payload = {"message": generic_message}

    try:
        logging.info(f"[site_procurement_put] Updating procurement data for site_id={site_id}")
        
        # Get current user
        current_user = get_current_user()
        if not current_user:
            payload = {
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": "Authentication required"
                }
            }
            return jsonify(payload), 401

        # Validate site_id
        try:
            site_id_int = int(site_id)
        except (TypeError, ValueError):
            payload = {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid site ID"
                }
            }
            return jsonify(payload), 400

        # Check if site exists
        site = Site.get_by_id(site_id_int)
        if not site:
            payload = {
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Site not found"
                }
            }
            return jsonify(payload), 404

        # Parse request body
        request_json = connexion.request.get_json() if connexion.request.is_json else (body or {})
        
        delivery_date_str = request_json.get("delivery_date")
        delivery_receipt_url = request_json.get("delivery_receipt_url")
        summary = request_json.get("summary")
        status = request_json.get("status", "draft")

        # Validate status - must be 'draft' for this endpoint
        if status and status != "draft":
            payload = {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Status must be 'draft' for this endpoint"
                }
            }
            return jsonify(payload), 400

        # Validate date if provided
        delivery_date = None
        if delivery_date_str:
            delivery_date, date_error = validate_date(delivery_date_str)
            if date_error:
                payload = {
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": date_error
                    }
                }
                return jsonify(payload), 400

        # Validate URL if provided
        if delivery_receipt_url:
            validated_url, url_error = validate_url(delivery_receipt_url)
            if url_error:
                payload = {
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": url_error
                    }
                }
                return jsonify(payload), 400
            delivery_receipt_url = validated_url

        # Validate summary length if provided
        if summary and len(summary) > 5000:
            payload = {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Summary cannot exceed 5000 characters"
                }
            }
            return jsonify(payload), 400

        # Get or create procurement data
        procurement = ProcurementData.get_by_site_id(site_id_int)
        
        if procurement:
            # Update existing record
            if delivery_date_str is not None:
                procurement.delivery_date = delivery_date
            if delivery_receipt_url is not None:
                procurement.delivery_receipt_url = delivery_receipt_url
            if summary is not None:
                procurement.summary = summary
            procurement.status = "draft"
            procurement.update_row()
        else:
            # Create new record
            procurement = ProcurementData(
                site_id=site_id_int,
                delivery_date=delivery_date,
                delivery_receipt_url=delivery_receipt_url,
                summary=summary,
                status="draft"
            )
            procurement.create_row()

        payload = {
            "message": "Procurement data updated successfully",
            "data": procurement.to_dict()
        }
        result = 200

    except IntegrityError as e:
        db.session.rollback()
        logging.error(f"[site_procurement_put] IntegrityError: {str(e)}")
        payload = {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "A procurement record already exists for this site"
            }
        }
        result = 400
    except Exception as error:
        db.session.rollback()
        logging.error(
            f"[site_procurement_put] Error updating procurement data for site_id={site_id}: {str(error)}\n"
            f"{traceback.format_exc()}"
        )
        payload = {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": generic_message
            }
        }
        result = 500

    return jsonify(payload), result


def site_procurement_complete_post(site_id, body):  # noqa: E501
    """Mark procurement as complete (Admin or Deployment Engineer only)

    :param site_id: Site ID
    :type site_id: int
    :param body: Procurement completion data
    :type body: dict | bytes

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 400
    payload = {"message": generic_message}

    try:
        logging.info(f"[site_procurement_complete_post] Marking procurement complete for site_id={site_id}")
        
        # Get current user
        current_user = get_current_user()
        if not current_user:
            payload = {
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": "Authentication required"
                }
            }
            return jsonify(payload), 401

        # Check role - only Admin or Deployment Engineer can mark as complete
        if not check_role(current_user, [ADMIN_ROLE, DEPLOYMENT_ENGINEER_ROLE]):
            payload = {
                "error": {
                    "code": "FORBIDDEN",
                    "message": "Only Admin or Deployment Engineer can mark procurement as complete"
                }
            }
            return jsonify(payload), 403

        # Validate site_id
        try:
            site_id_int = int(site_id)
        except (TypeError, ValueError):
            payload = {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid site ID"
                }
            }
            return jsonify(payload), 400

        # Check if site exists
        site = Site.get_by_id(site_id_int)
        if not site:
            payload = {
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Site not found"
                }
            }
            return jsonify(payload), 404

        # Parse request body
        request_json = connexion.request.get_json() if connexion.request.is_json else (body or {})
        
        delivery_date_str = request_json.get("delivery_date")
        delivery_receipt_url = request_json.get("delivery_receipt_url")
        summary = request_json.get("summary")

        # Validate required fields
        validation_errors = {}
        
        if not delivery_date_str:
            validation_errors["delivery_date"] = "Delivery date is required"
        else:
            delivery_date, date_error = validate_date(delivery_date_str)
            if date_error:
                validation_errors["delivery_date"] = date_error
            elif not delivery_date:
                validation_errors["delivery_date"] = "Invalid delivery date"

        if not delivery_receipt_url:
            validation_errors["delivery_receipt_url"] = "Delivery receipt URL is required"
        else:
            validated_url, url_error = validate_url(delivery_receipt_url)
            if url_error:
                validation_errors["delivery_receipt_url"] = url_error
            else:
                delivery_receipt_url = validated_url

        if not summary or not summary.strip():
            validation_errors["summary"] = "Summary is required and cannot be empty"
        elif len(summary) > 5000:
            validation_errors["summary"] = "Summary cannot exceed 5000 characters"

        if validation_errors:
            payload = {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Validation failed",
                    "details": validation_errors
                }
            }
            return jsonify(payload), 422

        # Get or create procurement data
        procurement = ProcurementData.get_by_site_id(site_id_int)
        
        if procurement:
            # Check if already completed
            if procurement.status == "completed":
                payload = {
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "Procurement is already marked as complete"
                    }
                }
                return jsonify(payload), 400
            
            # Update existing record
            procurement.delivery_date = delivery_date
            procurement.delivery_receipt_url = delivery_receipt_url
            procurement.summary = summary
            procurement.status = "completed"
            procurement.completed_at = datetime.utcnow()
            procurement.completed_by = current_user.id
            procurement.update_row()
        else:
            # Create new record as completed
            procurement = ProcurementData(
                site_id=site_id_int,
                delivery_date=delivery_date,
                delivery_receipt_url=delivery_receipt_url,
                summary=summary,
                status="completed",
                completed_by=current_user.id
            )
            procurement.completed_at = datetime.utcnow()
            procurement.create_row()

        # Update site status to 'procurement_done'
        site.status = 'procurement_done'
        site.update_row()

        payload = {
            "message": "Procurement marked as complete successfully",
            "data": procurement.to_dict()
        }
        result = 200

    except IntegrityError as e:
        db.session.rollback()
        logging.error(f"[site_procurement_complete_post] IntegrityError: {str(e)}")
        payload = {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "A procurement record already exists for this site"
            }
        }
        result = 400
    except Exception as error:
        db.session.rollback()
        logging.error(
            f"[site_procurement_complete_post] Error marking procurement complete for site_id={site_id}: {str(error)}\n"
            f"{traceback.format_exc()}"
        )
        payload = {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": generic_message
            }
        }
        result = 500

    return jsonify(payload), result

