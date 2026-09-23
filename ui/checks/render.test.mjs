import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createServer } from 'vite';
import { createElement } from 'react';
import { renderToString } from 'react-dom/server';

test('dashboard renders baseline, 14 cards and accessible initial controls', async () => {
  const server = await createServer({ server: { middlewareMode: true }, appType: 'custom' });
  try {
    const { default: App } = await server.ssrLoadModule('/src/App.tsx');
    const html = renderToString(createElement(App));
    assert.ok(html.includes('Аким на 5 часов'));
    assert.ok(html.includes('52.56'));
    assert.ok(html.includes('49.18'));
    assert.equal((html.match(/class="critical-badge"/g) || []).length, 2);
    assert.equal((html.match(/class="card initiative-card /g) || []).length, 14);
    assert.equal((html.match(/<select/g) || []).length, 10);
    assert.equal((html.match(/class="city-scope"/g) || []).length, 4);
    assert.match(html, /<button class="primary" disabled="">Симулировать/);
  } finally {
    await server.close();
  }
});
