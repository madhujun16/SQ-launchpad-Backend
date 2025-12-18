import json

def transform_field(field):
    _field = {}
    _field['field_id'] = getattr(field, 'id', None)
    _field['field_name'] = getattr(field, 'field_name', None)

    field_value = getattr(field, 'field_value', None)
    if isinstance(field_value, str):
        try:
            _field['field_value'] = json.loads(field_value or "{}")
        except json.JSONDecodeError:
            _field['field_value'] = {}
    else:
        _field['field_value'] = field_value

    _field['section_id'] = getattr(field, 'section_id', None)
    _field['created_at'] = getattr(field, 'created_at', None)
    _field['updated_at'] = getattr(field, 'updated_at', None)

    return _field


def transform_page(page):
    _page = {}
    _page['page_id'] = getattr(page, 'id', None)
    _page['page_name'] = getattr(page, 'page_name', None)
    _page['site_id'] = getattr(page, 'site_id', None)
    _page['created_at'] = getattr(page, 'created_at', None)
    _page['updated_at'] = getattr(page, 'updated_at', None)

    return _page


def transform_section(section):
    _section = {}
    _section['section_id'] = getattr(section, 'id', None)
    _section['section_name'] = getattr(section, 'section_name', None)
    _section['page_id'] = getattr(section, 'page_id', None)
    _section['created_at'] = getattr(section, 'created_at', None)
    _section['updated_at'] = getattr(section, 'updated_at', None)

    return _section


def transform_site(site):
    _site = {}
    _site['site_id'] = getattr(site, 'id', None)
    _site['status'] = getattr(site, 'status', None)
    _site['created_at'] = getattr(site, 'created_at', None)
    _site['updated_at'] = getattr(site, 'updated_at', None)

    return _site


def transform_org(org):
    _org = {}
    _org['org_id'] = getattr(org, 'id', None)
    _org['name'] = getattr(org, 'name', None)
    _org['description'] = getattr(org, 'description', None)
    _org['sector'] = getattr(org, 'sector', None)
    _org['unit_code'] = getattr(org, 'unit_code', None)
    _org['organization_logo'] = getattr(org, 'organization_logo', None)
    _org['created_at'] = getattr(org, 'created_at', None)
    _org['updated_at'] = getattr(org, 'updated_at', None)

    return _org


def transform_user(user):
    _user = {}
    _user['user_id'] = getattr(user, 'id', None)
    _user['name'] = getattr(user, 'name', None)
    _user['email'] = getattr(user, 'email', None)
    # Include role information so frontend user management can display it
    _user['role'] = getattr(user, 'role', None)
    _user['role_id'] = getattr(user, 'role', None)
    _user['last_logged_in'] = getattr(user, 'last_logged_in', None)
    _user['created_at'] = getattr(user, 'created_at', None)
    _user['updated_at'] = getattr(user, 'updated_at', None)

    return _user


# ---------- Bulk Transformers ----------

def transform_fields(fields):
    return [transform_field(f) for f in fields or []]

def transform_pages(pages):
    return [transform_page(p) for p in pages or []]

def transform_sections(sections):
    return [transform_section(s) for s in sections or []]

def transform_sites(sites):
    return [transform_site(s) for s in sites or []]

def transform_orgs(orgs):
    return [transform_org(o) for o in orgs or []]

def transform_users(users):
    return [transform_user(u) for u in users or []]