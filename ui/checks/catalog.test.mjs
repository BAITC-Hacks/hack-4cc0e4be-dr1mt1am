import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { parseCatalog, parseSimulation } from '../src/api/client.ts';
import { fixtures } from './fixtures.mjs';

test('catalog parser accepts authoritative API districts, initiatives and metadata', () => {
  const catalog = parseCatalog(fixtures.catalog);
  assert.equal(catalog.districts.length, 5);
  assert.equal(catalog.initiatives.length, 14);
  assert.equal(catalog.baseline_score, 52.55768);
  assert.equal(catalog.budget, 100);
  assert.equal(catalog.required_decisions, 5);
  for (const district of catalog.districts) {
    assert.deepEqual(district.indicators, catalog.baseline_indicators[district.id]);
    assert.equal(district.score, catalog.baseline_district_scores[district.id]);
    assert.equal(district.populationShare, catalog.population_shares[district.id]);
  }
  assert.equal(catalog.initiatives.find(item => item.id === 'M7').cost, 24);
});
test('frontend retains labels but no authoritative numerical catalog mirror', () => {
  const source = readFileSync(new URL('../src/data/catalog.ts', import.meta.url), 'utf8');
  assert.doesNotMatch(source, /BASELINE_SCORE|export const BUDGET|cost\s*:|lag\s*:|effects\s*:|score\s*:|populationShare\s*:/);
});
test('reference response retains precision, counts, budget and synergy', () => {
  const result = parseSimulation(fixtures.reference);
  assert.equal(result.valid, true);
  assert.equal(result.score_after, 56.54307);
  assert.equal(result.score_after.toFixed(2), '56.54');
  assert.equal(result.score_delta.toFixed(2), '3.99');
  assert.equal(result.budget_used, 95);
  assert.equal(result.budget_remaining, 5);
  assert.deepEqual([result.n_crit_before, result.n_crit_after], [2, 0]);
  assert.equal(result.weakest_district_after, 'Nura');
  assert.equal(result.triggered_synergies[0].synergy.first_initiative_id, 'M10');
  assert.equal(result.triggered_synergies[0].synergy.second_initiative_id, 'M12');
  assert.equal(result.triggered_synergies[0].district, 'Nura');
});
