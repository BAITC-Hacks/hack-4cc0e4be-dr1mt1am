import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { districts, initiatives, BASELINE_SCORE, BUDGET, REQUIRED_DECISIONS } from '../src/data/catalog.ts';

const source = readFileSync(new URL('../../engine/data.py', import.meta.url), 'utf8');
test('all five district baseline records match Python static data', () => {
  const entries = [...source.matchAll(/"(Esil|Almaty|Saryarka|Baikonur|Nura)": District\(([\s\S]*?)baseline_district_score=([\d.]+),/g)];
  assert.equal(entries.length, 5);
  assert.equal(districts.length, entries.length);
  for (const [, id, body, score] of entries) {
    const district = districts.find(item => item.id === id);
    assert.ok(district, id);
    assert.equal(district.score, Number(score), id);
    assert.equal(district.populationShare, Number(body.match(/population_share=([\d.]+)/)[1]), id);
    const indicators = Object.fromEntries([...body.matchAll(/"([TESBC][12])": (\d+)/g)].map(([,key,value])=>[key,Number(value)]));
    assert.deepEqual(district.indicators, indicators, id);
  }
});
test('all 14 initiatives match Python costs, lags, effects, direction and scope', () => {
  const entries = [...source.matchAll(/"(M\d+)": Initiative\(([\s\S]*?)(?=\n    "M|\n\}\))/g)];
  assert.equal(entries.length, 14);
  assert.equal(initiatives.length, entries.length);
  for (const [,id,body] of entries) {
    const item=initiatives.find(item=>item.id===id);
    assert.ok(item,id);
    assert.equal(item.cost,Number(body.match(/cost=(\d+)/)[1]),id);
    assert.equal(item.lag,Number(body.match(/lag=(\d+)/)[1]),id);
    assert.equal(item.type.toUpperCase(),body.match(/InitiativeType\.(\w+)/)[1],id);
    assert.equal(item.direction.toUpperCase(),body.match(/Direction\.(\w+)/)[1],id);
    assert.deepEqual(item.effects,[...body.matchAll(/InitiativeEffect\("(\w+)", (-?\d+)\)/g)].map(([,key,value])=>[key,Number(value)]),id);
  }
});
test('presentation constants and reference selection cost are preserved', () => {
  const constants=readFileSync(new URL('../../engine/constants.py',import.meta.url),'utf8');
  assert.equal(BUDGET,Number(constants.match(/BUDGET: Final\[int\] = (\d+)/)[1]));
  assert.equal(REQUIRED_DECISIONS,Number(constants.match(/REQUIRED_DECISION_COUNT: Final\[int\] = (\d+)/)[1]));
  assert.equal(BASELINE_SCORE,52.55768);
  assert.equal(BASELINE_SCORE.toFixed(2),'52.56');
  assert.equal(initiatives.filter(item=>['M7','M8','M10','M12','M5'].includes(item.id)).reduce((sum,item)=>sum+item.cost,0),95);
});
