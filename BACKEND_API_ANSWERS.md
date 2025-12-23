# Backend API Implementation - Detailed Answers

## 1. GET /api/site/all Endpoint Behavior

### Q1: Does GET /api/site/all automatically read from create_site/general_info and normalize fields?

**Answer:** **PARTIALLY YES, but with a discrepancy**

**Current Implementation:**
- The endpoint DOES automatically read from page fields and normalizes them
- **However**, the current query in `get_all_site_details()` is hardcoded to look for:
  - Page name: `'site_study'` (NOT `'create_site'`)
  - Section name: `'general_info'`
  
**Location:** `app/launchpad/launchpad_api/utils/queries.py` lines 30, 54

**What fields are normalized:**
The normalization happens in `site_controller.py` (lines 272-302):

1. **site_name → name**: If `site_name` field exists, it's extracted and mapped to `name`
2. **org_name → organization_name**: Both `org_name` and `organization_name` are accepted, normalized to `organization_name`
3. **unit_id → unit_code**: Both `unit_id` and `unit_code` are accepted, normalized to `unit_code`
4. **Other fields** that are normalized (if present):
   - `target_live_date`
   - `suggested_go_live`
   - `assigned_ops_manager`
   - `assigned_deployment_engineer`
   - `sector`
   - `organization_logo`
   - `organization_id`

**Field Value Extraction:**
- Field values are extracted using `_extract_display_value()` which handles:
  - Objects like `{value: "..."}` → extracts the `value` property
  - Objects like `{text: "..."}` → extracts the `text` property
  - Objects like `{label: "..."}` → extracts the `label` property
  - Plain strings → returned as-is

**⚠️ ACTION REQUIRED:** The query needs to be updated to look for `'create_site'` instead of `'site_study'` if that's the intended page name.

---

### Q2: What is the exact response structure of GET /api/site/all?

**Answer:**

**Response Structure:**
```json
{
  "message": "Succesfully fetched sites",
  "data": [
    {
      "site_id": 1,
      "status": "Created",
      "name": "Site Name Value",
      "organization_name": "Org Name Value",
      "unit_code": "UNIT123",
      "target_live_date": "2024-12-31",
      "suggested_go_live": "2024-11-15",
      "assigned_ops_manager": "Manager Name",
      "assigned_deployment_engineer": "Engineer Name",
      "sector": "Healthcare",
      "organization_logo": "url/to/logo",
      "organization_id": 123,
      // ... any other fields from create_site/general_info
    }
  ]
}
```

**Key Points:**
- Fields are normalized to top-level properties (NOT nested like `{org_name: {value: "..."}}`)
- Field values are extracted from objects (e.g., `{value: "..."}` → `"..."`)
- Only fields that exist in the page are included
- Missing fields are simply not present in the response (not null/empty)

**Location:** `app/launchpad/launchpad_api/controllers/site_controller.py` lines 195-313

---

### Q3: If a site doesn't have a create_site page yet, what does GET /api/site/all return?

**Answer:**

**Returns:**
```json
{
  "message": "Succesfully fetched sites",
  "data": [
    {
      "site_id": 1,
      "status": "Created"
      // No other fields - only site_id and status
    }
  ]
}
```

**Explanation:**
- The query uses `outerjoin`, so sites without pages/sections/fields are still returned
- Only `site_id` and normalized `status` are guaranteed
- No empty/null fields are added - missing fields simply don't appear in the response

**Location:** `app/launchpad/launchpad_api/utils/queries.py` - uses `outerjoin` which allows sites without pages

---

## 2. Page and Field Structure

### Q4: What is the exact format for field_value in page fields?

**Answer:**

**Field values can be in multiple formats:**

1. **JSON Object** (most common):
   ```json
   {"value": "some text"}
   {"text": "some text"}
   {"label": "some text"}
   ```

2. **Plain String**:
   ```json
   "some text"
   ```

3. **Other Object Shapes** (supported):
   - Any object with `value`, `text`, or `label` keys will be extracted
   - Other object shapes are preserved as-is if they don't match these patterns

**Storage:**
- Field values are stored as JSON in the database (`field_value` column is `db.JSON`)
- When creating fields via POST /api/page, values are JSON stringified: `json.dumps(field_value)`
- When reading fields via GET /api/page, values are parsed back from JSON

**Extraction Logic:**
- `_extract_display_value()` in `site_controller.py` (lines 206-219) handles the extraction
- In `transform_data.py`, field values are parsed from JSON strings if needed

**Location:**
- Storage: `app/launchpad/launchpad_api/db_models/fields.py` line 12
- Creation: `app/launchpad/launchpad_api/controllers/page_controller.py` line 243
- Transformation: `app/launchpad/launchpad_api/utils/transform_data.py` lines 3-21

---

### Q5: Are page names, section names, and field names case-sensitive?

**Answer:**

**YES - They are case-sensitive**

**Evidence:**
- Database queries use exact string matching: `Page.page_name == 'site_study'`
- No `.lower()` or case normalization is applied
- `'create_site'` ≠ `'Create_Site'` ≠ `'CREATE_SITE'`
- `'general_info'` ≠ `'General_Info'` ≠ `'GENERAL_INFO'`

**Recommendation:**
- Use consistent lowercase with underscores (snake_case) throughout
- Standardize on: `create_site`, `general_info`, `site_name`, etc.

**Location:** 
- Page lookup: `app/launchpad/launchpad_api/db_models/page.py` line 79
- Section lookup: `app/launchpad/launchpad_api/db_models/section.py` line 83
- Field lookup: Uses exact matching in queries

---

### Q6: Are there any reserved or required page/section/field names we should avoid?

**Answer:**

**No explicit reserved names found in the codebase**

**However, based on the implementation:**

1. **Unique Constraints:**
   - `(page_name, site_id)` must be unique (Page model)
   - `(section_name, page_id)` must be unique (Section model)
   - `(field_name, section_id)` must be unique (Field model)

2. **Current Usage:**
   - Page: `'site_study'` (used in queries - should probably be `'create_site'`)
   - Section: `'general_info'` (used in queries)

3. **Recommendation:**
   - Avoid names that conflict with database column names: `id`, `created_at`, `updated_at`, `site_id`, `page_id`, `section_id`
   - Use descriptive, lowercase, snake_case names

**Location:**
- Unique constraints: 
  - `app/launchpad/launchpad_api/db_models/page.py` lines 15-17
  - `app/launchpad/launchpad_api/db_models/section.py` lines 15-17
  - `app/launchpad/launchpad_api/db_models/fields.py` lines 17-19

---

## 3. Page Creation and Updates

### Q7: When we create a page with POST /api/page, what happens if:

**Answer:**

**a) The page already exists for that site?**
- **Result:** The page creation will **FAIL** due to unique constraint violation
- **Error:** Database `IntegrityError` will be raised
- **Response:** Transaction will rollback, returns 400 error
- **Constraint:** `UniqueConstraint('page_name', 'site_id')` in Page model

**b) A section already exists in that page?**
- **Result:** The section creation will **FAIL** due to unique constraint violation
- **Error:** Database `IntegrityError` will be raised
- **Response:** Transaction will rollback, returns 400 error
- **Constraint:** `UniqueConstraint('section_name', 'page_id')` in Section model

**c) A field already exists in that section?**
- **Result:** The field creation will **FAIL** and return `None` (not `False`)
- **Error:** `IntegrityError` is caught and returns `None`
- **Response:** Returns 400 with message: `"Duplicate field in section '{section_name}'. Each field_name must be unique per section."`
- **Constraint:** `UniqueConstraint('field_name', 'section_id')` in Field model

**Location:**
- Page creation: `app/launchpad/launchpad_api/controllers/page_controller.py` lines 175-274
- Field duplicate handling: `app/launchpad/launchpad_api/controllers/page_controller.py` lines 247-257
- Field model: `app/launchpad/launchpad_api/db_models/fields.py` lines 67-71

---

### Q8: Should we use PUT /api/page to update existing pages, or does POST /api/page handle both create and update?

**Answer:**

**POST /api/page is CREATE ONLY**
- Does NOT handle updates
- Will fail if page/section/field already exists (see Q7)
- Creates new page, sections, and fields from scratch

**PUT /api/page is UPDATE ONLY**
- Requires `page_id` in the request body
- Updates existing page, sections, and fields
- Requires `field_id` for each field being updated
- Also updates site status if provided

**Workflow:**
1. **First time:** Use POST /api/page to create
2. **Subsequent updates:** Use PUT /api/page with page_id and field_ids

**Location:**
- POST: `app/launchpad/launchpad_api/controllers/page_controller.py` lines 175-274
- PUT: `app/launchpad/launchpad_api/controllers/page_controller.py` lines 276-373

---

### Q9: When updating a field value, do we need to include field_id in the update payload, or can we update by field_name?

**Answer:**

**YES - field_id is REQUIRED for updates**

**Current Implementation:**
- PUT /api/page requires `field_id` for each field
- Updates are done by: `Field.get_by_id(field_id)`
- **Cannot** update by field_name alone

**Request Structure for PUT /api/page:**
```json
{
  "id": 123,  // page_id (required)
  "site_id": 1,
  "status": "site_study_done",
  "sections": [
    {
      "section_id": 456,  // required
      "fields": [
        {
          "field_id": 789,  // REQUIRED - cannot use field_name
          "field_value": {"value": "new value"}
        }
      ]
    }
  ]
}
```

**Location:** `app/launchpad/launchpad_api/controllers/page_controller.py` lines 351-361

**Note:** If you need to update by field_name, you would need to:
1. First GET /api/page to retrieve field_ids
2. Then PUT /api/page with the field_ids

---

## 4. Data Flow and Workflow

### Q10: For the sites list page, what's the recommended approach?

**Answer:**

**Option A is already implemented (with minor fix needed)**

**Current Implementation:**
- GET /api/site/all already normalizes `create_site/general_info` fields into top-level properties
- No need for frontend to fetch pages separately
- **However**, the query currently looks for `'site_study'` page instead of `'create_site'`

**Recommended Approach:**
1. **Fix the query** to look for `'create_site'` page instead of `'site_study'`
2. **Use GET /api/site/all** for the sites list - it already does the normalization
3. **Use GET /api/page** only when you need the full page structure with all sections/fields

**Performance:**
- Single query with joins is more efficient than multiple API calls
- Normalization happens server-side, reducing frontend complexity

**Location:** 
- Query: `app/launchpad/launchpad_api/utils/queries.py` lines 30, 54
- Normalization: `app/launchpad/launchpad_api/controllers/site_controller.py` lines 272-302

---

### Q11: Should we create all 7 workflow pages upfront, or create them lazily as the user progresses?

**Answer:**

**Recommendation: Create pages lazily (on-demand)**

**Reasons:**
1. **Database efficiency:** Only create pages when needed
2. **Flexibility:** User might skip stages or change workflow
3. **Current implementation supports both:**
   - POST /api/page can create pages on-demand
   - No requirement to create all pages upfront

**Performance Impact:**
- **Creating all upfront:**
  - Pros: Predictable structure, can pre-populate defaults
  - Cons: More database records, potential for unused pages
- **Creating lazily:**
  - Pros: Lean database, only what's needed
  - Cons: Need to handle missing pages in frontend

**Current Behavior:**
- GET /api/site/all handles missing pages gracefully (returns only site_id and status)
- GET /api/page returns 400 if page doesn't exist (see Q13)

**Recommendation:**
- Create `create_site` page when site is first created
- Create subsequent workflow pages when user reaches that stage
- Update site status when creating new workflow pages

**Location:** `app/launchpad/launchpad_api/controllers/page_controller.py` lines 175-274

---

### Q12: When a site status changes (e.g., Created → site_study_done), should we:

**Answer:**

**Current Implementation:**
- PUT /api/page **automatically updates site status** if provided in the request
- You can update status when creating/updating pages

**Code Evidence:**
```python
# In page_put() function:
site.status = status
site.updated_at = datetime.utcnow()
site_updated = site.update_row(False)
```

**Recommended Approach:**
1. **When creating a new workflow page:** Include the new status in POST /api/page
2. **When updating a page:** Include status update in PUT /api/page
3. **Or separately:** Use PUT /api/site to update status independently

**Location:** `app/launchpad/launchpad_api/controllers/page_controller.py` lines 301-316

---

## 5. Error Handling and Edge Cases

### Q13: What happens if we try to GET /api/page?page_name=create_site&site_id=X but the page doesn't exist?

**Answer:**

**Returns 404 with descriptive error message**

**Response:**
```json
{
  "message": "Page 'create_site' not found for site X"
}
```

**HTTP Status:** 404 (Not Found)

**Code Flow:**
1. Validates `site_id` (returns 400 if missing or invalid)
2. Verifies site exists (returns 404 if site not found)
3. `Page.get_by_siteid_and_pagename(site_id, page_name)` returns `None`
4. Returns 404 with descriptive message indicating which page is missing

**Error Handling:**
- **Missing/invalid site_id:** Returns 400 "Site ID is required" or "Invalid Site ID"
- **Site doesn't exist:** Returns 404 "Site not found"
- **Page doesn't exist:** Returns 404 "Page 'create_site' not found for site X"

**Location:** `app/launchpad/launchpad_api/controllers/page_controller.py` lines 82-117

**✅ UPDATED:** Changed from 400 to 404 for proper HTTP semantics and added site validation

---

### Q14: If a field value is missing or null in create_site/general_info, should we:

**Answer:**

**Current Behavior:**
- Missing fields are **not included** in the response (not null, not empty string)
- If a field exists but has `null` value, it will be included as `null`
- If a field doesn't exist, it simply won't appear in the response

**Example:**
```json
{
  "site_id": 1,
  "status": "Created",
  "name": "Site Name",
  // organization_name is missing - not in response at all
}
```

**Recommendation for Frontend:**
- Check if field exists: `if ('organization_name' in site)`
- If missing, show "N/A" or empty state in UI
- Don't assume fields will always be present

**Location:** `app/launchpad/launchpad_api/controllers/site_controller.py` lines 272-302

---

### Q15: Are there any rate limits or performance considerations?

**Answer:**

**No explicit rate limits found in the codebase**

**Performance Considerations:**

1. **Creating multiple pages in sequence:**
   - Each POST /api/page is a separate transaction
   - Consider batching if creating many pages
   - Current implementation commits after each page creation

2. **Fetching pages for multiple sites:**
   - GET /api/site/all uses a single query with joins (efficient)
   - GET /api/page fetches one page at a time (consider caching)
   - No batch endpoint exists currently

3. **Updating fields frequently:**
   - Each PUT /api/page updates all fields in a single transaction
   - Consider debouncing rapid updates on frontend
   - Database has indexes on foreign keys (should be performant)

**Recommendations:**
- Use GET /api/site/all for list views (single query)
- Cache page data on frontend when possible
- Batch field updates when possible (PUT /api/page handles this)

**Location:**
- Query implementation: `app/launchpad/launchpad_api/utils/queries.py`
- Page updates: `app/launchpad/launchpad_api/controllers/page_controller.py` lines 276-373

---

## 6. Field Name Mapping

### Q16: For create_site/general_info, are these the exact field names you expect?

**Answer:**

**Based on the normalization code, these field names are supported:**

**Primary field names (what to use):**
- `site_name` → normalized to `name` in response
- `org_name` OR `organization_name` → normalized to `organization_name` in response
- `unit_id` OR `unit_code` → normalized to `unit_code` in response
- `target_live_date` ✓
- `suggested_go_live` ✓
- `assigned_ops_manager` ✓
- `assigned_deployment_engineer` ✓
- `sector` ✓
- `organization_logo` ✓

**Note:** The code accepts both `org_name`/`organization_name` and `unit_id`/`unit_code`, but normalizes them to the canonical names.

**Location:** `app/launchpad/launchpad_api/controllers/site_controller.py` lines 275-300

---

### Q17: For create_site/location_info, what field names should we use?

**Answer:**

**No specific field names are enforced or normalized for location_info**

**Recommendation:**
Use descriptive, lowercase, snake_case names:
- `location` ✓
- `postcode` ✓
- `region` ✓
- `country` ✓
- `latitude` ✓
- `longitude` ✓

**Note:** These fields will be stored as-is and returned as-is (no normalization applied unless they're added to the normalization logic).

**Location:** Field names are stored directly in the database without transformation (except for the specific fields normalized in site_controller.py)

---

## 7. Data Consistency

### Q18: If we update a field in create_site/general_info, does it automatically update the site's normalized fields in GET /api/site/all?

**Answer:**

**YES - Updates are immediate (no cache)**

**How it works:**
1. PUT /api/page updates the field in the database
2. GET /api/site/all queries the database directly (no caching)
3. Changes are reflected immediately in the next GET request

**No delay/cache:** The query runs fresh each time, so updates are immediately visible.

**Location:**
- Update: `app/launchpad/launchpad_api/controllers/page_controller.py` lines 360-361
- Query: `app/launchpad/launchpad_api/utils/queries.py` - direct database query

---

### Q19: Should we update the site's status field when creating/updating workflow pages, or is that handled separately?

**Answer:**

**You can do either - both are supported**

**Option 1: Update status when creating/updating pages**
- POST /api/page accepts `status` parameter (creates site with status if site_id is missing)
- PUT /api/page accepts `status` parameter and updates site status automatically

**Option 2: Update status separately**
- Use PUT /api/site to update status independently

**Current Implementation:**
- PUT /api/page **automatically updates site status** if provided
- POST /api/page can create a site with status if site_id is missing

**Recommendation:**
- Include status in page creation/update requests to keep them in sync
- Or update status separately if you prefer to decouple page data from status

**Location:**
- POST: `app/launchpad/launchpad_api/controllers/page_controller.py` lines 194, 197
- PUT: `app/launchpad/launchpad_api/controllers/page_controller.py` lines 309-316

---

## Summary of Critical Issues

### ✅ FIXED:

1. **Page Name Mismatch:** 
   - ✅ Fixed: Query now looks for `'create_site'` instead of `'site_study'`
   - File: `app/launchpad/launchpad_api/utils/queries.py` lines 30, 54
   - Changed: `(p.page_name == 'site_study')` → `(p.page_name == 'create_site')`

2. **Missing Page Error Handling:**
   - ✅ Fixed: GET /api/page now returns 404 (Not Found) instead of 400 (Bad Request) for missing pages
   - ✅ Added: Site validation before checking for page
   - ✅ Improved: More descriptive error messages
   - File: `app/launchpad/launchpad_api/controllers/page_controller.py` lines 82-117

### ✅ Already Working:

- GET /api/site/all normalizes fields automatically
- Field value extraction handles multiple formats
- Missing pages/fields handled gracefully
- Status updates work with page operations

### 📝 Recommendations:

- Use consistent lowercase snake_case for all names
- Create pages lazily (on-demand)
- Use GET /api/site/all for list views
- Include field_id when updating fields
- Handle missing fields in frontend (show "N/A" or empty state)

