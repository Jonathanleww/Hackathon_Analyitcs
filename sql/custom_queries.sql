-- Key Performance Indicators
SELECT 
    'HACKDAVIS 2025 EXECUTIVE SUMMARY' as report_section;

SELECT 
    COUNT(*) as total_registrations,
    SUM(venue_checkin) as actual_attendance,
    ROUND(SUM(venue_checkin) * 100.0 / COUNT(*), 1) as attendance_rate,
    SUM(price) as total_revenue,
    ROUND(SUM(price) / COUNT(*), 0) as avg_revenue_per_attendee,
    COUNT(DISTINCT university) as universities_represented
FROM attendees;

-- Top recruiting targets and engagement
SELECT 
    university,
    COUNT(*) as students,
    ROUND(AVG(total_checkins), 2) as avg_engagement,
    SUM(price) as revenue_generated,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM attendees), 1) as market_share
FROM attendees 
GROUP BY university 
HAVING students >= 5
ORDER BY students DESC;

-- Peak registration periods (identify marketing campaign impact)
SELECT 
    DATE(ticket_created_date) as registration_date,
    COUNT(*) as daily_registrations,
    SUM(COUNT(*)) OVER (ORDER BY DATE(ticket_created_date)) as cumulative_registrations,
    DAYNAME(ticket_created_date) as day_of_week
FROM attendees 
WHERE ticket_created_date IS NOT NULL
GROUP BY DATE(ticket_created_date)
ORDER BY registration_date;

-- Participant engagement segmentation
SELECT 
    CASE 
        WHEN total_checkins >= 4 THEN 'High Engagement (4+ activities)'
        WHEN total_checkins >= 2 THEN 'Medium Engagement (2-3 activities)'
        WHEN total_checkins = 1 THEN 'Low Engagement (1 activity)'
        ELSE 'Registered Only (0 activities)'
    END as engagement_tier,
    COUNT(*) as participants,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM attendees), 1) as percentage,
    ROUND(AVG(price), 2) as avg_ticket_price
FROM attendees 
GROUP BY engagement_tier
ORDER BY AVG(total_checkins) DESC;

-- UC system vs other universities performance
SELECT 
    CASE 
        WHEN university LIKE 'UC %' THEN 'UC System'
        WHEN university LIKE '%.edu' AND university NOT LIKE 'UC %' THEN 'Other Universities'
        ELSE 'Non-University'
    END as institution_type,
    COUNT(*) as attendees,
    ROUND(AVG(total_checkins), 2) as avg_engagement,
    ROUND(AVG(price), 2) as avg_ticket_price,
    SUM(price) as total_revenue
FROM attendees 
GROUP BY institution_type;

-- Food service optimization
SELECT 
    'Saturday Lunch' as meal_service,
    COUNT(*) as planned_attendees,
    SUM(saturday_lunch_checkin) as actual_attendees,
    ROUND(SUM(saturday_lunch_checkin) * 100.0 / COUNT(*), 1) as attendance_rate,
    COUNT(*) - SUM(saturday_lunch_checkin) as potential_waste
FROM attendees
UNION ALL
SELECT 
    'Saturday Dinner',
    COUNT(*),
    SUM(saturday_dinner_checkin),
    ROUND(SUM(saturday_dinner_checkin) * 100.0 / COUNT(*), 1),
    COUNT(*) - SUM(saturday_dinner_checkin)
FROM attendees
UNION ALL
SELECT 
    'Sunday Brunch',
    COUNT(*),
    SUM(sunday_brunch_checkin),
    ROUND(SUM(sunday_brunch_checkin) * 100.0 / COUNT(*), 1),
    COUNT(*) - SUM(sunday_brunch_checkin)
FROM attendees;

-- Early registration vs engagement correlation
SELECT 
    CASE 
        WHEN DATEDIFF('2025-01-25', ticket_created_date) > 60 THEN 'Early Bird (60+ days)'
        WHEN DATEDIFF('2025-01-25', ticket_created_date) > 30 THEN 'Regular (30-60 days)'
        WHEN DATEDIFF('2025-01-25', ticket_created_date) > 7 THEN 'Late (7-30 days)'
        ELSE 'Last Minute (< 7 days)'
    END as registration_timing,
    COUNT(*) as registrations,
    ROUND(AVG(total_checkins), 2) as avg_engagement,
    ROUND(AVG(price), 2) as avg_price_paid
FROM attendees 
WHERE ticket_created_date IS NOT NULL
GROUP BY registration_timing;

-- Identify underperforming vs high-potential schools
SELECT 
    university,
    COUNT(*) as current_participants,
    ROUND(AVG(total_checkins), 2) as engagement_quality,
    CASE 
        WHEN COUNT(*) >= 30 AND AVG(total_checkins) >= 2.0 THEN 'Excellent Pipeline - Maintain'
        WHEN COUNT(*) >= 30 AND AVG(total_checkins) < 2.0 THEN 'High Volume, Low Engagement - Improve Quality'
        WHEN COUNT(*) BETWEEN 10 AND 29 AND AVG(total_checkins) >= 2.0 THEN 'Growth Opportunity - Scale Up'
        WHEN COUNT(*) BETWEEN 5 AND 9 THEN 'Emerging Pipeline - Nurture'
        ELSE 'Untapped Market - Explore'
    END as recruitment_strategy
FROM attendees 
WHERE university != 'Non-University'
GROUP BY university 
HAVING COUNT(*) >= 5
ORDER BY COUNT(*) DESC;