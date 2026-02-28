/**
 * useTypewriter.js - Muestra texto caracter a caracter; al terminar llama onComplete.
 * Velocidad en ms por caracter. Reutilizable y testeable (DRY).
 */
import { useState, useEffect, useRef } from 'react'

export function useTypewriter(text, speedMs = 40, onComplete) {
  const [display, setDisplay] = useState('')
  const indexRef = useRef(0)
  const onCompleteRef = useRef(onComplete)
  onCompleteRef.current = onComplete

  useEffect(() => {
    if (text == null || text === '') {
      setDisplay('')
      indexRef.current = 0
      return
    }
    indexRef.current = 0
    setDisplay('')

    const id = setInterval(() => {
      indexRef.current += 1
      setDisplay((prev) => text.slice(0, indexRef.current))
      if (indexRef.current >= text.length) {
        clearInterval(id)
        onCompleteRef.current?.()
      }
    }, speedMs)

    return () => clearInterval(id)
  }, [text, speedMs])

  return display
}
