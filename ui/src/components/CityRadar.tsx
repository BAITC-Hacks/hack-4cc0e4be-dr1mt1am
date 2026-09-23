import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';
import { useCatalog } from '../api/CatalogContext';
import { cityOverview } from '../utils/presentation';
import { IndicatorBar } from './Overview';
export default function CityRadar() {
  const { districts, directions } = useCatalog();
  const data = cityOverview(districts, directions);
  return <article className="card city-card"><div className="section-heading"><div><h2>Состояние города</h2><p>Пять направлений городской жизни</p></div><span className="badge neutral">До изменений</span></div><div className="city-overview"><div className="radar" role="img" aria-label="Радар исходных показателей. Числовые значения представлены рядом."><ResponsiveContainer width="100%" height="100%"><RadarChart data={data} outerRadius="68%"><PolarGrid stroke="#dce5ee"/><PolarAngleAxis dataKey="name" tick={{fill:'#64748b',fontSize:12}}/><PolarRadiusAxis domain={[0,100]} tick={false} axisLine={false}/><Radar dataKey="value" stroke="#3274d7" fill="#609ced" fillOpacity={0.23} isAnimationActive={false}/></RadarChart></ResponsiveContainer></div><div className="city-bars">{data.map(item=><IndicatorBar key={item.id} name={item.name} value={item.value} direction={item.id} critical={false}/>)}</div></div><p className="chart-note">Обзор: простое среднее двух показателей направления по пяти районам, без весов населения. Это описательная диаграмма, не итоговый Score.</p></article>;
}
