# GCP Database Migration Instructions for Scoping Approvals

## Overview

The Scoping Approval API requires two new database tables:
1. `scoping_approvals` - Stores scoping approval requests
2. `approval_actions` - Audit trail for approval actions

## Automatic Table Creation

The application **automatically creates these tables** when it starts up (via `main.py`). If your application is already running and the tables don't exist, you have two options:

### Option 1: Restart the Application (Recommended)
Simply restart your application, and the tables will be created automatically on startup.

### Option 2: Run Migration Script Manually
If you prefer to create the tables manually or if automatic creation fails, run the migration script.

## Manual Migration Steps

### Step 1: Access Your GCP Database

You can access your GCP database using one of these methods:

#### Method A: Cloud SQL Proxy (Recommended for Local)
```bash
# Install Cloud SQL Proxy if not already installed
# Download from: https://cloud.google.com/sql/docs/mysql/sql-proxy

# Start the proxy (replace with your connection name)
./cloud-sql-proxy INSTANCE_CONNECTION_NAME
```

#### Method B: GCP Console
1. Go to [Cloud SQL Console](https://console.cloud.google.com/sql)
2. Select your database instance
3. Click "Databases" tab
4. Click on your database name
5. Use the SQL editor

#### Method C: gcloud CLI
```bash
# Connect to your Cloud SQL instance
gcloud sql connect INSTANCE_NAME --user=USERNAME --database=DATABASE_NAME
```

### Step 2: Run the Migration Script

#### Option A: Using GCP Console SQL Editor
1. Open the SQL editor in GCP Console
2. Copy the contents of `database_migration_scoping_approvals.sql`
3. Paste into the SQL editor
4. Click "Run"

#### Option B: Using MySQL Client
```bash
# If using Cloud SQL Proxy
mysql -h 127.0.0.1 -u USERNAME -p DATABASE_NAME < database_migration_scoping_approvals.sql

# Or connect and run interactively
mysql -h 127.0.0.1 -u USERNAME -p DATABASE_NAME
# Then paste the SQL commands
```

#### Option C: Using gcloud CLI
```bash
gcloud sql connect INSTANCE_NAME --user=USERNAME --database=DATABASE_NAME < database_migration_scoping_approvals.sql
```

### Step 3: Verify Tables Were Created

Run these queries to verify:

```sql
-- Check if scoping_approvals table exists
SHOW TABLES LIKE 'scoping_approvals';

-- Check if approval_actions table exists
SHOW TABLES LIKE 'approval_actions';

-- View table structure
DESCRIBE scoping_approvals;
DESCRIBE approval_actions;
```

## Migration Script Location

The migration script is located at:
```
database_migration_scoping_approvals.sql
```

## Important Notes

### Database Requirements
- **MySQL 5.7+** or **MariaDB 10.2+** (for JSON support)
- The `scoping_data` and `cost_breakdown` columns use JSON type
- If your database doesn't support JSON, you may need to use TEXT or LONGTEXT instead

### Foreign Key Constraints
The tables have foreign key constraints to:
- `site` table (for site_id)
- `users` table (for deployment_engineer_id, ops_manager_id, reviewed_by, performed_by)

**Ensure these tables exist before running the migration.**

### If JSON Type is Not Supported

If your database version doesn't support JSON type, modify the migration script:

```sql
-- Replace JSON with TEXT or LONGTEXT
scoping_data TEXT NOT NULL,  -- or LONGTEXT
cost_breakdown TEXT NOT NULL,  -- or LONGTEXT
metadata TEXT NULL,  -- or LONGTEXT
```

Then update the models to handle JSON parsing:
- `app/launchpad/launchpad_api/db_models/scoping_approval.py`
- `app/launchpad/launchpad_api/db_models/approval_action.py`

## Troubleshooting

### Error: "Table already exists"
This is normal if tables were already created. The `CREATE TABLE IF NOT EXISTS` statement will skip creation if tables exist.

### Error: "Foreign key constraint fails"
Ensure that:
1. The `site` table exists
2. The `users` table exists
3. You have sample data in these tables (or the foreign keys will fail on inserts)

### Error: "Unknown column type 'JSON'"
Your database version doesn't support JSON. See "If JSON Type is Not Supported" section above.

### Error: "Access denied" or "CREATE command denied"
**This is a permissions issue.** Your database user doesn't have CREATE TABLE permissions.

**Solution Options:**

#### Option 1: Grant Permissions (Requires Admin Access)
Have a database administrator run:
```sql
-- Grant CREATE privilege
GRANT CREATE ON DATABASE_NAME.* TO 'sarthak'@'localhost';

-- Or grant all privileges (if appropriate)
GRANT ALL PRIVILEGES ON DATABASE_NAME.* TO 'sarthak'@'localhost';

-- Apply changes
FLUSH PRIVILEGES;
```

#### Option 2: Run Script as Admin User
Have a database administrator (with CREATE privileges) run the migration script instead.

#### Option 3: Let Application Create Tables (Recommended)
The application automatically creates tables on startup. Simply:
1. Ensure your application has a database user with CREATE privileges
2. Restart the application
3. Tables will be created automatically

**Required Permissions:**
- `CREATE` privilege (to create tables)
- `INDEX` privilege (to create indexes)
- `REFERENCES` privilege (to create foreign keys)
- `ALTER` privilege (to modify tables if needed)

## Verification Checklist

After running the migration:

- [ ] `scoping_approvals` table exists
- [ ] `approval_actions` table exists
- [ ] All indexes are created
- [ ] Foreign key constraints are in place
- [ ] Application can connect to database
- [ ] API endpoints work correctly

## Rollback (If Needed)

If you need to remove the tables:

```sql
-- Drop tables (WARNING: This will delete all data)
DROP TABLE IF EXISTS approval_actions;
DROP TABLE IF EXISTS scoping_approvals;
```

**⚠️ WARNING:** This will permanently delete all scoping approval data!

## Support

If you encounter issues:
1. Check the application logs for database errors
2. Verify database user permissions
3. Ensure database version supports required features
4. Check foreign key constraints are valid

---

**Status**: Ready to run migration script if automatic creation doesn't work.

