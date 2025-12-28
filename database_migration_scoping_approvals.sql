-- Database Migration Script for Scoping Approvals
-- Run this script in your GCP database if tables are not created automatically
-- The application will attempt to create these tables on startup, but for existing databases,
-- you may need to run this script manually.

-- Create scoping_approvals table
CREATE TABLE IF NOT EXISTS scoping_approvals (
  id INT AUTO_INCREMENT PRIMARY KEY,
  site_id INT NOT NULL,
  site_name VARCHAR(255) NOT NULL,
  deployment_engineer_id INT NOT NULL,
  deployment_engineer_name VARCHAR(255) NOT NULL,
  ops_manager_id INT NULL,
  ops_manager_name VARCHAR(255) NULL,
  status VARCHAR(50) NOT NULL DEFAULT 'pending',
  submitted_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  reviewed_at DATETIME NULL,
  reviewed_by INT NULL,
  review_comment TEXT NULL,
  rejection_reason TEXT NULL,
  scoping_data JSON NOT NULL,
  cost_breakdown JSON NOT NULL,
  version INT NOT NULL DEFAULT 1,
  previous_version_id INT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (site_id) REFERENCES site(id) ON DELETE CASCADE,
  FOREIGN KEY (deployment_engineer_id) REFERENCES users(id),
  FOREIGN KEY (ops_manager_id) REFERENCES users(id),
  FOREIGN KEY (reviewed_by) REFERENCES users(id),
  FOREIGN KEY (previous_version_id) REFERENCES scoping_approvals(id),
  INDEX idx_scoping_approvals_site_id (site_id),
  INDEX idx_scoping_approvals_status (status),
  INDEX idx_scoping_approvals_deployment_engineer_id (deployment_engineer_id)
);

-- Create approval_actions table (audit trail)
CREATE TABLE IF NOT EXISTS approval_actions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  approval_id INT NOT NULL,
  action VARCHAR(50) NOT NULL,
  performed_by INT NOT NULL,
  performed_by_role VARCHAR(50) NOT NULL,
  performed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  comment TEXT NULL,
  metadata JSON NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (approval_id) REFERENCES scoping_approvals(id) ON DELETE CASCADE,
  FOREIGN KEY (performed_by) REFERENCES users(id),
  INDEX idx_approval_actions_approval_id (approval_id)
);

-- Verify tables were created
SELECT 'scoping_approvals table created successfully' AS status;
SELECT 'approval_actions table created successfully' AS status;

