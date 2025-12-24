import connexion
from flask import jsonify, request
import logging
from ..utils.messages import generic_message
from ..db_models.software_category import SoftwareCategory
from ..db_models.software_module import SoftwareModule
from ..db_models.hardware_category import HardwareCategory
from ..db_models.hardware_item import HardwareItem
from ..db_models.recommendation_rule import RecommendationRule


def platform_software_categories_get():  # noqa: E501
    """Get list of software categories

     # noqa: E501

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 400
    payload = {"message": generic_message}

    try:
        logging.info("[platform_software_categories_get] Fetching software categories")
        
        # Get optional query parameters
        is_active = request.args.get('is_active', type=str)
        active_only = None
        if is_active:
            active_only = is_active.lower() == 'true'

        categories = SoftwareCategory.get_all(active_only=active_only) or []
        categories_data = [cat.to_dict() for cat in categories]

        payload = {
            "message": "Successfully fetched software categories",
            "data": categories_data
        }
        result = 200

    except Exception as error:
        logging.error(f"[platform_software_categories_get] Error: {error}")
        print(error)
        result = 400
        payload = {"message": generic_message}

    return jsonify(payload), result


def platform_software_modules_get():  # noqa: E501
    """Get list of software modules

     # noqa: E501

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 400
    payload = {"message": generic_message}

    try:
        logging.info("[platform_software_modules_get] Fetching software modules")
        
        # Get optional query parameters
        category_ids_param = request.args.get('category_ids', type=str)
        is_active = request.args.get('is_active', type=str)
        
        category_ids = None
        if category_ids_param:
            try:
                category_ids = [int(id.strip()) for id in category_ids_param.split(',') if id.strip()]
            except ValueError:
                logging.warning(f"[platform_software_modules_get] Invalid category_ids: {category_ids_param}")
                category_ids = None

        active_only = None
        if is_active:
            active_only = is_active.lower() == 'true'

        modules = SoftwareModule.get_all(category_ids=category_ids, active_only=active_only) or []
        modules_data = [module.to_dict() for module in modules]

        payload = {
            "message": "Successfully fetched software modules",
            "data": modules_data
        }
        result = 200

    except Exception as error:
        logging.error(f"[platform_software_modules_get] Error: {error}")
        print(error)
        result = 400
        payload = {"message": generic_message}

    return jsonify(payload), result


def platform_hardware_items_get():  # noqa: E501
    """Get list of hardware items

     # noqa: E501

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 400
    payload = {"message": generic_message}

    try:
        logging.info("[platform_hardware_items_get] Fetching hardware items")
        
        # Get optional query parameters
        category_ids_param = request.args.get('category_ids', type=str)
        is_active = request.args.get('is_active', type=str)
        
        category_ids = None
        if category_ids_param:
            try:
                category_ids = [int(id.strip()) for id in category_ids_param.split(',') if id.strip()]
            except ValueError:
                logging.warning(f"[platform_hardware_items_get] Invalid category_ids: {category_ids_param}")
                category_ids = None

        active_only = None
        if is_active:
            active_only = is_active.lower() == 'true'

        items = HardwareItem.get_all(category_ids=category_ids, active_only=active_only) or []
        items_data = [item.to_dict() for item in items]

        payload = {
            "message": "Successfully fetched hardware items",
            "data": items_data
        }
        result = 200

    except Exception as error:
        logging.error(f"[platform_hardware_items_get] Error: {error}")
        print(error)
        result = 400
        payload = {"message": generic_message}

    return jsonify(payload), result


def platform_recommendation_rules_get():  # noqa: E501
    """Get list of recommendation rules

     # noqa: E501

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 400
    payload = {"message": generic_message}

    try:
        logging.info("[platform_recommendation_rules_get] Fetching recommendation rules")
        
        # Get optional query parameters
        category_ids_param = request.args.get('category_ids', type=str)
        
        category_ids = None
        if category_ids_param:
            try:
                category_ids = [int(id.strip()) for id in category_ids_param.split(',') if id.strip()]
            except ValueError:
                logging.warning(f"[platform_recommendation_rules_get] Invalid category_ids: {category_ids_param}")
                category_ids = None

        rules = RecommendationRule.get_all(category_ids=category_ids) or []
        rules_data = [rule.to_dict() for rule in rules]

        payload = {
            "message": "Successfully fetched recommendation rules",
            "data": rules_data
        }
        result = 200

    except Exception as error:
        logging.error(f"[platform_recommendation_rules_get] Error: {error}")
        print(error)
        result = 400
        payload = {"message": generic_message}

    return jsonify(payload), result

