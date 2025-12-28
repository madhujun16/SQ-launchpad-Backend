# Scoping Approval API Implementation

## ✅ Implementation Complete

All backend API endpoints for the scoping approval workflow have been implemented.

## 📁 Files Created/Modified

### New Files
1. **`app/launchpad/launchpad_api/db_models/scoping_approval.py`**
   - Database model for `scoping_approvals` table
   - Includes CRUD operations and query methods
   - Handles JSON data for scoping_data and cost_breakdown

2. **`app/launchpad/launchpad_api/db_models/approval_action.py`**
   - Database model for `approval_actions` table (audit trail)
   - Tracks all actions performed on approvals

3. **`app/launchpad/launchpad_api/controllers/scoping_approval_controller.py`**
   - All controller functions for scoping approval endpoints
   - Includes authentication and role checking logic

### Modified Files
1. **`app/launchpad/launchpad_api/openapi/openapi.yaml`**
   - Added all scoping approval endpoints
   - Added request/response schemas

2. **`app/launchpad/launchpad_api/main.py`**
   - Added database table creation SQL for `scoping_approvals` and `approval_actions`

3. **`app/launchpad/launchpad_api/db_models/__init__.py`**
   - Added imports for new models

## 🔌 API Endpoints

### 1. Submit Scoping for Approval
- **Endpoint:** `POST /api/site/{site_id}/scoping/submit`
- **Controller:** `site_scoping_submit()`
- **Auth:** Deployment Engineer only
- **Validations:**
  - Site must exist
  - No pending approval for site (409 Conflict if exists)
  - At least one software or hardware item required

### 2. Resubmit Scoping After Rejection
- **Endpoint:** `POST /api/site/{site_id}/scoping/resubmit`
- **Controller:** `site_scoping_resubmit()`
- **Auth:** Deployment Engineer only
- **Validations:**
  - Previous approval must exist and be in 'rejected' status
  - Site ID must match previous approval

### 3. Get Scoping Approvals
- **Endpoint:** `GET /api/scoping-approvals?status={status}&site_id={site_id}`
- **Controller:** `scoping_approvals_get()`
- **Auth:** Required
- **Query Params:**
  - `status`: Filter by status (pending, approved, rejected, changes_requested)
  - `site_id`: Filter by site ID (returns most recent if provided)

### 4. Get Scoping Approval by ID
- **Endpoint:** `GET /api/scoping-approvals/{approval_id}`
- **Controller:** `scoping_approvals_id_get()`
- **Auth:** Required

### 5. Approve Scoping
- **Endpoint:** `POST /api/scoping-approvals/{approval_id}/approve`
- **Controller:** `scoping_approvals_id_approve()`
- **Auth:** Admin or Operations Manager only
- **Actions:**
  - Updates approval status to 'approved'
  - Updates site status to 'approved'
  - Creates audit trail entry

### 6. Reject Scoping
- **Endpoint:** `POST /api/scoping-approvals/{approval_id}/reject`
- **Controller:** `scoping_approvals_id_reject()`
- **Auth:** Admin or Operations Manager only
- **Actions:**
  - Updates approval status to 'rejected'
  - Stores rejection reason and comment
  - Creates audit trail entry

## 🔐 Authentication & Authorization

### Current Implementation
The controller includes placeholder authentication functions:
- `get_current_user()`: Gets current user from session/auth
- `check_role()`: Checks if user has required role

### Role Constants (TODO: Update to match your system)
```python
ADMIN_ROLE = 1
OPS_MANAGER_ROLE = 2
DEPLOYMENT_ENGINEER_ROLE = 3
```

**⚠️ IMPORTANT:** You need to:
1. Update these role constants to match your actual role system
2. Implement proper authentication in `get_current_user()`
3. Replace placeholder `X-User-Id` header with actual session/auth mechanism

### Recommended Authentication Implementation
```python
def get_current_user():
    """Get current user from session/authentication."""
    # Option 1: From session
    user_id = session.get('user_id')
    
    # Option 2: From JWT token
    # token = request.headers.get('Authorization')
    # user_id = decode_jwt_token(token)
    
    # Option 3: From cookie
    # token = request.cookies.get('session_id')
    # user_id = decrypt_token(token)
    
    if user_id:
        return User.get_by_id(int(user_id))
    return None
```

## 📊 Database Schema

### Table: `scoping_approvals`
- Uses INT for IDs (not UUID) to match existing codebase
- Stores scoping data and cost breakdown as JSON
- Supports versioning with `previous_version_id`
- Foreign keys to `site` and `users` tables

### Table: `approval_actions`
- Audit trail for all approval actions
- Tracks who performed what action and when
- Optional metadata field for additional information

## 🔄 Business Logic

### Status Flow
```
pending → approved (via approve endpoint)
pending → rejected (via reject endpoint)
rejected → pending (via resubmit endpoint, creates new approval)
```

### Submission Rules
- ✅ Only one pending approval per site at a time
- ✅ Returns 409 Conflict if pending approval exists
- ✅ Deployment Engineer must be authenticated

### Approval/Rejection Rules
- ✅ Only Admin or Operations Manager can approve/reject
- ✅ Can only approve/reject pending approvals
- ✅ Updates site status on approval
- ✅ Creates audit trail entry

### Resubmission Rules
- ✅ Can only resubmit rejected approvals
- ✅ Creates new approval with incremented version
- ✅ Links to previous approval via `previous_version_id`

## 🧪 Testing Checklist

### Submit Scoping
- [ ] Submit with valid data → Returns 200
- [ ] Submit when pending exists → Returns 409
- [ ] Submit with invalid site_id → Returns 404
- [ ] Submit without authentication → Returns 401
- [ ] Submit as non-Deployment Engineer → Returns 403

### Resubmit Scoping
- [ ] Resubmit after rejection → Returns 200 with incremented version
- [ ] Resubmit without previous rejection → Returns 400
- [ ] Resubmit with invalid previous_approval_id → Returns 404

### Get Approvals
- [ ] Get all approvals → Returns list
- [ ] Get by status → Returns filtered list
- [ ] Get by site_id → Returns most recent approval
- [ ] Get non-existent approval → Returns 404

### Approve Scoping
- [ ] Approve pending approval → Returns 200, updates site status
- [ ] Approve already approved → Returns 400
- [ ] Approve as non-Admin/Ops Manager → Returns 403

### Reject Scoping
- [ ] Reject pending approval → Returns 200
- [ ] Reject already rejected → Returns 400
- [ ] Reject as non-Admin/Ops Manager → Returns 403

## ⚠️ Important Notes

1. **Authentication**: The current implementation uses placeholder authentication. You must implement actual authentication before deploying.

2. **Role Constants**: Update the role constants in `scoping_approval_controller.py` to match your role system.

3. **Database**: Tables are created automatically via `main.py` on application startup. For existing databases, you may need to run the SQL manually.

4. **JSON Fields**: MySQL/MariaDB JSON type is used. Ensure your database version supports JSON (MySQL 5.7+ or MariaDB 10.2+).

5. **Error Handling**: All endpoints include comprehensive error handling with appropriate HTTP status codes.

6. **Audit Trail**: Approval actions are logged to `approval_actions` table for audit purposes.

## 🚀 Next Steps

1. **Implement Authentication**: Replace placeholder `get_current_user()` with actual authentication
2. **Update Role Constants**: Match role values to your system
3. **Test Endpoints**: Use the testing checklist above
4. **Frontend Integration**: Connect frontend to these endpoints
5. **Optional Enhancements**:
   - Add email notifications on approval/rejection
   - Add validation for software/hardware IDs
   - Add cost calculation verification
   - Add pagination for approvals list

## 📝 Example Requests

### Submit Scoping
```bash
POST /api/site/1/scoping/submit
Content-Type: application/json
X-User-Id: 123

{
  "site_name": "Birmingham South Cafeteria",
  "selected_software": [
    {"id": "1", "quantity": 2}
  ],
  "selected_hardware": [
    {"id": "1", "quantity": 3}
  ],
  "cost_summary": {
    "hardwareCost": 5000,
    "totalCapex": 7250,
    "totalInvestment": 10850
  }
}
```

### Approve Scoping
```bash
POST /api/scoping-approvals/1/approve
Content-Type: application/json
X-User-Id: 456

{
  "comment": "Approved. Proceed with procurement."
}
```

---

**Status**: ✅ Implementation Complete - Ready for authentication integration and testing!

