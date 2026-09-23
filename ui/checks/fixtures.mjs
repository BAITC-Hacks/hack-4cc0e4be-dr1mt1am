// Generate contract fixtures from the actual Python API in memory, never OpenAI.
import { execFileSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { resolve } from 'node:path';
const root = fileURLToPath(new URL('../../', import.meta.url));
const venv = resolve(root, process.platform === 'win32' ? '.venv/Scripts/python.exe' : '.venv/bin/python');
const python = process.env.PYTHON || (existsSync(venv) ? venv : 'python');
export const fixtures = JSON.parse(execFileSync(python, ['-B', '-c', `
import json
from fastapi.testclient import TestClient
from api.app import app
decisions = [dict(initiative_id=i, district=d) for i,d in [('M7','Nura'),('M8','Nura'),('M10','Nura'),('M12',None),('M5','Saryarka')]]
with TestClient(app) as client:
    print(json.dumps({'catalog':client.get('/api/catalog').json(), 'decisions':decisions,
      'reference':client.post('/api/simulate',json={'decisions':decisions}).json(),
      'invalid':client.post('/api/simulate',json={'decisions':[]}).json()},ensure_ascii=True))
`], { cwd: root, encoding: 'utf8' }));
export const analysis = {
  summary: 'Score вырос на 3.99; число критических показателей снизилось с 2 до 0.',
  strengths: ['Улучшилась социальная инфраструктура Нуры.'], risks: ['Транспорт остаётся слабым местом.'],
  tradeoffs: ['В наборе нет транспортных инициатив.'], recommendations: ['Проверить альтернативный набор из пяти мер.'],
};
