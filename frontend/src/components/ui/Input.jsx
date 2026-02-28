/**
 * Input.jsx - Campo de texto estilo 16-bit.
 * variant=default: fondo oscuro; variant=light: fondo claro (login, cards).
 */
export function Input({
  label,
  type = 'text',
  variant = 'default',
  className = '',
  ...props
}) {
  const bg = variant === 'light' ? 'var(--pixel-panel-light)' : 'var(--pixel-panel)'
  const textColor = variant === 'light' ? 'var(--pixel-text-on-light)' : 'var(--pixel-text-on-dark)'
  const inputClass =
    'w-full px-4 py-2 border-2 border-[var(--pixel-border)] rounded-none text-sm font-pixel ' +
    className
  return (
    <div>
      {label && (
        <label className="block text-xs mb-2 text-[var(--pixel-text-muted)]">
          {label}
        </label>
      )}
      <input type={type} className={inputClass} style={{ backgroundColor: bg, color: textColor }} {...props} />
    </div>
  )
}
