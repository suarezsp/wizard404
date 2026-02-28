/**
 * AnimatedView.jsx - Wrapper para animacion de entrada de vistas (opacity + translateY).
 * Mantiene estetica 16-bit; transicion corta al montar. Ver index.css .animate-view-in
 */
export function AnimatedView({ children, className = '' }) {
  return <div className={`animate-view-in ${className}`.trim()}>{children}</div>
}
