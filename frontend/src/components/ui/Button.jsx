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
    'font-pixel text-xs transition-colors border-2 disabled:opacity-50 disabled:cursor-not-allowed rounded-none '
  const variants = {
    primary:
      'border-[var(--pixel-title-border)] text-[var(--pixel-accent)] bg-[var(--pixel-bg)] hover:bg-[var(--pixel-accent)] hover:text-[var(--pixel-bg)]',
    secondary:
      'border-[var(--pixel-border)] text-[var(--pixel-text-on-dark)] bg-[var(--pixel-bg)] hover:border-[var(--pixel-title-border)] hover:text-[var(--pixel-accent-gold)]',
    ghost:
      'border-transparent text-[var(--pixel-text-muted)] hover:text-[var(--pixel-accent)]',
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
