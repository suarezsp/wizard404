/**
 * CRTContentWrapper.jsx - Envuelve el contenido principal cuando el overlay CRT esta activo.
 * Aplica el filtro barrel (url #crt-barrel). Overlay transparente redirige clics a coordenadas
 * logicas para que el hit-testing coincida con lo que se ve.
 */
import { useRef, useCallback } from 'react'
import { barrelVisualToLogical } from '../utils/crtBarrelMap'

function forwardPointerEvent(e, containerRef, overlayRef) {
  const container = containerRef.current
  const overlay = overlayRef.current
  if (!container || !overlay) return
  const rect = container.getBoundingClientRect()
  const relX = e.clientX - rect.left
  const relY = e.clientY - rect.top
  const { x: logicalX, y: logicalY } = barrelVisualToLogical(relX, relY, rect.width, rect.height)
  const clientX = rect.left + logicalX
  const clientY = rect.top + logicalY
  overlay.style.pointerEvents = 'none'
  const target =
    typeof document.elementFromPoint === 'function'
      ? document.elementFromPoint(clientX, clientY)
      : null
  overlay.style.pointerEvents = 'auto'
  if (!target) return
  const type = e.type
  const opts = {
    bubbles: true,
    cancelable: true,
    view: e.view,
    detail: e.detail,
    screenX: e.screenX,
    screenY: e.screenY,
    clientX,
    clientY,
    button: e.button,
    buttons: e.buttons,
    relatedTarget: e.relatedTarget,
  }
  if (type === 'click') {
    target.dispatchEvent(new MouseEvent('click', opts))
  } else if (type === 'mousedown') {
    target.dispatchEvent(new MouseEvent('mousedown', opts))
  } else if (type === 'mouseup') {
    target.dispatchEvent(new MouseEvent('mouseup', opts))
  } else if (type === 'dblclick') {
    target.dispatchEvent(new MouseEvent('dblclick', opts))
  }
}

export function CRTContentWrapper({ children }) {
  const containerRef = useRef(null)
  const overlayRef = useRef(null)

  const handlePointer = useCallback(
    (e) => {
      e.preventDefault()
      e.stopPropagation()
      forwardPointerEvent(e, containerRef, overlayRef)
    },
    []
  )

  return (
    <div ref={containerRef} className="crt-content-wrapper-container" style={{ position: 'relative', width: '100%', minHeight: '100%' }}>
      <div
        className="crt-content-wrapper"
        style={{ filter: 'url(#crt-barrel)', minHeight: '100%' }}
      >
        {children}
      </div>
      <div
        ref={overlayRef}
        className="crt-content-wrapper-overlay"
        style={{
          position: 'absolute',
          inset: 0,
          pointerEvents: 'auto',
          zIndex: 1,
        }}
        onMouseDown={handlePointer}
        onMouseUp={handlePointer}
        onClick={handlePointer}
        onDoubleClick={handlePointer}
        aria-hidden="true"
      />
    </div>
  )
}
