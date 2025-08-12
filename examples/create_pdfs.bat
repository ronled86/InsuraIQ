@echo off
echo.
echo ========================================
echo  InsuraIQ PDF Creation Helper
echo ========================================
echo.
echo This script will open the HTML policy files in your default browser
echo so you can easily convert them to PDF using Print to PDF.
echo.
echo Instructions:
echo 1. Each HTML file will open in your browser
echo 2. Press Ctrl+P when the page loads
echo 3. Select "Save as PDF" 
echo 4. Save in this same folder with .pdf extension
echo.
pause

echo.
echo Opening State Farm Auto Policy...
start "" "state_farm_auto_policy.html"
echo Press Ctrl+P and save as: state_farm_auto_policy.pdf
pause

echo.
echo Opening Allstate Home Policy...
start "" "allstate_home_policy.html"
echo Press Ctrl+P and save as: allstate_home_policy.pdf
pause

echo.
echo Opening Progressive Commercial Auto Policy...
start "" "progressive_commercial_auto.html"
echo Press Ctrl+P and save as: progressive_commercial_auto.pdf
pause

echo.
echo ========================================
echo PDF creation complete!
echo.
echo You should now have these PDF files:
echo - state_farm_auto_policy.pdf
echo - allstate_home_policy.pdf
echo - progressive_commercial_auto.pdf
echo.
echo Next steps:
echo 1. Open InsuraIQ at http://localhost:5174
echo 2. Go to Policies tab
echo 3. Use "Choose PDF File" to select a PDF
echo 4. Click "Import PDF" to test the extraction
echo ========================================
pause
