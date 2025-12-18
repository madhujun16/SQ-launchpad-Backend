import connexion
from typing import Dict
from typing import Tuple
from typing import Union
from flask import jsonify
from ..models.organization_request import OrganizationRequest  # noqa: E501
from ..db_models.organization import Organization
from ..utils import messages, transform_data



def organization_delete(organization_id):  # noqa: E501
    """Delete an organization

     # noqa: E501

    :param organization_id: 
    :type organization_id: int

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    return 'do some magic!'


def organization_get(organization_id=None):  # noqa: E501
    """Get list of organizations

     # noqa: E501

    :param organization_id: 
    :type organization_id: int

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    payload = {'message': messages.generic_message}
    result = 400

    try:
        # When no organization_id is provided OR it is "all", return all organizations
        if organization_id is None or str(organization_id).lower() == "all":
            orgs = Organization.get_all_orgs() or []
            all_orgs = transform_data.transform_orgs(orgs)
            payload = {"message": "details fetched succesfully", "data": all_orgs}
            result = 200
        else:
            # For specific organization, ensure we have a valid integer ID
            try:
                org_id = int(organization_id)
            except (TypeError, ValueError):
                payload = {"message": "Invalid organization_id"}
                return jsonify(payload), result

            org = Organization.get_by_id(org_id)
            _org = transform_data.transform_org(org)

            payload = {"message": "details fetched succesfully", "data": _org}
            result = 200

    except Exception as error:
        print(error)

    return jsonify(payload), result


def organization_post(body):  # noqa: E501
    """Create a new organization

     # noqa: E501

    :param organization_request: 
    :type organization_request: dict | bytes

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    organization_request = body
    if connexion.request.is_json:
        organization_request = OrganizationRequest.from_dict(connexion.request.get_json())  # noqa: E501

    payload = {'message':messages.generic_message}
    result = 400
    try:
        name = organization_request.name
        description = organization_request.description
        sector = organization_request.sector
        unit_code = organization_request.unit_code
        logo = organization_request.organization_logo
        # logo = f"https://storage.googleapis.com/launchpad_logo/{org_id}.svg"
        organization = Organization(name,description,sector,unit_code,logo)

        org = organization.create_row()

        if org:
            _org = transform_data.transform_org(org)
            payload = {'message':"Organization created successfully","data":_org}
            result = 200
        else:
            payload = {'message':"Unable to create organization"}
            result = 400

    except Exception as error:
        print(error)
    return jsonify(payload),result


def organization_put(body):  # noqa: E501
    """Update an existing organization

     # noqa: E501

    :param organization_request: 
    :type organization_request: dict | bytes

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    organization_request = body
    if connexion.request.is_json:
        organization_request = OrganizationRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
