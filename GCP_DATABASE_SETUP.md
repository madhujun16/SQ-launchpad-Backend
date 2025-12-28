# GCP Database Setup Instructions

This document provides instructions for setting up the database tables required for Software and Hardware CRUD operations in Google Cloud Platform.

## Prerequisites

1. A GCP Cloud SQL instance (MySQL) or access to your MySQL database
2. Appropriate database credentials and permissions
3. `gcloud` CLI installed and configured (optional, for Cloud SQL)

## Option 1: Using gcloud CLI (Recommended for Cloud SQL)

### Step 1: Connect to your Cloud SQL instance

```bash
# Replace with your instance connection name
gcloud sql connect YOUR_INSTANCE_NAME --user=YOUR_USERNAME
```

### Step 2: Select your database

```sql
USE your_database_name;
```

### Step 3: Run the migration script

```bash
# From your local machine, run:
gcloud sql connect YOUR_INSTANCE_NAME --user=YOUR_USERNAME < database_migration_software_hardware.sql
```

Or copy and paste the contents of `database_migration_software_hardware.sql` into the SQL prompt.

## Option 2: Using Cloud SQL Proxy

### Step 1: Start Cloud SQL Proxy

```bash
./cloud_sql_proxy -instances=PROJECT_ID:REGION:INSTANCE_NAME=tcp:3306
```

### Step 2: Connect using MySQL client

```bash
mysql -h 127.0.0.1 -u YOUR_USERNAME -p your_database_name
```

### Step 3: Run the migration script

```bash
mysql -h 127.0.0.1 -u YOUR_USERNAME -p your_database_name < database_migration_software_hardware.sql
```

## Option 3: Using Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **SQL** > **Databases**
3. Select your Cloud SQL instance
4. Click on **Databases** tab
5. Select your database
6. Click on **SQL** tab
7. Copy and paste the contents of `database_migration_software_hardware.sql`
8. Click **Run**

## Option 4: Direct MySQL Connection

If you have direct access to your MySQL database:

```bash
mysql -h YOUR_HOST -u YOUR_USERNAME -p YOUR_DATABASE < database_migration_software_hardware.sql
```

## Verification

After running the migration, verify the tables were created:

```sql
-- Check if tables exist
SHOW TABLES LIKE '%software%';
SHOW TABLES LIKE '%hardware%';

-- Verify table structure
DESCRIBE software_categories;
DESCRIBE hardware_categories;
DESCRIBE software_modules;
DESCRIBE hardware_items;
DESCRIBE recommendation_rules;

-- Check indexes
SHOW INDEX FROM software_modules;
SHOW INDEX FROM hardware_items;
```

## Tables Created

The migration script creates the following tables:

1. **software_categories** - Stores software category information
2. **hardware_categories** - Stores hardware category information
3. **software_modules** - Stores software module/application details
4. **hardware_items** - Stores hardware item/product details
5. **recommendation_rules** - Stores rules linking software and hardware categories

## Important Notes

- The script uses `CREATE TABLE IF NOT EXISTS`, so it's safe to run multiple times
- Foreign key constraints ensure data integrity
- Indexes are created for better query performance
- All tables include `created_at` and `updated_at` timestamps
- The `is_active` field allows soft deletion/archiving

## Troubleshooting

### Error: Access Denied
- Ensure your database user has CREATE TABLE permissions
- Check that you're connected to the correct database

### Error: Foreign Key Constraint
- Make sure parent tables (categories) are created before child tables (modules/items)
- The script creates tables in the correct order, but if running manually, follow the order in the script

### Error: Table Already Exists
- This is normal if tables already exist. The script uses `IF NOT EXISTS` so it won't fail
- If you need to recreate tables, drop them first (be careful with production data!)

## Next Steps

After running the migration:

1. Verify all tables were created successfully
2. Test the API endpoints to ensure they work correctly
3. Optionally insert sample data for testing (see commented section in migration script)

## Support

If you encounter issues:
1. Check the GCP Cloud SQL logs
2. Verify your database connection settings
3. Ensure all required permissions are granted
4. Review the error messages for specific guidance

