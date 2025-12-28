import connexion
from flask import jsonify, request
import logging
from sqlalchemy.exc import IntegrityError
from ..utils.messages import generic_message
from ..db import db
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


def platform_hardware_categories_get():  # noqa: E501
    """Get list of hardware categories

     # noqa: E501

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 400
    payload = {"message": generic_message}

    try:
        logging.info("[platform_hardware_categories_get] Fetching hardware categories")
        
        # Get optional query parameters
        is_active = request.args.get('is_active', type=str)
        active_only = None
        if is_active:
            active_only = is_active.lower() == 'true'

        categories = HardwareCategory.get_all(active_only=active_only) or []
        categories_data = [cat.to_dict() for cat in categories]

        payload = {
            "message": "Successfully fetched hardware categories",
            "data": categories_data
        }
        result = 200

    except Exception as error:
        logging.error(f"[platform_hardware_categories_get] Error: {error}")
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


def platform_recommendation_rules_post(body):  # noqa: E501
    """Create a new recommendation rule

     # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 400
    payload = {"message": generic_message}

    try:
        logging.info("[platform_recommendation_rules_post] Creating recommendation rule")
        request_json = connexion.request.get_json() if connexion.request.is_json else (body or {})

        software_category = request_json.get("software_category")
        hardware_category = request_json.get("hardware_category")
        is_mandatory = request_json.get("is_mandatory", False)
        quantity = request_json.get("quantity", 1)

        # Validation
        if not software_category:
            payload = {"message": "software_category is required"}
            return jsonify(payload), result

        if not hardware_category:
            payload = {"message": "hardware_category is required"}
            return jsonify(payload), result

        try:
            software_category_id = int(software_category)
            hardware_category_id = int(hardware_category)
        except (TypeError, ValueError):
            payload = {"message": "Invalid category ID format"}
            return jsonify(payload), result

        if quantity < 1:
            payload = {"message": "quantity must be >= 1", "code": "INVALID_QUANTITY"}
            return jsonify(payload), result

        if not isinstance(is_mandatory, bool):
            payload = {"message": "is_mandatory must be a boolean"}
            return jsonify(payload), result

        # Validate categories exist
        software_cat = SoftwareCategory.get_by_id(software_category_id)
        if not software_cat:
            payload = {"message": "Invalid software_category ID", "code": "INVALID_CATEGORY"}
            return jsonify(payload), result

        hardware_cat = HardwareCategory.get_by_id(hardware_category_id)
        if not hardware_cat:
            payload = {"message": "Invalid hardware_category ID", "code": "INVALID_CATEGORY"}
            return jsonify(payload), result

        # Check for duplicate rule
        existing_rule = RecommendationRule.get_by_categories(software_category_id, hardware_category_id)
        if existing_rule:
            payload = {
                "message": "Recommendation rule already exists for this software and hardware category combination",
                "code": "DUPLICATE_RULE"
            }
            return jsonify(payload), 409

        # Create the rule
        rule = RecommendationRule(
            software_category_id=software_category_id,
            hardware_category_id=hardware_category_id,
            is_mandatory=is_mandatory,
            quantity=quantity
        )

        created_rule = rule.create_row()

        if created_rule:
            payload = {
                "message": "Recommendation rule created successfully",
                "data": created_rule.to_dict()
            }
            result = 200
        elif created_rule is None:
            # IntegrityError (duplicate constraint)
            payload = {
                "message": "Recommendation rule already exists for this software and hardware category combination",
                "code": "DUPLICATE_RULE"
            }
            result = 409
        else:
            payload = {"message": "Unable to create recommendation rule"}
            result = 400

    except Exception as error:
        logging.error(f"[platform_recommendation_rules_post] Error: {error}")
        print(error)
        result = 500
        payload = {"message": "An unexpected error occurred while creating the recommendation rule"}

    return jsonify(payload), result


def platform_recommendation_rules_id_put(id, body):  # noqa: E501
    """Update an existing recommendation rule

     # noqa: E501

    :param id: 
    :type id: int
    :param body: 
    :type body: dict | bytes

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 400
    payload = {"message": generic_message}

    try:
        logging.info(f"[platform_recommendation_rules_id_put] Updating recommendation rule id={id}")
        
        try:
            rule_id = int(id)
        except (TypeError, ValueError):
            payload = {"message": "Invalid rule ID"}
            return jsonify(payload), result

        rule = RecommendationRule.get_by_id(rule_id)
        if not rule:
            payload = {"message": "Recommendation rule not found"}
            return jsonify(payload), 404

        request_json = connexion.request.get_json() if connexion.request.is_json else (body or {})

        # Update fields if provided
        software_category_id = None
        hardware_category_id = None

        if "software_category" in request_json:
            try:
                software_category_id = int(request_json["software_category"])
                # Validate category exists
                software_cat = SoftwareCategory.get_by_id(software_category_id)
                if not software_cat:
                    payload = {"message": "Invalid software_category ID", "code": "INVALID_CATEGORY"}
                    return jsonify(payload), result
                rule.software_category_id = software_category_id
            except (TypeError, ValueError):
                payload = {"message": "Invalid software_category ID format"}
                return jsonify(payload), result

        if "hardware_category" in request_json:
            try:
                hardware_category_id = int(request_json["hardware_category"])
                # Validate category exists
                hardware_cat = HardwareCategory.get_by_id(hardware_category_id)
                if not hardware_cat:
                    payload = {"message": "Invalid hardware_category ID", "code": "INVALID_CATEGORY"}
                    return jsonify(payload), result
                rule.hardware_category_id = hardware_category_id
            except (TypeError, ValueError):
                payload = {"message": "Invalid hardware_category ID format"}
                return jsonify(payload), result

        if "is_mandatory" in request_json:
            if not isinstance(request_json["is_mandatory"], bool):
                payload = {"message": "is_mandatory must be a boolean"}
                return jsonify(payload), result
            rule.is_mandatory = request_json["is_mandatory"]

        if "quantity" in request_json:
            quantity = int(request_json["quantity"])
            if quantity < 1:
                payload = {"message": "quantity must be >= 1", "code": "INVALID_QUANTITY"}
                return jsonify(payload), result
            rule.quantity = quantity

        # Check for duplicate if categories are being updated
        if software_category_id is not None or hardware_category_id is not None:
            final_software_id = software_category_id if software_category_id is not None else rule.software_category_id
            final_hardware_id = hardware_category_id if hardware_category_id is not None else rule.hardware_category_id
            
            existing_rule = RecommendationRule.get_by_categories(final_software_id, final_hardware_id, exclude_id=rule_id)
            if existing_rule:
                payload = {
                    "message": "Recommendation rule already exists for this software and hardware category combination",
                    "code": "DUPLICATE_RULE"
                }
                return jsonify(payload), 409

        try:
            if rule.update_row():
                payload = {
                    "message": "Recommendation rule updated successfully",
                    "data": rule.to_dict()
                }
                result = 200
            else:
                payload = {"message": "Unable to update recommendation rule"}
                result = 400
        except IntegrityError as e:
            db.session.rollback()
            logging.error(f"[platform_recommendation_rules_id_put] IntegrityError: {str(e)}")
            payload = {
                "message": "Recommendation rule already exists for this software and hardware category combination",
                "code": "DUPLICATE_RULE"
            }
            result = 409
        except Exception as db_error:
            db.session.rollback()
            logging.error(f"[platform_recommendation_rules_id_put] Database error: {str(db_error)}")
            payload = {"message": "Unable to update recommendation rule due to database error"}
            result = 500

    except ValueError as ve:
        logging.error(f"[platform_recommendation_rules_id_put] ValueError: {str(ve)}")
        payload = {"message": f"Invalid input: {str(ve)}"}
        result = 400
    except Exception as error:
        logging.error(f"[platform_recommendation_rules_id_put] Error: {error}")
        print(error)
        result = 500
        payload = {"message": "An unexpected error occurred while updating the recommendation rule"}

    return jsonify(payload), result


def platform_recommendation_rules_id_delete(id):  # noqa: E501
    """Delete a recommendation rule

     # noqa: E501

    :param id: 
    :type id: int

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 400
    payload = {"message": generic_message}

    try:
        logging.info(f"[platform_recommendation_rules_id_delete] Deleting recommendation rule id={id}")
        
        try:
            rule_id = int(id)
        except (TypeError, ValueError):
            payload = {"message": "Invalid rule ID"}
            return jsonify(payload), result

        rule = RecommendationRule.get_by_id(rule_id)
        if not rule:
            payload = {"message": "Recommendation rule not found"}
            return jsonify(payload), 404

        try:
            if rule.delete_row():
                payload = {"message": "Recommendation rule deleted successfully"}
                result = 200
            else:
                payload = {"message": "Unable to delete recommendation rule"}
                result = 400
        except Exception as db_error:
            db.session.rollback()
            logging.error(f"[platform_recommendation_rules_id_delete] Database error: {str(db_error)}")
            payload = {"message": "Unable to delete recommendation rule due to database error"}
            result = 500

    except Exception as error:
        logging.error(f"[platform_recommendation_rules_id_delete] Error: {error}")
        print(error)
        result = 500
        payload = {"message": "An unexpected error occurred while deleting the recommendation rule"}

    return jsonify(payload), result


def platform_software_modules_post(body):  # noqa: E501
    """Create a new software module

     # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 400
    payload = {"message": generic_message}

    try:
        logging.info("[platform_software_modules_post] Creating software module")
        request_json = connexion.request.get_json() if connexion.request.is_json else (body or {})

        name = request_json.get("name")
        category_id = request_json.get("category_id")
        description = request_json.get("description")
        license_fee = request_json.get("license_fee")
        is_active = request_json.get("is_active", True)

        if not name:
            payload = {"message": "name is required"}
            return jsonify(payload), result

        if not category_id:
            payload = {"message": "category_id is required"}
            return jsonify(payload), result

        # Validate category exists
        category = SoftwareCategory.get_by_id(int(category_id))
        if not category:
            payload = {"message": "Invalid category_id"}
            return jsonify(payload), result

        software_module = SoftwareModule(
            name=name,
            category_id=int(category_id),
            description=description,
            license_fee=float(license_fee) if license_fee is not None else None,
            is_active=is_active
        )

        module = software_module.create_row()

        if module:
            payload = {
                "message": "Software module created successfully",
                "data": module.to_dict()
            }
            result = 200
        else:
            payload = {"message": "Unable to create software module"}
            result = 400

    except Exception as error:
        logging.error(f"[platform_software_modules_post] Error: {error}")
        print(error)
        result = 400
        payload = {"message": generic_message}

    return jsonify(payload), result


def platform_software_modules_id_put(id, body):  # noqa: E501
    """Update an existing software module

     # noqa: E501

    :param id: 
    :type id: int
    :param body: 
    :type body: dict | bytes

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 400
    payload = {"message": generic_message}

    try:
        logging.info(f"[platform_software_modules_id_put] Updating software module id={id}")
        
        try:
            module_id = int(id)
        except (TypeError, ValueError):
            payload = {"message": "Invalid module ID"}
            return jsonify(payload), result

        module = SoftwareModule.get_by_id(module_id)
        if not module:
            payload = {"message": "Software module not found"}
            return jsonify(payload), 404

        request_json = connexion.request.get_json() if connexion.request.is_json else (body or {})

        # Update fields if provided
        if "name" in request_json:
            module.name = request_json["name"]
        if "description" in request_json:
            module.description = request_json["description"]
        if "category_id" in request_json:
            category_id = int(request_json["category_id"])
            # Validate category exists
            category = SoftwareCategory.get_by_id(category_id)
            if not category:
                payload = {"message": "Invalid category_id"}
                return jsonify(payload), result
            module.category_id = category_id
        if "license_fee" in request_json:
            module.license_fee = float(request_json["license_fee"]) if request_json["license_fee"] is not None else None
        if "is_active" in request_json:
            module.is_active = request_json["is_active"]

        try:
            if module.update_row():
                payload = {
                    "message": "Software module updated successfully",
                    "data": module.to_dict()
                }
                result = 200
            else:
                payload = {"message": "Unable to update software module"}
                result = 400
        except IntegrityError as e:
            db.session.rollback()
            logging.error(f"[platform_software_modules_id_put] IntegrityError: {str(e)}")
            payload = {"message": "Unable to update software module: database constraint violation"}
            result = 400
        except Exception as db_error:
            db.session.rollback()
            logging.error(f"[platform_software_modules_id_put] Database error: {str(db_error)}")
            payload = {"message": "Unable to update software module due to database error"}
            result = 500

    except ValueError as ve:
        logging.error(f"[platform_software_modules_id_put] ValueError: {str(ve)}")
        payload = {"message": f"Invalid input: {str(ve)}"}
        result = 400
    except Exception as error:
        logging.error(f"[platform_software_modules_id_put] Error: {error}")
        print(error)
        result = 500
        payload = {"message": "An unexpected error occurred while updating the software module"}

    return jsonify(payload), result


def platform_software_modules_id_delete(id):  # noqa: E501
    """Delete a software module

     # noqa: E501

    :param id: 
    :type id: int

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 400
    payload = {"message": generic_message}

    try:
        logging.info(f"[platform_software_modules_id_delete] Deleting software module id={id}")
        
        try:
            module_id = int(id)
        except (TypeError, ValueError):
            payload = {"message": "Invalid module ID"}
            return jsonify(payload), result

        module = SoftwareModule.get_by_id(module_id)
        if not module:
            payload = {"message": "Software module not found"}
            return jsonify(payload), 404

        try:
            if module.delete_row():
                payload = {"message": "Software module deleted successfully"}
                result = 200
            else:
                payload = {"message": "Unable to delete software module"}
                result = 400
        except IntegrityError as e:
            db.session.rollback()
            logging.error(f"[platform_software_modules_id_delete] IntegrityError: {str(e)}")
            payload = {
                "message": "Cannot delete software module: it is referenced by other records",
                "code": "MODULE_IN_USE"
            }
            result = 409
        except Exception as db_error:
            db.session.rollback()
            logging.error(f"[platform_software_modules_id_delete] Database error: {str(db_error)}")
            payload = {"message": "Unable to delete software module due to database error"}
            result = 500

    except Exception as error:
        logging.error(f"[platform_software_modules_id_delete] Error: {error}")
        print(error)
        result = 500
        payload = {"message": "An unexpected error occurred while deleting the software module"}

    return jsonify(payload), result


def platform_software_modules_id_archive_put(id):  # noqa: E501
    """Archive a software module

     # noqa: E501

    :param id: 
    :type id: int

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 400
    payload = {"message": generic_message}

    try:
        logging.info(f"[platform_software_modules_id_archive_put] Archiving software module id={id}")
        
        try:
            module_id = int(id)
        except (TypeError, ValueError):
            payload = {"message": "Invalid module ID"}
            return jsonify(payload), result

        module = SoftwareModule.get_by_id(module_id)
        if not module:
            payload = {"message": "Software module not found"}
            return jsonify(payload), 404

        module.is_active = False
        if module.update_row():
            payload = {
                "message": "Software module archived successfully",
                "data": module.to_dict()
            }
            result = 200
        else:
            payload = {"message": "Unable to archive software module"}
            result = 400

    except Exception as error:
        logging.error(f"[platform_software_modules_id_archive_put] Error: {error}")
        print(error)
        result = 400
        payload = {"message": generic_message}

    return jsonify(payload), result


def platform_software_modules_id_unarchive_put(id):  # noqa: E501
    """Unarchive a software module

     # noqa: E501

    :param id: 
    :type id: int

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 400
    payload = {"message": generic_message}

    try:
        logging.info(f"[platform_software_modules_id_unarchive_put] Unarchiving software module id={id}")
        
        try:
            module_id = int(id)
        except (TypeError, ValueError):
            payload = {"message": "Invalid module ID"}
            return jsonify(payload), result

        module = SoftwareModule.get_by_id(module_id)
        if not module:
            payload = {"message": "Software module not found"}
            return jsonify(payload), 404

        module.is_active = True
        if module.update_row():
            payload = {
                "message": "Software module unarchived successfully",
                "data": module.to_dict()
            }
            result = 200
        else:
            payload = {"message": "Unable to unarchive software module"}
            result = 400

    except Exception as error:
        logging.error(f"[platform_software_modules_id_unarchive_put] Error: {error}")
        print(error)
        result = 400
        payload = {"message": generic_message}

    return jsonify(payload), result


def platform_hardware_items_post(body):  # noqa: E501
    """Create a new hardware item

     # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 400
    payload = {"message": generic_message}

    try:
        logging.info("[platform_hardware_items_post] Creating hardware item")
        request_json = connexion.request.get_json() if connexion.request.is_json else (body or {})

        name = request_json.get("name")
        category_id = request_json.get("category_id")
        unit_cost = request_json.get("unit_cost")
        description = request_json.get("description")
        subcategory = request_json.get("subcategory")
        manufacturer = request_json.get("manufacturer")
        configuration_notes = request_json.get("configuration_notes")
        support_type = request_json.get("support_type")
        support_cost = request_json.get("support_cost")
        is_active = request_json.get("is_active", True)

        if not name:
            payload = {"message": "name is required"}
            return jsonify(payload), result

        if not category_id:
            payload = {"message": "category_id is required"}
            return jsonify(payload), result

        if unit_cost is None:
            payload = {"message": "unit_cost is required"}
            return jsonify(payload), result

        # Validate category exists
        category = HardwareCategory.get_by_id(int(category_id))
        if not category:
            payload = {"message": "Invalid category_id"}
            return jsonify(payload), result

        hardware_item = HardwareItem(
            name=name,
            category_id=int(category_id),
            unit_cost=float(unit_cost),
            description=description,
            subcategory=subcategory,
            manufacturer=manufacturer,
            configuration_notes=configuration_notes,
            support_type=support_type,
            support_cost=float(support_cost) if support_cost is not None else None,
            is_active=is_active
        )

        item = hardware_item.create_row()

        if item:
            payload = {
                "message": "Hardware item created successfully",
                "data": item.to_dict()
            }
            result = 200
        else:
            payload = {"message": "Unable to create hardware item"}
            result = 400

    except Exception as error:
        logging.error(f"[platform_hardware_items_post] Error: {error}")
        print(error)
        result = 400
        payload = {"message": generic_message}

    return jsonify(payload), result


def platform_hardware_items_id_put(id, body):  # noqa: E501
    """Update an existing hardware item

     # noqa: E501

    :param id: 
    :type id: int
    :param body: 
    :type body: dict | bytes

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 400
    payload = {"message": generic_message}

    try:
        logging.info(f"[platform_hardware_items_id_put] Updating hardware item id={id}")
        
        try:
            item_id = int(id)
        except (TypeError, ValueError):
            payload = {"message": "Invalid item ID"}
            return jsonify(payload), result

        item = HardwareItem.get_by_id(item_id)
        if not item:
            payload = {"message": "Hardware item not found"}
            return jsonify(payload), 404

        request_json = connexion.request.get_json() if connexion.request.is_json else (body or {})

        # Update fields if provided
        if "name" in request_json:
            item.name = request_json["name"]
        if "description" in request_json:
            item.description = request_json["description"]
        if "category_id" in request_json:
            category_id = int(request_json["category_id"])
            # Validate category exists
            category = HardwareCategory.get_by_id(category_id)
            if not category:
                payload = {"message": "Invalid category_id"}
                return jsonify(payload), result
            item.category_id = category_id
        if "subcategory" in request_json:
            item.subcategory = request_json["subcategory"]
        if "manufacturer" in request_json:
            item.manufacturer = request_json["manufacturer"]
        if "configuration_notes" in request_json:
            item.configuration_notes = request_json["configuration_notes"]
        if "unit_cost" in request_json:
            unit_cost = float(request_json["unit_cost"])
            if unit_cost < 0:
                payload = {"message": "unit_cost must be a positive number"}
                return jsonify(payload), 400
            item.unit_cost = unit_cost
        if "support_type" in request_json:
            item.support_type = request_json["support_type"]
        if "support_cost" in request_json:
            item.support_cost = float(request_json["support_cost"]) if request_json["support_cost"] is not None else None
        if "is_active" in request_json:
            item.is_active = request_json["is_active"]

        try:
            if item.update_row():
                payload = {
                    "message": "Hardware item updated successfully",
                    "data": item.to_dict()
                }
                result = 200
            else:
                payload = {"message": "Unable to update hardware item"}
                result = 400
        except IntegrityError as e:
            db.session.rollback()
            logging.error(f"[platform_hardware_items_id_put] IntegrityError: {str(e)}")
            payload = {"message": "Unable to update hardware item: database constraint violation"}
            result = 400
        except Exception as db_error:
            db.session.rollback()
            logging.error(f"[platform_hardware_items_id_put] Database error: {str(db_error)}")
            payload = {"message": "Unable to update hardware item due to database error"}
            result = 500

    except ValueError as ve:
        logging.error(f"[platform_hardware_items_id_put] ValueError: {str(ve)}")
        payload = {"message": f"Invalid input: {str(ve)}"}
        result = 400
    except Exception as error:
        logging.error(f"[platform_hardware_items_id_put] Error: {error}")
        print(error)
        result = 500
        payload = {"message": "An unexpected error occurred while updating the hardware item"}

    return jsonify(payload), result


def platform_hardware_items_id_delete(id):  # noqa: E501
    """Delete a hardware item

     # noqa: E501

    :param id: 
    :type id: int

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 400
    payload = {"message": generic_message}

    try:
        logging.info(f"[platform_hardware_items_id_delete] Deleting hardware item id={id}")
        
        try:
            item_id = int(id)
        except (TypeError, ValueError):
            payload = {"message": "Invalid item ID"}
            return jsonify(payload), result

        item = HardwareItem.get_by_id(item_id)
        if not item:
            payload = {"message": "Hardware item not found"}
            return jsonify(payload), 404

        try:
            if item.delete_row():
                payload = {"message": "Hardware item deleted successfully"}
                result = 200
            else:
                payload = {"message": "Unable to delete hardware item"}
                result = 400
        except IntegrityError as e:
            db.session.rollback()
            logging.error(f"[platform_hardware_items_id_delete] IntegrityError: {str(e)}")
            payload = {
                "message": "Cannot delete hardware item: it is referenced by other records",
                "code": "ITEM_IN_USE"
            }
            result = 409
        except Exception as db_error:
            db.session.rollback()
            logging.error(f"[platform_hardware_items_id_delete] Database error: {str(db_error)}")
            payload = {"message": "Unable to delete hardware item due to database error"}
            result = 500

    except Exception as error:
        logging.error(f"[platform_hardware_items_id_delete] Error: {error}")
        print(error)
        result = 500
        payload = {"message": "An unexpected error occurred while deleting the hardware item"}

    return jsonify(payload), result


def platform_hardware_items_id_archive_put(id):  # noqa: E501
    """Archive a hardware item

     # noqa: E501

    :param id: 
    :type id: int

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 400
    payload = {"message": generic_message}

    try:
        logging.info(f"[platform_hardware_items_id_archive_put] Archiving hardware item id={id}")
        
        try:
            item_id = int(id)
        except (TypeError, ValueError):
            payload = {"message": "Invalid item ID"}
            return jsonify(payload), result

        item = HardwareItem.get_by_id(item_id)
        if not item:
            payload = {"message": "Hardware item not found"}
            return jsonify(payload), 404

        item.is_active = False
        if item.update_row():
            payload = {
                "message": "Hardware item archived successfully",
                "data": item.to_dict()
            }
            result = 200
        else:
            payload = {"message": "Unable to archive hardware item"}
            result = 400

    except Exception as error:
        logging.error(f"[platform_hardware_items_id_archive_put] Error: {error}")
        print(error)
        result = 400
        payload = {"message": generic_message}

    return jsonify(payload), result


def platform_hardware_items_id_unarchive_put(id):  # noqa: E501
    """Unarchive a hardware item

     # noqa: E501

    :param id: 
    :type id: int

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 400
    payload = {"message": generic_message}

    try:
        logging.info(f"[platform_hardware_items_id_unarchive_put] Unarchiving hardware item id={id}")
        
        try:
            item_id = int(id)
        except (TypeError, ValueError):
            payload = {"message": "Invalid item ID"}
            return jsonify(payload), result

        item = HardwareItem.get_by_id(item_id)
        if not item:
            payload = {"message": "Hardware item not found"}
            return jsonify(payload), 404

        item.is_active = True
        if item.update_row():
            payload = {
                "message": "Hardware item unarchived successfully",
                "data": item.to_dict()
            }
            result = 200
        else:
            payload = {"message": "Unable to unarchive hardware item"}
            result = 400

    except Exception as error:
        logging.error(f"[platform_hardware_items_id_unarchive_put] Error: {error}")
        print(error)
        result = 400
        payload = {"message": generic_message}

    return jsonify(payload), result


def platform_software_categories_post(body):  # noqa: E501
    """Create a new software category

     # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 400
    payload = {"message": generic_message}

    try:
        logging.info("[platform_software_categories_post] Creating software category")
        request_json = connexion.request.get_json() if connexion.request.is_json else (body or {})

        name = request_json.get("name")
        description = request_json.get("description")
        is_active = request_json.get("is_active", True)

        if not name:
            payload = {"message": "name is required"}
            return jsonify(payload), result

        # Check if category with same name already exists
        existing_categories = SoftwareCategory.get_all(active_only=False) or []
        if any(cat.name.lower() == name.lower() for cat in existing_categories):
            payload = {"message": "Category with this name already exists"}
            return jsonify(payload), 400

        category = SoftwareCategory(
            name=name,
            description=description,
            is_active=is_active
        )

        created_category = category.create_row()

        if created_category:
            payload = {
                "message": "Software category created successfully",
                "data": created_category.to_dict()
            }
            result = 200
        else:
            payload = {"message": "Unable to create software category"}
            result = 400

    except Exception as error:
        logging.error(f"[platform_software_categories_post] Error: {error}")
        print(error)
        result = 400
        payload = {"message": generic_message}

    return jsonify(payload), result


def platform_software_categories_id_put(id, body):  # noqa: E501
    """Update an existing software category

     # noqa: E501

    :param id: 
    :type id: int
    :param body: 
    :type body: dict | bytes

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 400
    payload = {"message": generic_message}

    try:
        logging.info(f"[platform_software_categories_id_put] Updating software category id={id}")
        
        try:
            category_id = int(id)
        except (TypeError, ValueError):
            payload = {"message": "Invalid category ID"}
            return jsonify(payload), result

        category = SoftwareCategory.get_by_id(category_id)
        if not category:
            payload = {"message": "Software category not found"}
            return jsonify(payload), 404

        request_json = connexion.request.get_json() if connexion.request.is_json else (body or {})

        # Update fields if provided
        if "name" in request_json:
            # Check if another category with same name exists
            existing_categories = SoftwareCategory.get_all(active_only=False) or []
            if any(cat.id != category_id and cat.name.lower() == request_json["name"].lower() for cat in existing_categories):
                payload = {"message": "Category with this name already exists"}
                return jsonify(payload), 400
            category.name = request_json["name"]
        if "description" in request_json:
            category.description = request_json["description"]
        if "is_active" in request_json:
            category.is_active = request_json["is_active"]

        try:
            if category.update_row():
                payload = {
                    "message": "Software category updated successfully",
                    "data": category.to_dict()
                }
                result = 200
            else:
                payload = {"message": "Unable to update software category"}
                result = 400
        except IntegrityError as e:
            db.session.rollback()
            logging.error(f"[platform_software_categories_id_put] IntegrityError: {str(e)}")
            payload = {"message": "Unable to update software category: database constraint violation"}
            result = 400
        except Exception as db_error:
            db.session.rollback()
            logging.error(f"[platform_software_categories_id_put] Database error: {str(db_error)}")
            payload = {"message": "Unable to update software category due to database error"}
            result = 500

    except ValueError as ve:
        logging.error(f"[platform_software_categories_id_put] ValueError: {str(ve)}")
        payload = {"message": f"Invalid input: {str(ve)}"}
        result = 400
    except Exception as error:
        logging.error(f"[platform_software_categories_id_put] Error: {error}")
        print(error)
        result = 500
        payload = {"message": "An unexpected error occurred while updating the software category"}

    return jsonify(payload), result


def platform_software_categories_id_delete(id):  # noqa: E501
    """Delete a software category

     # noqa: E501

    :param id: 
    :type id: int

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 400
    payload = {"message": generic_message}

    try:
        logging.info(f"[platform_software_categories_id_delete] Deleting software category id={id}")
        
        try:
            category_id = int(id)
        except (TypeError, ValueError):
            payload = {"message": "Invalid category ID"}
            return jsonify(payload), result

        category = SoftwareCategory.get_by_id(category_id)
        if not category:
            payload = {"message": "Software category not found"}
            return jsonify(payload), 404

        # Check if category has associated modules
        module_count = len(category.modules) if category.modules else 0
        if module_count > 0:
            payload = {
                "message": f"Cannot delete category: it is in use by {module_count} software module{'s' if module_count > 1 else ''}",
                "code": "CATEGORY_IN_USE"
            }
            return jsonify(payload), 409

        try:
            if category.delete_row():
                payload = {"message": "Software category deleted successfully"}
                result = 200
            else:
                payload = {"message": "Unable to delete software category"}
                result = 400
        except IntegrityError as e:
            db.session.rollback()
            logging.error(f"[platform_software_categories_id_delete] IntegrityError: {str(e)}")
            payload = {
                "message": "Cannot delete category: it is referenced by other records",
                "code": "CATEGORY_IN_USE"
            }
            result = 409
        except Exception as db_error:
            db.session.rollback()
            logging.error(f"[platform_software_categories_id_delete] Database error: {str(db_error)}")
            payload = {"message": "Unable to delete software category due to database error"}
            result = 500

    except Exception as error:
        logging.error(f"[platform_software_categories_id_delete] Error: {error}")
        print(error)
        result = 500
        payload = {"message": "An unexpected error occurred while deleting the software category"}

    return jsonify(payload), result


def platform_hardware_categories_post(body):  # noqa: E501
    """Create a new hardware category

     # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 400
    payload = {"message": generic_message}

    try:
        logging.info("[platform_hardware_categories_post] Creating hardware category")
        request_json = connexion.request.get_json() if connexion.request.is_json else (body or {})

        name = request_json.get("name")
        description = request_json.get("description")
        is_active = request_json.get("is_active", True)

        if not name:
            payload = {"message": "name is required"}
            return jsonify(payload), result

        # Check if category with same name already exists
        existing_categories = HardwareCategory.get_all(active_only=False) or []
        if any(cat.name.lower() == name.lower() for cat in existing_categories):
            payload = {"message": "Category with this name already exists"}
            return jsonify(payload), 400

        category = HardwareCategory(
            name=name,
            description=description,
            is_active=is_active
        )

        created_category = category.create_row()

        if created_category:
            payload = {
                "message": "Hardware category created successfully",
                "data": created_category.to_dict()
            }
            result = 200
        else:
            payload = {"message": "Unable to create hardware category"}
            result = 400

    except Exception as error:
        logging.error(f"[platform_hardware_categories_post] Error: {error}")
        print(error)
        result = 400
        payload = {"message": generic_message}

    return jsonify(payload), result


def platform_hardware_categories_id_put(id, body):  # noqa: E501
    """Update an existing hardware category

     # noqa: E501

    :param id: 
    :type id: int
    :param body: 
    :type body: dict | bytes

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 400
    payload = {"message": generic_message}

    try:
        logging.info(f"[platform_hardware_categories_id_put] Updating hardware category id={id}")
        
        try:
            category_id = int(id)
        except (TypeError, ValueError):
            payload = {"message": "Invalid category ID"}
            return jsonify(payload), result

        category = HardwareCategory.get_by_id(category_id)
        if not category:
            payload = {"message": "Hardware category not found"}
            return jsonify(payload), 404

        request_json = connexion.request.get_json() if connexion.request.is_json else (body or {})

        # Update fields if provided
        if "name" in request_json:
            # Check if another category with same name exists
            existing_categories = HardwareCategory.get_all(active_only=False) or []
            if any(cat.id != category_id and cat.name.lower() == request_json["name"].lower() for cat in existing_categories):
                payload = {"message": "Category with this name already exists"}
                return jsonify(payload), 400
            category.name = request_json["name"]
        if "description" in request_json:
            category.description = request_json["description"]
        if "is_active" in request_json:
            category.is_active = request_json["is_active"]

        try:
            if category.update_row():
                payload = {
                    "message": "Hardware category updated successfully",
                    "data": category.to_dict()
                }
                result = 200
            else:
                payload = {"message": "Unable to update hardware category"}
                result = 400
        except IntegrityError as e:
            db.session.rollback()
            logging.error(f"[platform_hardware_categories_id_put] IntegrityError: {str(e)}")
            payload = {"message": "Unable to update hardware category: database constraint violation"}
            result = 400
        except Exception as db_error:
            db.session.rollback()
            logging.error(f"[platform_hardware_categories_id_put] Database error: {str(db_error)}")
            payload = {"message": "Unable to update hardware category due to database error"}
            result = 500

    except ValueError as ve:
        logging.error(f"[platform_hardware_categories_id_put] ValueError: {str(ve)}")
        payload = {"message": f"Invalid input: {str(ve)}"}
        result = 400
    except Exception as error:
        logging.error(f"[platform_hardware_categories_id_put] Error: {error}")
        print(error)
        result = 500
        payload = {"message": "An unexpected error occurred while updating the hardware category"}

    return jsonify(payload), result


def platform_hardware_categories_id_delete(id):  # noqa: E501
    """Delete a hardware category

     # noqa: E501

    :param id: 
    :type id: int

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 400
    payload = {"message": generic_message}

    try:
        logging.info(f"[platform_hardware_categories_id_delete] Deleting hardware category id={id}")
        
        try:
            category_id = int(id)
        except (TypeError, ValueError):
            payload = {"message": "Invalid category ID"}
            return jsonify(payload), result

        category = HardwareCategory.get_by_id(category_id)
        if not category:
            payload = {"message": "Hardware category not found"}
            return jsonify(payload), 404

        # Check if category has associated items
        item_count = len(category.items) if category.items else 0
        if item_count > 0:
            payload = {
                "message": f"Cannot delete category: it is in use by {item_count} hardware item{'s' if item_count > 1 else ''}",
                "code": "CATEGORY_IN_USE"
            }
            return jsonify(payload), 409

        try:
            if category.delete_row():
                payload = {"message": "Hardware category deleted successfully"}
                result = 200
            else:
                payload = {"message": "Unable to delete hardware category"}
                result = 400
        except IntegrityError as e:
            db.session.rollback()
            logging.error(f"[platform_hardware_categories_id_delete] IntegrityError: {str(e)}")
            payload = {
                "message": "Cannot delete category: it is referenced by other records",
                "code": "CATEGORY_IN_USE"
            }
            result = 409
        except Exception as db_error:
            db.session.rollback()
            logging.error(f"[platform_hardware_categories_id_delete] Database error: {str(db_error)}")
            payload = {"message": "Unable to delete hardware category due to database error"}
            result = 500

    except Exception as error:
        logging.error(f"[platform_hardware_categories_id_delete] Error: {error}")
        print(error)
        result = 500
        payload = {"message": "An unexpected error occurred while deleting the hardware category"}

    return jsonify(payload), result

