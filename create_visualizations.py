import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import mysql.connector
import numpy as np
import warnings
warnings.filterwarnings('ignore')
from config import DATABASE_CONFIG

# Non-interactive backend
import matplotlib
matplotlib.use('Agg')

# Database connection
from config import DATABASE_CONFIG
config = DATABASE_CONFIG

def get_data(query):
    connection = mysql.connector.connect(**config)
    df = pd.read_sql(query, connection)
    connection.close()
    return df

def save_chart(filename, title="Chart"):
    plt.tight_layout()
    plt.savefig(f'results/charts/{filename}', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ {title} saved")

def chart1_university_breakdown():
    """University participation analysis"""
    query = """
    SELECT 
        CASE 
            WHEN university = 'UC Davis' THEN 'UC Davis'
            WHEN university LIKE '%uc%' OR university LIKE 'UC %' THEN 'Other UC Schools'
            WHEN university = 'sjsu.edu' THEN 'San Jose State'
            WHEN university LIKE '%csu%' OR university IN ('sfsu.edu', 'csus.edu') THEN 'Other CSU Schools'
            WHEN university = 'Stanford' THEN 'Stanford'
            WHEN university = 'Non-University' THEN 'General Public'
            ELSE 'Other Universities'
        END as school_type,
        COUNT(*) as attendees,
        ROUND(AVG(total_checkins), 2) as avg_engagement
    FROM attendees GROUP BY school_type ORDER BY attendees DESC;
    """
    
    df = get_data(query)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Pie chart
    colors = ['#2E8B57', '#4682B4', '#DAA520', '#CD5C5C', '#9370DB', '#FF6347', '#20B2AA']
    ax1.pie(df['attendees'], labels=df['school_type'], autopct='%1.1f%%', 
           colors=colors, startangle=90)
    ax1.set_title('University Participation (n=1,171)', fontsize=14, fontweight='bold')
    
    # Engagement bars
    bars = ax2.bar(df['school_type'], df['avg_engagement'], color=colors)
    ax2.set_title('Average Engagement by School Type', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Avg Check-ins')
    ax2.tick_params(axis='x', rotation=45)
    
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                f'{height:.1f}', ha='center', va='bottom', fontweight='bold')
    
    save_chart('1_university_breakdown.png', 'University breakdown')

def chart2_engagement_distribution():
    """Engagement tier analysis - IMPROVED VERSION"""
    query = """
    SELECT 
        CASE 
            WHEN total_checkins >= 4 THEN 'High (4+ meals)'
            WHEN total_checkins >= 2 THEN 'Medium (2-3 meals)'
            WHEN total_checkins = 1 THEN 'Low (1 meal)'
            ELSE 'None (0 meals)'
        END as engagement_level,
        COUNT(*) as participants,
        ROUND(AVG(price), 2) as avg_price
    FROM attendees GROUP BY engagement_level
    ORDER BY AVG(total_checkins) DESC;
    """
    
    df = get_data(query)
    
    # SINGLE HORIZONTAL CHART - better aspect ratio
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))  # Better proportions
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    
    # Colors
    colors = ['#2E8B57', '#4682B4', '#DAA520', '#CD5C5C']
    
    # Horizontal bars (easier to read)
    bars = ax.barh(df['engagement_level'], df['participants'], 
                   color=colors[:len(df)], height=0.6, alpha=0.8)
    
    # Large, readable title and labels
    ax.set_title('HackDavis 2025: Participant Engagement Distribution', 
                 fontsize=18, fontweight='bold', pad=25, color='black')
    ax.set_xlabel('Number of Participants', fontsize=14, fontweight='bold', color='black')
    
    # Add data labels
    total = df['participants'].sum()
    for i, (bar, count, price) in enumerate(zip(bars, df['participants'], df['avg_price'])):
        width = bar.get_width()
        percentage = count / total * 100
        
        # Count inside bar (white text)
        ax.text(width/2, bar.get_y() + bar.get_height()/2.,
                f'{count:,}', ha='center', va='center', 
                fontsize=14, fontweight='bold', color='white')
        
        # Percentage and price outside bar (black text)
        ax.text(width + 30, bar.get_y() + bar.get_height()/2.,
                f'{percentage:.1f}% (Avg: ${price:.0f})', ha='left', va='center', 
                fontsize=12, fontweight='bold', color='black')
    
    # Style improvements
    ax.set_xlim(0, max(df['participants']) * 1.3)
    ax.tick_params(axis='y', labelsize=12, colors='black')
    ax.tick_params(axis='x', labelsize=11, colors='black')
    
    # Clean spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('gray')
    ax.spines['left'].set_color('gray')
    
    # Light grid
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    
    # Add insight box
    high_medium = df['participants'].head(2).sum()
    engagement_rate = high_medium / total * 100
    
    ax.text(0.98, 0.02, f'Key Insight: {engagement_rate:.1f}% show medium-high engagement', 
            transform=ax.transAxes, fontsize=11, ha='right', va='bottom',
            bbox=dict(boxstyle="round,pad=0.4", facecolor="lightblue", alpha=0.8),
            fontweight='bold')
    
    save_chart('2_engagement_distribution.png', 'Engagement distribution')

def chart3_registration_timeline():
    """Registration pattern over time"""
    query = """
    SELECT 
        DATE(ticket_created_date) as date,
        COUNT(*) as daily_regs,
        SUM(COUNT(*)) OVER (ORDER BY DATE(ticket_created_date)) as cumulative
    FROM attendees 
    WHERE ticket_created_date IS NOT NULL
    GROUP BY DATE(ticket_created_date) ORDER BY date;
    """
    
    df = get_data(query)
    df['date'] = pd.to_datetime(df['date'])
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10))
    
    # Daily registrations
    ax1.bar(df['date'], df['daily_regs'], color='skyblue', alpha=0.7)
    ax1.set_title('Daily Registration Pattern', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Daily Registrations')
    
    # Cumulative
    ax2.plot(df['date'], df['cumulative'], color='darkgreen', linewidth=3, marker='o')
    ax2.fill_between(df['date'], df['cumulative'], alpha=0.3, color='lightgreen')
    ax2.set_title('Cumulative Registration Growth', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Total Registrations')
    ax2.grid(True, alpha=0.3)
    
    save_chart('3_registration_timeline.png', 'Registration timeline')

def chart4_geographic_analysis():
    """Geographic distribution"""
    query = """
    SELECT 
        CASE 
            WHEN university IN ('UC Davis', 'UC Berkeley', 'sjsu.edu', 'Stanford') THEN 'Bay Area/Sac'
            WHEN university LIKE '%uc%' OR university LIKE '%csu%' THEN 'Other California'
            WHEN university LIKE '%.edu' THEN 'Out-of-State'
            ELSE 'General Public'
        END as region,
        COUNT(*) as attendees,
        ROUND(AVG(total_checkins), 2) as engagement
    FROM attendees GROUP BY region ORDER BY attendees DESC;
    """
    
    df = get_data(query)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Regional distribution
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
    ax1.pie(df['attendees'], labels=df['region'], autopct='%1.1f%%', 
           colors=colors, startangle=90)
    ax1.set_title('Geographic Distribution', fontsize=14, fontweight='bold')
    
    # Engagement by region
    bars = ax2.bar(df['region'], df['engagement'], color=colors)
    ax2.set_title('Engagement by Region', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Avg Check-ins')
    ax2.tick_params(axis='x', rotation=45)
    
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                f'{height:.2f}', ha='center', va='bottom', fontweight='bold')
    
    save_chart('4_geographic_analysis.png', 'Geographic analysis')

def chart5_meal_analysis():
    """Meal attendance and waste analysis"""
    query = """
    SELECT 
        'Sat Lunch' as meal, SUM(saturday_lunch_checkin) as attended,
        COUNT(*) - SUM(saturday_lunch_checkin) as waste,
        ROUND(SUM(saturday_lunch_checkin) * 100.0 / COUNT(*), 1) as rate
    FROM attendees
    UNION ALL
    SELECT 'Sat Dinner', SUM(saturday_dinner_checkin), 
           COUNT(*) - SUM(saturday_dinner_checkin),
           ROUND(SUM(saturday_dinner_checkin) * 100.0 / COUNT(*), 1) FROM attendees
    UNION ALL
    SELECT 'Sun Brunch', SUM(sunday_brunch_checkin),
           COUNT(*) - SUM(sunday_brunch_checkin),
           ROUND(SUM(sunday_brunch_checkin) * 100.0 / COUNT(*), 1) FROM attendees;
    """
    
    df = get_data(query)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Attendance rates
    colors = ['#FF9999', '#66B2FF', '#99FF99']
    bars1 = ax1.bar(df['meal'], df['rate'], color=colors)
    ax1.set_title('Meal Attendance Rates', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Attendance Rate (%)')
    ax1.set_ylim(0, 100)
    
    for bar, rate in zip(bars1, df['rate']):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 2,
                f'{rate}%', ha='center', va='bottom', fontweight='bold')
    
    # Waste analysis
    x = np.arange(len(df))
    width = 0.35
    ax2.bar(x - width/2, df['attended'], width, label='Attended', color=colors, alpha=0.8)
    ax2.bar(x + width/2, df['waste'], width, label='Waste', color='red', alpha=0.6)
    ax2.set_title('Attendance vs Food Waste', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Number of Portions')
    ax2.set_xticks(x)
    ax2.set_xticklabels(df['meal'])
    ax2.legend()
    
    save_chart('5_meal_analysis.png', 'Meal analysis')

def chart6_top_schools():
    """Top performing schools"""
    query = """
    SELECT university, COUNT(*) as attendees, 
           ROUND(AVG(total_checkins), 2) as engagement,
           SUM(price) as revenue
    FROM attendees 
    WHERE university != 'Non-University'
    GROUP BY university HAVING attendees >= 8
    ORDER BY attendees DESC LIMIT 12;
    """
    
    df = get_data(query)
    df['short_name'] = df['university'].str.replace('.edu', '').str.replace('csu', 'CSU').str.title()
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
    
    # Top schools by attendance
    bars1 = ax1.barh(df['short_name'], df['attendees'], color='lightblue')
    ax1.set_title('Top Schools by Attendance', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Number of Attendees')
    
    for i, bar in enumerate(bars1):
        width = bar.get_width()
        ax1.text(width + 2, bar.get_y() + bar.get_height()/2.,
                f'{int(width)}', ha='left', va='center', fontweight='bold')
    
    # Performance matrix
    ax2.scatter(df['attendees'], df['engagement'], s=df['revenue']/20, 
               alpha=0.6, color='purple', edgecolors='black')
    ax2.set_title('Performance Matrix (Bubble = Revenue)', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Attendees')
    ax2.set_ylabel('Avg Engagement')
    ax2.grid(True, alpha=0.3)
    
    for i, name in enumerate(df['short_name']):
        ax2.annotate(name[:8], (df['attendees'].iloc[i], df['engagement'].iloc[i]),
                    xytext=(5, 5), textcoords='offset points', fontsize=9)
    
    save_chart('6_top_schools.png', 'Top schools analysis')

def chart7_executive_dashboard():
    """Key metrics dashboard"""
    query = """
    SELECT COUNT(*) as total_reg, SUM(venue_checkin) as attendance,
           ROUND(SUM(venue_checkin) * 100.0 / COUNT(*), 1) as attend_rate,
           SUM(price) as revenue, COUNT(DISTINCT university) as universities,
           ROUND(AVG(total_checkins), 2) as avg_engagement
    FROM attendees;
    """
    
    metrics = get_data(query).iloc[0]
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('HackDavis 2025 Executive Dashboard', fontsize=20, fontweight='bold')
    
    # Flatten axes for easier indexing
    axes = axes.flatten()
    
    metrics_data = [
        (f"{int(metrics['total_reg']):,}", 'Total\nRegistrations', '#2E8B57'),
        (f"{int(metrics['attendance']):,}", 'Actual\nAttendance', '#4682B4'),
        (f"{metrics['attend_rate']}%", 'Attendance\nRate', '#DAA520'),
        (f"${metrics['revenue']:,.0f}", 'Total\nRevenue', '#CD5C5C'),
        (f"{int(metrics['universities'])}", 'Universities\nRepresented', '#9370DB'),
        (f"{metrics['avg_engagement']}", 'Average\nEngagement', '#FF6347')
    ]
    
    for i, (value, label, color) in enumerate(metrics_data):
        ax = axes[i]
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        # Create metric card
        ax.add_patch(plt.Rectangle((0.1, 0.3), 0.8, 0.4, 
                                  facecolor=color, alpha=0.3, edgecolor=color, linewidth=2))
        ax.text(0.5, 0.6, value, ha='center', va='center', 
               fontsize=28, fontweight='bold', color=color)
        ax.text(0.5, 0.15, label, ha='center', va='center', 
               fontsize=12, fontweight='bold')
    
    save_chart('7_executive_dashboard.png', 'Executive dashboard')

def main():
    print("🎨 Creating HackDavis Analytics - All 7 Charts")
    print("=" * 50)
    
    import os
    os.makedirs('results/charts', exist_ok=True)
    
    chart1_university_breakdown()
    chart2_engagement_distribution()
    chart3_registration_timeline()
    chart4_geographic_analysis()
    chart5_meal_analysis()
    chart6_top_schools()
    chart7_executive_dashboard()
    
    print("\n🎉 All 7 charts completed!")
    print("📁 Saved in: results/charts/")

if __name__ == "__main__":
    main()