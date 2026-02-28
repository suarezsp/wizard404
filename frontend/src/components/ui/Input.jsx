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
  const bg = variant === 'light' ? 'var(--pixel-bg)' : '#000'
  const inputClass =
    'w-full px-4 py-2 border-2 border-[var(--pixel-border)] text-sm font-pixel text-[var(--pixel-text)] ' +
    className
  return (
    <div>
      {label && (
        <label className="block text-xs mb-2 text-[var(--pixel-muted)]">
          {label}
        </label>
      )}
      <input type={type} className={inputClass} style={{ backgroundColor: bg }} {...props} />
    </div>
  )
}
