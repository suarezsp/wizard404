/**
 * CRTOverlay.jsx - Capa visual fija estilo CRT/VHS: scanlines, vignette y borde curvado.
 * Se monta por encima del contenido cuando el overlay esta activo; pointer-events: none.
 * Relacion: usado desde App.jsx; complementa CRTContentWrapper (distorsion) y CRTToggleButton (toggle).
 */
export function CRTOverlay() {
  return (
    <div
      className="fixed inset-0 pointer-events-none"
      style={{ zIndex: 90 }}
      aria-hidden="true"
    >
      {/* Scanlines: lineas horizontales semitransparentes */}
      <div
        className="absolute inset-0 opacity-[0.06]"
        style={{
          backgroundImage: 'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.4) 2px, rgba(0,0,0,0.4) 4px)',
        }}
      />
      {/* Vignette: bordes oscuros */}
      <div
        className="absolute inset-0 opacity-80"
        style={{
          background: 'radial-gradient(ellipse 70% 70% at 50% 50%, transparent 40%, rgba(0,0,0,0.5) 100%)',
        }}
      />
      {/* Borde curvado tipo tubo: clip opcional con bordes redondeados */}
      <div
        className="absolute inset-2 pointer-events-none rounded-[2rem] border-4 border-black/30"
        style={{ boxShadow: 'inset 0 0 60px rgba(0,0,0,0.15)' }}
      />
    </div>
  )
}
