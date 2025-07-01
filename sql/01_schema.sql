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