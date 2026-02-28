/**
 * Card.jsx - Contenedor con marco estilo 16-bit (PixelFrame).
 * Borde 2-4px. variant=default: fondo oscuro; variant=light: fondo claro (Home).
 */
export function Card({
  borderWidth = 4,
  variant = 'default',
  className = '',
  children,
  ...props
}) {
  const borderClass = borderWidth === 2 ? 'border-2' : 'border-4'
  const bgClass = variant === 'light' ? 'bg-[var(--pixel-bg-2)]' : 'bg-[var(--pixel-bg)]'
  return (
    <div
      className={`${borderClass} border-[var(--pixel-border)] rounded-none ${bgClass} ${className}`}
      {...props}
    >
      {children}
    </div>
  )
}
