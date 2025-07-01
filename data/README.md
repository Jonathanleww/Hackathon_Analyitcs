# Data Directory

## Structure
- `sample/` - Contains sample/demo data for testing the analytics framework
- Your actual event data should be placed here but will be ignored by git

## Usage
1. Place your event CSV file in this directory
2. Update the file path in `import_csv.py` 
3. Run the import script

## Data Format
The CSV should include columns for:
- Registration timestamps
- Participant information  
- Check-in data
- Pricing information

See `sample/sample_event_data.csv` for the expected format.
