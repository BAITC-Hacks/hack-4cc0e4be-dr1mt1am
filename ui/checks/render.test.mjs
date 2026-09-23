import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createServer } from 'vite';
import { createElement } from 'react';
import { renderToString } from 'react-dom/server';
import { fixtures, analysis } from './fixtures.mjs';

test('React renders real API reference, validation, loading and AI panels', async () => {
  const server = await createServer({ server: { middlewareMode: true }, appType: 'custom' });
  try {
    const { default: App, Dashboard } = await server.ssrLoadModule('/src/App.tsx');
    const { CatalogProvider, presentCatalog } = await server.ssrLoadModule('/src/api/CatalogContext.tsx');
    const { Results, RequestStatus, AnalysisPanel } = await server.ssrLoadModule('/src/components/Results.tsx');
    const wrap = element => createElement(CatalogProvider, {value:presentCatalog(fixtures.catalog)}, element);
    const render = element => renderToString(element).replaceAll('<!-- -->', '');
    const loading = render(createElement(App));
    assert.match(loading, /role="status"/);
    assert.ok(loading.includes('Загружаем данные города'));
    const initial = render(wrap(createElement(Dashboard)));
    assert.ok(initial.includes('Аким на 5 часов'));
    assert.ok(initial.includes('52.56'));
    assert.ok(initial.includes('49.18'));
    assert.equal((initial.match(/class="critical-badge"/g) || []).length, 2);
    assert.equal((initial.match(/class="card initiative-card /g) || []).length, 14);
    assert.equal((initial.match(/<select/g) || []).length, 10);
    assert.equal((initial.match(/class="city-scope"/g) || []).length, 4);
    assert.match(initial, /<button class="primary" disabled="">Симулировать/);
    const results = render(wrap(createElement(Results, {result:fixtures.reference})));
    for (const expected of ['52.56','56.54','+3.99','95 / 100','2 → 0','Нура → Нура','M10 + M12 → Нура','52.96']) assert.ok(results.includes(expected), expected);
    const validation = render(createElement(RequestStatus, {errors:fixtures.invalid.errors}));
    assert.ok(validation.includes(fixtures.invalid.errors[0].message));
    assert.match(validation, /role="alert"/);
    assert.match(render(createElement(RequestStatus, {loading:true})), /role="status"/);
    const aiLoading = render(createElement(AnalysisPanel, {analysis:null,loading:true,error:'',onAnalyze:()=>{}}));
    assert.ok(aiLoading.includes('AI анализирует сценарий'));
    assert.match(aiLoading, /disabled=""/);
    const ai = render(createElement(AnalysisPanel, {analysis,loading:false,error:'',onAnalyze:()=>{}}));
    assert.ok(ai.includes(analysis.summary));
    for (const key of ['strengths','risks','tradeoffs','recommendations']) assert.ok(ai.includes(analysis[key][0]));
    const failedAI = render(wrap(createElement('div', null, createElement(Results, {result:fixtures.reference}), createElement(AnalysisPanel, {analysis:null,loading:false,error:'AI недоступен',onAnalyze:()=>{}}))));
    assert.ok(failedAI.includes('56.54'));
    assert.ok(failedAI.includes('AI недоступен'));
    const escaped = render(createElement(AnalysisPanel, {analysis:{...analysis,summary:'<script>unsafe()</script>'},loading:false,error:'',onAnalyze:()=>{}}));
    assert.ok(!escaped.includes('<script>unsafe()'));
  } finally { await server.close(); }
});
