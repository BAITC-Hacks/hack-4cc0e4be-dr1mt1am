import { ArrowUpRight, Building2, ChartNoAxesCombined, CircleHelp, GitCompareArrows, House, MapPin, SlidersHorizontal, Wallet, BusFront, Leaf, HeartPulse, ShieldCheck, Settings2 } from 'lucide-react';
import type { Direction, District, DistrictId } from '../types';
import { BASELINE_SCORE, BUDGET, directions, districts, indicatorNames } from '../data/catalog';
import { level, levelLabel } from '../utils/presentation';


export const directionIcons = { Transport: BusFront, Ecology: Leaf, Social: HeartPulse, Safety: ShieldCheck, Services: Settings2 };
export function Sidebar({ onPending }: { onPending: (message: string) => void }) {
  return <aside className="sidebar"><a className="brand" href="#home"><Building2 size={32}/><span>ASTANA<small>City Simulator</small></span></a>
    <div className="sidebar-label">ВАШ ГОРОД</div><nav aria-label="Основная навигация">
      <a href="#home"><House/>Главная</a><a href="#initiatives"><SlidersHorizontal/>Планировать</a>
      <button onClick={() => onPending('Результаты появятся после подключения simulation engine.')}><ChartNoAxesCombined/>Результаты<span className="soon">Скоро</span></button>
      <button onClick={() => onPending('Сравнение сценариев будет доступно на следующем этапе.')}><GitCompareArrows/>Сравнить<span className="soon">Скоро</span></button>
      <a href="#about"><CircleHelp/>О проекте</a></nav>
    <div className="sidebar-budget"><Wallet/><span>Бюджет фиксирован<strong>100 единиц</strong></span><small>Большие перемены начинаются<br/>с ваших решений.</small></div>
  </aside>;
}
export function Hero() {
  return <section className="hero" id="home"><div className="hero-copy"><span className="eyebrow"><span className="live-dot"/> ГОРОД В ВАШИХ РУКАХ</span><h1>Аким на 5 часов</h1><h2>Твой город. Твой бюджет. Твои решения.</h2><p>У тебя есть 100 единиц городского бюджета.<br/>Выбери ровно 5 инициатив и посмотри,<br/>как твои решения изменят качество жизни в Астане.</p><a className="primary hero-cta" href="#initiatives">Начать планирование <ArrowUpRight size={18}/></a></div>
    <div className="skyline" aria-hidden="true"><div className="sun"/><div className="skyline-grid"/><div className="city-buildings">{[45,75,100,65,125,80,110,60,90].map((height,i)=><i key={i} style={{height}}/>)}</div><div className="baiterek"><i/><b/></div><div className="city-label">ASTANA <span>51°10′ N · 71°26′ E</span></div></div>
  </section>;
}
export function Metrics({ spent, count }: { spent: number; count: number }) {
  return <section className="metrics" aria-label="Обзор сценария"><article className="card metric score-card"><div><span className="eyebrow">ASTANA QUALITY OF LIFE SCORE</span><div className="metric-value">{BASELINE_SCORE.toFixed(2)}<small> / 100</small></div><span className="muted">Исходное состояние</span></div><div className="score-ring" role="img" aria-label="Исходный Score 52.56 из 100"><Building2 size={27}/></div></article>
    <article className="card metric"><span className="eyebrow">ГОРОДСКОЙ БЮДЖЕТ <Wallet size={17}/></span><div className="metric-value">{BUDGET-spent}<small> / {BUDGET}</small></div><progress aria-label="Потраченный бюджет" value={spent} max={BUDGET}/><div className="metric-foot"><span>Потрачено: <b>{spent}</b></span><span>Осталось: <b>{BUDGET-spent}</b></span></div></article>
    <article className="card metric"><span className="eyebrow">ВАШИ РЕШЕНИЯ <SlidersHorizontal size={17}/></span><div className="decision-line"><div className="metric-value">{count}<small> / 5</small></div><div className="decision-dots" aria-hidden="true">{[1,2,3,4,5].map(n=><span className={n<=count?'filled':''} key={n}>{n<=count?'✓':n}</span>)}</div></div><span className="muted">{count===5?'5 из 5 — сценарий готов':count ? `Выберите ещё ${5-count}`:'Выберите ровно 5 мероприятий'}</span></article></section>;
}
export function IndicatorBar({ name, value, direction, critical = true }: { name: string; value: number; direction: Direction; critical?: boolean }) {
  const isCritical = critical && value < 40;
  return <div className={`indicator ${direction} ${isCritical?'critical':''}`}><div className="indicator-label"><span>{name}</span><span>{isCritical&&<b className="critical-badge">Критично</b>}<strong>{Number(value.toFixed(1))}</strong><small> / 100</small></span></div><progress max={100} value={value} aria-label={name}/></div>;
}
export function DistrictMap({ selected, onSelect }: { selected: DistrictId; onSelect: (id: DistrictId) => void }) {
  return <article className="card map-card"><div className="section-heading"><div><h2>Районы Астаны</h2><p>У каждого района — свои приоритеты</p></div><MapPin className="muted" size={21}/></div><div className="district-map"><div className="river" aria-hidden="true"/><span className="map-compass" aria-hidden="true">N ↑</span>{districts.map(d=><button key={d.id} aria-pressed={selected===d.id} onClick={()=>onSelect(d.id)} className={`map-district district-${d.id} ${level(d.score)} ${selected===d.id?'selected':''}`}><span>{d.name}</span><strong>{d.score.toFixed(2)}</strong>{d.id==='Nura'&&<small>Требует внимания</small>}</button>)}</div><div className="map-legend"><span><i className="good"/>60+ Хороший</span><span><i className="medium"/>50–59.99 Средний</span><span><i className="attention"/>&lt;50 Требует внимания</span></div><p className="map-note">Схема районов, не географическая карта. Нажмите на район, чтобы узнать больше.</p></article>;
}
export function DistrictDetails({ district }: { district: District }) {
  return <article className="card district-details"><div className="section-heading"><div><span className="eyebrow">ВЫБРАННЫЙ РАЙОН</span><h2>{district.name}</h2></div><strong className="district-score">{district.score.toFixed(2)}</strong></div><span className={`badge ${level(district.score)}`}>{levelLabel(district.score)}</span><p className="district-profile">{district.profile}</p><div className="district-indicators">{directions.map(direction=>{const Icon=directionIcons[direction.id]; return <section className="indicator-group" key={direction.id}><h3><Icon size={15}/>{direction.name}</h3>{direction.indicators.map(id=><IndicatorBar key={id} name={indicatorNames[id]} value={district.indicators[id]} direction={direction.id}/>)}</section>;})}</div></article>;
}
export function InfoLegend() {
  return <section className="card info-card" id="about"><CircleHelp size={25}/><div><h2>Как читать показатели?</h2><p>Все показатели имеют шкалу от 0 до 100. Чем выше значение, тем лучше состояние города.</p><div className="direction-legend">{directions.map(d=>{const Icon=directionIcons[d.id]; return <span className={d.id} key={d.id}><Icon size={16}/>{d.name}</span>;})}</div><p>Значение ниже 40 считается критическим.</p><small>«Аким на 5 часов» — городской decision simulator. Выберите пять инициатив и исследуйте последствия решений. Результаты расчёта будут доступны после подключения симулятора.</small></div></section>;
}
