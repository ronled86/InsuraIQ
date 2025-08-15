import React from 'react'
import { createRoot } from 'react-dom/client'
import { App } from './ui/App'
import './styles/app.css'

// Configure PDF.js globally with matching version worker
import { pdfjs } from 'react-pdf'

// Use the exact version that react-pdf expects
const workerSrc = `https://unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`
pdfjs.GlobalWorkerOptions.workerSrc = workerSrc

// Only log in development mode
if (import.meta.env.DEV) {
  console.log('PDF.js version:', pdfjs.version)
  console.log('Worker source:', workerSrc)
}

createRoot(document.getElementById('root')!).render(<App />)