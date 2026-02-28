/**
 * useTypewriter.test.js - Tests del hook typewriter: revelado caracter a caracter y onComplete.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useTypewriter } from './useTypewriter'

describe('useTypewriter', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })
  afterEach(() => {
    vi.useRealTimers()
  })

  it('starts with empty display when text is provided', () => {
    const { result } = renderHook(() => useTypewriter('Hi', 50))
    expect(result.current).toBe('')
  })

  it('reveals one character after first tick', () => {
    const { result } = renderHook(() => useTypewriter('Hi', 50))
    act(() => { vi.advanceTimersByTime(50) })
    expect(result.current).toBe('H')
  })

  it('reveals full text after enough ticks and calls onComplete', () => {
    const onComplete = vi.fn()
    const { result } = renderHook(() => useTypewriter('Hi', 50, onComplete))
    act(() => { vi.advanceTimersByTime(50) })
    expect(result.current).toBe('H')
    act(() => { vi.advanceTimersByTime(50) })
    expect(result.current).toBe('Hi')
    act(() => { vi.advanceTimersByTime(10) })
    expect(onComplete).toHaveBeenCalledTimes(1)
  })

  it('resets when text becomes empty', () => {
    const { result, rerender } = renderHook(
      ({ text }) => useTypewriter(text, 50),
      { initialProps: { text: 'Ab' } }
    )
    act(() => { vi.advanceTimersByTime(100) })
    expect(result.current).toBe('Ab')
    rerender({ text: '' })
    expect(result.current).toBe('')
  })
})
