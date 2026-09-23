// TEMPORARY FRONTEND CATALOG MIRROR of engine/data.py and engine/constants.py.
// Replace with GET /api/catalog. Values are baseline facts, never simulated results.
// Russian labels are presentation only. Effects are full, NOT lag-scaled.
import type { Direction, District, IndicatorId, Initiative } from '../types';
export const BUDGET = 100;
export const REQUIRED_DECISIONS = 5;
export const BASELINE_SCORE = 52.55768;
export const directions: { id: Direction; name: string; indicators: IndicatorId[] }[] = [
  { id: 'Transport', name: 'Транспорт', indicators: ['T1','T2'] },
  { id: 'Ecology', name: 'Экология', indicators: ['E1','E2'] },
  { id: 'Social', name: 'Соцсфера', indicators: ['S1','S2'] },
  { id: 'Safety', name: 'Безопасность', indicators: ['B1','B2'] },
  { id: 'Services', name: 'Сервисы', indicators: ['C1','C2'] },
];
export const indicatorNames: Record<IndicatorId,string> = {
  T1:'Разгрузка дорог', T2:'Доступность общественного транспорта', E1:'Озеленение', E2:'Качество воздуха',
  S1:'Школы и детсады', S2:'Поликлиники и первичная медпомощь', B1:'Безопасность улиц', B2:'Безопасность дорожного движения', C1:'Надёжность ЖКХ', C2:'Скорость решения обращений',
};
export const districts: District[] = [
  { id:'Esil',name:'Есиль',populationShare:.27,score:62.99,indicators:{T1:45,T2:62,E1:68,E2:72,S1:48,S2:55,B1:78,B2:60,C1:75,C2:70},profile:'Развитый район. Основные вызовы — пробки на мостах и переполненные школы.' },
  { id:'Almaty',name:'Алматы',populationShare:.24,score:57.06,indicators:{T1:40,T2:75,E1:50,E2:55,S1:60,S2:65,B1:62,B2:52,C1:50,C2:60},profile:'Старые коммунальные сети и высокая нагрузка на дороги.' },
  { id:'Saryarka',name:'Сарыарка',populationShare:.20,score:54.65,indicators:{T1:50,T2:70,E1:42,E2:40,S1:62,S2:68,B1:58,B2:55,C1:45,C2:55},profile:'Смог от отопления частного сектора и недостаток зелёных пространств.' },
  { id:'Baikonur',name:'Байконур',populationShare:.13,score:56.63,indicators:{T1:52,T2:68,E1:55,E2:50,S1:58,S2:60,B1:52,B2:58,C1:55,C2:58},profile:'Сбалансированный район без выраженных критических слабостей.' },
  { id:'Nura',name:'Нура',populationShare:.16,score:49.18,indicators:{T1:55,T2:40,E1:45,E2:65,S1:38,S2:35,B1:55,B2:50,C1:60,C2:50},profile:'Особого внимания требуют школы, медицина и доступность общественного транспорта.' },
];
export const initiatives: Initiative[] = [
  {id:'M1',direction:'Transport',name:'Выделенные полосы для автобусов',type:'District',cost:18,lag:2,effects:[['T1',6],['T2',9]]},
  {id:'M2',direction:'Transport',name:'Умные светофоры',type:'City',cost:22,lag:2,effects:[['T1',4],['B2',3]]},
  {id:'M3',direction:'Transport',name:'Строительство и расширение LRT',type:'District',cost:30,lag:4,effects:[['T1',16],['T2',20],['E2',4]]},
  {id:'M4',direction:'Ecology',name:'Новый парк или сквер',type:'District',cost:15,lag:2,effects:[['E1',12],['E2',3],['B1',2]]},
  {id:'M5',direction:'Ecology',name:'Чистое отопление частного сектора',type:'District',cost:25,lag:3,effects:[['E2',14],['C1',4]]},
  {id:'M6',direction:'Ecology',name:'Озеленение и ветрозащитные полосы',type:'City',cost:20,lag:4,effects:[['E1',5],['E2',3]]},
  {id:'M7',direction:'Social',name:'Модульные школы и детские сады',type:'District',cost:24,lag:3,effects:[['S1',16]]},
  {id:'M8',direction:'Social',name:'Семейная поликлиника',type:'District',cost:20,lag:3,effects:[['S2',14]]},
  {id:'M9',direction:'Social',name:'Спортивные площадки во дворах',type:'District',cost:10,lag:1,effects:[['S1',3],['S2',3],['B1',3]]},
  {id:'M10',direction:'Safety',name:'Освещение и камеры «Безопасный город»',type:'District',cost:12,lag:1,effects:[['B1',12],['B2',2]]},
  {id:'M11',direction:'Safety',name:'Безопасные переходы и школьные зоны',type:'District',cost:10,lag:1,effects:[['B2',12],['T1',-2]]},
  {id:'M12',direction:'Services',name:'Единая платформа обращений жителей',type:'City',cost:14,lag:1,effects:[['C2',5]]},
  {id:'M13',direction:'Services',name:'Модернизация тепловых и водопроводных сетей',type:'District',cost:28,lag:4,effects:[['C1',18],['E2',2]]},
  {id:'M14',direction:'Services',name:'Аварийные бригады и раннее оповещение',type:'City',cost:16,lag:1,effects:[['C1',5],['C2',2]]},
];
