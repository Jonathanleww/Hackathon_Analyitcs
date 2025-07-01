# Hackathon Analytics Framework

A comprehensive analytics framework for hackathons, conferences, and events. Provides registration analysis, engagement tracking, and automated reporting.

## Features
- Registration timeline analysis
- Participant engagement metrics
- University/organization breakdown  
- Food service optimization
- Revenue tracking
- Automated visualizations

## Quick Start
1. `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and configure database
3. `mysql < sql/01_schema.sql`
4. `python import_csv.py`
5. `python create_visualizations.py`

Originally developed for HackDavis 2025.
