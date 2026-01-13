import connexion
from flask import jsonify, request
import logging
import traceback
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from ..utils.messages import generic_message
from ..db import db
from ..db_models.scoping_approval import ScopingApproval
from ..db_models.approval_action import ApprovalAction
from ..db_models.site import Site
from ..db_models.user import User
from ..utils.cookie_manager import decrypt_token

# TODO: Define role constants - these should match your role system
# Assuming: 1=Admin, 2=Operations Manager, 3=Deployment Engineer
ADMIN_ROLE = 1
OPS_MANAGER_ROLE = 2
DEPLOYMENT_ENGINEER_ROLE = 3


def get_current_user():
    """Get current user from session cookie (same as /api/user/me endpoint)."""
    try:
        # Get session cookie
        token = request.cookies.get('session_id')
        if not token:
            return None
        
        # Decode JWT token to get email
        email = decrypt_token(token)
        if not email:
            return None
        
        # Get user from database by email
        user = User.get_by_email(email)
        return user
    except Exception as e:
        logging.error(f"[get_current_user] Error decoding session token: {e}")
        return None


def check_role(user, allowed_roles):
    """Check if user has one of the allowed roles."""
    if not user:
        return False
    return user.role in allowed_roles


def site_scoping_submit(site_id, body):  # noqa: E501
    """Submit scoping for approval

    :param site_id: Site ID
    :type site_id: int
    :param body: Scoping submission data
    :type body: dict | bytes

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 400
    payload = {"message": generic_message}

    try:
        logging.info(f"[site_scoping_submit] Submitting scoping for site_id={site_id}")
        
        # Get current user
        current_user = get_current_user()
        if not current_user:
            payload = {"message": "Authentication required"}
            return jsonify(payload), 401

        # Check role - only Deployment Engineer can submit
        if not check_role(current_user, [DEPLOYMENT_ENGINEER_ROLE]):
            payload = {"message": "Only Deployment Engineers can submit scoping for approval"}
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

        # Check if there's already a pending approval for this site
        pending_approval = ScopingApproval.get_pending_by_site_id(site_id_int)
        if pending_approval:
            payload = {
                "message": "A pending approval already exists for this site",
                "code": "CONFLICT"
            }
            return jsonify(payload), 409

        # Parse request body
        request_json = connexion.request.get_json() if connexion.request.is_json else (body or {})
        
        site_name = request_json.get("site_name")
        selected_software = request_json.get("selected_software", [])
        selected_hardware = request_json.get("selected_hardware", [])
        cost_summary = request_json.get("cost_summary", {})

        # Validation
        if not site_name:
            payload = {"message": "site_name is required"}
            return jsonify(payload), result

        if not selected_software and not selected_hardware:
            payload = {"message": "At least one software or hardware item must be selected"}
            return jsonify(payload), result

        # Validate software and hardware IDs exist and are active
        # TODO: Add validation for software/hardware IDs if needed

        # Create scoping data structure
        scoping_data = {
            "selected_software": selected_software,
            "selected_hardware": selected_hardware
        }

        # Create approval record
        approval = ScopingApproval(
            site_id=site_id_int,
            site_name=site_name,
            deployment_engineer_id=current_user.id,
            deployment_engineer_name=current_user.name,
            scoping_data=scoping_data,
            cost_breakdown=cost_summary,
            status='pending',
            version=1
        )

        try:
            approval_id = approval.create_row()
            
            # Create audit trail entry
            try:
                action = ApprovalAction(
                    approval_id=approval_id,
                    action='submit',
                    performed_by=current_user.id,
                    performed_by_role='deployment_engineer',
                    comment=f"Scoping submitted for {site_name}"
                )
                action.create_row()
            except Exception as action_error:
                logging.warning(f"[site_scoping_submit] Failed to create audit trail: {str(action_error)}")
                # Don't fail the request if audit trail fails

            payload = {
                "message": "Scoping submitted for approval successfully",
                "data": approval.to_dict()
            }
            result = 200

        except IntegrityError as e:
            db.session.rollback()
            error_details = str(e.orig) if hasattr(e, 'orig') else str(e)
            logging.error(f"[site_scoping_submit] IntegrityError: {error_details}")
            payload = {"message": "Database error while creating approval"}
            result = 500
        except Exception as db_error:
            db.session.rollback()
            error_details = str(db_error)
            logging.error(f"[site_scoping_submit] Database error: {error_details}")
            logging.error(f"[site_scoping_submit] Full traceback: {traceback.format_exc()}")
            payload = {"message": f"Error creating approval: {error_details}"}
            result = 500

    except Exception as error:
        db.session.rollback()
        error_trace = traceback.format_exc()
        logging.error(f"[site_scoping_submit] Unexpected error: {str(error)}")
        logging.error(f"[site_scoping_submit] Full traceback: {error_trace}")
        result = 500
        payload = {"message": "An unexpected error occurred while submitting scoping"}

    return jsonify(payload), result


def site_scoping_resubmit(site_id, body):  # noqa: E501
    """Resubmit scoping after rejection

    :param site_id: Site ID
    :type site_id: int
    :param body: Resubmission data
    :type body: dict | bytes

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 400
    payload = {"message": generic_message}

    try:
        logging.info(f"[site_scoping_resubmit] Resubmitting scoping for site_id={site_id}")
        
        # Get current user
        current_user = get_current_user()
        if not current_user:
            payload = {"message": "Authentication required"}
            return jsonify(payload), 401

        # Check role
        if not check_role(current_user, [DEPLOYMENT_ENGINEER_ROLE]):
            payload = {"message": "Only Deployment Engineers can resubmit scoping"}
            return jsonify(payload), 403

        # Validate site_id
        try:
            site_id_int = int(site_id)
        except (TypeError, ValueError):
            payload = {"message": "Invalid site ID"}
            return jsonify(payload), result

        # Parse request body
        request_json = connexion.request.get_json() if connexion.request.is_json else (body or {})
        
        previous_approval_id = request_json.get("previous_approval_id")
        site_name = request_json.get("site_name")
        selected_software = request_json.get("selected_software", [])
        selected_hardware = request_json.get("selected_hardware", [])
        cost_summary = request_json.get("cost_summary", {})

        # Validation
        if not previous_approval_id:
            payload = {"message": "previous_approval_id is required"}
            return jsonify(payload), result

        # Get previous approval
        try:
            previous_approval_id_int = int(previous_approval_id)
        except (TypeError, ValueError):
            payload = {"message": "Invalid previous_approval_id"}
            return jsonify(payload), result

        previous_approval = ScopingApproval.get_by_id(previous_approval_id_int)
        if not previous_approval:
            payload = {"message": "Previous approval not found"}
            return jsonify(payload), 404

        # Check if previous approval is rejected
        if previous_approval.status != 'rejected':
            payload = {
                "message": "Can only resubmit rejected approvals",
                "code": "INVALID_STATUS"
            }
            return jsonify(payload), 400

        # Check site matches
        if previous_approval.site_id != site_id_int:
            payload = {"message": "Site ID does not match previous approval"}
            return jsonify(payload), 400

        # Validation
        if not site_name:
            payload = {"message": "site_name is required"}
            return jsonify(payload), result

        # Create scoping data structure
        scoping_data = {
            "selected_software": selected_software,
            "selected_hardware": selected_hardware
        }

        # Create new approval with incremented version
        new_version = previous_approval.version + 1
        approval = ScopingApproval(
            site_id=site_id_int,
            site_name=site_name,
            deployment_engineer_id=current_user.id,
            deployment_engineer_name=current_user.name,
            scoping_data=scoping_data,
            cost_breakdown=cost_summary,
            status='pending',
            version=new_version,
            previous_version_id=previous_approval_id_int
        )

        try:
            approval_id = approval.create_row()
            
            # Create audit trail entry
            try:
                action = ApprovalAction(
                    approval_id=approval_id,
                    action='resubmit',
                    performed_by=current_user.id,
                    performed_by_role='deployment_engineer',
                    comment=f"Scoping resubmitted for {site_name} (version {new_version})"
                )
                action.create_row()
            except Exception as action_error:
                logging.warning(f"[site_scoping_resubmit] Failed to create audit trail: {str(action_error)}")

            payload = {
                "message": "Scoping resubmitted successfully",
                "data": approval.to_dict()
            }
            result = 200

        except IntegrityError as e:
            db.session.rollback()
            error_details = str(e.orig) if hasattr(e, 'orig') else str(e)
            logging.error(f"[site_scoping_resubmit] IntegrityError: {error_details}")
            payload = {"message": "Database error while creating approval"}
            result = 500
        except Exception as db_error:
            db.session.rollback()
            error_details = str(db_error)
            logging.error(f"[site_scoping_resubmit] Database error: {error_details}")
            logging.error(f"[site_scoping_resubmit] Full traceback: {traceback.format_exc()}")
            payload = {"message": f"Error creating approval: {error_details}"}
            result = 500

    except Exception as error:
        db.session.rollback()
        error_trace = traceback.format_exc()
        logging.error(f"[site_scoping_resubmit] Unexpected error: {str(error)}")
        logging.error(f"[site_scoping_resubmit] Full traceback: {error_trace}")
        result = 500
        payload = {"message": "An unexpected error occurred while resubmitting scoping"}

    return jsonify(payload), result


def scoping_approvals_get():  # noqa: E501
    """Get scoping approvals

    Query parameters:
    - status: Filter by status (pending, approved, rejected, changes_requested)
    - site_id: Filter by site ID

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 400
    payload = {"message": generic_message}

    try:
        logging.info("[scoping_approvals_get] Fetching scoping approvals")
        
        # Get current user
        current_user = get_current_user()
        if not current_user:
            payload = {"message": "Authentication required"}
            return jsonify(payload), 401

        # Get query parameters
        status = request.args.get('status')
        site_id = request.args.get('site_id')

        # If site_id is provided, get most recent approval for that site
        if site_id:
            try:
                site_id_int = int(site_id)
                approval = ScopingApproval.get_by_site_id(site_id_int, status=status)
                if approval:
                    payload = {
                        "message": "Successfully fetched scoping approval",
                        "data": approval.to_dict()
                    }
                    result = 200
                else:
                    payload = {"message": "Scoping approval not found for this site"}
                    result = 404
            except (TypeError, ValueError):
                payload = {"message": "Invalid site_id"}
                return jsonify(payload), result
        else:
            # Get all approvals with filters
            approvals = ScopingApproval.get_all(status=status, site_id=None)
            if approvals is None:
                payload = {"message": "Error fetching approvals"}
                result = 500
            else:
                approvals_data = [approval.to_dict() for approval in approvals]
                payload = {
                    "message": "Successfully fetched scoping approvals",
                    "data": approvals_data
                }
                result = 200

    except Exception as error:
        error_trace = traceback.format_exc()
        logging.error(f"[scoping_approvals_get] Unexpected error: {str(error)}")
        logging.error(f"[scoping_approvals_get] Full traceback: {error_trace}")
        result = 500
        payload = {"message": "An unexpected error occurred while fetching approvals"}

    return jsonify(payload), result


def scoping_approvals_id_get(approval_id):  # noqa: E501
    """Get scoping approval by ID

    :param approval_id: Approval ID
    :type approval_id: int

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 400
    payload = {"message": generic_message}

    try:
        logging.info(f"[scoping_approvals_id_get] Fetching approval id={approval_id}")
        
        # Get current user
        current_user = get_current_user()
        if not current_user:
            payload = {"message": "Authentication required"}
            return jsonify(payload), 401

        # Validate approval_id
        try:
            approval_id_int = int(approval_id)
        except (TypeError, ValueError):
            payload = {"message": "Invalid approval ID"}
            return jsonify(payload), result

        approval = ScopingApproval.get_by_id(approval_id_int)
        if not approval:
            payload = {"message": "Scoping approval not found"}
            return jsonify(payload), 404

        payload = {
            "message": "Successfully fetched scoping approval",
            "data": approval.to_dict()
        }
        result = 200

    except Exception as error:
        error_trace = traceback.format_exc()
        logging.error(f"[scoping_approvals_id_get] Unexpected error: {str(error)}")
        logging.error(f"[scoping_approvals_id_get] Full traceback: {error_trace}")
        result = 500
        payload = {"message": "An unexpected error occurred while fetching approval"}

    return jsonify(payload), result


def scoping_approvals_id_approve(approval_id, body):  # noqa: E501
    """Approve a scoping request

    :param approval_id: Approval ID
    :type approval_id: int
    :param body: Approval data
    :type body: dict | bytes

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 400
    payload = {"message": generic_message}

    try:
        logging.info(f"[scoping_approvals_id_approve] Approving approval id={approval_id}")
        
        # Get current user
        current_user = get_current_user()
        if not current_user:
            payload = {"message": "Authentication required"}
            return jsonify(payload), 401

        # Check role - only Admin or Operations Manager can approve
        if not check_role(current_user, [ADMIN_ROLE, OPS_MANAGER_ROLE]):
            payload = {"message": "Only Admin or Operations Manager can approve scoping"}
            return jsonify(payload), 403

        # Validate approval_id
        try:
            approval_id_int = int(approval_id)
        except (TypeError, ValueError):
            payload = {"message": "Invalid approval ID"}
            return jsonify(payload), result

        approval = ScopingApproval.get_by_id(approval_id_int)
        if not approval:
            payload = {"message": "Scoping approval not found"}
            return jsonify(payload), 404

        # Check if approval is in pending status
        if approval.status != 'pending':
            payload = {
                "message": f"Cannot approve approval with status '{approval.status}'. Only pending approvals can be approved.",
                "code": "INVALID_STATUS"
            }
            return jsonify(payload), 400

        # Parse request body
        request_json = connexion.request.get_json() if connexion.request.is_json else (body or {})
        comment = request_json.get("comment", "")

        # Update approval
        approval.status = 'approved'
        approval.reviewed_at = datetime.utcnow()
        approval.reviewed_by = current_user.id
        approval.review_comment = comment
        approval.ops_manager_id = current_user.id if current_user.role == OPS_MANAGER_ROLE else approval.ops_manager_id
        approval.ops_manager_name = current_user.name if current_user.role == OPS_MANAGER_ROLE else approval.ops_manager_name

        try:
            approval.update_row()
            
            # Update site status
            site = Site.get_by_id(approval.site_id)
            if site:
                site.status = 'approved'
                site.update_row()

            # Create audit trail entry
            try:
                action = ApprovalAction(
                    approval_id=approval_id_int,
                    action='approve',
                    performed_by=current_user.id,
                    performed_by_role='admin' if current_user.role == ADMIN_ROLE else 'ops_manager',
                    comment=comment
                )
                action.create_row()
            except Exception as action_error:
                logging.warning(f"[scoping_approvals_id_approve] Failed to create audit trail: {str(action_error)}")

            payload = {
                "message": "Scoping approved successfully",
                "data": approval.to_dict()
            }
            result = 200

        except Exception as db_error:
            db.session.rollback()
            error_details = str(db_error)
            logging.error(f"[scoping_approvals_id_approve] Database error: {error_details}")
            logging.error(f"[scoping_approvals_id_approve] Full traceback: {traceback.format_exc()}")
            payload = {"message": f"Error approving scoping: {error_details}"}
            result = 500

    except Exception as error:
        db.session.rollback()
        error_trace = traceback.format_exc()
        logging.error(f"[scoping_approvals_id_approve] Unexpected error: {str(error)}")
        logging.error(f"[scoping_approvals_id_approve] Full traceback: {error_trace}")
        result = 500
        payload = {"message": "An unexpected error occurred while approving scoping"}

    return jsonify(payload), result


def scoping_approvals_id_reject(approval_id, body):  # noqa: E501
    """Reject a scoping request

    :param approval_id: Approval ID
    :type approval_id: int
    :param body: Rejection data
    :type body: dict | bytes

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 400
    payload = {"message": generic_message}

    try:
        logging.info(f"[scoping_approvals_id_reject] Rejecting approval id={approval_id}")
        
        # Get current user
        current_user = get_current_user()
        if not current_user:
            payload = {"message": "Authentication required"}
            return jsonify(payload), 401

        # Check role - only Admin or Operations Manager can reject
        if not check_role(current_user, [ADMIN_ROLE, OPS_MANAGER_ROLE]):
            payload = {"message": "Only Admin or Operations Manager can reject scoping"}
            return jsonify(payload), 403

        # Validate approval_id
        try:
            approval_id_int = int(approval_id)
        except (TypeError, ValueError):
            payload = {"message": "Invalid approval ID"}
            return jsonify(payload), result

        approval = ScopingApproval.get_by_id(approval_id_int)
        if not approval:
            payload = {"message": "Scoping approval not found"}
            return jsonify(payload), 404

        # Check if approval is in pending status
        if approval.status != 'pending':
            payload = {
                "message": f"Cannot reject approval with status '{approval.status}'. Only pending approvals can be rejected.",
                "code": "INVALID_STATUS"
            }
            return jsonify(payload), 400

        # Parse request body
        request_json = connexion.request.get_json() if connexion.request.is_json else (body or {})
        comment = request_json.get("comment", "")
        rejection_reason = request_json.get("rejection_reason", comment)  # Use comment if rejection_reason not provided

        # Update approval
        approval.status = 'rejected'
        approval.reviewed_at = datetime.utcnow()
        approval.reviewed_by = current_user.id
        approval.review_comment = comment
        approval.rejection_reason = rejection_reason
        approval.ops_manager_id = current_user.id if current_user.role == OPS_MANAGER_ROLE else approval.ops_manager_id
        approval.ops_manager_name = current_user.name if current_user.role == OPS_MANAGER_ROLE else approval.ops_manager_name

        try:
            approval.update_row()

            # Create audit trail entry
            try:
                action = ApprovalAction(
                    approval_id=approval_id_int,
                    action='reject',
                    performed_by=current_user.id,
                    performed_by_role='admin' if current_user.role == ADMIN_ROLE else 'ops_manager',
                    comment=comment
                )
                action.create_row()
            except Exception as action_error:
                logging.warning(f"[scoping_approvals_id_reject] Failed to create audit trail: {str(action_error)}")

            payload = {
                "message": "Scoping rejected successfully",
                "data": approval.to_dict()
            }
            result = 200

        except Exception as db_error:
            db.session.rollback()
            error_details = str(db_error)
            logging.error(f"[scoping_approvals_id_reject] Database error: {error_details}")
            logging.error(f"[scoping_approvals_id_reject] Full traceback: {traceback.format_exc()}")
            payload = {"message": f"Error rejecting scoping: {error_details}"}
            result = 500

    except Exception as error:
        db.session.rollback()
        error_trace = traceback.format_exc()
        logging.error(f"[scoping_approvals_id_reject] Unexpected error: {str(error)}")
        logging.error(f"[scoping_approvals_id_reject] Full traceback: {error_trace}")
        result = 500
        payload = {"message": "An unexpected error occurred while rejecting scoping"}

    return jsonify(payload), result

