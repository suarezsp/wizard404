/**
 * RouteTransition.jsx - Envuelve Routes y aplica animacion de salida (viewOut) y entrada (viewIn) al cambiar de ruta.
 * Mantiene location controlada: al navegar, primero anima salida del contenido actual, luego muestra el nuevo.
 */
import { useState, useEffect, cloneElement } from 'react'
import { useLocation } from 'react-router-dom'

export function RouteTransition({ children }) {
  const location = useLocation()
  const [currentLocation, setCurrentLocation] = useState(location)
  const [nextLocation, setNextLocation] = useState(null)

  useEffect(() => {
    if (location.pathname !== currentLocation.pathname && !nextLocation) {
      setNextLocation(location)
    }
  }, [location, currentLocation.pathname, nextLocation])

  const handleAnimationEnd = () => {
    if (nextLocation) {
      setCurrentLocation(nextLocation)
      setNextLocation(null)
    }
  }

  const isExiting = nextLocation != null
  const content = cloneElement(children, { location: currentLocation })

  return (
    <div
      key={currentLocation.pathname}
      className={isExiting ? 'animate-view-out' : 'animate-view-in'}
      onAnimationEnd={handleAnimationEnd}
    >
      {content}
    </div>
  )
}
