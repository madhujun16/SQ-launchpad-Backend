import connexion
from flask import jsonify, request
import logging
import traceback
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from ..utils.messages import generic_message
from ..db import db
from ..db_models.go_live_data import GoLiveData
from ..db_models.site import Site
from ..db_models.user import User
from ..db_models.procurement_data import ProcurementData

# TODO: Define role constants - these should match your role system
# Assuming: 1=Admin, 2=Operations Manager, 3=Deployment Engineer
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


def site_go_live_get(site_id):  # noqa: E501
    """Get go live data for a site

    :param site_id: Site ID
    :type site_id: int

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 400
    payload = {"message": generic_message}

    try:
        logging.info(f"[site_go_live_get] Fetching go live data for site_id={site_id}")
        
        # Get current user
        current_user = get_current_user()
        if not current_user:
            payload = {"message": "Authentication required"}
            return jsonify(payload), 401

        # Validate site_id
        try:
            site_id_int = int(site_id)
        except (TypeError, ValueError):
            payload = {"message": "Invalid site ID"}
            return jsonify(payload), result

        # Check if site exists
        site = Site.get_by_id(site_id_int)
        if not site:
            payload = {"message": "Site not found"}
            return jsonify(payload), 404

        # Get go live data
        go_live = GoLiveData.get_by_site_id(site_id_int)
        if not go_live:
            payload = {
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Go live data not found for this site"
                }
            }
            return jsonify(payload), 404

        payload = {
            "message": "Successfully fetched go live data",
            "data": go_live.to_dict()
        }
        result = 200

    except Exception as error:
        error_trace = traceback.format_exc()
        logging.error(f"[site_go_live_get] Unexpected error: {str(error)}")
        logging.error(f"[site_go_live_get] Full traceback: {error_trace}")
        result = 500
        payload = {"message": "An unexpected error occurred while fetching go live data"}

    return jsonify(payload), result


def site_go_live_activate(site_id, body):  # noqa: E501
    """Mark site as live

    :param site_id: Site ID
    :type site_id: int
    :param body: Activation data
    :type body: dict | bytes

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 400
    payload = {"message": generic_message}

    try:
        logging.info(f"[site_go_live_activate] Activating go live for site_id={site_id}")
        
        # Get current user
        current_user = get_current_user()
        if not current_user:
            payload = {"message": "Authentication required"}
            return jsonify(payload), 401

        # Check role - only Admin or Deployment Engineer can activate
        if not check_role(current_user, [ADMIN_ROLE, DEPLOYMENT_ENGINEER_ROLE]):
            payload = {"message": "Only Admin or Deployment Engineer can mark site as live"}
            return jsonify(payload), 403

        # Validate site_id
        try:
            site_id_int = int(site_id)
        except (TypeError, ValueError):
            payload = {"message": "Invalid site ID"}
            return jsonify(payload), result

        # Check if site exists
        site = Site.get_by_id(site_id_int)
        if not site:
            payload = {"message": "Site not found"}
            return jsonify(payload), 404

        # Check prerequisites: Site must be in 'deployed' status (deployment must be completed)
        if site.status != 'deployed':
            payload = {
                "error": {
                    "code": "PREREQUISITE_NOT_MET",
                    "message": f"Cannot go live: site status is '{site.status}'. Deployment must be completed first (all deployment steps must be completed)."
                }
            }
            return jsonify(payload), 400

        # Parse request body
        request_json = connexion.request.get_json() if connexion.request.is_json else (body or {})
        notes = request_json.get("notes", "")

        # Validation: notes are required
        if not notes or not notes.strip():
            payload = {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Notes are required when going live",
                    "details": {
                        "field": "notes"
                    }
                }
            }
            return jsonify(payload), 422

        # Validate notes length
        if len(notes) > 5000:
            payload = {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Notes cannot exceed 5000 characters",
                    "details": {
                        "field": "notes"
                    }
                }
            }
            return jsonify(payload), 422

        # Get or create go live data
        go_live = GoLiveData.get_by_site_id(site_id_int)
        
        if go_live:
            # Update existing record
            go_live.status = 'live'
            go_live.go_live_date = datetime.utcnow()
            go_live.signed_off_by = current_user.id
            go_live.notes = notes
            try:
                go_live.update_row()
            except Exception as db_error:
                db.session.rollback()
                error_details = str(db_error)
                logging.error(f"[site_go_live_activate] Database error: {error_details}")
                logging.error(f"[site_go_live_activate] Full traceback: {traceback.format_exc()}")
                payload = {"message": f"Error updating go live data: {error_details}"}
                result = 500
                return jsonify(payload), result
        else:
            # Create new record
            go_live = GoLiveData(
                site_id=site_id_int,
                status='live',
                go_live_date=datetime.utcnow(),
                signed_off_by=current_user.id,
                notes=notes
            )
            try:
                go_live.create_row()
            except IntegrityError as e:
                db.session.rollback()
                error_details = str(e.orig) if hasattr(e, 'orig') else str(e)
                logging.error(f"[site_go_live_activate] IntegrityError: {error_details}")
                payload = {"message": "Error creating go live data: duplicate entry"}
                result = 409
                return jsonify(payload), result
            except Exception as db_error:
                db.session.rollback()
                error_details = str(db_error)
                logging.error(f"[site_go_live_activate] Database error: {error_details}")
                logging.error(f"[site_go_live_activate] Full traceback: {traceback.format_exc()}")
                payload = {"message": f"Error creating go live data: {error_details}"}
                result = 500
                return jsonify(payload), result

        # Update site status to 'live'
        site.status = 'live'
        try:
            site.update_row()
        except Exception as site_error:
            db.session.rollback()
            logging.warning(f"[site_go_live_activate] Failed to update site status: {str(site_error)}")
            # Don't fail the request if site update fails, but log it

        payload = {
            "message": "Site marked as live successfully",
            "data": go_live.to_dict()
        }
        result = 200

    except Exception as error:
        db.session.rollback()
        error_trace = traceback.format_exc()
        logging.error(f"[site_go_live_activate] Unexpected error: {str(error)}")
        logging.error(f"[site_go_live_activate] Full traceback: {error_trace}")
        result = 500
        payload = {"message": "An unexpected error occurred while marking site as live"}

    return jsonify(payload), result


def site_go_live_deactivate(site_id, body):  # noqa: E501
    """Mark site as offline

    :param site_id: Site ID
    :type site_id: int
    :param body: Deactivation data
    :type body: dict | bytes

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 400
    payload = {"message": generic_message}

    try:
        logging.info(f"[site_go_live_deactivate] Deactivating go live for site_id={site_id}")
        
        # Get current user
        current_user = get_current_user()
        if not current_user:
            payload = {"message": "Authentication required"}
            return jsonify(payload), 401

        # Check role - only Admin or Deployment Engineer can deactivate
        if not check_role(current_user, [ADMIN_ROLE, DEPLOYMENT_ENGINEER_ROLE]):
            payload = {"message": "Only Admin or Deployment Engineer can take site offline"}
            return jsonify(payload), 403

        # Validate site_id
        try:
            site_id_int = int(site_id)
        except (TypeError, ValueError):
            payload = {"message": "Invalid site ID"}
            return jsonify(payload), result

        # Check if site exists
        site = Site.get_by_id(site_id_int)
        if not site:
            payload = {"message": "Site not found"}
            return jsonify(payload), 404

        # Get go live data
        go_live = GoLiveData.get_by_site_id(site_id_int)
        if not go_live:
            payload = {
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Go live data not found for this site"
                }
            }
            return jsonify(payload), 404

        # Check if site is currently live
        if go_live.status != 'live':
            payload = {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": f"Cannot take site offline: site status is '{go_live.status}', not 'live'"
                }
            }
            return jsonify(payload), 400

        # Parse request body
        request_json = connexion.request.get_json() if connexion.request.is_json else (body or {})
        notes = request_json.get("notes", "")

        # Validate notes length if provided
        if notes and len(notes) > 5000:
            payload = {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Notes cannot exceed 5000 characters",
                    "details": {
                        "field": "notes"
                    }
                }
            }
            return jsonify(payload), 422

        # Update go live data
        # Preserve go_live_date and signed_off_by for historical record
        go_live.status = 'offline'
        if notes:
            go_live.notes = notes
        # Keep go_live_date and signed_off_by unchanged

        try:
            go_live.update_row()
        except Exception as db_error:
            db.session.rollback()
            error_details = str(db_error)
            logging.error(f"[site_go_live_deactivate] Database error: {error_details}")
            logging.error(f"[site_go_live_deactivate] Full traceback: {traceback.format_exc()}")
            payload = {"message": f"Error updating go live data: {error_details}"}
            result = 500
            return jsonify(payload), result

        # Update site status back to 'procurement_done'
        site.status = 'procurement_done'
        try:
            site.update_row()
        except Exception as site_error:
            db.session.rollback()
            logging.warning(f"[site_go_live_deactivate] Failed to update site status: {str(site_error)}")
            # Don't fail the request if site update fails, but log it

        payload = {
            "message": "Site taken offline successfully",
            "data": go_live.to_dict()
        }
        result = 200

    except Exception as error:
        db.session.rollback()
        error_trace = traceback.format_exc()
        logging.error(f"[site_go_live_deactivate] Unexpected error: {str(error)}")
        logging.error(f"[site_go_live_deactivate] Full traceback: {error_trace}")
        result = 500
        payload = {"message": "An unexpected error occurred while taking site offline"}

    return jsonify(payload), result

