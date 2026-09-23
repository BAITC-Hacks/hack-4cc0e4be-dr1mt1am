import type { Direction, District, IndicatorId } from '../types';
export const level = (score: number) => score >= 60 ? 'good' : score >= 50 ? 'medium' : 'attention';
export const levelLabel = (score: number) => score >= 60 ? 'Хороший уровень' : score >= 50 ? 'Средний уровень' : 'Требует внимания';
export const displayNumber = (value: number, signed = false) => `${signed && value > 0 ? '+' : ''}${value.toFixed(2)}`;
// Descriptive mean only. Never used as official city Score or as input to simulation.
export const cityOverview = (districts: District[], directions: { id: Direction; name: string; indicators: IndicatorId[] }[]) => directions.map(direction => ({
  ...direction,
  value: districts.reduce((total, district) => total + direction.indicators.reduce((sum, id) => sum + district.indicators[id], 0), 0) / (districts.length * direction.indicators.length),
}));
