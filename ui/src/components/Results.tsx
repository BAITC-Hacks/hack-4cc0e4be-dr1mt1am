import type { AIAnalysis, SimulationResult, ValidationIssue } from '../api/types';
import { useCatalog } from '../api/CatalogContext';
import { indicatorNames } from '../data/catalog';
import { displayNumber } from '../utils/presentation';
import type { IndicatorId } from '../types';

export function RequestStatus({ loading = false, error = '', errors = [] }: { loading?: boolean; error?: string; errors?: ValidationIssue[] }) {
  return <>
    {loading && <div className="card request-status" role="status">Рассчитываем последствия решений…</div>}
    {error && <div className="card request-status api-error" role="alert">{error}</div>}
    {errors.length > 0 && <div className="card request-status api-error" role="alert"><h3>Сценарий требует корректировки</h3><ul>{errors.map((item, i) => <li key={`${item.code}-${i}`}>{item.message}</li>)}</ul></div>}
  </>;
}

export function AnalysisPanel({ analysis, loading, error, onAnalyze }: { analysis: AIAnalysis | null; loading: boolean; error: string; onAnalyze: () => void }) {
  return <article className="card ai-panel" aria-busy={loading}>
    <div className="section-heading"><div><span className="eyebrow">AI ANALYSIS</span><h2>Взгляд AI-аналитика</h2></div>
      <button className="primary" disabled={loading || analysis !== null} onClick={onAnalyze}>{loading ? 'AI анализирует сценарий…' : analysis ? 'Анализ готов' : 'Сформировать AI-анализ'}</button></div>
    {loading && <p role="status">Объясняем рассчитанные изменения, сильные стороны и риски…</p>}
    {error && <p className="api-error" role="alert">{error}</p>}
    {analysis && <><p className="analysis-summary">{analysis.summary}</p><div className="analysis-sections">{([
      ['Сильные стороны', analysis.strengths], ['Риски', analysis.risks],
      ['Компромиссы', analysis.tradeoffs], ['Рекомендации', analysis.recommendations],
    ] as [string, string[]][]).map(([title, items]) => <section key={title}><h3>{title}</h3><ul>{items.map((item, i) => <li key={i}>{item}</li>)}</ul></section>)}</div></>}
    {!analysis && !loading && !error && <p className="muted">AI запускается только по вашей команде. Рекомендации требуют проверки в новой симуляции.</p>}
  </article>;
}

export function Results({ result }: { result: SimulationResult }) {
  const catalog = useCatalog();
  const name = (id: string) => catalog.districts.find(item => item.id === id)?.name ?? id;
  return <>
    <article className="card simulation-result">
      <span className="eyebrow">ASTANA QUALITY OF LIFE SCORE</span>
      <div className="result-score"><span>{displayNumber(result.score_before)}</span><span aria-hidden="true">→</span><strong>{displayNumber(result.score_after)}</strong><b className={result.score_delta < 0 ? 'negative' : ''}>{displayNumber(result.score_delta, true)}</b></div>
      <div className="result-kpis">
        <div><small>Бюджет</small><strong>{result.budget_used} / {catalog.budget}</strong><span>Остаток: {result.budget_remaining}</span></div>
        <div><small>Критические показатели</small><strong>{result.n_crit_before} → {result.n_crit_after}</strong><span>Пары «район × показатель» ниже {catalog.critical_threshold}</span></div>
        <div><small>Слабейший район</small><strong>{name(result.weakest_district_before)} → {name(result.weakest_district_after)}</strong><span>{displayNumber(result.min_district_score_before)} → {displayNumber(result.min_district_score_after)}</span></div>
        <div><small>Синергии</small><strong>{result.triggered_synergies.length}</strong>{result.triggered_synergies.map(item => <span key={`${item.synergy.first_initiative_id}-${item.district}`}>{item.synergy.first_initiative_id} + {item.synergy.second_initiative_id} → {name(item.district)}</span>)}</div>
      </div>
    </article>
    <article className="card comparison-panel"><div className="section-heading"><h2>Районы: до и после</h2><span className="muted">Score / 100</span></div>
      <div className="comparison-legend"><span>До</span><strong>После</strong></div>
      {catalog.districts.map(district => <div className="comparison-row" key={district.id}>
        <strong>{district.name}</strong><div className="comparison-bars">
          <div><progress max={100} value={result.district_scores_before[district.id]} aria-label={`${district.name}: до`}/><span>{displayNumber(result.district_scores_before[district.id])}</span></div>
          <div className="after"><progress max={100} value={result.district_scores_after[district.id]} aria-label={`${district.name}: после`}/><span>{displayNumber(result.district_scores_after[district.id])}</span></div>
        </div><b>{displayNumber(result.district_score_changes[district.id], true)}</b>
      </div>)}
    </article>
    <article className="card indicator-details"><h2>Подробнее по районам</h2>{catalog.districts.map(district => <details key={district.id}><summary>{district.name}</summary><div className="table-scroll"><table><thead><tr><th>Показатель</th><th>До</th><th>После</th><th>Изменение</th></tr></thead><tbody>
      {(Object.keys(catalog.indicator_metadata) as IndicatorId[]).map(id => <tr key={id}><td>{id} · {indicatorNames[id] ?? catalog.indicator_metadata[id].name}</td><td>{displayNumber(result.indicators_before[district.id][id])}</td><td>{displayNumber(result.indicators_after[district.id][id])}</td><td>{displayNumber(result.indicator_changes[district.id][id], true)}</td></tr>)}
    </tbody></table></div></details>)}</article>
  </>;
}
