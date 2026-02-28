/**
 * MageContext.test.jsx - say() actualiza mensaje; sayForScene('login') pone uno del array login.
 */
import { describe, it, expect } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { MageProvider, useMage } from './MageContext'
import { DIALOGUE_BY_SCENE } from '../dataMage/mageDialogue'

function wrapper({ children }) {
  return <MageProvider>{children}</MageProvider>
}

describe('MageContext', () => {
  it('say(text) updates message and consumer sees it', () => {
    const { result } = renderHook(() => useMage(), { wrapper })
    expect(result.current.message).toBe(null)
    act(() => {
      result.current.say('Hello wizard')
    })
    expect(result.current.message).toBe('Hello wizard')
    expect(result.current.isSpeaking).toBe(true)
  })

  it('sayForScene(login) sets message to one of the login phrases', () => {
    const loginPhrases = DIALOGUE_BY_SCENE.login
    const { result } = renderHook(() => useMage(), { wrapper })
    act(() => {
      result.current.sayForScene('login')
    })
    expect(loginPhrases).toContain(result.current.message)
  })
})
