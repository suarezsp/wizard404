/**
 * ParticleBackground.jsx - Fondo con asteriscos que parpadean (estetica mistica 16-bit).
 * Parallax: el fondo se mueve mas lento que el scroll para dar profundidad.
 */
import { useMemo, useState, useEffect } from 'react'

const PARTICLE_COUNT = 32
const PARALLAX_FACTOR = 0.25

function useParticles() {
  return useMemo(() => {
    return Array.from({ length: PARTICLE_COUNT }, () => ({
      left: Math.random() * 100,
      top: Math.random() * 100,
      delay: Math.random() * 4,
    }))
  }, [])
}

export function ParticleBackground() {
  const particles = useParticles()
  const [offsetY, setOffsetY] = useState(0)

  useEffect(() => {
    const onScroll = () => {
      setOffsetY(window.scrollY * PARALLAX_FACTOR)
    }
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <div
      className="fixed inset-0 pointer-events-none"
      style={{ zIndex: 0, transform: `translateY(${offsetY * 0.5}px)` }}
      aria-hidden="true"
    >
      {particles.map((p, i) => (
        <span
          key={i}
          className="particle-asterisk absolute text-[var(--pixel-text-muted)] font-pixel"
          style={{
            left: `${p.left}%`,
            top: `${p.top}%`,
            fontSize: '0.6rem',
            opacity: 0.2,
            animationDelay: `${p.delay}s`,
          }}
        >
          *
        </span>
      ))}
    </div>
  )
}
