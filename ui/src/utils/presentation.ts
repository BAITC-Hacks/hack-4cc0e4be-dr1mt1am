import { directions, districts } from '../data/catalog';
export const level = (score: number) => score >= 60 ? 'good' : score >= 50 ? 'medium' : 'attention';
export const levelLabel = (score: number) => score >= 60 ? 'Хороший уровень' : score >= 50 ? 'Средний уровень' : 'Требует внимания';
// Descriptive chart only: simple mean of 10 baseline values per direction
// (2 indicators × 5 districts). No population/score weights, no official Score.
export const cityOverview = directions.map(direction => ({
  ...direction,
  value: districts.reduce((total, district) => total + direction.indicators.reduce((sum, id) => sum + district.indicators[id], 0), 0) / (districts.length * direction.indicators.length),
}));
