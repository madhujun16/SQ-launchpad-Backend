-- Database Migration Script for Software and Hardware CRUD
-- This script creates the necessary tables for software and hardware management
-- Execute this script in your GCP Cloud SQL instance or MySQL database

-- Note: Replace {database_name} with your actual database name
-- USE {database_name};

-- Create software_categories table
CREATE TABLE IF NOT EXISTS software_categories (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_name (name),
  INDEX idx_is_active (is_active)
);

-- Create hardware_categories table
CREATE TABLE IF NOT EXISTS hardware_categories (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_name (name),
  INDEX idx_is_active (is_active)
);

-- Create software_modules table
CREATE TABLE IF NOT EXISTS software_modules (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT NULL,
  category_id INT NOT NULL,
  license_fee DECIMAL(10, 2) NULL,
  is_active BOOLEAN DEFAULT TRUE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (category_id) REFERENCES software_categories(id) ON DELETE CASCADE,
  INDEX idx_category_id (category_id),
  INDEX idx_is_active (is_active),
  INDEX idx_name (name)
);

-- Create hardware_items table
CREATE TABLE IF NOT EXISTS hardware_items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT NULL,
  category_id INT NOT NULL,
  subcategory VARCHAR(255) NULL,
  manufacturer VARCHAR(255) NULL,
  configuration_notes TEXT NULL,
  unit_cost DECIMAL(10, 2) NOT NULL,
  support_type VARCHAR(255) NULL,
  support_cost DECIMAL(10, 2) NULL,
  is_active BOOLEAN DEFAULT TRUE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  created_by VARCHAR(255) NULL,
  updated_by VARCHAR(255) NULL,
  FOREIGN KEY (category_id) REFERENCES hardware_categories(id) ON DELETE CASCADE,
  INDEX idx_category_id (category_id),
  INDEX idx_is_active (is_active),
  INDEX idx_name (name),
  INDEX idx_manufacturer (manufacturer)
);

-- Create recommendation_rules table (if not already exists)
CREATE TABLE IF NOT EXISTS recommendation_rules (
  id INT AUTO_INCREMENT PRIMARY KEY,
  software_category_id INT NOT NULL,
  hardware_category_id INT NOT NULL,
  is_mandatory BOOLEAN DEFAULT FALSE,
  quantity INT DEFAULT 1,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (software_category_id) REFERENCES software_categories(id) ON DELETE CASCADE,
  FOREIGN KEY (hardware_category_id) REFERENCES hardware_categories(id) ON DELETE CASCADE,
  INDEX idx_software_category_id (software_category_id),
  INDEX idx_hardware_category_id (hardware_category_id)
);

-- Optional: Insert sample data for testing (uncomment if needed)
/*
-- Sample Software Categories
INSERT INTO software_categories (name, description, is_active) VALUES
('POS Systems', 'Point of Sale software solutions', TRUE),
('Inventory Management', 'Inventory tracking and management systems', TRUE),
('Payment Processing', 'Payment gateway and processing software', TRUE)
ON DUPLICATE KEY UPDATE name=name;

-- Sample Hardware Categories
INSERT INTO hardware_categories (name, description, is_active) VALUES
('Tablets', 'Tablet devices for POS and kiosk use', TRUE),
('Printers', 'Receipt and label printers', TRUE),
('Scanners', 'Barcode and QR code scanners', TRUE)
ON DUPLICATE KEY UPDATE name=name;
*/

