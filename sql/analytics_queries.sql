-- ============================================
-- HACKDAVIS ANALYTICS DATABASE SCHEMA
-- ============================================

DROP DATABASE IF EXISTS hackdavis_analytics;
CREATE DATABASE hackdavis_analytics;
USE hackdavis_analytics;

-- Main attendees table (matches your CSV structure)
CREATE TABLE attendees (
    number INT PRIMARY KEY,
    ticket_created_date DATETIME,
    ticket_last_updated_date DATETIME,
    ticket VARCHAR(100),
    ticket_full_name VARCHAR(100),
    ticket_first_name VARCHAR(50),
    ticket_last_name VARCHAR(50),
    ticket_email VARCHAR(100) NOT NULL,
    ticket_company_name VARCHAR(100),
    ticket_job_title VARCHAR(100),
    ticket_phone_number VARCHAR(20),
    event VARCHAR(100),
    void_status VARCHAR(20),
    price DECIMAL(10,2),
    discount_status VARCHAR(50),
    ticket_reference VARCHAR(50),
    tags TEXT,
    unique_ticket_url TEXT,
    unique_order_url TEXT,
    order_reference VARCHAR(50),
    order_name VARCHAR(100),
    order_email VARCHAR(100),
    order_phone_number VARCHAR(20),
    order_discount_code VARCHAR(50),
    order_ip VARCHAR(50),
    order_created_date DATETIME,
    order_completed_date DATETIME,
    source VARCHAR(100),
    source_type VARCHAR(50),
    venue_checkin TINYINT(1) DEFAULT 0,
    saturday_lunch_checkin TINYINT(1) DEFAULT 0,
    sunday_brunch_checkin TINYINT(1) DEFAULT 0,
    saturday_dinner_checkin TINYINT(1) DEFAULT 0,
    sunday_midnight_snack_checkin VARCHAR(10),
    mentor_checkin TINYINT(1) DEFAULT 0,
    volunteer_checkin TINYINT(1) DEFAULT 0,
    -- Derived fields
    university VARCHAR(100),
    is_mentor BOOLEAN AS (ticket LIKE '%Mentor%') STORED,
    is_volunteer BOOLEAN AS (ticket LIKE '%Volunteer%') STORED,
    total_checkins INT AS (
        COALESCE(venue_checkin, 0) + 
        COALESCE(saturday_lunch_checkin, 0) + 
        COALESCE(sunday_brunch_checkin, 0) + 
        COALESCE(saturday_dinner_checkin, 0) + 
        COALESCE(mentor_checkin, 0) + 
        COALESCE(volunteer_checkin, 0)
    ) STORED
);

-- Indexes for performance
CREATE INDEX idx_ticket_email ON attendees(ticket_email);
CREATE INDEX idx_ticket_created_date ON attendees(ticket_created_date);
CREATE INDEX idx_ticket ON attendees(ticket);
CREATE INDEX idx_source ON attendees(source);
CREATE INDEX idx_order_created_date ON attendees(order_created_date);
CREATE INDEX idx_void_status ON attendees(void_status);

-- Views for analysis
CREATE VIEW orders_analysis AS
SELECT 
    order_reference as order_id,
    number as attendee_number,
    order_created_date,
    order_completed_date,
    price as total_amount,
    order_discount_code as discount_code,
    source as registration_source,
    source_type,
    CASE 
        WHEN void_status IS NULL OR void_status = '' THEN 'completed'
        ELSE 'void'
    END as payment_status
FROM attendees;

-- Success message
SELECT 'Database schema created successfully!' as status;
sql/02_data_import.sql
sql-- ============================================
-- DATA IMPORT SCRIPT
-- ============================================

-- Method 1: Using LOAD DATA INFILE (if you have file access)
LOAD DATA INFILE '/path/to/your/event_data.csv'
INTO TABLE attendees
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(number, ticket_created_date, ticket_last_updated_date, ticket, 
 ticket_full_name, ticket_first_name, ticket_last_name, ticket_email,
 ticket_company_name, ticket_job_title, ticket_phone_number, event,
 void_status, price, discount_status, ticket_reference, tags,
 unique_ticket_url, unique_order_url, order_reference, order_name,
 order_email, order_phone_number, order_discount_code, order_ip,
 order_created_date, order_completed_date, source, source_type,
 venue_checkin, saturday_lunch_checkin, sunday_brunch_checkin,
 saturday_dinner_checkin, sunday_midnight_snack_checkin,
 mentor_checkin, volunteer_checkin);

-- Method 2: If LOAD DATA doesn't work, use MySQL Workbench Table Data Import Wizard
-- File -> Import -> Table Data Import Wizard -> Select CSV -> Map columns

-- Post-import data cleaning
UPDATE attendees 
SET university = CASE 
    WHEN ticket_email LIKE '%ucdavis.edu' THEN 'UC Davis'
    WHEN ticket_email LIKE '%berkeley.edu' THEN 'UC Berkeley'
    WHEN ticket_email LIKE '%stanford.edu' THEN 'Stanford'
    WHEN ticket_email LIKE '%.edu' THEN SUBSTRING_INDEX(SUBSTRING_INDEX(ticket_email, '@', -1), '.', -2)
    ELSE 'Non-University'
END;

-- Convert check-in fields from float to boolean if needed
UPDATE attendees SET venue_checkin = 1 WHERE venue_checkin > 0;
UPDATE attendees SET saturday_lunch_checkin = 1 WHERE saturday_lunch_checkin > 0;
UPDATE attendees SET sunday_brunch_checkin = 1 WHERE sunday_brunch_checkin > 0;
UPDATE attendees SET saturday_dinner_checkin = 1 WHERE saturday_dinner_checkin > 0;
UPDATE attendees SET mentor_checkin = 1 WHERE mentor_checkin > 0;
UPDATE attendees SET volunteer_checkin = 1 WHERE volunteer_checkin > 0;

-- Verify import
SELECT 
    COUNT(*) as total_records,
    COUNT(CASE WHEN void_status IS NULL THEN 1 END) as valid_records,
    MIN(ticket_created_date) as earliest_registration,
    MAX(ticket_created_date) as latest_registration
FROM attendees;

SELECT 'Data import completed!' as status;