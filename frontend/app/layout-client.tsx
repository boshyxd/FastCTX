'use client'

import { useEffect } from 'react'

export function DisableErrorOverlay() {
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const style = document.createElement('style')
      style.innerHTML = `
        nextjs-portal {
          display: none !important;
        }
        [data-nextjs-dialog-overlay] {
          display: none !important;
        }
        [data-nextjs-dialog] {
          display: none !important;
        }
        #__next-build-indicator {
          display: none !important;
        }
      `
      document.head.appendChild(style)

      window.addEventListener('error', (e) => {
        e.preventDefault()
        console.error('Suppressed error:', e.error)
      })

      window.addEventListener('unhandledrejection', (e) => {
        e.preventDefault()
        console.error('Suppressed rejection:', e.reason)
      })
    }
  }, [])

  return null
}