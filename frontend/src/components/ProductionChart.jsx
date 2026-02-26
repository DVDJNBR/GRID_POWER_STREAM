/**
 * ProductionChart — Story 5.1, Task 2.2
 *
 * Stacked area chart showing energy production by source over time.
 * AC #1: Displays production per source.
 * AC #2: Updates when region changes.
 * Uses recharts AreaChart.
 */
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts'

const SOURCE_COLORS = {
  nucleaire:   '#7c3aed',
  eolien:      '#10b981',
  solaire:     '#f59e0b',
  hydraulique: '#3b82f6',
  gaz:         '#ef4444',
  bioenergies: '#84cc16',
  charbon:     '#6b7280',
  fioul:       '#f97316',
}

const SOURCE_LABELS = {
  nucleaire:   'Nucléaire',
  eolien:      'Éolien',
  solaire:     'Solaire',
  hydraulique: 'Hydraulique',
  gaz:         'Gaz',
  bioenergies: 'Bioénergies',
  charbon:     'Charbon',
  fioul:       'Fioul',
}

/**
 * Transform API records into recharts-compatible data.
 * @param {Array} records - data array from the production API
 * @returns {Array}
 */
export function transformProductionData(records) {
  return records.map(r => ({
    timestamp: new Date(r.timestamp).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }),
    ...r.sources,
  }))
}

/** @param {{ data: Array, loading?: boolean, error?: string|null }} props */
export function ProductionChart({ data, loading = false, error = null }) {
  if (loading) {
    return (
      <div className="glass-card chart-card" data-testid="production-chart-loading">
        <div className="skeleton" style={{ height: '300px' }} />
      </div>
    )
  }

  if (error) {
    return (
      <div className="glass-card chart-card chart-error" data-testid="production-chart-error">
        <p>Erreur de chargement : {error}</p>
      </div>
    )
  }

  const chartData = transformProductionData(data)
  const sources = chartData.length > 0
    ? Object.keys(chartData[0]).filter(k => k !== 'timestamp')
    : []

  return (
    <section className="glass-card chart-card" data-testid="production-chart">
      <h2 className="chart-title">Production par source (MW)</h2>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={chartData} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
          <defs>
            {sources.map(source => (
              <linearGradient key={source} id={`grad-${source}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%"  stopColor={SOURCE_COLORS[source] || '#888'} stopOpacity={0.4} />
                <stop offset="95%" stopColor={SOURCE_COLORS[source] || '#888'} stopOpacity={0.05} />
              </linearGradient>
            ))}
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
          <XAxis dataKey="timestamp" tick={{ fill: '#8b9ab5', fontSize: 11 }} />
          <YAxis tick={{ fill: '#8b9ab5', fontSize: 11 }} unit=" MW" width={70} />
          <Tooltip
            contentStyle={{ background: '#111827', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
            labelStyle={{ color: '#f0f4ff' }}
          />
          <Legend formatter={name => SOURCE_LABELS[name] || name} />
          {sources.map(source => (
            <Area
              key={source}
              type="monotone"
              dataKey={source}
              stackId="1"
              stroke={SOURCE_COLORS[source] || '#888'}
              fill={`url(#grad-${source})`}
              strokeWidth={2}
            />
          ))}
        </AreaChart>
      </ResponsiveContainer>
    </section>
  )
}
