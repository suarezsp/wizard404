/**
 * ToastList.jsx - Lista de toasts fija en la parte superior; estetica 16-bit.
 */
import { useToast } from '../context/ToastContext'

const typeStyles = {
  error: 'border-[#8b2942] text-[var(--pixel-text-on-light)]',
  warning: 'border-amber-600 text-[var(--pixel-text-on-light)]',
  info: 'border-[var(--pixel-title-border)] text-[var(--pixel-text-on-light)]',
}

export function ToastList() {
  const { toasts, removeToast } = useToast()
  if (toasts.length === 0) return null

  return (
    <div
      className="fixed top-4 left-1/2 -translate-x-1/2 z-[100] flex flex-col gap-2 max-w-md w-full px-4"
      role="region"
      aria-label="Notifications"
    >
      {toasts.map(({ id, message, type }) => (
        <div
          key={id}
          data-testid="toast"
          className={`border-4 rounded-none p-3 font-pixel text-xs flex justify-between items-start gap-2 ${typeStyles[type] || typeStyles.error}`}
          style={{ backgroundColor: 'var(--pixel-panel-light)' }}
        >
          <span className="flex-1">{message}</span>
          <button
            type="button"
            onClick={() => removeToast(id)}
            className="flex-shrink-0 opacity-70 hover:opacity-100 focus:outline-none"
            aria-label="Cerrar"
          >
            ✕
          </button>
        </div>
      ))}
    </div>
  )
}
