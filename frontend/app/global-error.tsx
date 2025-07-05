'use client'

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  console.error('Global error:', error)
  
  return (
    <html>
      <body>
        <div style={{ display: 'none' }}>
          Error suppressed
        </div>
      </body>
    </html>
  )
}