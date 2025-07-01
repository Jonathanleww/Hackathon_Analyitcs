import pandas as pd
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import re
import os
from config import DATABASE_CONFIG

def clean_datetime(date_str):
    """Convert datetime string to MySQL format"""
    if pd.isna(date_str) or date_str == '':
        return None
    
    # Remove timezone info (-0800, -0700, etc.)
    cleaned = re.sub(r'\s*-\d{4}$', '', str(date_str))
    
    try:
        # Parse and format for MySQL
        dt = pd.to_datetime(cleaned)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return None

def clean_numeric(value):
    """Clean numeric values"""
    if pd.isna(value) or value == '':
        return None
    # Convert 1.0 to 1, 0.0 to 0 for check-ins
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value

def import_event_data(csv_file_path='data/sample/sample_event_data.csv'):
    """
    Import event registration data from CSV to MySQL database
    
    Args:
        csv_file_path (str): Path to the CSV file containing event data
        
    Returns:
        bool: True if import successful, False otherwise
    """
    
    try:
        # Verify file exists
        if not os.path.exists(csv_file_path):
            print(f"Error: File {csv_file_path} not found!")
            return False
            
        # Read CSV
        print("Reading CSV file...")
        df = pd.read_csv(csv_file_path)
        print(f"Found {len(df)} records")
        
        # Map CSV columns to database columns
        column_mapping = {
            'Number': 'number',
            'Ticket Created Date (-07:00 Pacific Time (US & Canada))': 'ticket_created_date',
            'Ticket Last Updated Date (-07:00 Pacific Time (US & Canada))': 'ticket_last_updated_date',
            'Ticket': 'ticket',
            'Ticket Full Name': 'ticket_full_name',
            'Ticket First Name': 'ticket_first_name',
            'Ticket Last Name': 'ticket_last_name',
            'Ticket Email': 'ticket_email',
            'Ticket Company Name': 'ticket_company_name',
            'Ticket Job Title': 'ticket_job_title',
            'Ticket Phone Number': 'ticket_phone_number',
            'Event': 'event',
            'Void Status': 'void_status',
            'Price': 'price',
            'Discount Status': 'discount_status',
            'Ticket Reference': 'ticket_reference',
            'Tags': 'tags',
            'Unique Ticket URL': 'unique_ticket_url',
            'Unique Order URL': 'unique_order_url',
            'Order Reference': 'order_reference',
            'Order Name': 'order_name',
            'Order Email': 'order_email',
            'Order Phone Number': 'order_phone_number',
            'Order Discount Code': 'order_discount_code',
            'Order IP': 'order_ip',
            'Order Created Date (-07:00 Pacific Time (US & Canada))': 'order_created_date',
            'Order Completed Date (-07:00 Pacific Time (US & Canada))': 'order_completed_date',
            'Source': 'source',
            'Source Type': 'source_type',
            'Check-ins: Venue Check-In List': 'venue_checkin',
            'Check-ins: Saturday Lunch Check-in': 'saturday_lunch_checkin',
            'Check-ins: Sunday Brunch Check-in': 'sunday_brunch_checkin',
            'Check-ins: Saturday Dinner Check-in': 'saturday_dinner_checkin',
            'Check-ins: Sunday Midnight Snack Check-in': 'sunday_midnight_snack_checkin',
            'Check-ins: Mentor Check in': 'mentor_checkin',
            'Check-ins: Volunteer Check in List': 'volunteer_checkin'
        }
        
        # Rename columns
        df.rename(columns=column_mapping, inplace=True)
        
        # FILTER OUT INVALID RECORDS
        print("Filtering out invalid records...")
        initial_count = len(df)
        
        # Remove records with missing email addresses
        df = df[df['ticket_email'].notna() & (df['ticket_email'] != '')]
        
        print(f"Removed {initial_count - len(df)} records with missing emails")
        print(f"Processing {len(df)} valid records")
        
        # Clean datetime columns
        date_columns = ['ticket_created_date', 'ticket_last_updated_date', 'order_created_date', 'order_completed_date']
        for col in date_columns:
            if col in df.columns:
                df[col] = df[col].apply(clean_datetime)
        
        # Clean check-in columns (convert floats to integers)
        checkin_columns = ['venue_checkin', 'saturday_lunch_checkin', 'sunday_brunch_checkin', 
                          'saturday_dinner_checkin', 'mentor_checkin', 'volunteer_checkin']
        for col in checkin_columns:
            if col in df.columns:
                df[col] = df[col].apply(clean_numeric)
        
        # Connect to MySQL using config
        print("Connecting to MySQL...")
        connection = mysql.connector.connect(**DATABASE_CONFIG)
        cursor = connection.cursor()
        
        # Clear existing data
        cursor.execute("TRUNCATE TABLE attendees")
        
        # Prepare the INSERT statement
        db_columns = [
            'number', 'ticket_created_date', 'ticket_last_updated_date', 'ticket',
            'ticket_full_name', 'ticket_first_name', 'ticket_last_name', 'ticket_email',
            'ticket_company_name', 'ticket_job_title', 'ticket_phone_number', 'event',
            'void_status', 'price', 'discount_status', 'ticket_reference', 'tags',
            'unique_ticket_url', 'unique_order_url', 'order_reference', 'order_name',
            'order_email', 'order_phone_number', 'order_discount_code', 'order_ip',
            'order_created_date', 'order_completed_date', 'source', 'source_type',
            'venue_checkin', 'saturday_lunch_checkin', 'sunday_brunch_checkin',
            'saturday_dinner_checkin', 'sunday_midnight_snack_checkin',
            'mentor_checkin', 'volunteer_checkin'
        ]
        
        placeholders = ', '.join(['%s'] * len(db_columns))
        columns = ', '.join(db_columns)
        sql = f"INSERT INTO attendees ({columns}) VALUES ({placeholders})"
        
        # Insert data row by row
        print("Inserting data...")
        inserted_count = 0
        for index, row in df.iterrows():
            # Get values in the correct order
            values = []
            for col in db_columns:
                value = row.get(col, None)
                # Convert empty strings to None (except for required fields like email)
                if pd.isna(value) or value == '':
                    if col == 'ticket_email':
                        # Skip this record if email is empty (shouldn't happen after filtering)
                        print(f"Warning: Empty email at row {index}, skipping...")
                        break
                    values.append(None)
                else:
                    values.append(value)
            else:
                # This else block runs if the for loop completed without break
                cursor.execute(sql, tuple(values))
                inserted_count += 1
                
                if inserted_count % 100 == 0:
                    print(f"Inserted {inserted_count} records...")
        
        # Commit changes
        connection.commit()
        
        # Run data cleaning
        print("Cleaning data...")
        cursor.execute("""
            UPDATE attendees 
            SET university = CASE 
                WHEN ticket_email LIKE '%ucdavis.edu' THEN 'UC Davis'
                WHEN ticket_email LIKE '%berkeley.edu' THEN 'UC Berkeley'
                WHEN ticket_email LIKE '%stanford.edu' THEN 'Stanford'
                WHEN ticket_email LIKE '%.edu' THEN SUBSTRING_INDEX(SUBSTRING_INDEX(ticket_email, '@', -1), '.', -2)
                ELSE 'Non-University'
            END
        """)
        connection.commit()
        
        # Verify
        cursor.execute("SELECT COUNT(*) FROM attendees")
        count = cursor.fetchone()[0]
        print(f"Successfully imported {count} records!")
        
        # Show sample data (anonymized for privacy)
        cursor.execute("SELECT COUNT(*) as total, university, AVG(total_checkins) as avg_engagement FROM attendees GROUP BY university LIMIT 5")
        results = cursor.fetchall()
        print("\nSample university data:")
        for row in results:
            print(f"University: {row[1]}, Count: {row[0]}, Avg Engagement: {row[2]:.2f}")
        
        return True
        
    except Error as e:
        print(f"Database Error: {e}")
        return False
        
    except Exception as e:
        print(f"Error: {e}")
        return False
        
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    print("Event Data Import Tool")
    print("=" * 50)
    print("⚠️  IMPORTANT: This tool processes event registration data.")
    print("   Make sure your CSV file contains participant information.")
    print("   The database will be cleared and repopulated.")
    print()
    
    # Allow user to specify different file
    user_path = input("Enter CSV file path (or press Enter for sample data): ").strip()
    csv_path = user_path if user_path else 'data/sample/sample_event_data.csv'
    
    # Confirm before proceeding
    confirm = input(f"Import data from '{csv_path}'? (y/N): ").strip().lower()
    if confirm == 'y':
        success = import_event_data(csv_path)
        if success:
            print("\n✅ Import completed successfully!")
        else:
            print("\n❌ Import failed. Check the error messages above.")
    else:
        print("Import cancelled.")