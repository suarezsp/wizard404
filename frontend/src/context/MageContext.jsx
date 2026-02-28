/**
 * MageContext.jsx - Contexto del mago: unica fuente de verdad para que dice y cuando.
 * Expone say(text) y sayForScene(sceneId). Las paginas llaman a estos metodos para mostrar dialogos.
 */
import { createContext, useContext, useState, useCallback, useRef } from 'react'
import { DIALOGUE_BY_SCENE } from '../dataMage/mageDialogue'

const MageContext = createContext(null)

const SPEAK_DISMISS_MS = 2500

export function MageProvider({ children }) {
  const [message, setMessage] = useState(null)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const dismissRef = useRef(null)

  const say = useCallback((text) => {
    if (dismissRef.current) clearTimeout(dismissRef.current)
    setMessage(text ?? '')
    setIsSpeaking(!!text)
  }, [dismissRef])

  const onTypewriterComplete = useCallback(() => {
    dismissRef.current = setTimeout(() => {
      setMessage(null)
      setIsSpeaking(false)
      dismissRef.current = null
    }, SPEAK_DISMISS_MS)
  }, [dismissRef])

  const sayForScene = useCallback((sceneId) => {
    const list = DIALOGUE_BY_SCENE[sceneId]
    if (!list || list.length === 0) return
    const idx = Math.floor(Math.random() * list.length)
    say(list[idx])
  }, [say])

  const value = {
    message,
    isSpeaking,
    say,
    sayForScene,
    onTypewriterComplete,
  }

  return (
    <MageContext.Provider value={value}>
      {children}
    </MageContext.Provider>
  )
}

export function useMage() {
  const ctx = useContext(MageContext)
  if (!ctx) throw new Error('useMage must be used within MageProvider')
  return ctx
}
