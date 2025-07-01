-- ============================================
-- CUSTOM EXPLORATION QUERIES
-- Add your own queries here for specific investigations
-- ============================================

-- Template for new queries
/*
-- Query Name: [Describe what this analyzes]
-- Business Question: [What business question does this answer?]
-- Expected Impact: [How will this insight help HackDavis?]

SELECT 
    -- Your query here
;
*/

-- Example Custom Query 1: Price Sensitivity Analysis
-- Business Question: What's the optimal ticket price for maximum engagement?
SELECT 
    price_range,
    COUNT(*) as registrations,
    ROUND(AVG(total_checkins), 2) as avg_engagement,
    SUM(price) as revenue
FROM (
    SELECT *,
        CASE 
            WHEN price = 0 THEN 'Free'
            WHEN price <= 25 THEN '$1-25'
            WHEN price <= 50 THEN '$26-50'
            WHEN price <= 75 THEN '$51-75'
            ELSE '$76+'
        END as price_range
    FROM attendees 
    WHERE void_status IS NULL
) price_analysis
GROUP BY price_range
ORDER BY avg_engagement DESC;

-- Example Custom Query 2: Registration Timing vs Engagement
-- Business Question: Do early registrants engage more than last-minute ones?
SELECT 
    registration_timing,
    COUNT(*) as registrations,
    ROUND(AVG(total_checkins), 2) as avg_engagement,
    ROUND(AVG(price), 2) as avg_price
FROM (
    SELECT *,
        CASE 
            WHEN DATEDIFF('2025-01-25', ticket_created_date) > 60 THEN 'Super Early (60+ days)'
            WHEN DATEDIFF('2025-01-25', ticket_created_date) > 30 THEN 'Early (30-60 days)'
            WHEN DATEDIFF('2025-01-25', ticket_created_date) > 7 THEN 'Regular (7-30 days)'
            WHEN DATEDIFF('2025-01-25', ticket_created_date) > 1 THEN 'Last Week'
            ELSE 'Last Minute'
        END as registration_timing
    FROM attendees 
    WHERE ticket_created_date IS NOT NULL AND void_status IS NULL
) timing_analysis
GROUP BY registration_timing
ORDER BY avg_engagement DESC;

--Registration categories Early-Bird -> Last Minute count

SELECT 
    timing_categories.category as registration_timing,
    COALESCE(COUNT(a.ticket_created_date), 0) as registrations,
    ROUND(AVG(a.total_checkins), 2) as avg_engagement,
    ROUND(AVG(a.price), 2) as avg_price_paid
FROM (
    SELECT 'Early Bird (60+ days)' as category, 1 as sort_order
    UNION SELECT 'Regular (30-60 days)', 2
    UNION SELECT 'Late (7-30 days)', 3
    UNION SELECT 'Last Minute (< 7 days)', 4
) timing_categories
LEFT JOIN attendees a ON 
    timing_categories.category = CASE 
        WHEN DATEDIFF(a.ticket_created_date, '2025-01-25') > 60 THEN 'Early Bird (60+ days)'
        WHEN DATEDIFF(a.ticket_created_date, '2025-01-25') > 30 THEN 'Regular (30-60 days)'
        WHEN DATEDIFF(a.ticket_created_date, '2025-01-25') > 7 THEN 'Late (7-30 days)'
        ELSE 'Last Minute (< 7 days)'
    END
    AND a.ticket_created_date IS NOT NULL
GROUP BY timing_categories.category, timing_categories.sort_order
ORDER BY timing_categories.sort_order;