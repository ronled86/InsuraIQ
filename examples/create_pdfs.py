#!/usr/bin/env python3
"""
PDF Generator for InsuraIQ Examples
This script converts HTML policy documents to PDF format for testing the PDF import functionality.
"""

import os
import sys
from pathlib import Path

def convert_with_weasyprint():
    """Convert HTML to PDF using WeasyPrint (recommended)"""
    try:
        from weasyprint import HTML
        
        html_files = [
            'state_farm_auto_policy.html',
            'allstate_home_policy.html', 
            'progressive_commercial_auto.html'
        ]
        
        print("🔄 Converting HTML files to PDF using WeasyPrint...")
        
        for html_file in html_files:
            if os.path.exists(html_file):
                pdf_file = html_file.replace('.html', '.pdf')
                try:
                    HTML(filename=html_file).write_pdf(pdf_file)
                    print(f"✅ Created: {pdf_file}")
                except Exception as e:
                    print(f"❌ Error converting {html_file}: {e}")
            else:
                print(f"❌ File not found: {html_file}")
                
        return True
        
    except ImportError:
        print("❌ WeasyPrint not installed. Install with: pip install weasyprint")
        return False

def convert_with_pdfkit():
    """Convert HTML to PDF using pdfkit (requires wkhtmltopdf)"""
    try:
        import pdfkit
        
        html_files = [
            'state_farm_auto_policy.html',
            'allstate_home_policy.html', 
            'progressive_commercial_auto.html'
        ]
        
        print("🔄 Converting HTML files to PDF using pdfkit...")
        
        # Configure pdfkit options for better output
        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'no-outline': None
        }
        
        for html_file in html_files:
            if os.path.exists(html_file):
                pdf_file = html_file.replace('.html', '.pdf')
                try:
                    pdfkit.from_file(html_file, pdf_file, options=options)
                    print(f"✅ Created: {pdf_file}")
                except Exception as e:
                    print(f"❌ Error converting {html_file}: {e}")
            else:
                print(f"❌ File not found: {html_file}")
                
        return True
        
    except ImportError:
        print("❌ pdfkit not installed. Install with: pip install pdfkit")
        print("   Also need wkhtmltopdf: https://wkhtmltopdf.org/downloads.html")
        return False

def print_manual_instructions():
    """Print manual conversion instructions"""
    print("\n📋 MANUAL CONVERSION INSTRUCTIONS:")
    print("=" * 50)
    print("Since automatic conversion tools aren't available, here's how to create PDFs manually:")
    print()
    print("Method 1 - Using Web Browser (Easiest):")
    print("1. Open each HTML file in your web browser")
    print("2. Press Ctrl+P (or Cmd+P on Mac)")
    print("3. Select 'Save as PDF' as destination")
    print("4. Save with the same name but .pdf extension")
    print()
    print("Method 2 - Using Microsoft Word:")
    print("1. Open Microsoft Word")
    print("2. File → Open → Select HTML file")
    print("3. File → Save As → Choose PDF format")
    print()
    print("Method 3 - Online Converters:")
    print("• https://html-to-pdf.net/")
    print("• https://www.sodapdf.com/html-to-pdf/")
    print("• https://smallpdf.com/html-to-pdf/")
    print()
    print("HTML files ready for conversion:")
    for html_file in ['state_farm_auto_policy.html', 'allstate_home_policy.html', 'progressive_commercial_auto.html']:
        if os.path.exists(html_file):
            print(f"✅ {html_file}")
        else:
            print(f"❌ {html_file} (not found)")

def main():
    print("🚀 InsuraIQ PDF Generator")
    print("=" * 30)
    
    # Change to the examples directory
    examples_dir = Path(__file__).parent
    os.chdir(examples_dir)
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Try different conversion methods
    success = False
    
    # Try WeasyPrint first (better CSS support)
    if not success:
        success = convert_with_weasyprint()
    
    # Try pdfkit as fallback
    if not success:
        success = convert_with_pdfkit()
    
    # If both fail, show manual instructions
    if not success:
        print_manual_instructions()
    else:
        print("\n🎉 PDF conversion complete!")
        print("\nYou can now test PDF import in InsuraIQ:")
        print("1. Go to the Policies tab")
        print("2. Click 'Choose PDF File'")
        print("3. Select one of the generated PDF files")
        print("4. Click 'Import PDF'")
        print("5. Watch the AI extract policy information!")

if __name__ == "__main__":
    main()
