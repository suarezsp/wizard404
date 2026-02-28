/**
 * CRTToggleButton.jsx - Boton fijo para activar/desactivar el overlay CRT/VHS.
 * Estilo 16-bit coherente con el resto de la app; persistencia se gestiona en App.jsx.
 */
export function CRTToggleButton({ active, onToggle }) {
  return (
    <button
      type="button"
      onClick={onToggle}
      aria-pressed={active}
      aria-label={active ? 'Desactivar efecto pantalla CRT' : 'Activar efecto pantalla CRT'}
      className="fixed bottom-4 left-4 border-4 px-3 py-2 text-xs font-bold transition-colors"
      style={{
        zIndex: 95,
        backgroundColor: 'var(--pixel-dialogue-bg)',
        borderColor: active ? 'var(--pixel-accent)' : 'var(--pixel-border)',
        color: 'var(--pixel-text)',
      }}
      data-testid="crt-toggle"
    >
      CRT
    </button>
  )
}
