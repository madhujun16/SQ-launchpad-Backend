# API Integration Guide for Frontend

## Base URL
- **Local Development**: `http://localhost:8080/api`
- **Production**: `https://[YOUR-APP-ENGINE-URL]/api`
- **Swagger UI**: `http://localhost:8080/api/ui/` (for API documentation)

## Authentication Flow

### 1. OTP-Based Login (Two-Step Process)

#### Step 1: Request OTP
**Endpoint**: `POST /api/send/otp`

**Request Body**:
```json
{
  "email": "user@example.com"
}
```

**Response** (200):
```json
{
  "message": "OTP sent successfully to user@example.com"
}
```

**Error Response** (400):
```json
{
  "error": "User is not registered"
}
```

#### Step 2: Verify OTP & Login
**Endpoint**: `POST /api/verify/otp`

**Request Body**:
```json
{
  "email": "user@example.com",
  "otp": "123456"
}
```

**Response** (200):
- Sets HTTP-only cookie: `session_id` (JWT token)
- Cookie settings:
  - `HttpOnly: true`
  - `Secure: false` (set to `true` in production with HTTPS)
  - `SameSite: Lax`
  - `Max-Age: 3600` (1 hour)
- Response body:
```json
{
  "message": "Login successful"
}
```

**Error Response** (400):
```json
{
  "message": "Invalid or expired OTP"
}
```

### 2. Authenticated Requests

After login, all protected endpoints require the `session_id` cookie to be sent with requests.

**Important**: 
- Frontend must include credentials in requests: `credentials: 'include'` (fetch) or `withCredentials: true` (axios)
- Cookie is automatically sent by browser if credentials are included

**Example (Fetch)**:
```javascript
fetch('http://localhost:8080/api/organization', {
  method: 'GET',
  credentials: 'include', // Required for cookies
  headers: {
    'Content-Type': 'application/json'
  }
})
```

**Example (Axios)**:
```javascript
axios.get('http://localhost:8080/api/organization', {
  withCredentials: true // Required for cookies
})
```

### 3. Logout
Simply clear/delete the `session_id` cookie on the frontend.

---

## CORS Configuration

- **CORS Enabled**: Yes
- **Credentials**: Supported (`supports_credentials=True`)
- **Allowed Origins**: Configured in backend (check with backend team for production origins)

**Frontend Configuration Required**:
- Always include `credentials: 'include'` in fetch requests
- Or `withCredentials: true` in axios configuration

---

## API Endpoints

### Organization Management

#### Get Organizations
**Endpoint**: `GET /api/organization?organization_id={id}`

**Query Parameters**:
- `organization_id` (optional): 
  - If `"all"`: Returns all organizations
  - If number: Returns specific organization
  - If omitted: Returns all organizations

**Response** (200):
```json
{
  "message": "details fetched succesfully",
  "data": [
    {
      "org_id": 1,
      "name": "Organization Name",
      "description": "Description",
      "sector": "Technology",
      "unit_code": "ORG001",
      "organization_logo": "https://storage.googleapis.com/launchpad_logo/1.svg",
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  ]
}
```

#### Create Organization
**Endpoint**: `POST /api/organization`

**Request Body**:
```json
{
  "name": "Organization Name",
  "description": "Description text",
  "sector": "Technology",
  "unit_code": "ORG001",
  "organization_logo": "https://storage.googleapis.com/launchpad_logo/1.svg"
}
```

**Response** (200):
```json
{
  "message": "Organization created successfully",
  "data": {
    "org_id": 1,
    "name": "Organization Name",
    ...
  }
}
```

#### Update Organization
**Endpoint**: `PUT /api/organization`

**Request Body**: Same as Create, but include `id` field

#### Delete Organization
**Endpoint**: `DELETE /api/organization?organization_id={id}`

---

### Site Management

#### Get All Sites
**Endpoint**: `GET /api/site/all`

**Response** (200):
```json
{
  "message": "Succesfully fetched sites",
  "data": [
    {
      "site_id": 1,
      "status": "approved",
      "field_name_1": { /* JSON field value */ },
      "field_name_2": { /* JSON field value */ }
    }
  ]
}
```

#### Create Site
**Endpoint**: `POST /api/site`

**Request Body**:
```json
{
  "name": "Site Name",  // Note: Currently not used in backend
  "status": "created"
}
```

**Response** (200):
```json
{
  "message": "Site Created Succesfully"
}
```

#### Update Site
**Endpoint**: `PUT /api/site`

**Request Body**:
```json
{
  "id": 1,
  "name": "Updated Site Name",
  "status": "approved"
}
```

#### Delete Site
**Endpoint**: `DELETE /api/site?site_id={id}`

---

### Page Management

#### Get Page
**Endpoint**: `GET /api/page?page_name={name}&site_id={id}`

**Query Parameters**:
- `page_name` (required): Name of the page (e.g., "site_study")
- `site_id` (required): Site ID

**Response** (200):
```json
{
  "message": "Succesfully fetched the data",
  "data": {
    "page_id": 1,
    "page_name": "site_study",
    "site_id": 1,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00",
    "sections": [
      {
        "section_id": 1,
        "section_name": "general_info",
        "page_id": 1,
        "fields": [
          {
            "field_id": 1,
            "field_name": "site_name",
            "field_value": { /* JSON object */ },
            "section_id": 1
          }
        ]
      }
    ]
  }
}
```

#### Create Page
**Endpoint**: `POST /api/page`

**Request Body**:
```json
{
  "page_name": "Home Page",
  "site_id": 1,  // Optional: if not provided, creates new site
  "status": "created",  // Site status if creating new site
  "sections": [
    {
      "section_name": "Hero Banner",
      "fields": [
        {
          "field_name": "heading",
          "field_value": {
            "text": "Welcome",
            "color": "#000000"
          }
        },
        {
          "field_name": "subheading",
          "field_value": {
            "text": "Subtitle"
          }
        }
      ]
    }
  ]
}
```

**Response** (200):
```json
{
  "message": "Page saved successfully",
  "data": {
    "site_id": 1,
    "page_id": 1,
    "page_name": "Home Page",
    "sections": [
      {
        "section_id": 1,
        "section_name": "Hero Banner",
        "fields": [
          {
            "field_id": 1,
            "field_name": "heading",
            "field_value": { /* JSON */ }
          }
        ]
      }
    ]
  }
}
```

#### Update Page
**Endpoint**: `PUT /api/page`

**Request Body**:
```json
{
  "id": 1,  // Page ID (required)
  "page_name": "Home Page",
  "site_id": 1,
  "status": "approved",  // Updates site status
  "sections": [
    {
      "section_id": 1,  // Required for updates
      "section_name": "Hero Banner",
      "fields": [
        {
          "field_id": 1,  // Required for updates
          "field_value": {
            "text": "Updated Welcome",
            "color": "#FF0000"
          }
        }
      ]
    }
  ]
}
```

**Response** (200):
```json
{
  "message": "Page updated successfully"
}
```

---

### Section Management

#### Get Sections
**Endpoint**: `GET /api/section?page_id={id}&section_name={name}`

**Query Parameters**:
- `page_id` (required): Page ID
- `section_name` (optional): Filter by section name

#### Create Section
**Endpoint**: `POST /api/section`

**Request Body**:
```json
{
  "page_id": 1,
  "section_name": "Hero Banner",
  "fields": {}
}
```

---

### File Upload (Logo Upload)

#### Generate Upload URL
**Endpoint**: `POST /api/generate-upload-url`

**Request Body**:
```json
{
  "data_identifier": "org_123"  // Unique identifier for the file
}
```

**Response** (200):
```json
{
  "message": "upload data",
  "data": {
    "upload_url": "https://storage.googleapis.com/launchpad_logo/org_123.svg?X-Goog-Algorithm=...",
    "public_url": "https://storage.googleapis.com/launchpad_logo/org_123.svg"
  }
}
```

**Upload Process**:
1. Call this endpoint to get `upload_url`
2. Upload file to `upload_url` using HTTP PUT
3. Use `public_url` when creating/updating organization

**Upload Example**:
```javascript
// Step 1: Get signed URL
const response = await fetch('/api/generate-upload-url', {
  method: 'POST',
  credentials: 'include',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ data_identifier: 'org_123' })
});
const { data } = await response.json();

// Step 2: Upload file
const file = /* your file */;
await fetch(data.upload_url, {
  method: 'PUT',
  body: file,
  headers: {
    'Content-Type': 'image/png'  // Must match backend expectation
  }
});

// Step 3: Use public_url in organization
```

**Note**: 
- File is stored as SVG format: `{data_identifier}.svg`
- Upload URL expires in 15 minutes
- Content-Type must be `image/png` for upload

---

## Error Handling

### Standard Error Response Format
```json
{
  "message": "Oops Something went Wrong !!!"
}
```

### Common HTTP Status Codes
- `200`: Success
- `400`: Bad Request / Validation Error
- `401`: Unauthorized (Missing or invalid session cookie)
- `500`: Internal Server Error

### Authentication Errors
- Missing cookie: `401 Unauthorized`
- Expired token: `401 Unauthorized` (token expires after 1 hour)
- Invalid token: `401 Unauthorized`

---

## Request/Response Format

### Content-Type
- **Request**: `application/json`
- **Response**: `application/json`

### Headers Required
```javascript
{
  'Content-Type': 'application/json'
}
```

### Cookies
- Automatically handled by browser when `credentials: 'include'` is set
- Cookie name: `session_id`
- Cookie is HTTP-only (not accessible via JavaScript)

---

## Data Models

### Field Values (JSON)
Fields store flexible JSON data. Examples:

```json
{
  "text": "Some text",
  "color": "#000000",
  "size": 16,
  "nested": {
    "property": "value"
  }
}
```

### Site Status Values
Common statuses:
- `"created"`
- `"approved"`
- `"pending"`
- `"rejected"`

---

## Important Notes for Frontend

1. **Cookie Handling**:
   - Always use `credentials: 'include'` (fetch) or `withCredentials: true` (axios)
   - Cookie is HTTP-only, so you cannot read it via JavaScript
   - Cookie expires after 1 hour - implement token refresh or re-login

2. **OTP Flow**:
   - OTP expires in 5 minutes (300 seconds)
   - OTP is 6 digits
   - User must be registered before requesting OTP

3. **File Uploads**:
   - Use signed URLs for uploads (not direct POST to API)
   - Upload URL expires in 15 minutes
   - Files are stored as SVG format

4. **Unique Constraints**:
   - Organization: `name` and `unit_code` must be unique
   - Page: `page_name` + `site_id` must be unique
   - Section: `section_name` + `page_id` must be unique
   - Field: `field_name` + `section_id` must be unique

5. **Cascade Deletes**:
   - Deleting a site deletes all pages, sections, and fields
   - Deleting a page deletes all sections and fields
   - Deleting a section deletes all fields

6. **Field Values**:
   - Always send field values as JSON objects (not strings)
   - Backend handles JSON serialization/deserialization

---

## Testing

### Swagger UI
Access interactive API documentation at:
- Local: `http://localhost:8080/api/ui/`
- OpenAPI Spec: `http://localhost:8080/api/openapi.json`

### Test Credentials
- Some test emails are hardcoded: `sarthak@gmail.com`, `madhu@gmail.com`
- OTP for test emails: Check backend code (currently `123456` for `sarthakg35@gmail.com`)

---

## Environment Variables (Backend)

These are configured on the backend, but good to know:
- `SECRET_KEY`: JWT signing key
- `MAIL_USERNAME`: Email sender address
- `MAIL_PASSWORD`: Email password
- Database credentials: Stored in GCP Secret Manager

---

## Support

For API issues or questions:
1. Check Swagger UI documentation: `/api/ui/`
2. Review OpenAPI spec: `/api/openapi.json`
3. Contact backend team

---

## Quick Reference

### Authentication Flow
```
1. POST /api/send/otp { email }
2. POST /api/verify/otp { email, otp }
   → Receives session_id cookie
3. All subsequent requests include cookie automatically
```

### Common Endpoints
- `GET /api/organization?organization_id=all` - List all orgs
- `GET /api/site/all` - List all sites
- `GET /api/page?page_name=site_study&site_id=1` - Get page with sections/fields
- `POST /api/page` - Create page with nested structure
- `PUT /api/page` - Update page (requires IDs for sections/fields)

