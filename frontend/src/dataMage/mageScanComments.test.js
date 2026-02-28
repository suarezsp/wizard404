/**
 * mageScanComments.test.js - Tests de getScanComment (frase del mago segun extension dominante).
 */
import { describe, it, expect } from 'vitest'
import { getScanComment, PHRASE_BY_CATEGORY } from './mageScanComments'

describe('getScanComment', () => {
  it('devuelve frase de programacion cuando .java es dominante', () => {
    const phrase = getScanComment({ '.java': 60, '.xml': 11 })
    expect(phrase).toBe(PHRASE_BY_CATEGORY.programming)
  })

  it('devuelve frase de excel cuando .xlsx es dominante', () => {
    const phrase = getScanComment({ '.xlsx': 20, '.pdf': 5 })
    expect(phrase).toBe(PHRASE_BY_CATEGORY.excel)
  })

  it('devuelve null para by_extension vacio', () => {
    expect(getScanComment({})).toBeNull()
    expect(getScanComment(null)).toBeNull()
  })

  it('devuelve frase de imagenes cuando .png es dominante', () => {
    const phrase = getScanComment({ '.png': 10, '.txt': 2 })
    expect(phrase).toBe(PHRASE_BY_CATEGORY.images)
  })
})
