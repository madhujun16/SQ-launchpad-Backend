import connexion
from flask import jsonify
import logging
from ..utils.messages import generic_message
from ..db_models.site import Site
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
            payload = {"message": "Site not found"}
            return jsonify(payload), 404

        # Business rule: allow delete only for non-live deployments
        normalized_status = str(site.status or "").strip().lower()
        non_deletable_statuses = {"deployed", "live"}

        if normalized_status in non_deletable_statuses:
            payload = {
                "message": "Cannot delete a site once it is deployed or live"
            }
            return jsonify(payload), result

        # At this point, deleting the site will cascade to pages/sections/fields
        deleted_id = site.delete_row()

        if deleted_id:
            payload = {"message": "Site deleted successfully"}
            result = 200
        else:
            payload = {"message": "Unable to delete the site"}
            result = 400

    except Exception as error:
        print(error)
        result = 400
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
                try:
                    if isinstance(raw_value, str):
                        value = json.loads(raw_value)
                    else:
                        value = raw_value
                except Exception:
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