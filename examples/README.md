# InsuraIQ Example Files

This folder contains sample insurance policy files that you can use to test the import functionality of InsuraIQ.

## CSV Files

### sample_policies_1.csv
Contains 5 common insurance policies:
- Auto Insurance (Allstate, Progressive, GEICO)
- Home Insurance (State Farm)
- Renters Insurance (Liberty Mutual)

### sample_policies_2.csv
Contains 5 health and business insurance policies:
- Health Insurance (Blue Cross Blue Shield, Aetna)
- Life Insurance (MetLife, Prudential)
- Business Insurance (Travelers)

### sample_policies_3.csv
Contains 5 specialty insurance policies:
- Motorcycle Insurance (Nationwide)
- Umbrella Insurance (USAA)
- Boat Insurance (Farmers)
- Pet Insurance (Hartford)
- Jewelry Insurance (Chubb)

## Text Files (for PDF Import Testing)

These files simulate the content that would be extracted from PDF policy documents:

### state_farm_auto_policy.txt
- State Farm auto insurance policy
- Policy holder: Michael Thompson
- Monthly premium: $225.00
- Vehicle: 2021 Honda Accord

### allstate_home_policy.txt
- Allstate homeowners insurance
- Policy holder: Amanda Rodriguez
- Monthly premium: $140.00
- Property: Single family home

### bcbs_health_policy.txt
- Blue Cross Blue Shield health insurance
- Policy holder: Dr. James Patterson
- Monthly premium: $485.00
- Plan: BlueCare PPO Plus with dental

### progressive_commercial_auto.txt
- Progressive commercial auto insurance
- Business: Rodriguez Delivery Services LLC
- Monthly premium: $895.00
- Fleet: 3 commercial vehicles

### metlife_term_life.txt
- MetLife term life insurance
- Policy holder: Sarah Chen
- Monthly premium: $95.00
- Coverage: $500,000 death benefit

### lemonade_renters_policy.txt
- Modern app-based renters insurance
- Policy holder: Emma Thompson
- Monthly premium: $32.00
- Coverage: NYC apartment

## HTML Files (for PDF Creation)

Professional-looking HTML policy documents that you can convert to PDF:

### state_farm_auto_policy.html
- Formatted State Farm auto insurance declaration page
- Ready to convert to PDF using browser Print function

### allstate_home_policy.html  
- Professional Allstate homeowners declaration page
- Includes detailed coverage tables and property information

### progressive_commercial_auto.html
- Commercial auto policy certificate
- Multi-vehicle fleet with business details

## Creating PDF Files

### Quick Method (Using Browser):
1. Run `create_pdfs.bat` (Windows) or open HTML files manually
2. Each file will open in your browser
3. Press `Ctrl+P` and select "Save as PDF"
4. Save with `.pdf` extension in the examples folder

### Automated Method:
1. Install Python packages: `pip install weasyprint` or `pip install pdfkit`
2. Run: `python create_pdfs.py`
3. PDFs will be automatically generated

### Alternative Methods:
- Use Microsoft Word (Open HTML → Save as PDF)
- Use online converters (see `PDF_CREATION_GUIDE.md`)
- Use any PDF printer software

### bcbs_health_policy.txt
- Blue Cross Blue Shield health insurance
- Policy holder: Dr. James Patterson
- Monthly premium: $485.00
- Plan: BlueCare PPO Plus with dental

### progressive_commercial_auto.txt
- Progressive commercial auto insurance
- Business: Rodriguez Delivery Services LLC
- Monthly premium: $895.00
- Fleet: 3 commercial vehicles

### metlife_term_life.txt
- MetLife term life insurance
- Policy holder: Sarah Chen
- Monthly premium: $95.00
- Coverage: $500,000 death benefit

## How to Use

1. **CSV Import**: 
   - Go to the Policies tab in InsuraIQ
   - Click "Choose CSV File" and select one of the CSV files
   - Click "Upload CSV" to import multiple policies at once

2. **PDF Import** (using text files):
   - Go to the Policies tab in InsuraIQ
   - Click "Choose PDF File" and select one of the .txt files
   - The system will extract policy information and create a new policy record
   - Note: You may need to rename .txt files to .pdf if the system requires it

## Expected Results

After importing these files, you should see:
- Multiple insurance policies in your dashboard
- Various insurance companies and policy types
- Different premium amounts and coverage limits
- Realistic policy numbers and dates
- Mix of personal and commercial insurance policies

This will give you a comprehensive dataset to test all the features of InsuraIQ including:
- Policy comparison
- Recommendations engine
- Quote generation
- Historical tracking
