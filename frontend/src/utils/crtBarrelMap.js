/**
 * utils/crtBarrelMap.js - Mapeo inverso del filtro barrel para corregir hit-testing.
 * Dado un punto (visual) donde el usuario hizo clic, devuelve las coordenadas logicas
 * (donde esta el elemento en el DOM antes del filtro). feDisplacementMap con mapa
 * radial: desplazamiento = scale * (V - 0.5), con V = 0.5*(1 - min(1, dist_centro)).
 */

import { BARREL_SCALE } from '../constants/crt'

/** Valor del mapa radial en coords normalizadas (0-1). Centro 0.5,0.5. */
function barrelValueAt(nx, ny) {
  const dx = 2 * nx - 1
  const dy = 2 * ny - 1
  const dist = Math.sqrt(dx * dx + dy * dy)
  const v = 0.5 * (1 - Math.min(1, dist))
  return v
}

/**
 * Dado (visualX, visualY) en pixels relativos al contenedor, devuelve (logicalX, logicalY)
 * en pixels (en coordenadas del documento para elementFromPoint). Resuelve de forma iterativa:
 * el pixel que vemos en (visual) proviene de (logical) donde visual = logical + scale*(V-0.5).
 */
export function barrelVisualToLogical(visualX, visualY, width, height) {
  if (width <= 0 || height <= 0) return { x: visualX, y: visualY }
  const scaleNormX = BARREL_SCALE / width
  const scaleNormY = BARREL_SCALE / height
  const vnx = visualX / width
  const vny = visualY / height
  let lx = vnx
  let ly = vny
  for (let i = 0; i < 10; i++) {
    const v = barrelValueAt(lx, ly)
    const d = v - 0.5
    lx = vnx - scaleNormX * d
    ly = vny - scaleNormY * d
  }
  return {
    x: lx * width,
    y: ly * height,
  }
}
