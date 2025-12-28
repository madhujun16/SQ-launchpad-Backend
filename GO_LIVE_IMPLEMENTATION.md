# Go Live API Implementation

## ✅ Implementation Complete

All backend API endpoints for the go live workflow have been implemented.

## 📁 Files Created/Modified

### New Files
1. **`app/launchpad/launchpad_api/db_models/go_live_data.py`**
   - Database model for `go_live_data` table
   - Includes CRUD operations and query methods
   - Handles status management (live/offline/postponed)

2. **`app/launchpad/launchpad_api/controllers/go_live_controller.py`**
   - All controller functions for go live endpoints
   - Includes authentication and role checking logic
   - Implements prerequisites validation

### Modified Files
1. **`app/launchpad/launchpad_api/openapi/openapi.yaml`**
   - Added all go live endpoints
   - Added request/response schemas

2. **`app/launchpad/launchpad_api/main.py`**
   - Added database table creation SQL for `go_live_data`

3. **`app/launchpad/launchpad_api/db_models/__init__.py`**
   - Added import for GoLiveData model

## 🔌 API Endpoints

### 1. Get Go Live Data
- **Endpoint:** `GET /api/site/{site_id}/go-live`
- **Controller:** `site_go_live_get()`
- **Auth:** Required
- **Response:** Returns go live data or 404 if not found (acceptable for new sites)

### 2. Mark Site as Live
- **Endpoint:** `POST /api/site/{site_id}/go-live/activate`
- **Controller:** `site_go_live_activate()`
- **Auth:** Admin or Deployment Engineer only
- **Prerequisites:**
  - Site status must be 'procurement_done'
  - Notes are required (non-empty, max 5000 chars)
- **Actions:**
  - Creates/updates go_live_data record
  - Sets status to 'live'
  - Sets go_live_date to current timestamp
  - Updates site status to 'live'

### 3. Mark Site as Offline
- **Endpoint:** `POST /api/site/{site_id}/go-live/deactivate`
- **Controller:** `site_go_live_deactivate()`
- **Auth:** Admin or Deployment Engineer only
- **Prerequisites:**
  - Site must be currently 'live'
- **Actions:**
  - Updates go_live_data status to 'offline'
  - Preserves go_live_date and signed_off_by for historical record
  - Updates site status back to 'procurement_done'
  - Notes are optional

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

## 📊 Database Schema

### Table: `go_live_data`
- Uses INT for IDs (not UUID) to match existing codebase
- Unique constraint on `site_id` (one record per site)
- Stores status, go_live_date, signed_off_by, and notes
- Foreign keys to `site` and `users` tables

## 🔄 Business Logic

### Prerequisites for Going Live
1. **Site Status Check:**
   - Site must be in 'procurement_done' status
   - Cannot go live if procurement is not completed
   - Returns 400 with clear error message if prerequisites not met

2. **Notes Requirement:**
   - Notes are **required** when going live
   - Notes are **optional** when taking offline
   - Maximum length: 5000 characters

### Role-Based Access
1. **Get Go Live Data:**
   - Any authenticated user can view go live status

2. **Mark as Live/Offline:**
   - Only Admin or Deployment Engineer can toggle go live status
   - Backend verifies user role before allowing toggle

### Status Flow
```
offline → live (via activate endpoint)
live → offline (via deactivate endpoint)
```

### Historical Data
- When a site is taken offline, `go_live_date` and `signed_off_by` are preserved
- This allows tracking when the site first went live
- Only `status` and `notes` are updated when toggling

## 🧪 Testing Checklist

### Get Go Live Data
- [ ] Get existing go live data → Returns 200 with data
- [ ] Get non-existent go live data → Returns 404 (acceptable)
- [ ] Get without authentication → Returns 401

### Mark Site as Live
- [ ] Mark live with valid prerequisites (Admin) → Returns 200, updates site status
- [ ] Mark live with valid prerequisites (Deployment Engineer) → Returns 200
- [ ] Mark live without completed procurement → Returns 400
- [ ] Mark live without notes → Returns 422
- [ ] Mark live with notes > 5000 chars → Returns 422
- [ ] Mark live as Ops Manager → Returns 403
- [ ] Mark live without authentication → Returns 401
- [ ] Verify site status updated to 'live'
- [ ] Verify go_live_date and signed_off_by are set correctly

### Mark Site as Offline
- [ ] Take offline when site is live (Admin) → Returns 200, reverts site status
- [ ] Take offline when site is live (Deployment Engineer) → Returns 200
- [ ] Take offline when site is not live → Returns 400
- [ ] Take offline as Ops Manager → Returns 403
- [ ] Take offline without authentication → Returns 401
- [ ] Verify go_live_date is preserved
- [ ] Verify site status reverted to 'procurement_done'

## ⚠️ Important Notes

1. **Authentication**: The current implementation uses placeholder authentication. You must implement actual authentication before deploying.

2. **Role Constants**: Update the role constants in `go_live_controller.py` to match your role system.

3. **Database**: Tables are created automatically via `main.py` on application startup. For existing databases, you may need to run the SQL manually.

4. **Prerequisites**: The backend enforces that procurement must be completed (site.status = 'procurement_done') before allowing go live.

5. **Historical Tracking**: `go_live_date` and `signed_off_by` are preserved when taking a site offline for audit purposes.

6. **One Record Per Site**: Unique constraint ensures only one go live record per site.

## 🚀 Next Steps

1. **Implement Authentication**: Replace placeholder `get_current_user()` with actual authentication
2. **Update Role Constants**: Match role values to your system
3. **Test Endpoints**: Use the testing checklist above
4. **Frontend Integration**: Connect frontend to these endpoints

## 📝 Example Requests

### Get Go Live Data
```bash
GET /api/site/123/go-live
```

### Mark Site as Live
```bash
POST /api/site/123/go-live/activate
Content-Type: application/json
X-User-Id: 456

{
  "notes": "Site went live successfully. All systems operational. Staff training completed."
}
```

### Mark Site as Offline
```bash
POST /api/site/123/go-live/deactivate
Content-Type: application/json
X-User-Id: 456

{
  "notes": "Site taken offline for maintenance. Expected to be back online in 2 hours."
}
```

---

**Status**: ✅ Implementation Complete - Ready for authentication integration and testing!

