import { lazy, Suspense, useState } from 'react';
import { MapPin, X, Info } from 'lucide-react';
import { districts, initiatives } from './data/catalog';
import type { Decision, Direction, DistrictId, InitiativeId } from './types';
import { Sidebar, Hero, Metrics, DistrictMap, DistrictDetails, InfoLegend } from './components/Overview';
import { InitiativeCard, InitiativeFilters, ScenarioBar } from './components/Initiatives';

const CityRadar = lazy(() => import('./components/CityRadar'));

export default function App() {
  const [selectedDistrict,setSelectedDistrict] = useState<DistrictId>('Nura');
  const [filter,setFilter] = useState<Direction|'all'>('all');
  const [decisions,setDecisions] = useState<Decision[]>([]);
  const [targets,setTargets] = useState<Partial<Record<InitiativeId,DistrictId>>>({});
  const [notice,setNotice] = useState('');
  const spent = decisions.reduce((total,decision)=>total+initiatives.find(i=>i.id===decision.initiative_id)!.cost,0);
  function changeTarget(id: InitiativeId, district: DistrictId | undefined) {
    setTargets(current=>({...current,[id]:district}));
    setDecisions(current=>district ? current.map(d=>d.initiative_id===id?{...d,district}:d) : current.filter(d=>d.initiative_id!==id));
    setNotice('');
  }
  function toggle(id: InitiativeId) {
    const initiative = initiatives.find(i=>i.id===id)!;
    setDecisions(current=>{
      if(current.some(d=>d.initiative_id===id)) return current.filter(d=>d.initiative_id!==id);
      const cost = current.reduce((sum,d)=>sum+initiatives.find(i=>i.id===d.initiative_id)!.cost,0);
      if(current.length>=5 || cost+initiative.cost>100 || (initiative.type==='District'&&!targets[id])) return current;
      return [...current,{initiative_id:id,district:initiative.type==='City'?null:targets[id]!}];
    });
    setNotice('');
  }
  return <><a className="skip-link" href="#main">Перейти к содержимому</a><Sidebar onPending={setNotice}/><main id="main"><header className="topbar"><div><span className="breadcrumb">Городской симулятор</span><span className="slash">/</span>Обзор города</div><span className="location"><MapPin size={15}/> Астана, Казахстан <i/></span></header><Hero/><Metrics spent={spent} count={decisions.length}/><div className="section-kicker">01 <span>ИЗУЧИТЕ ГОРОД</span><span className="kicker-line"/></div><section className="district-layout" aria-label="Районы и их показатели"><div className="district-left"><DistrictMap selected={selectedDistrict} onSelect={setSelectedDistrict}/><Suspense fallback={<div className="card chart-loading">Загрузка диаграммы состояния города…</div>}><CityRadar/></Suspense></div><DistrictDetails district={districts.find(d=>d.id===selectedDistrict)!}/></section><section id="initiatives"><div className="section-kicker">02 <span>ВЫБЕРИТЕ ПРИОРИТЕТЫ</span><span className="kicker-line"/></div><div className="section-heading initiatives-heading"><div><h2>Городские инициативы</h2><p>Выберите 5 мероприятий в рамках бюджета</p></div><span className="badge neutral">14 возможностей изменить город</span></div><InitiativeFilters active={filter} onChange={setFilter}/><div className="initiative-grid">{initiatives.filter(i=>filter==='all'||i.direction===filter).map(i=><InitiativeCard key={i.id} initiative={i} target={targets[i.id]} decision={decisions.find(d=>d.initiative_id===i.id)} spent={spent} count={decisions.length} onTarget={target=>changeTarget(i.id,target)} onToggle={()=>toggle(i.id)}/>)}</div><p className="planning-note">Полная проверка направлений и совместимости мероприятий будет выполнена при подключении симулятора. Пока доступно составление сценария.</p></section><InfoLegend/><footer className="page-footer"><span>ASTANA · CITY SIMULATOR</span><span>Город будущего начинается с решений сегодня.</span></footer></main><ScenarioBar spent={spent} count={decisions.length} onClear={()=>{setDecisions([]);setTargets({});setNotice('');}} onSimulate={()=>setNotice('Интеграция с simulation engine будет подключена следующим этапом.')}/><div className="notice-host" aria-live="polite" aria-atomic="true">{notice&&<div className="notice"><Info size={21}/><span>{notice}</span><button onClick={()=>setNotice('')} aria-label="Закрыть уведомление"><X size={18}/></button></div>}</div></>;
}
