/**
 * BackgroundImage.jsx - Fondo con bg.png y efecto parallax (se mueve mas lento que el scroll).
 */
import { useState, useEffect } from 'react'

const PARALLAX_FACTOR = 0.01

export function BackgroundImage() {
  const [offsetY, setOffsetY] = useState(0)

  useEffect(() => {
    const onScroll = () => setOffsetY(window.scrollY * PARALLAX_FACTOR)
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <div
      className="fixed inset-0 pointer-events-none"
      style={{
        zIndex: -1,
        opacity: 0.6,
        backgroundImage: 'url(/bg.jpg )',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
        transform: `translateY(${offsetY}px)`,
      }}
      aria-hidden="true"
    />
  )
}
