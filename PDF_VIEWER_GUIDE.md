# PDF Viewer Feature - User Guide

## Overview
The InsuraIQ app now includes a built-in PDF viewer that allows you to view insurance policy documents directly within the application without needing to download them.

## How to Use the PDF Viewer

### 1. Upload a PDF Policy
- Go to the **Policies** tab
- In the "Upload Policy Documents" section, click "Choose PDF File"
- Select your insurance policy PDF file
- Click "Import PDF" to upload and process the document

### 2. View a PDF
- After uploading, you'll see your policies in the table below
- Look for the **PDF** column in the policies table
- If a policy has an uploaded PDF, you'll see a blue "📄 View PDF" button
- If no PDF is available, you'll see "📄 No PDF" in gray

### 3. PDF Viewer Controls
When you click "View PDF", a full-screen modal will open with these controls:

#### Navigation
- **← Previous**: Go to the previous page
- **→ Next**: Go to the next page  
- **Page indicator**: Shows current page / total pages (e.g., "3 / 15")

#### Zoom Controls
- **- (Minus)**: Zoom out (minimum 50%)
- **+ (Plus)**: Zoom in (maximum 300%)
- **Reset**: Reset zoom to 100%
- **Zoom indicator**: Shows current zoom level (e.g., "150%")

#### Other Controls
- **✕ Close**: Close the PDF viewer
- Click outside the PDF area to close the viewer

## Features

### Security
- Only authenticated users can view PDFs
- Users can only view their own uploaded policy documents
- All PDF access is logged and secured

### File Support
- Supports standard PDF files
- Works with multi-page documents
- Handles various PDF sizes and formats
- Compatible with both English and Hebrew documents

### Performance
- PDFs are stored efficiently on the server
- Fast loading and rendering
- Optimized for large insurance policy documents

## Troubleshooting

### PDF Won't Load
- Check your internet connection
- Refresh the page and try again
- Ensure the PDF was uploaded successfully (check for "View PDF" button)

### Viewer Controls Not Working
- Try refreshing the page
- Ensure JavaScript is enabled in your browser
- Check browser console for any error messages

### PDF Quality Issues
- Use the zoom controls to adjust the view
- Ensure the original PDF file is of good quality
- Try re-uploading the PDF if the quality seems poor

## Technical Details

### Supported Browsers
- Chrome (recommended)
- Firefox
- Safari
- Edge

### File Limitations
- Maximum file size: 50MB per PDF
- Supported format: PDF only
- Multi-page documents supported

### Storage
- PDFs are stored securely on the server
- Files are linked to your specific policy records
- Automatic cleanup of orphaned files

## Tips for Best Experience

1. **Use high-quality PDFs**: Clear, text-based PDFs work better than scanned images
2. **Organize your policies**: Use descriptive policy names when uploading
3. **Regular cleanup**: Delete old or duplicate policy records to keep your dashboard clean
4. **Zoom as needed**: Use zoom controls for better readability of small text
5. **Page navigation**: Use keyboard arrow keys for quick page navigation (if supported by browser)

For additional support or feature requests, please contact your system administrator.
