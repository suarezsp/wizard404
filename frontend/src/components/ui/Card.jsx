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
  const bgClass = variant === 'light' ? 'bg-[var(--pixel-dialogue-bg)]' : 'bg-[#1a1a2e]'
  return (
    <div
      className={`${borderClass} border-[var(--pixel-border)] ${bgClass} ${className}`}
      {...props}
    >
      {children}
    </div>
  )
}
