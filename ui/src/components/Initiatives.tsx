import { useState } from 'react';
import { Check, Plus, Clock3, ArrowRight, RotateCcw, Globe2 } from 'lucide-react';
import type { Decision, Direction, DistrictId, Initiative } from '../types';
import { BUDGET, directions, districts, indicatorNames } from '../data/catalog';
import { directionIcons } from './Overview';

export function InitiativeVisual({ initiative }: { initiative: Initiative }) {
  const [failedSource, setFailedSource] = useState<string>();
  const Icon = directionIcons[initiative.direction];
  return <div className={`initiative-visual ${initiative.direction}`}>
    {initiative.image && failedSource !== initiative.image ? <img src={initiative.image} alt="" onError={()=>setFailedSource(initiative.image)}/> : <><div className="visual-orbit"/><Icon size={56} strokeWidth={1.25}/><span className="visual-lines"/></>}
    <span className="visual-label">ASTANA / {initiative.direction.toUpperCase()}</span>
  </div>;
}
export function InitiativeFilters({ active, onChange }: { active: Direction | 'all'; onChange: (direction: Direction | 'all') => void }) {
  return <div className="filters" aria-label="Фильтр по направлению"><button aria-pressed={active==='all'} onClick={()=>onChange('all')}>Все <span>14</span></button>{directions.map(d=>{const Icon=directionIcons[d.id]; return <button key={d.id} aria-pressed={active===d.id} onClick={()=>onChange(d.id)}><Icon size={16}/>{d.name}</button>;})}</div>;
}
export function InitiativeCard({ initiative, decision, target, spent, count, onTarget, onToggle }: {
  initiative: Initiative; decision?: Decision; target?: DistrictId; spent: number; count: number;
  onTarget: (target: DistrictId | undefined) => void; onToggle: () => void;
}) {
  const selected = !!decision;
  const reason = !selected ? count>=5 ? 'Выбрано 5 мероприятий' : spent+initiative.cost>BUDGET ? 'Недостаточно бюджета' : initiative.type==='District' && !target ? 'Сначала выберите район' : '' : '';
  return <article className={`card initiative-card ${selected?'is-selected':''}`}><div className="initiative-top"><span className="initiative-id">{initiative.id}</span><span className={`direction-tag ${initiative.direction}`}>{directions.find(d=>d.id===initiative.direction)?.name}</span>{selected&&<Check className="selected-check" size={18}/>}</div><InitiativeVisual initiative={initiative}/><div className="initiative-body"><h3>{initiative.name}</h3><div className="initiative-facts"><div><small>Стоимость</small><strong>{initiative.cost}<span> ед.</span></strong></div><div><small><Clock3 size={13}/> Эффект начнётся через</small><strong>{initiative.lag}<span> {initiative.lag===1?'квартал':'квартала'}</span></strong></div></div><ul className="effects">{initiative.effects.map(([id,value])=><li key={id}><span>{indicatorNames[id]} <small>{id}</small></span><b className={value<0?'negative':''}>{value>0?'+':''}{value}</b></li>)}</ul><p className="effects-note">Полные эффекты до учёта лага</p><div className="initiative-actions">{initiative.type==='District'?<label className="district-select"><span className="sr-only">Район для {initiative.id}</span><select value={target??''} onChange={event=>onTarget(event.target.value ? event.target.value as DistrictId : undefined)}><option value="">Выберите район</option>{districts.map(d=><option key={d.id} value={d.id}>{d.name}</option>)}</select></label>:<div className="city-scope"><Globe2 size={16}/>Весь город</div>}<button className={selected?'select-button selected':'select-button'} disabled={!!reason} onClick={onToggle} aria-pressed={selected} aria-label={`${selected?'Отменить выбор':'Выбрать'} ${initiative.id}`} aria-describedby={`${initiative.id}-hint`}>{selected?<Check size={17}/>:<Plus size={17}/>} {selected?'Выбрано · отменить':'Выбрать'}</button><small className="selection-hint" id={`${initiative.id}-hint`}>{reason || (selected?'Добавлено в ваш сценарий':'Доступно для выбора')}</small></div></div></article>;
}
export function ScenarioBar({ spent, count, onClear, onSimulate }: { spent: number; count: number; onClear: () => void; onSimulate: () => void }) {
  return <section className="scenario-bar" aria-label="Ваш сценарий"><div className="scenario-title"><span className="live-dot"/><strong>Ваш сценарий</strong><small>{count===5?'5 из 5 — сценарий готов':`Выберите ещё ${5-count}`}</small></div><div className="scenario-stat"><small>Бюджет</small><strong>{spent}<span> / 100</span></strong></div><div className="scenario-stat"><small>Решения</small><strong>{count}<span> / 5</span></strong></div><div className="scenario-stat remaining"><small>Осталось</small><strong>{BUDGET-spent}</strong></div><button className="clear-button" onClick={onClear} disabled={!count}><RotateCcw size={16}/>Очистить</button><button className="primary" disabled={count!==5} onClick={onSimulate}>Симулировать<ArrowRight size={17}/></button></section>;
}
