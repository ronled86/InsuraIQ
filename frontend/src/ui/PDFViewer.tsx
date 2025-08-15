import React, { useState, useMemo, useRef, useEffect, useCallback } from 'react'
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
  const [currentPage, setCurrentPage] = useState(1)
  const [scale, setScale] = useState(1.0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [viewMode, setViewMode] = useState<'single' | 'continuous'>('continuous')
  const [pageInput, setPageInput] = useState('')
  const [userHasScrolled, setUserHasScrolled] = useState(false)
  
  const scrollContainerRef = useRef<HTMLDivElement>(null)
  const pageRefs = useRef<(HTMLDivElement | null)[]>([])
  const initialLoadRef = useRef(true)

  const pdfUrl = `${apiBase}/policies/${policyId}/pdf`

  const documentOptions = useMemo(() => ({
    httpHeaders: {
      'Authorization': `Bearer ${token}`
    }
  }), [token])

  // Initialize component to start from page 1
  useEffect(() => {
    // Reset all state when component mounts or policy changes
    setCurrentPage(1)
    setLoading(true)
    setError(null)
    setScale(1.0)
    setPageInput('')
    setUserHasScrolled(false)
    initialLoadRef.current = true
    
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollTop = 0
      scrollContainerRef.current.scrollLeft = 0
    }
  }, [policyId]) // Reset when policy changes

  // Intersection Observer to track which page is currently in view
  useEffect(() => {
    if (!numPages || viewMode !== 'continuous' || !userHasScrolled) return

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const pageIndex = parseInt(entry.target.getAttribute('data-page') || '1')
            setCurrentPage(pageIndex)
          }
        })
      },
      { 
        threshold: 0.5,
        root: scrollContainerRef.current
      }
    )

    pageRefs.current.forEach((ref) => {
      if (ref) observer.observe(ref)
    })

    return () => observer.disconnect()
  }, [numPages, viewMode, userHasScrolled])

  // Track user scroll events
  useEffect(() => {
    const container = scrollContainerRef.current
    if (!container) return

    const handleScroll = () => {
      if (initialLoadRef.current) {
        initialLoadRef.current = false
        return
      }
      setUserHasScrolled(true)
    }

    container.addEventListener('scroll', handleScroll, { passive: true })
    return () => container.removeEventListener('scroll', handleScroll)
  }, [])

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.target instanceof HTMLInputElement) return // Don't interfere with input fields
      
      switch (event.key) {
        case 'ArrowUp':
        case 'PageUp':
          event.preventDefault()
          goToPrevPage()
          break
        case 'ArrowDown':
        case 'PageDown':
        case ' ': // Spacebar
          event.preventDefault()
          goToNextPage()
          break
        case 'Home':
          event.preventDefault()
          scrollToPage(1)
          break
        case 'End':
          event.preventDefault()
          scrollToPage(numPages || 1)
          break
        case 'v':
        case 'V':
          if (event.ctrlKey || event.metaKey) return // Don't interfere with paste
          event.preventDefault()
          toggleViewMode()
          break
        case '+':
        case '=':
          event.preventDefault()
          zoomIn()
          break
        case '-':
          event.preventDefault()
          zoomOut()
          break
        case '0':
          event.preventDefault()
          resetZoom()
          break
        case 'Escape':
          event.preventDefault()
          onClose()
          break
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [numPages, onClose])

  // Auto-scroll on mouse wheel in continuous mode
  useEffect(() => {
    if (viewMode !== 'continuous' || !scrollContainerRef.current) return

    const container = scrollContainerRef.current
    
    const handleWheel = (event: WheelEvent) => {
      // Allow normal scrolling behavior
      // The browser will handle smooth scrolling automatically
    }

    container.addEventListener('wheel', handleWheel, { passive: true })
    return () => container.removeEventListener('wheel', handleWheel)
  }, [viewMode])

  // Mouse wheel navigation for single page mode
  useEffect(() => {
    if (viewMode !== 'single' || !scrollContainerRef.current) return

    const container = scrollContainerRef.current
    
    const handleWheel = (event: WheelEvent) => {
      event.preventDefault()
      
      if (event.deltaY > 0) {
        // Scrolling down - go to next page
        if (currentPage < (numPages || 1)) {
          goToNextPage()
        }
      } else if (event.deltaY < 0) {
        // Scrolling up - go to previous page
        if (currentPage > 1) {
          goToPrevPage()
        }
      }
    }

    container.addEventListener('wheel', handleWheel, { passive: false })
    return () => container.removeEventListener('wheel', handleWheel)
  }, [viewMode, currentPage, numPages])

  // Smooth scroll to specific page
  const scrollToPage = useCallback((pageNum: number) => {
    if (viewMode === 'continuous') {
      if (pageNum === 1) {
        // For page 1, always scroll to top
        if (scrollContainerRef.current) {
          scrollContainerRef.current.scrollTop = 0
        }
      } else if (pageRefs.current[pageNum - 1]) {
        pageRefs.current[pageNum - 1]?.scrollIntoView({ 
          behavior: userHasScrolled ? 'smooth' : 'auto', 
          block: 'start' 
        })
      }
    } else {
      setCurrentPage(pageNum)
    }
  }, [viewMode, userHasScrolled])

  function onDocumentLoadSuccess({ numPages }: { numPages: number }) {
    setNumPages(numPages)
    setLoading(false)
    setError(null)
    setCurrentPage(1) // Always start from the first page
    // Initialize page refs array
    pageRefs.current = new Array(numPages).fill(null)
    
    // Reset scroll tracking first
    setUserHasScrolled(false)
    initialLoadRef.current = true
    
    // Only handle scroll positioning for continuous mode
    if (viewMode === 'continuous' && scrollContainerRef.current) {
      // Force immediate scroll to top
      scrollContainerRef.current.scrollTop = 0
      scrollContainerRef.current.scrollLeft = 0
      
      // Use requestAnimationFrame for smoother control
      requestAnimationFrame(() => {
        if (scrollContainerRef.current) {
          scrollContainerRef.current.scrollTop = 0
        }
      })
    }
  }

  // Handle scroll tracking for intersection observer
  useEffect(() => {
    if (!scrollContainerRef.current || viewMode !== 'continuous' || !numPages || userHasScrolled) return

    const container = scrollContainerRef.current
    const options = {
      root: container,
      rootMargin: '0px',
      threshold: 0.5
    }

    const observer = new IntersectionObserver((entries) => {
      // Only update current page if user has scrolled
      if (userHasScrolled) {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const pageElement = entry.target as HTMLElement
            const pageNum = parseInt(pageElement.getAttribute('data-page') || '1', 10)
            setCurrentPage(pageNum)
          }
        })
      }
    }, options)

    // Observe all page elements
    pageRefs.current.forEach((pageRef) => {
      if (pageRef) observer.observe(pageRef)
    })

    return () => observer.disconnect()
  }, [viewMode, numPages, userHasScrolled])

  // Simple continuous mode scroll reset - only when document loads
  useEffect(() => {
    if (numPages && viewMode === 'continuous' && !userHasScrolled && scrollContainerRef.current) {
      // Set scroll position to top immediately
      scrollContainerRef.current.scrollTop = 0
      
      // Also ensure after first page renders
      const handleFirstPageRender = () => {
        if (scrollContainerRef.current && !userHasScrolled) {
          scrollContainerRef.current.scrollTop = 0
        }
      }
      
      // Wait for first page to render, then reset position
      setTimeout(handleFirstPageRender, 100)
    }
  }, [numPages, viewMode])

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
    const newPage = Math.max(1, currentPage - 1)
    scrollToPage(newPage)
  }

  function goToNextPage() {
    const newPage = Math.min(numPages || 1, currentPage + 1)
    scrollToPage(newPage)
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

  function toggleViewMode() {
    const newMode = viewMode === 'single' ? 'continuous' : 'single'
    setViewMode(newMode)
    
    // When switching to continuous mode, scroll to current page
    if (newMode === 'continuous') {
      setTimeout(() => {
        scrollToPage(currentPage)
      }, 100) // Small delay to ensure DOM is updated
    }
  }

  function handlePageJump(event: React.FormEvent) {
    event.preventDefault()
    const pageNum = parseInt(pageInput)
    if (pageNum >= 1 && pageNum <= (numPages || 1)) {
      scrollToPage(pageNum)
      setPageInput('')
    }
  }

  function handlePageInputChange(event: React.ChangeEvent<HTMLInputElement>) {
    setPageInput(event.target.value)
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
                disabled={currentPage <= 1}
                title="Previous page"
              >
                ←
              </button>
              <span className="page-info">
                {numPages ? `${currentPage} / ${numPages}` : 'Loading...'}
              </span>
              <button 
                className="btn btn-secondary btn-sm" 
                onClick={goToNextPage} 
                disabled={currentPage >= (numPages || 1)}
                title="Next page"
              >
                →
              </button>
              <form onSubmit={handlePageJump} className="page-jump-form">
                <input
                  type="number"
                  min="1"
                  max={numPages || 1}
                  value={pageInput}
                  onChange={handlePageInputChange}
                  placeholder="Page #"
                  className="page-jump-input"
                  title="Jump to page"
                />
                <button type="submit" className="btn btn-secondary btn-sm" title="Go to page">
                  Go
                </button>
              </form>
            </div>
            <div className="pdf-view-mode">
              <button 
                className={`btn btn-sm ${viewMode === 'continuous' ? 'btn-primary' : 'btn-secondary'}`}
                onClick={toggleViewMode}
                title={`Switch to ${viewMode === 'continuous' ? 'single page' : 'continuous'} view`}
              >
                {viewMode === 'continuous' ? '📄 Single' : '📜 Continuous'}
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

        <div 
          className={`pdf-viewer-content ${viewMode === 'continuous' ? 'pdf-continuous-view' : 'pdf-single-view'}`}
          ref={scrollContainerRef}
          onScroll={() => {
            if (!userHasScrolled) {
              setUserHasScrolled(true)
            }
          }}
          style={{ 
            scrollBehavior: userHasScrolled ? 'smooth' : 'auto',
            // Ensure container starts at top for continuous mode
            ...(viewMode === 'continuous' && !userHasScrolled ? { scrollTop: 0 } : {})
          }}
        >
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
            {viewMode === 'continuous' ? (
              // Continuous view - render all pages
              <div className="pdf-continuous-container">
                {numPages && Array.from(new Array(numPages), (el, index) => (
                  <div
                    key={`page_${index + 1}`}
                    ref={(ref) => {
                      pageRefs.current[index] = ref
                    }}
                    data-page={index + 1}
                    className="pdf-page-container"
                  >
                    <div className="pdf-page-number">
                      Page {index + 1} of {numPages}
                    </div>
                    <Page 
                      pageNumber={index + 1} 
                      scale={scale}
                      loading=""
                      error=""
                      onLoadSuccess={() => {
                        // Only reset scroll for the first page and only once
                        if (index === 0 && !userHasScrolled && scrollContainerRef.current) {
                          scrollContainerRef.current.scrollTop = 0
                        }
                      }}
                    />
                  </div>
                ))}
              </div>
            ) : (
              // Single page view - render current page only
              <div className="pdf-page-container">
                <Page 
                  pageNumber={currentPage} 
                  scale={scale}
                  loading=""
                  error=""
                />
              </div>
            )}
          </Document>
        </div>
      </div>
    </div>
  )
}
