import { lazy, Suspense, useEffect, useMemo, useState } from 'react';
import { MapPin, X, Info } from 'lucide-react';
import type { Decision, Direction, DistrictId, InitiativeId } from './types';
import type { Catalog } from './api/types';
import { ApiError, getCatalog } from './api/client';
import { CatalogProvider, presentCatalog, useCatalog } from './api/CatalogContext';
import { useScenario } from './hooks/useScenario';
import { Sidebar, Hero, Metrics, DistrictMap, DistrictDetails, InfoLegend } from './components/Overview';
import { InitiativeCard, InitiativeFilters, ScenarioBar } from './components/Initiatives';
import { AnalysisPanel, RequestStatus, Results } from './components/Results';

const CityRadar = lazy(() => import('./components/CityRadar'));
// A selection preset, not a second catalog or a calculated result.
const DEMO: Decision[] = [
  { initiative_id: 'M7', district: 'Nura' }, { initiative_id: 'M8', district: 'Nura' },
  { initiative_id: 'M10', district: 'Nura' }, { initiative_id: 'M12', district: null },
  { initiative_id: 'M5', district: 'Saryarka' },
];

export function Dashboard() {
  const catalog = useCatalog();
  const { districts, initiatives, budget, required_decisions } = catalog;
  const [selectedDistrict, setSelectedDistrict] = useState<DistrictId>(catalog.weakest_district);
  const [filter, setFilter] = useState<Direction | 'all'>('all');
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [targets, setTargets] = useState<Partial<Record<InitiativeId, DistrictId>>>({});
  const [notice, setNotice] = useState('');
  const scenario = useScenario(decisions);
  const spent = decisions.reduce((total, decision) => total + initiatives.find(item => item.id === decision.initiative_id)!.cost, 0);
  function changeDecisions(next: Decision[]) { scenario.clearResults(); setDecisions(next); setNotice(''); }
  function changeTarget(id: InitiativeId, district: DistrictId | undefined) {
    setTargets(current => ({ ...current, [id]: district }));
    if (decisions.some(item => item.initiative_id === id)) changeDecisions(district ? decisions.map(item => item.initiative_id === id ? { ...item, district } : item) : decisions.filter(item => item.initiative_id !== id));
  }
  function toggle(id: InitiativeId) {
    if (decisions.some(item => item.initiative_id === id)) { changeDecisions(decisions.filter(item => item.initiative_id !== id)); return; }
    const initiative = initiatives.find(item => item.id === id)!;
    // UX only; Python performs all authoritative validation on submission.
    if (decisions.length >= required_decisions || spent + initiative.cost > budget || (initiative.type === 'District' && !targets[id])) return;
    changeDecisions([...decisions, { initiative_id: id, district: initiative.type === 'City' ? null : targets[id]! }]);
  }
  function demo() {
    const selection = DEMO.map(item => ({ ...item }));
    changeDecisions(selection);
    setTargets(Object.fromEntries(selection.filter(item => item.district !== null).map(item => [item.initiative_id, item.district])));
  }
  return <><a className="skip-link" href="#main">Перейти к содержимому</a><Sidebar onPending={setNotice}/><main id="main">
    <header className="topbar"><div><span className="breadcrumb">Городской симулятор</span><span className="slash">/</span>Обзор города</div><span className="location"><MapPin size={15}/> Астана, Казахстан <i/></span></header>
    <Hero/><Metrics spent={spent} count={decisions.length}/>
    <div className="section-kicker">01 <span>ИЗУЧИТЕ ГОРОД</span><span className="kicker-line"/></div>
    <section className="district-layout" aria-label="Районы и их показатели"><div className="district-left"><DistrictMap selected={selectedDistrict} onSelect={setSelectedDistrict}/><Suspense fallback={<div className="card chart-loading">Загрузка диаграммы состояния города…</div>}><CityRadar/></Suspense></div><DistrictDetails district={districts.find(item => item.id === selectedDistrict)!}/></section>
    <section id="initiatives"><div className="section-kicker">02 <span>ВЫБЕРИТЕ ПРИОРИТЕТЫ</span><span className="kicker-line"/></div>
      <div className="section-heading initiatives-heading"><div><h2>Городские инициативы</h2><p>Выберите {required_decisions} мероприятий в рамках бюджета</p></div><button className="demo-button" onClick={demo}>Загрузить демо-сценарий</button></div>
      <InitiativeFilters active={filter} onChange={setFilter}/><div className="initiative-grid">{initiatives.filter(item => filter === 'all' || item.direction === filter).map(item => <InitiativeCard key={item.id} initiative={item} target={targets[item.id]} decision={decisions.find(decision => decision.initiative_id === item.id)} spent={spent} count={decisions.length} onTarget={target => changeTarget(item.id, target)} onToggle={() => toggle(item.id)}/>)}</div>
      <p className="planning-note">Направления, совместимость и окончательную допустимость сценария проверяет сервер при запуске.</p>
    </section>
    <section id="results" aria-label="Результаты симуляции" aria-busy={scenario.loading}>
      <div className="section-kicker">03 <span>ОЦЕНИТЕ РЕЗУЛЬТАТ</span><span className="kicker-line"/></div>
      <RequestStatus loading={scenario.loading} error={scenario.error} errors={scenario.errors}/>
      {scenario.result ? <><Results result={scenario.result}/><AnalysisPanel analysis={scenario.analysis} loading={scenario.aiLoading} error={scenario.aiError} onAnalyze={() => void scenario.runAnalysis()}/></> : !scenario.loading && !scenario.error && scenario.errors.length === 0 && <div className="card request-status">Выберите инициативы и нажмите «Симулировать». После изменения решений результаты нужно рассчитать заново.</div>}
    </section>
    <InfoLegend/><footer className="page-footer"><span>ASTANA · CITY SIMULATOR</span><span>Город будущего начинается с решений сегодня.</span></footer>
  </main><ScenarioBar spent={spent} count={decisions.length} loading={scenario.loading || scenario.aiLoading} onClear={() => { changeDecisions([]); setTargets({}); }} onSimulate={() => { void scenario.runSimulation(); document.getElementById('results')?.scrollIntoView({ behavior: 'smooth' }); }}/>
    <div className="notice-host" aria-live="polite" aria-atomic="true">{notice && <div className="notice"><Info size={21}/><span>{notice}</span><button onClick={() => setNotice('')} aria-label="Закрыть уведомление"><X size={18}/></button></div>}</div>
  </>;
}

export default function App() {
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [error, setError] = useState('');
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    const request = new AbortController(); setError('');
    getCatalog(request.signal).then(value => { if (!request.signal.aborted) setCatalog(value); }).catch(cause => {
      if (!request.signal.aborted) setError(cause instanceof ApiError ? cause.message : 'Не удалось загрузить каталог.');
    });
    return () => request.abort();
  }, [attempt]);
  const displayCatalog = useMemo(() => catalog ? presentCatalog(catalog) : null, [catalog]);
  if (!displayCatalog) return <div className="catalog-status card"><h1>Аким на 5 часов</h1>{error ? <><p role="alert">{error}</p><button className="primary" onClick={() => setAttempt(value => value + 1)}>Повторить загрузку</button></> : <p role="status">Загружаем данные города…</p>}</div>;
  return <CatalogProvider value={displayCatalog}><Dashboard/></CatalogProvider>;
}
