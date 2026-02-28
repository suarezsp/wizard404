/**
 * CRTFilterDefs.jsx - Definiciones SVG del filtro barrel (id="crt-barrel") para uso global.
 * Se renderiza en App cuando el overlay CRT esta activo; CRTContentWrapper y MageWizard usan url(#crt-barrel).
 * Ocuto (w-0 h-0), no afecta layout.
 */
import { useMemo } from 'react'
import { BARREL_MAP_SIZE, BARREL_SCALE } from '../constants/crt'

function createBarrelDisplacementMapDataUrl() {
  try {
    const canvas = document.createElement('canvas')
    canvas.width = BARREL_MAP_SIZE
    canvas.height = BARREL_MAP_SIZE
    const ctx = canvas.getContext('2d')
    if (!ctx) return null
    const center = BARREL_MAP_SIZE / 2
    const gradient = ctx.createRadialGradient(center, center, 0, center, center, center)
    gradient.addColorStop(0, 'rgb(128, 128, 128)')
    gradient.addColorStop(1, 'rgb(0, 0, 0)')
    ctx.fillStyle = gradient
    ctx.fillRect(0, 0, BARREL_MAP_SIZE, BARREL_MAP_SIZE)
    return canvas.toDataURL('image/png')
  } catch (_) {
    return null
  }
}

export function CRTFilterDefs() {
  const barrelMapUrl = useMemo(createBarrelDisplacementMapDataUrl, [])

  if (!barrelMapUrl) return null

  return (
    <svg aria-hidden="true" className="absolute w-0 h-0 overflow-hidden" focusable="false">
      <defs>
        <filter id="crt-barrel" x="-20%" y="-20%" width="140%" height="140%">
          <feImage href={barrelMapUrl} result="barrelMap" />
          <feDisplacementMap
            in="SourceGraphic"
            in2="barrelMap"
            scale={BARREL_SCALE}
            xChannelSelector="R"
            yChannelSelector="G"
            result="displaced"
          />
          <feMerge>
            <feMergeNode in="displaced" />
          </feMerge>
        </filter>
      </defs>
    </svg>
  )
}
