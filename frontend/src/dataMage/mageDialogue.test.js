/**
 * mageDialogue.test.js - Comprueba que todas las escenas existen y tienen frases no vacias.
 */
import { describe, it, expect } from 'vitest'
import { DIALOGUE_BY_SCENE } from './mageDialogue'

const EXPECTED_SCENES = [
  'login',
  'register',
  'dashboard',
  'documentDetail',
  'loading',
  'home',
  'scan',
  'import',
  'search',
  'explore',
  'organize',
  'cleanup',
]

describe('mageDialogue', () => {
  it('has all expected scene keys', () => {
    EXPECTED_SCENES.forEach((key) => {
      expect(DIALOGUE_BY_SCENE).toHaveProperty(key)
    })
  })

  it('each scene is a non-empty array of strings', () => {
    EXPECTED_SCENES.forEach((key) => {
      const list = DIALOGUE_BY_SCENE[key]
      expect(Array.isArray(list)).toBe(true)
      expect(list.length).toBeGreaterThan(0)
      list.forEach((phrase) => {
        expect(typeof phrase).toBe('string')
        expect(phrase.trim().length).toBeGreaterThan(0)
      })
    })
  })
})
