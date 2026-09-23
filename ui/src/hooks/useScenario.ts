import { useEffect, useRef, useState } from 'react';
import { analyzeScenario, ApiError, simulateScenario } from '../api/client';
import type { AIAnalysis, SimulationResult, ValidationIssue } from '../api/types';
import type { Decision } from '../types';

export function useScenario(decisions: Decision[]) {
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [analysis, setAnalysis] = useState<AIAnalysis | null>(null);
  const [errors, setErrors] = useState<ValidationIssue[]>([]);
  const [error, setError] = useState('');
  const [aiError, setAIError] = useState('');
  const [loading, setLoading] = useState(false);
  const [aiLoading, setAILoading] = useState(false);
  const pending = useRef<AbortController | null>(null);
  useEffect(() => () => pending.current?.abort(), []);

  function clearResults() {
    pending.current?.abort(); pending.current = null;
    setResult(null); setAnalysis(null); setErrors([]); setError(''); setAIError('');
    setLoading(false); setAILoading(false);
  }
  async function runSimulation() {
    if (pending.current) return;
    clearResults();
    const request = new AbortController(); pending.current = request; setLoading(true);
    try {
      const response = await simulateScenario(decisions, request.signal);
      if (pending.current !== request || request.signal.aborted) return;
      if (response.valid) setResult(response); else setErrors(response.errors);
    } catch (cause) {
      if (pending.current === request && !request.signal.aborted) setError(cause instanceof ApiError ? cause.message : 'Не удалось выполнить симуляцию.');
    } finally {
      if (pending.current === request) { pending.current = null; setLoading(false); }
    }
  }
  async function runAnalysis() {
    if (pending.current || !result || analysis) return;
    const request = new AbortController(); pending.current = request;
    setAILoading(true); setAIError('');
    try {
      const response = await analyzeScenario(decisions, request.signal);
      if (pending.current !== request || request.signal.aborted) return;
      if ('valid' in response) setErrors(response.errors); else setAnalysis(response);
    } catch (cause) {
      if (pending.current === request && !request.signal.aborted) setAIError(cause instanceof ApiError ? cause.message : 'Не удалось получить AI-анализ. Результаты симуляции сохранены.');
    } finally {
      if (pending.current === request) { pending.current = null; setAILoading(false); }
    }
  }
  return { result, analysis, errors, error, aiError, loading, aiLoading, clearResults, runSimulation, runAnalysis };
}
