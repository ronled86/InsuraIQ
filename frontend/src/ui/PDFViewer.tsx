import React, { useState, useMemo } from 'react'
import { Document, Page, pdfjs } from 'react-pdf'
import 'react-pdf/dist/Page/AnnotationLayer.css'
import 'react-pdf/dist/Page/TextLayer.css'

// Configure PDF.js properly without worker
pdfjs.GlobalWorkerOptions.workerSrc = ''

interface PDFViewerProps {
  policyId: number
  filename?: string
  apiBase: string
  token: string
  onClose: () => void
}

export function PDFViewer({ policyId, filename, apiBase, token, onClose }: PDFViewerProps) {
  const [numPages, setNumPages] = useState<number | null>(null)
  const [pageNumber, setPageNumber] = useState(1)
  const [scale, setScale] = useState(1.0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const pdfUrl = `${apiBase}/policies/${policyId}/pdf`

  const documentOptions = useMemo(() => ({
    httpHeaders: {
      'Authorization': `Bearer ${token}`
    }
  }), [token])

  function onDocumentLoadSuccess({ numPages }: { numPages: number }) {
    setNumPages(numPages)
    setLoading(false)
    setError(null)
  }

  function onDocumentLoadError(error: Error) {
    console.error('Error loading PDF:', error)
    let errorMessage = 'Failed to load PDF'
    
    if (error.message.includes('worker')) {
      errorMessage = 'PDF worker configuration issue. Please refresh the page.'
    } else if (error.message.includes('CORS')) {
      errorMessage = 'PDF loading blocked by browser security. Please check server configuration.'
    } else if (error.message.includes('404') || error.message.includes('Not Found')) {
      errorMessage = 'PDF file not found. It may have been deleted or moved.'
    } else if (error.message.includes('401') || error.message.includes('Unauthorized')) {
      errorMessage = 'Not authorized to view this PDF. Please log in again.'
    } else {
      errorMessage = `Failed to load PDF: ${error.message}`
    }
    
    setError(errorMessage)
    setLoading(false)
  }

  function goToPrevPage() {
    setPageNumber(prev => Math.max(1, prev - 1))
  }

  function goToNextPage() {
    setPageNumber(prev => Math.min(numPages || 1, prev + 1))
  }

  function zoomIn() {
    setScale(prev => Math.min(3.0, prev + 0.2))
  }

  function zoomOut() {
    setScale(prev => Math.max(0.5, prev - 0.2))
  }

  function resetZoom() {
    setScale(1.0)
  }

  return (
    <div className="pdf-viewer-overlay">
      <div className="pdf-viewer-container">
        <div className="pdf-viewer-header">
          <div className="pdf-viewer-title">
            <h3>📄 {filename || `Policy ${policyId}`}</h3>
          </div>
          <div className="pdf-viewer-controls">
            <div className="pdf-navigation">
              <button 
                className="btn btn-secondary btn-sm" 
                onClick={goToPrevPage} 
                disabled={pageNumber <= 1}
                title="Previous page"
              >
                ←
              </button>
              <span className="page-info">
                {numPages ? `${pageNumber} / ${numPages}` : 'Loading...'}
              </span>
              <button 
                className="btn btn-secondary btn-sm" 
                onClick={goToNextPage} 
                disabled={pageNumber >= (numPages || 1)}
                title="Next page"
              >
                →
              </button>
            </div>
            <div className="pdf-zoom-controls">
              <button 
                className="btn btn-secondary btn-sm" 
                onClick={zoomOut} 
                disabled={scale <= 0.5}
                title="Zoom out"
              >
                -
              </button>
              <span className="zoom-level">{Math.round(scale * 100)}%</span>
              <button 
                className="btn btn-secondary btn-sm" 
                onClick={zoomIn} 
                disabled={scale >= 3.0}
                title="Zoom in"
              >
                +
              </button>
              <button 
                className="btn btn-secondary btn-sm" 
                onClick={resetZoom}
                title="Reset zoom"
              >
                Reset
              </button>
            </div>
            <button className="btn btn-danger btn-sm" onClick={onClose}>
              ✕ Close
            </button>
          </div>
        </div>

        <div className="pdf-viewer-content">
          {loading && (
            <div className="pdf-loading">
              <div className="spinner"></div>
              <p>Loading PDF...</p>
            </div>
          )}
          
          {error && (
            <div className="pdf-error">
              <div className="alert alert-error">
                <h4>Error Loading PDF</h4>
                <p>{error}</p>
                <p>Make sure the PDF file exists and you have permission to view it.</p>
              </div>
            </div>
          )}

          <Document
            file={pdfUrl}
            onLoadSuccess={onDocumentLoadSuccess}
            onLoadError={onDocumentLoadError}
            loading=""
            error=""
            options={documentOptions}
          >
            <Page 
              pageNumber={pageNumber} 
              scale={scale}
              loading=""
              error=""
            />
          </Document>
        </div>
      </div>
    </div>
  )
}
