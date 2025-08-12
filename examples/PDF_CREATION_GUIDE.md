# PDF Creation Guide for InsuraIQ Examples

## Method 1: Using Browser (Easiest)

1. Open any of the HTML files in your web browser:
   - `state_farm_auto_policy.html`
   - `allstate_home_policy.html` 
   - `progressive_commercial_auto.html`

2. Press `Ctrl+P` (or `Cmd+P` on Mac) to print

3. Select "Save as PDF" as the destination

4. Save the PDF files in the examples folder

## Method 2: Using Python Script (Automated)

Save this script as `convert_to_pdf.py` and run it:

```python
import pdfkit
import os

# List of HTML files to convert
html_files = [
    'state_farm_auto_policy.html',
    'allstate_home_policy.html', 
    'progressive_commercial_auto.html'
]

# Convert each HTML file to PDF
for html_file in html_files:
    if os.path.exists(html_file):
        pdf_file = html_file.replace('.html', '.pdf')
        try:
            pdfkit.from_file(html_file, pdf_file)
            print(f"✅ Created: {pdf_file}")
        except Exception as e:
            print(f"❌ Error converting {html_file}: {e}")
    else:
        print(f"❌ File not found: {html_file}")

print("\n🎉 PDF conversion complete!")
```

### To use this script:
1. Install required package: `pip install pdfkit`
2. Install wkhtmltopdf: https://wkhtmltopdf.org/downloads.html
3. Run: `python convert_to_pdf.py`

## Method 3: Online Conversion Tools

Upload the HTML files to any of these free online converters:
- https://html-to-pdf.net/
- https://www.sodapdf.com/html-to-pdf/
- https://smallpdf.com/html-to-pdf

## Method 4: Using Microsoft Word

1. Open Microsoft Word
2. File → Open → Select HTML file
3. File → Save As → Choose PDF format

## What You'll Get

After conversion, you'll have professional-looking PDF files that contain:

### State Farm Auto Policy PDF:
- Policy holder: Michael Thompson
- Monthly premium: $225.00
- Auto insurance for 2021 Honda Accord
- Realistic coverage details and discounts

### Allstate Home Policy PDF:
- Policy holder: Amanda Rodriguez  
- Monthly premium: $140.00
- Homeowners insurance for single family home
- Detailed coverage limits and construction info

### Progressive Commercial Auto PDF:
- Business: Rodriguez Delivery Services LLC
- Monthly premium: $895.00
- Commercial fleet insurance for 3 vehicles
- Business operations and cargo coverage

## Testing PDF Import

Once you have the PDF files:
1. Go to InsuraIQ Policies tab
2. Click "Choose PDF File"
3. Select one of your created PDFs
4. Click "Import PDF"
5. Watch the AI extract policy information!

The PDF import should automatically detect and extract:
- Policy holder names
- Policy numbers  
- Premium amounts
- Coverage limits
- Insurance companies
- Policy dates
- Product types
