-- ============================================
-- CORE BUSINESS ANALYTICS QUERIES
-- ============================================

-- 1. Executive Summary Dashboard
SELECT 
    'HACKDAVIS 2025 EXECUTIVE SUMMARY' as report_title,
    '' as separator;

SELECT 
    'Total Registrations' as metric,
    COUNT(*) as value,
    '' as notes
FROM attendees WHERE void_status IS NULL
UNION ALL
SELECT 
    'Actual Venue Attendance',
    SUM(venue_checkin),
    CONCAT(ROUND(SUM(venue_checkin) * 100.0 / COUNT(*), 1), '% show rate')
FROM attendees WHERE void_status IS NULL
UNION ALL
SELECT 
    'Total Revenue',
    SUM(price),
    CONCAT('$', ROUND(SUM(price) / COUNT(*), 0), ' avg per ticket')
FROM attendees WHERE void_status IS NULL
UNION ALL
SELECT 
    'UC Davis Students',
    SUM(CASE WHEN ticket_email LIKE '%ucdavis.edu' THEN 1 ELSE 0 END),
    CONCAT(ROUND(SUM(CASE WHEN ticket_email LIKE '%ucdavis.edu' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1), '% of total')
FROM attendees WHERE void_status IS NULL;

-- 2. Registration Timeline Analysis
SELECT 
    'REGISTRATION TIMELINE ANALYSIS' as analysis_title;

SELECT 
    DATE(ticket_created_date) as registration_date,
    COUNT(*) as daily_registrations,
    SUM(COUNT(*)) OVER (ORDER BY DATE(ticket_created_date)) as cumulative_registrations,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM attendees WHERE void_status IS NULL), 2) as daily_percentage
FROM attendees 
WHERE ticket_created_date IS NOT NULL AND void_status IS NULL
GROUP BY DATE(ticket_created_date)
ORDER BY registration_date;

-- 3. Revenue Analysis
SELECT 
    'REVENUE ANALYSIS BY SOURCE' as analysis_title;

SELECT 
    source,
    COUNT(*) as registrations,
    SUM(price) as total_revenue,
    ROUND(AVG(price), 2) as avg_ticket_price,
    ROUND(SUM(price) * 100.0 / (SELECT SUM(price) FROM attendees WHERE void_status IS NULL), 2) as revenue_share
FROM attendees
WHERE void_status IS NULL AND source IS NOT NULL
GROUP BY source
ORDER BY total_revenue DESC;

-- 4. Engagement Analysis
SELECT 
    'PARTICIPANT ENGAGEMENT ANALYSIS' as analysis_title;

SELECT 
    engagement_level,
    participant_count,
    ROUND(participant_count * 100.0 / total_participants, 2) as percentage,
    avg_ticket_price
FROM (
    SELECT 
        CASE 
            WHEN total_checkins >= 4 THEN 'High Engagement (4+ meals)'
            WHEN total_checkins >= 2 THEN 'Medium Engagement (2-3 meals)'
            WHEN total_checkins = 1 THEN 'Low Engagement (1 meal)'
            ELSE 'No Meal Participation'
        END as engagement_level,
        COUNT(*) as participant_count,
        ROUND(AVG(price), 2) as avg_ticket_price,
        (SELECT COUNT(*) FROM attendees WHERE void_status IS NULL) as total_participants
    FROM attendees 
    WHERE void_status IS NULL
    GROUP BY engagement_level
) engagement_data
ORDER BY 
    CASE engagement_level
        WHEN 'High Engagement (4+ meals)' THEN 1
        WHEN 'Medium Engagement (2-3 meals)' THEN 2
        WHEN 'Low Engagement (1 meal)' THEN 3
        ELSE 4
    END;

-- 5. Meal Planning Insights
SELECT 
    'MEAL PLANNING OPTIMIZATION' as analysis_title;

SELECT 
    meal_name,
    planned_portions,
    actual_attendance,
    ROUND(actual_attendance * 100.0 / planned_portions, 2) as attendance_rate,
    planned_portions - actual_attendance as waste_estimate
FROM (
    SELECT 'Saturday Lunch' as meal_name, COUNT(*) as planned_portions, SUM(saturday_lunch_checkin) as actual_attendance
    FROM attendees WHERE void_status IS NULL
    UNION ALL
    SELECT 'Saturday Dinner', COUNT(*), SUM(saturday_dinner_checkin)
    FROM attendees WHERE void_status IS NULL
    UNION ALL
    SELECT 'Sunday Brunch', COUNT(*), SUM(sunday_brunch_checkin)
    FROM attendees WHERE void_status IS NULL
) meal_data;

-- 6. University Participation
SELECT 
    'UNIVERSITY PARTICIPATION BREAKDOWN' as analysis_title;

SELECT 
    university,
    COUNT(*) as students,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM attendees WHERE void_status IS NULL), 2) as percentage,
    ROUND(AVG(total_checkins), 2) as avg_engagement,
    SUM(price) as total_revenue
FROM attendees
WHERE void_status IS NULL
GROUP BY university
ORDER BY students DESC;