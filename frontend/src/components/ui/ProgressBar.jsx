/**
 * ProgressBar.jsx - Barra de progreso estilo 16-bit para Scan y operaciones largas.
 * Reutilizable: porcentaje 0-100 o indeterminado (animacion).
 */
export function ProgressBar({ percent = 0, indeterminate = false, label = '' }) {
  const value = Math.min(100, Math.max(0, percent))

  return (
    <div
      className="border-2 border-[var(--pixel-border)] p-2 font-pixel"
      style={{ backgroundColor: 'var(--pixel-dialogue-bg)' }}
      role="progressbar"
      aria-valuenow={indeterminate ? undefined : value}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label={label || 'Progress'}
    >
      {label && (
        <p className="text-xs text-[var(--pixel-muted)] mb-1">{label}</p>
      )}
      <div className="h-4 w-full border-2 border-[var(--pixel-border)] overflow-hidden">
        {indeterminate ? (
          <div className="h-full overflow-hidden">
            <div
              className="h-full w-1/3"
              style={{
                backgroundColor: 'var(--pixel-accent)',
                animation: 'progressIndeterminate 1.2s ease-in-out infinite',
              }}
            />
          </div>
        ) : (
          <div
            className="h-full transition-[width] duration-300 ease-out"
            style={{
              width: `${value}%`,
              backgroundColor: 'var(--pixel-accent)',
            }}
          />
        )}
      </div>
      {!indeterminate && (
        <p className="text-xs text-[var(--pixel-text)] mt-1">{Math.round(value)}%</p>
      )}
    </div>
  )
}
