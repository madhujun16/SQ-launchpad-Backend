-- Database Migration Script for Procurement Data
-- Run this script in your GCP database if tables are not created automatically
-- The application will attempt to create these tables on startup, but for existing databases,
-- you may need to run this script manually.

-- Create procurement_data table
CREATE TABLE IF NOT EXISTS procurement_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    site_id INT NOT NULL,
    delivery_date DATE NULL,
    delivery_receipt_url VARCHAR(500) NULL,
    summary TEXT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    completed_at DATETIME NULL,
    completed_by INT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (site_id) REFERENCES site(id) ON DELETE CASCADE,
    FOREIGN KEY (completed_by) REFERENCES users(id),
    UNIQUE KEY unique_site_procurement (site_id),
    INDEX idx_procurement_data_site_id (site_id),
    INDEX idx_procurement_data_status (status)
);

-- Verify table was created
SELECT 'procurement_data table created successfully' AS status;

