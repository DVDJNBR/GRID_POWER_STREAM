/**
 * API client tests — Story 5.1, Task 6.2
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { buildQueryString } from '../api.js'

// ── buildQueryString ──────────────────────────────────────────────────────────

describe('buildQueryString', () => {
  it('returns empty string for empty params', () => {
    expect(buildQueryString({})).toBe('')
  })

  it('returns empty string when all values are null', () => {
    expect(buildQueryString({ a: null, b: undefined })).toBe('')
  })

  it('returns empty string when all values are empty string', () => {
    expect(buildQueryString({ a: '' })).toBe('')
  })

  it('builds query string from valid params', () => {
    const qs = buildQueryString({ limit: 100, offset: 0 })
    expect(qs).toBe('?limit=100&offset=0')
  })

  it('omits null and undefined values', () => {
    const qs = buildQueryString({ region_code: null, limit: 50 })
    expect(qs).toBe('?limit=50')
    expect(qs).not.toContain('region_code')
  })

  it('omits empty string values', () => {
    const qs = buildQueryString({ region_code: '', limit: 10 })
    expect(qs).not.toContain('region_code')
    expect(qs).toContain('limit=10')
  })

  it('includes string parameters', () => {
    const qs = buildQueryString({ region_code: '11', source_type: 'nucleaire' })
    expect(qs).toContain('region_code=11')
    expect(qs).toContain('source_type=nucleaire')
  })
})

// ── fetchProduction — fetch mocking ──────────────────────────────────────────

describe('fetchProduction', () => {
  let originalFetch

  beforeEach(() => {
    originalFetch = global.fetch
    // Mock acquireToken — api.js imports auth.js which calls acquireToken
    vi.mock('../auth.js', () => ({
      acquireToken: vi.fn().mockResolvedValue('mock-token'),
    }))
  })

  afterEach(() => {
    global.fetch = originalFetch
    vi.restoreAllMocks()
  })

  it('calls fetch with Authorization header', async () => {
    const { fetchProduction } = await import('../api.js')
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ data: [], total_records: 0, request_id: 'req-1' }),
    })

    await fetchProduction({ limit: 10 })

    expect(global.fetch).toHaveBeenCalledOnce()
    const [url, options] = global.fetch.mock.calls[0]
    expect(url).toContain('/v1/production/regional')
    expect(options.headers.Authorization).toBe('Bearer mock-token')
  })

  it('passes limit to query string', async () => {
    const { fetchProduction } = await import('../api.js')
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ data: [], total_records: 0, request_id: 'req-2' }),
    })

    await fetchProduction({ limit: 42 })

    const [url] = global.fetch.mock.calls[0]
    expect(url).toContain('limit=42')
  })

  it('passes regionCode as region_code param', async () => {
    const { fetchProduction } = await import('../api.js')
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ data: [], total_records: 0, request_id: 'req-3' }),
    })

    await fetchProduction({ regionCode: '11' })

    const [url] = global.fetch.mock.calls[0]
    expect(url).toContain('region_code=11')
  })

  it('throws ApiError on non-ok response', async () => {
    const { fetchProduction, ApiError } = await import('../api.js')
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 401,
      json: async () => ({ message: 'Unauthorized', request_id: 'req-err' }),
    })

    await expect(fetchProduction()).rejects.toBeInstanceOf(ApiError)
  })

  it('ApiError carries status code', async () => {
    const { fetchProduction, ApiError } = await import('../api.js')
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 404,
      json: async () => ({ message: 'Not found' }),
    })

    try {
      await fetchProduction()
    } catch (err) {
      expect(err).toBeInstanceOf(ApiError)
      expect(err.status).toBe(404)
    }
  })
})
