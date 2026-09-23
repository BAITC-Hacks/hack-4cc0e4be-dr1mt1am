import type { Decision } from '../types';
import type { AIAnalysis, Catalog, InvalidSimulation, SimulationResponse } from './types';

export class ApiError extends Error {
  code: string;
  constructor(message: string, code = 'API_ERROR') { super(message); this.name = 'ApiError'; this.code = code; }
}
const record = (value: unknown): value is Record<string, unknown> => typeof value === 'object' && value !== null && !Array.isArray(value);
const numeric = (value: unknown): value is number => typeof value === 'number' && Number.isFinite(value);
const numericMap = (value: unknown): boolean => record(value) && Object.values(value).every(numeric);
const indicatorMap = (value: unknown): boolean => record(value) && Object.values(value).every(numericMap);
const textList = (value: unknown): boolean => Array.isArray(value) && value.every(item => typeof item === 'string');
function requireShape(ok: boolean): asserts ok {
  if (!ok) throw new ApiError('Сервер вернул неожиданный формат данных.', 'INVALID_RESPONSE');
}
export function parseCatalog(value: unknown): Catalog {
  requireShape(record(value));
  for (const key of ['budget', 'required_decisions', 'max_per_direction', 'horizon', 'critical_threshold', 'baseline_score', 'baseline_n_crit']) requireShape(numeric(value[key]));
  requireShape(Array.isArray(value.districts) && value.districts.length > 0 && value.districts.every(item =>
    record(item) && typeof item.id === 'string' && typeof item.name === 'string' && typeof item.profile === 'string' && numeric(item.populationShare) && numeric(item.score) && numericMap(item.indicators)));
  requireShape(Array.isArray(value.initiatives) && value.initiatives.length > 0 && value.initiatives.every(item =>
    record(item) && typeof item.id === 'string' && typeof item.name === 'string' && typeof item.direction === 'string' && ['District', 'City'].includes(String(item.type)) && numeric(item.cost) && numeric(item.lag) &&
    Array.isArray(item.effects) && item.effects.every(effect => Array.isArray(effect) && effect.length === 2 && typeof effect[0] === 'string' && numeric(effect[1]))));
  requireShape(record(value.indicator_metadata) && Object.values(value.indicator_metadata).every(item =>
    record(item) && typeof item.id === 'string' && typeof item.direction === 'string' && typeof item.name === 'string' && numeric(item.weight)));
  for (const key of ['indicator_weights', 'direction_weights', 'population_shares', 'baseline_district_scores']) requireShape(numericMap(value[key]));
  requireShape(indicatorMap(value.baseline_indicators) && typeof value.weakest_district === 'string');
  requireShape(Array.isArray(value.synergies) && Array.isArray(value.incompatibilities));
  return value as unknown as Catalog;
}
export function parseSimulation(value: unknown): SimulationResponse {
  requireShape(record(value) && typeof value.valid === 'boolean');
  if (!value.valid) {
    requireShape(Array.isArray(value.errors) && value.errors.every(item => record(item) && typeof item.code === 'string' && typeof item.message === 'string'));
    requireShape((value.budget_used === null || numeric(value.budget_used)) && (value.budget_remaining === null || numeric(value.budget_remaining)));
  } else {
    for (const key of ['budget_used', 'budget_remaining', 'score_before', 'score_after', 'score_delta', 'd_avg_before', 'd_avg_after', 'n_crit_before', 'n_crit_after', 'min_district_score_before', 'min_district_score_after']) requireShape(numeric(value[key]));
    for (const key of ['district_scores_before', 'district_scores_after', 'district_score_changes']) requireShape(numericMap(value[key]));
    for (const key of ['indicators_before', 'indicators_after', 'indicator_changes']) requireShape(indicatorMap(value[key]));
    requireShape(typeof value.weakest_district_before === 'string' && typeof value.weakest_district_after === 'string');
    requireShape(Array.isArray(value.triggered_synergies) && value.triggered_synergies.every(item => record(item) && typeof item.district === 'string' && record(item.synergy) && typeof item.synergy.first_initiative_id === 'string' && typeof item.synergy.second_initiative_id === 'string'));
  }
  return value as unknown as SimulationResponse;
}
export function parseAnalysis(value: unknown): AIAnalysis | InvalidSimulation {
  if (record(value) && value.valid === false) return parseSimulation(value) as InvalidSimulation;
  requireShape(record(value) && typeof value.summary === 'string');
  for (const key of ['strengths', 'risks', 'tradeoffs', 'recommendations']) requireShape(textList(value[key]));
  return value as unknown as AIAnalysis;
}
export function createApiClient(baseUrl = import.meta.env?.VITE_API_URL || 'http://localhost:8000', transport: typeof fetch = (...args) => fetch(...args)) {
  async function request(path: string, decisions?: Decision[], signal?: AbortSignal): Promise<unknown> {
    let response: Response;
    try {
      response = await transport(`${baseUrl.replace(/\/$/, '')}${path}`, {
        method: decisions ? 'POST' : 'GET', signal,
        ...(decisions ? { headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ decisions }) } : {}),
      });
    } catch (error) {
      if (signal?.aborted) throw error;
      throw new ApiError('Не удалось связаться с сервером. Проверьте, что Python API запущен.', 'NETWORK_ERROR');
    }
    let data: unknown;
    try { data = await response.json(); } catch { throw new ApiError('Сервер вернул неожиданный формат данных.', 'INVALID_RESPONSE'); }
    if (!response.ok) {
      if (record(data) && record(data.error) && typeof data.error.message === 'string' && typeof data.error.code === 'string') throw new ApiError(data.error.message, data.error.code);
      throw new ApiError('Не удалось выполнить запрос. Попробуйте ещё раз.', 'HTTP_ERROR');
    }
    return data;
  }
  return {
    getCatalog: async (signal?: AbortSignal) => parseCatalog(await request('/api/catalog', undefined, signal)),
    simulateScenario: async (decisions: Decision[], signal?: AbortSignal) => parseSimulation(await request('/api/simulate', decisions, signal)),
    analyzeScenario: async (decisions: Decision[], signal?: AbortSignal) => parseAnalysis(await request('/api/analyze', decisions, signal)),
  };
}
export const { getCatalog, simulateScenario, analyzeScenario } = createApiClient();
