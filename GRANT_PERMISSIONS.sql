-- Grant Permissions Script for Scoping Approvals Tables
-- Run this script as a database administrator (root or admin user)
-- Replace 'sarthak' with your actual database username
-- Replace 'DATABASE_NAME' with your actual database name

-- Grant CREATE privilege
GRANT CREATE ON DATABASE_NAME.* TO 'sarthak'@'localhost';

-- Grant INDEX privilege (for creating indexes)
GRANT INDEX ON DATABASE_NAME.* TO 'sarthak'@'localhost';

-- Grant ALTER privilege (for modifying tables)
GRANT ALTER ON DATABASE_NAME.* TO 'sarthak'@'localhost';

-- Grant REFERENCES privilege (for foreign keys)
GRANT REFERENCES ON DATABASE_NAME.* TO 'sarthak'@'localhost';

-- Or grant all privileges (if appropriate for your security policy)
-- GRANT ALL PRIVILEGES ON DATABASE_NAME.* TO 'sarthak'@'localhost';

-- Apply changes
FLUSH PRIVILEGES;

-- Verify permissions
SHOW GRANTS FOR 'sarthak'@'localhost';

