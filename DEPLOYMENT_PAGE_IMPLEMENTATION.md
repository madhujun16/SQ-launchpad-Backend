# Deployment Page Integration

## Overview

The Deployment page is integrated into the site workflow using the existing **Page/Section/Field** architecture. This document describes the implementation details, business logic, and API usage for the Deployment page.

---

## Architecture

The Deployment page uses the existing page/section/field tables with no new database schema required:

- **Page**: `deployment` (one per site)
- **Sections**: 
  - `deployment_checklist` - Stores deployment steps as JSON
  - `installation` - Stores deployment team info, dates, and progress
  - `testing` - Stores deployment notes as JSON
- **Fields**: Various fields within each section

---

## API Endpoints

The Deployment page uses the existing Page API endpoints:

### 1. Get Deployment Page

**Endpoint:** `GET /api/page?page_name=deployment&site_id={siteId}`

**Description:** Retrieves the deployment page with all sections and fields.

**Response:**
```json
{
  "message": "Succesfully fetched the data",
  "data": {
    "page_id": 123,
    "page_name": "deployment",
    "site_id": 456,
    "created_at": "2025-01-10T08:00:00Z",
    "updated_at": "2025-01-15T14:30:00Z",
    "sections": [
      {
        "section_id": 789,
        "section_name": "deployment_checklist",
        "page_id": 123,
        "fields": [
          {
            "field_id": 1001,
            "field_name": "steps",
            "field_value": "[{\"id\":\"hardware_delivery\",\"name\":\"Hardware Delivery\",\"status\":\"completed\",...}]",
            "section_id": 789
          }
        ]
      },
      {
        "section_id": 790,
        "section_name": "installation",
        "page_id": 123,
        "fields": [
          {
            "field_id": 1002,
            "field_name": "deployment_engineer",
            "field_value": "John Doe",
            "section_id": 790
          },
          {
            "field_id": 1003,
            "field_name": "start_date",
            "field_value": "2025-01-15",
            "section_id": 790
          },
          {
            "field_id": 1004,
            "field_name": "target_date",
            "field_value": "2025-01-25",
            "section_id": 790
          },
          {
            "field_id": 1005,
            "field_name": "progress",
            "field_value": "65",
            "section_id": 790
          }
        ]
      },
      {
        "section_id": 791,
        "section_name": "testing",
        "page_id": 123,
        "fields": [
          {
            "field_id": 1006,
            "field_name": "notes",
            "field_value": "[{\"id\":\"note-1\",\"author\":\"John Doe\",\"content\":\"Site assessment completed.\",...}]",
            "section_id": 791
          }
        ]
      }
    ]
  }
}
```

### 2. Create Deployment Page

**Endpoint:** `POST /api/page`

**Description:** Creates a new deployment page for a site. If the `deployment_checklist` section has an empty or missing `steps` field, it will be automatically initialized with default steps.

**Request Body:**
```json
{
  "page_name": "deployment",
  "site_id": 456,
  "status": "created",
  "sections": [
    {
      "section_name": "deployment_checklist",
      "fields": [
        {
          "field_name": "steps",
          "field_value": "[]"
        }
      ]
    },
    {
      "section_name": "installation",
      "fields": [
        {
          "field_name": "deployment_engineer",
          "field_value": ""
        },
        {
          "field_name": "start_date",
          "field_value": ""
        },
        {
          "field_name": "target_date",
          "field_value": ""
        },
        {
          "field_name": "progress",
          "field_value": "0"
        }
      ]
    },
    {
      "section_name": "testing",
      "fields": [
        {
          "field_name": "notes",
          "field_value": "[]"
        }
      ]
    }
  ]
}
```

**Note:** If `steps` field is empty or missing, default steps will be automatically initialized:
- `hardware_delivery` (4 hours)
- `software_installation` (8 hours)
- `network_setup` (6 hours)
- `system_testing` (4 hours)

### 3. Update Deployment Page

**Endpoint:** `PUT /api/page`

**Description:** Updates deployment page fields. The backend automatically:
- Validates step progression
- Calculates and updates progress percentage
- Updates site status to `'deployed'` when all steps are completed

**Request Body:**
```json
{
  "id": 123,
  "site_id": 456,
  "status": "in_progress",
  "sections": [
    {
      "section_id": 789,
      "section_name": "deployment_checklist",
      "fields": [
        {
          "field_id": 1001,
          "field_name": "steps",
          "field_value": "[{\"id\":\"hardware_delivery\",\"name\":\"Hardware Delivery\",\"status\":\"completed\",\"completedAt\":\"2025-01-15T10:00:00Z\",\"completedBy\":\"John Doe\",\"notes\":\"All hardware received\",\"estimatedHours\":4,\"actualHours\":3,\"deliveryReceipt\":\"https://storage.example.com/receipts/receipt-123.pdf\"}]"
        }
      ]
    }
  ]
}
```

---

## Business Logic

### 1. Default Steps Initialization

When creating a deployment page, if the `steps` field is empty or missing, the backend automatically initializes it with these default steps:

```json
[
  {
    "id": "hardware_delivery",
    "name": "Hardware Delivery",
    "status": "pending",
    "estimatedHours": 4
  },
  {
    "id": "software_installation",
    "name": "Software Installation",
    "status": "pending",
    "estimatedHours": 8
  },
  {
    "id": "network_setup",
    "name": "Network Setup",
    "status": "pending",
    "estimatedHours": 6
  },
  {
    "id": "system_testing",
    "name": "System Testing",
    "status": "pending",
    "estimatedHours": 4
  }
]
```

### 2. Step Validation

The backend validates deployment steps with the following rules:

#### Required Fields
- `id` (string): Unique step identifier
- `name` (string): Step display name
- `status` (string): Must be one of: `pending`, `in_progress`, `completed`, `blocked`
- `estimatedHours` (number): Positive number

#### Optional Fields
- `completedAt` (string): ISO date string
- `completedBy` (string): Name of person who completed the step
- `notes` (string): Step notes
- `actualHours` (number): Positive number
- `deliveryReceipt` (string): URL to delivery receipt (required for `hardware_delivery` when status is `completed`)

#### Step Progression Rules
- Steps must be completed in order: `hardware_delivery` → `software_installation` → `network_setup` → `system_testing`
- A step cannot be marked `completed` if the previous step is not `completed`
- A step cannot be marked `in_progress` if the previous step is not `completed` (except for the first step)

### 3. Progress Calculation

Progress is automatically calculated and updated when deployment steps change:

```
Progress = (completed_steps / total_steps) * 100
```

The progress is stored in the `installation.progress` field and updated automatically on each step change.

### 4. Site Status Update

When all deployment steps are marked as `completed`, the backend automatically:
- Updates the site status to `'deployed'`
- Logs the status change

This allows the site to proceed to the "Go Live" stage.

### 5. Hardware Delivery Receipt Requirement

The `hardware_delivery` step requires a `deliveryReceipt` URL before it can be marked as `completed`. If the step is marked as `completed` without a receipt, the backend returns a validation error.

---

## Field Structures

### deployment_checklist Section

#### steps (JSON Array)
```json
[
  {
    "id": "hardware_delivery",
    "name": "Hardware Delivery",
    "status": "completed",
    "completedAt": "2025-01-15T10:00:00Z",
    "completedBy": "John Doe",
    "notes": "All hardware received and verified",
    "estimatedHours": 4,
    "actualHours": 3,
    "deliveryReceipt": "https://storage.example.com/receipts/receipt-123.pdf"
  }
]
```

### installation Section

#### deployment_engineer (String)
- Optional
- Max length: 255 characters
- Example: `"John Doe"`

#### start_date (String)
- Optional
- Format: `YYYY-MM-DD`
- Example: `"2025-01-15"`

#### target_date (String)
- Optional
- Format: `YYYY-MM-DD`
- Must be after `start_date` if both provided
- Example: `"2025-01-25"`

#### progress (String, Number)
- Auto-calculated by backend
- Range: 0-100
- Stored as string
- Example: `"65"`

### testing Section

#### notes (JSON Array)
```json
[
  {
    "id": "note-1",
    "author": "John Doe",
    "content": "Site assessment completed. All requirements confirmed.",
    "timestamp": "2025-01-15T10:00:00Z"
  }
]
```

---

## Error Handling

### Validation Errors (400 Bad Request)

#### Invalid Steps Field
```json
{
  "message": "Invalid steps field: must be a valid JSON array"
}
```

#### Invalid Step Data
```json
{
  "message": "Invalid step: Step missing required field: status"
}
```

#### Step Progression Error
```json
{
  "message": "Step progression error: Cannot complete 'Software Installation' before 'Hardware Delivery' is completed"
}
```

#### Missing Delivery Receipt
```json
{
  "message": "Invalid step: hardware_delivery step requires deliveryReceipt when status is 'completed'"
}
```

#### Invalid Installation Field
```json
{
  "message": "Invalid installation field: target_date must be after start_date"
}
```

#### Invalid Notes Field
```json
{
  "message": "Invalid notes field: Note missing required field: timestamp"
}
```

### Not Found Errors (404)

#### Page Not Found
```json
{
  "message": "Page 'deployment' not found for site 456"
}
```

#### Site Not Found
```json
{
  "message": "Site not found"
}
```

---

## Integration with Site Workflow

### Site Status Progression

1. **procurement_done** → Site procurement is complete
2. **deployed** → All deployment steps are completed (automatically set by backend)
3. **live** → Site is live and operational (set via Go Live API)

### Go Live Prerequisites

The Go Live API now requires the site to be in `'deployed'` status (instead of `'procurement_done'`). This ensures that:
- All deployment steps are completed
- Hardware is delivered and verified
- Software is installed
- Network is configured
- System testing is complete

---

## Implementation Details

### Files Modified

1. **`app/launchpad/launchpad_api/utils/deployment_utils.py`** (NEW)
   - Helper functions for deployment validation
   - Step validation and progression checking
   - Progress calculation
   - Default steps initialization

2. **`app/launchpad/launchpad_api/controllers/page_controller.py`**
   - Added deployment-specific logic in `page_post()`:
     - Initialize default steps if missing
     - Validate steps, installation fields, and notes
   - Added deployment-specific logic in `page_put()`:
     - Validate step progression
     - Auto-calculate and update progress
     - Update site status to `'deployed'` when all steps complete

3. **`app/launchpad/launchpad_api/controllers/go_live_controller.py`**
   - Updated prerequisite check from `'procurement_done'` to `'deployed'`

4. **`app/launchpad/launchpad_api/db_models/page.py`**
   - Fixed `get_by_siteid_and_pagename()` to be a static method

### Database Schema

No new tables or columns are required. The deployment page uses the existing:
- `page` table
- `section` table
- `field` table (with JSON field_value)

---

## Testing Checklist

### Unit Tests

- [ ] Create deployment page with empty steps field → default steps initialized
- [ ] Create deployment page with custom steps → custom steps preserved
- [ ] Update deployment steps → progress calculated correctly
- [ ] Complete all steps → site status updated to `'deployed'`
- [ ] Try to complete step 2 before step 1 → validation error
- [ ] Try to complete hardware_delivery without receipt → validation error
- [ ] Update installation fields → validation works correctly
- [ ] Update notes field → validation works correctly

### Integration Tests

- [ ] Create deployment page → verify default steps
- [ ] Update steps → verify progress auto-update
- [ ] Complete all steps → verify site status change
- [ ] Try to go live before deployment complete → error
- [ ] Complete deployment → go live succeeds

### Edge Cases

- [ ] Handle missing deployment page gracefully
- [ ] Handle invalid JSON in steps/notes fields
- [ ] Handle missing required fields
- [ ] Handle duplicate step IDs
- [ ] Handle progress calculation with zero steps
- [ ] Handle date validation (target_date before start_date)

---

## Frontend Integration

The frontend uses the existing `PageService` to interact with the deployment page:

```typescript
// Get deployment page
const page = await PageService.getPage('deployment', siteId);

// Update steps
const steps = [
  {
    id: "hardware_delivery",
    name: "Hardware Delivery",
    status: "completed",
    completedAt: new Date().toISOString(),
    completedBy: "John Doe",
    notes: "All hardware received",
    estimatedHours: 4,
    actualHours: 3,
    deliveryReceipt: "https://storage.example.com/receipts/receipt-123.pdf"
  }
];

await PageService.updateField(
  siteId,
  'deployment',
  'deployment_checklist',
  'steps',
  JSON.stringify(steps)
);
```

The frontend should:
- Parse JSON fields (steps, notes) for display
- Handle progress updates (backend calculates automatically)
- Validate step progression before submission
- Handle file upload for delivery receipts
- Display validation errors from backend

---

## Notes

1. **No Database Migration Required**: The deployment page uses existing tables.

2. **JSON Fields**: The `steps` and `notes` fields store JSON data. The backend handles parsing and validation.

3. **Automatic Progress Calculation**: Progress is calculated and updated automatically by the backend. The frontend can display it but doesn't need to calculate it.

4. **Site Status Automation**: Site status is automatically updated to `'deployed'` when all steps are completed. No manual status update is required.

5. **Step Order Enforcement**: The backend enforces step order to ensure proper workflow progression.

6. **Delivery Receipt Requirement**: The `hardware_delivery` step requires a receipt URL before completion. The frontend should handle file upload separately and provide the URL.

---

## Summary

The Deployment page integration:
- ✅ Uses existing page/section/field architecture (no new tables)
- ✅ Automatically initializes default steps
- ✅ Validates step progression and data
- ✅ Auto-calculates and updates progress
- ✅ Updates site status to `'deployed'` when complete
- ✅ Integrates with Go Live API (requires `'deployed'` status)
- ✅ Provides comprehensive error handling and validation

The implementation is complete and ready for frontend integration.

