import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createApiClient, parseCatalog, parseSimulation, parseAnalysis } from '../src/api/client.ts';
import { fixtures, analysis } from './fixtures.mjs';

test('API client loads catalog and posts only decisions to simulation and analysis', async () => {
  const requests = [];
  const bodies = [fixtures.catalog, fixtures.reference, analysis];
  const api = createApiClient('http://example.invalid/', async (url, options) => {
    requests.push({url, options}); return Response.json(bodies.shift());
  });
  assert.deepEqual(await api.getCatalog(), fixtures.catalog);
  assert.deepEqual(await api.simulateScenario(fixtures.decisions), fixtures.reference);
  assert.deepEqual(await api.analyzeScenario(fixtures.decisions), analysis);
  assert.deepEqual(requests.map(item => item.url), ['http://example.invalid/api/catalog', 'http://example.invalid/api/simulate', 'http://example.invalid/api/analyze']);
  for (const item of requests.slice(1)) {
    assert.deepEqual(JSON.parse(item.options.body), {decisions: fixtures.decisions});
    assert.equal(item.options.method, 'POST');
    assert.deepEqual(item.options.headers, {'Content-Type':'application/json'});
  }
});
test('validation errors are retained without a fabricated score', async () => {
  const api = createApiClient('http://example.invalid', async () => Response.json(fixtures.invalid));
  const result = await api.simulateScenario([]);
  assert.equal(result.valid, false);
  assert.deepEqual(result.errors, fixtures.invalid.errors);
  assert.equal('score_after' in result, false);
  assert.deepEqual(await api.analyzeScenario([]), fixtures.invalid);
});
test('network failures are controlled without leaking raw errors', async () => {
  const api = createApiClient('http://example.invalid', async () => { throw new Error('raw-sensitive-transport-details'); });
  await assert.rejects(api.getCatalog(), error => error.code === 'NETWORK_ERROR' && !error.message.includes('raw-sensitive'));
});
test('AI controlled error and unstructured HTTP failure are handled', async () => {
  const missing = createApiClient('http://example.invalid', async () => Response.json({error:{code:'API_KEY_MISSING',message:'AI недоступен'}}, {status:503}));
  await assert.rejects(missing.analyzeScenario(fixtures.decisions), error => error.code === 'API_KEY_MISSING' && error.message === 'AI недоступен');
  const failed = createApiClient('http://example.invalid', async () => Response.json({private:'do-not-display'}, {status:500}));
  await assert.rejects(failed.getCatalog(), error => error.code === 'HTTP_ERROR' && !error.message.includes('do-not-display'));
});
test('malformed API data is rejected', async () => {
  for (const [parse, value] of [[parseCatalog, {}], [parseSimulation, {valid:true,score_after:'56.54'}], [parseAnalysis, {...analysis,strengths:42}]]) {
    assert.throws(() => parse(value), error => error.code === 'INVALID_RESPONSE');
  }
  const api = createApiClient('http://example.invalid', async () => new Response('not json'));
  await assert.rejects(api.getCatalog(), error => error.code === 'INVALID_RESPONSE');
});
test('AbortSignal is passed to transport and cancellation is preserved', async () => {
  const controller = new AbortController(); controller.abort();
  const api = createApiClient('http://example.invalid', async (_url, options) => {
    assert.equal(options.signal, controller.signal); throw new DOMException('Aborted', 'AbortError');
  });
  await assert.rejects(api.simulateScenario(fixtures.decisions, controller.signal), error => error.name === 'AbortError');
});
