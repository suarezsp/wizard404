/**
 * Button.jsx - Boton reutilizable estilo 16-bit.
 * Variantes: primary, secondary, ghost. Usa --pixel-border, --pixel-accent, font-pixel.
 */
export function Button({
  variant = 'primary',
  type = 'button',
  disabled = false,
  className = '',
  children,
  ...props
}) {
  const base =
    'font-pixel text-xs transition-colors border-2 disabled:opacity-50 disabled:cursor-not-allowed '
  const variants = {
    primary:
      'border-[var(--pixel-accent)] text-[var(--pixel-accent)] bg-transparent hover:bg-[var(--pixel-accent)] hover:text-black',
    secondary:
      'border-[var(--pixel-border)] text-[var(--pixel-text)] bg-transparent hover:border-[var(--pixel-accent)] hover:text-[var(--pixel-accent)]',
    ghost:
      'border-transparent text-[var(--pixel-muted)] hover:text-[var(--pixel-accent)]',
  }
  return (
    <button
      type={type}
      disabled={disabled}
      className={`${base} ${variants[variant] || variants.primary} ${className}`}
      {...props}
    >
      {children}
    </button>
  )
}
