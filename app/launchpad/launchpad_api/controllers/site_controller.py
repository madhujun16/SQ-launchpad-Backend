import connexion
from flask import jsonify
import logging
import traceback
from sqlalchemy.exc import IntegrityError, OperationalError
from ..utils.messages import generic_message
from ..db_models.site import Site
from ..db_models.page import Page
from ..db_models.section import Section
from ..db_models.fields import Field
from ..db import db
from ..utils.queries import get_all_site_details
from collections import defaultdict
import json

def site_delete(site_id):  # noqa: E501
    """Delete a site

     # noqa: E501

    :param site_id: 
    :type site_id: str

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 400
    payload = {"message": generic_message}

    try:
        logging.info(f"[site_delete] Incoming request to delete site_id={site_id}")

        if not site_id:
            payload = {"message": "Site ID is missing"}
            result = 400
            return jsonify(payload), result

        # Ensure we have an integer ID
        try:
            site_id_int = int(site_id)
        except (TypeError, ValueError):
            payload = {"message": "Invalid Site ID"}
            return jsonify(payload), result

        site = Site.get_by_id(site_id_int)

        if not site:
            logging.info(f"[site_delete] Site not found for id={site_id_int}")
            payload = {"message": "Site not found"}
            return jsonify(payload), 404

        logging.info(
            f"[site_delete] Found site id={site.id}, status={site.status}"
        )

        # Business rule: allow delete only for non-live deployments
        normalized_status = str(site.status or "").strip().lower()
        non_deletable_statuses = {"deployed", "live"}

        if normalized_status in non_deletable_statuses:
            payload = {
                "message": "Cannot delete a site once it is deployed or live"
            }
            logging.info(
                f"[site_delete] Rejecting delete for id={site.id} with status={site.status}"
            )
            return jsonify(payload), result

        # Try to delete the site - CASCADE should handle related records
        # If that fails, manually delete related records
        try:
            # First, try simple delete (relying on CASCADE if database has it)
            db.session.delete(site)
            db.session.commit()
            
            logging.info(f"[site_delete] Successfully deleted site id={site_id_int} (with CASCADE)")
            payload = {"message": "Site deleted successfully"}
            result = 200
            
        except (IntegrityError, OperationalError) as db_error:
            # CASCADE might not be working - manually delete related records
            db.session.rollback()
            logging.warning(
                f"[site_delete] CASCADE delete failed for site {site_id_int}. "
                f"Error: {str(db_error)}. Attempting manual cascade delete..."
            )
            
            try:
                # Re-fetch site to ensure we have a valid object after rollback
                site = Site.get_by_id(site_id_int)
                if not site:
                    payload = {"message": "Site not found after rollback"}
                    result = 404
                    return jsonify(payload), result
                
                # Get all pages for this site
                pages = Page.query.filter(Page.site_id == site_id_int).all()
                page_ids = [page.id for page in pages] if pages else []
                
                if page_ids:
                    # Get all sections for these pages
                    sections = Section.query.filter(Section.page_id.in_(page_ids)).all()
                    section_ids = [section.id for section in sections] if sections else []
                    
                    if section_ids:
                        # Delete all fields for these sections
                        fields_deleted = Field.query.filter(Field.section_id.in_(section_ids)).delete(synchronize_session=False)
                        logging.info(f"[site_delete] Deleted {fields_deleted} fields for site {site_id_int}")
                    
                    # Delete all sections
                    sections_deleted = Section.query.filter(Section.page_id.in_(page_ids)).delete(synchronize_session=False)
                    logging.info(f"[site_delete] Deleted {sections_deleted} sections for site {site_id_int}")
                
                # Delete all pages
                pages_deleted = Page.query.filter(Page.site_id == site_id_int).delete(synchronize_session=False)
                logging.info(f"[site_delete] Deleted {pages_deleted} pages for site {site_id_int}")
                
                # Now delete the site
                db.session.delete(site)
                db.session.commit()
                
                logging.info(f"[site_delete] Successfully deleted site id={site_id_int} (manual cascade)")
                payload = {"message": "Site deleted successfully"}
                result = 200
                
            except Exception as manual_delete_error:
                db.session.rollback()
                logging.error(
                    f"[site_delete] Manual cascade delete also failed for site {site_id_int}. "
                    f"Error: {str(manual_delete_error)}\n"
                    f"Traceback: {traceback.format_exc()}"
                )
                payload = {
                    "message": f"Unable to delete the site due to an internal error: {str(manual_delete_error)}"
                }
                result = 500
                
        except Exception as error:
            db.session.rollback()
            logging.error(
                f"[site_delete] Unexpected error deleting site {site_id_int}: {str(error)}\n"
                f"Traceback: {traceback.format_exc()}"
            )
            payload = {
                "message": f"Unable to delete the site due to an internal error: {str(error)}"
            }
            result = 500

    except Exception as error:
        logging.error(
            f"[site_delete] Exception while deleting site_id={site_id}: {error}\n"
            f"{traceback.format_exc()}"
        )
        result = 500
        payload = {"message": generic_message}

    return jsonify(payload), result

def site_get(id):  # noqa: E501
    """Get list of sites

     # noqa: E501


    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    
    return "site get api not implement yet"


def site_post(body):  # noqa: E501
    """Create a new site

     # noqa: E501

    :param site_request: 
    :type site_request: dict | bytes

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 400
    payload = {"message": generic_message}

    try:
        # Be flexible with the payload and ignore extra fields like `name`
        request_json = connexion.request.get_json() if connexion.request.is_json else (body or {})

        status = request_json.get("status")

        if not status:
            payload = {"message": "status is required"}
            return jsonify(payload), result

        # We currently only persist site status; name and other details live in the page/field structure.
        site = Site(status=status)
        site_id = site.create_row()

        if site_id:
            payload = {
                "message": "Site Created Succesfully",
                "data": {
                    "site_id": site_id,
                    "status": status,
                },
            }
            result = 200
        else:
            payload = {"message": "Site creation failed"}
            result = 400

    except Exception as error:
        print(error)
        result = 400
        payload = {"message": generic_message}


    return jsonify(payload),result


def site_put(body):  # noqa: E501
    """Update an existing site

     # noqa: E501

    :param site_request: 
    :type site_request: dict | bytes

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 400
    payload = {"message": generic_message}

    try:
        request_json = connexion.request.get_json() if connexion.request.is_json else (body or {})

        site_id = request_json.get("id")
        status = request_json.get("status")

        if not site_id:
            payload = {"message": "Invalid Site ID"}
            result = 400
            return jsonify(payload), result
        
        site = Site.get_by_id(site_id)

        if site:
            site.status = status
            site.update_row()
            payload = {"message": "Site updated successfully"}
            result = 200

        else:
            payload = {"message": "Invalid Site ID"}
            result = 400
        
    except Exception as error:
        print(error)
        result = 400
        payload = {"message": generic_message}

    return jsonify(payload),result

def site_all_get():  # noqa: E501
    """Get list of sites

     # noqa: E501


    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 400
    payload = {"message": generic_message}

    def _extract_display_value(value):
        """
        Helper to normalize field values that might be stored as simple
        strings or small JSON objects (e.g. {\"value\": \"asda\"}).
        """
        try:
            if isinstance(value, dict):
                # Common patterns used for field_value payloads
                for key in ("value", "text", "label"):
                    if key in value:
                        return value[key]
            return value
        except Exception:
            return value

    def _normalize_status(status):
        """Map internal statuses to the canonical values used by the frontend."""
        if not status:
            return status

        s = str(status).strip().lower()
        mapping = {
            "site-created": "Created",
            "created": "Created",
            "site_study_done": "site_study_done",
            "site-study-done": "site_study_done",
            "scoping_done": "scoping_done",
            "scoping-done": "scoping_done",
            "approved": "approved",
            "procurement_done": "procurement_done",
            "procurement-done": "procurement_done",
            "deployed": "deployed",
            "live": "live",
        }
        return mapping.get(s, status)

    try:
        all_sites = get_all_site_details()
        sites = defaultdict(dict)

        if all_sites is None:
            payload = {"message": "Unable to fetch sites"}
            result = 400
            return jsonify(payload), result

        # Aggregate raw data by site_id
        for site in all_sites:
            site_id = site.id
            _site = sites.get(site_id, {})
            _site["site_id"] = site_id
            _site["status"] = _normalize_status(site.status)

            if getattr(site, "field_name", None):
                raw_value = site.field_value
                # Handle field values that might be:
                # 1. Plain strings: "Site Name"
                # 2. JSON-encoded strings: "\"Site Name\"" or "{\"value\": \"Site Name\"}"
                # 3. Already parsed objects/dicts: {"value": "Site Name"}
                try:
                    if isinstance(raw_value, str):
                        # Try to parse as JSON (handles JSON-encoded strings)
                        try:
                            value = json.loads(raw_value)
                        except (json.JSONDecodeError, ValueError):
                            # Not valid JSON, use as plain string
                            value = raw_value
                    else:
                        # Already an object/dict, use as-is
                        value = raw_value
                except Exception:
                    # Fallback: use raw value if anything goes wrong
                    value = raw_value

                _site[site.field_name] = value

            sites[site_id] = _site

        # Normalize field names and shapes to what the frontend expects
        normalized_sites = []
        for _site in sites.values():
            # Derive primary name from site_name if present
            if "site_name" in _site and _site.get("site_name") is not None:
                _site["name"] = _extract_display_value(_site["site_name"])

            # Organization name: org_name -> organization_name
            org_name = _site.get("organization_name") or _site.get("org_name")
            if org_name is not None:
                _site["organization_name"] = _extract_display_value(org_name)

            # Unit code: prefer unit_code field, fall back to unit_id
            unit = _site.get("unit_code") or _site.get("unit_id")
            if unit is not None:
                _site["unit_code"] = _extract_display_value(unit)

            # Normalize commonly used fields (if present)
            for key in [
                "target_live_date",
                "suggested_go_live",
                "assigned_ops_manager",
                "assigned_deployment_engineer",
                "sector",
                "organization_logo",
                "organization_id",
            ]:
                if key in _site and _site[key] is not None:
                    _site[key] = _extract_display_value(_site[key])

            normalized_sites.append(_site)

        payload = {"data": normalized_sites, "message": "Succesfully fetched sites"}
        result = 200

    except Exception as error:
        logging.info(error)
        print(error)
        result = 400
        payload = {"message": generic_message}

    return jsonify(payload), result