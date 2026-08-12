// setup-local-model.mjs — 内网/本地模型一键配置（不碰 Control UI）
//
// 给"内网/离线"场景:用纯命令行问几个问题，直接写好 openclaw.json，
// 再当场实测能不能连上、能不能回话。全程不依赖会挂的 dashboard 网页。
// 支持两类本地/内网模型：
//   1) Ollama（本机，http://127.0.0.1:11434）
//   2) newapi / 任意 OpenAI 兼容中转（内网 IP + token）
//
// 写入只 merge 模型相关字段，保留 gateway 等原有配置；写前自动备份。
//
// 用法：node setup-local-model.mjs <CONFIG_PATH>

import { readFileSync, writeFileSync, existsSync, copyFileSync, mkdirSync } from 'node:fs';
import { dirname } from 'node:path';
import { createInterface } from 'node:readline/promises';
import { stdin as input, stdout as output } from 'node:process';
import http from 'node:http';
import https from 'node:https';

// 输入抽象：真控制台(TTY)走交互式 readline；被管道喂入(测试/脚本)则一次读完按行出队。
function makePrompter() {
  if (input.isTTY) {
    const rl = createInterface({ input, output });
    return {
      ask: async (q, def) => {
        const a = (await rl.question(`${q}${def ? ` [${def}]` : ''}: `)).trim();
        return a || def || '';
      },
      close: () => rl.close(),
    };
  }
  let queued = [];
  try { queued = readFileSync(0, 'utf8').split(/\r?\n/); } catch {}
  let i = 0;
  return {
    ask: async (q, def) => {
      const raw = (queued[i++] ?? '').trim();
      const val = raw || def || '';
      output.write(`${q}${def ? ` [${def}]` : ''}: ${val}\n`);
      return val;
    },
    close: () => {},
  };
}

const CHAT_TIMEOUT_MS = 30000;
function line(s = '') { output.write(s + '\n'); }
function withScheme(raw) { return /^[a-z][a-z0-9+.-]*:\/\//i.test(raw) ? raw : `http://${raw}`; }
function hostOf(raw) {
  try { return new URL(withScheme(String(raw).trim())).hostname || null; } catch { return null; }
}

function applyNoProxyFor(baseUrl) {
  const host = hostOf(baseUrl);
  const existing = (process.env.NO_PROXY || process.env.no_proxy || '')
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean);
  const merged = Array.from(new Set([...existing, 'localhost', '127.0.0.1', '::1', ...(host ? [host] : [])]));
  process.env.NO_PROXY = merged.join(',');
  process.env.no_proxy = process.env.NO_PROXY;
}

async function chatTest(baseUrl, apiKey, modelId) {
  applyNoProxyFor(baseUrl);
  const url = withScheme(baseUrl).replace(/\/+$/, '') + '/chat/completions';
  const started = Date.now();
  try {
    const res = await requestText(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...(apiKey ? { Authorization: `Bearer ${apiKey}` } : {}) },
      body: JSON.stringify({ model: modelId, messages: [{ role: 'user', content: '请回复四个字：连接成功' }], max_tokens: 64, stream: false }),
      timeoutMs: CHAT_TIMEOUT_MS,
    });
    const ms = Date.now() - started;
    const text = res.body;
    if (!res.ok) return { ok: false, status: res.status, body: text.slice(0, 300), ms };
    let reply = '';
    try { const j = JSON.parse(text); reply = j?.choices?.[0]?.message?.content ?? j?.choices?.[0]?.text ?? ''; }
    catch { reply = text.slice(0, 200); }
    return { ok: true, reply: String(reply).trim(), ms };
  } catch (err) {
    const ms = Date.now() - started;
    if (err?.code === 'ETIMEDOUT') return { ok: false, error: `ETIMEDOUT(>${CHAT_TIMEOUT_MS / 1000}s)`, ms };
    return { ok: false, error: `${err?.cause?.code || err?.code || err?.name || 'ERR'}: ${err?.message || ''}`, ms };
  }
}

function requestText(rawUrl, { method = 'GET', headers = {}, body, timeoutMs }) {
  return new Promise((resolve, reject) => {
    const u = new URL(rawUrl);
    const client = u.protocol === 'https:' ? https : http;
    const req = client.request(u, { method, headers }, (res) => {
      const chunks = [];
      res.on('data', (chunk) => chunks.push(chunk));
      res.on('end', () => {
        const text = Buffer.concat(chunks).toString('utf8');
        resolve({ ok: res.statusCode >= 200 && res.statusCode < 300, status: res.statusCode, body: text });
      });
    });
    req.setTimeout(timeoutMs, () => {
      const err = new Error('request timed out');
      err.code = 'ETIMEDOUT';
      req.destroy(err);
    });
    req.on('error', reject);
    if (body) req.write(body);
    req.end();
  });
}

async function main() {
  const configPath = process.argv[2] || process.env.OPENCLAW_CONFIG_PATH;
  if (!configPath) { line('用法: node setup-local-model.mjs <CONFIG_PATH>'); process.exitCode = 2; return; }

  line('========================================');
  line('  Z-Claw 内网/本地模型 一键配置');
  line('========================================');
  line('');

  const rl = makePrompter();
  const ask = rl.ask;

  try {
    line('选择模型类型：');
    line('  1) Ollama（本机部署，http://127.0.0.1:11434）');
    line('  2) newapi / 其它 OpenAI 兼容中转（内网 IP + token）');
    const kind = await ask('输入 1 或 2', '1');

    let providerKey, baseUrl, apiKey, modelId;
    if (kind === '2') {
      providerKey = 'newapi';
      line('');
      line('提示：baseUrl 通常形如 http://192.168.1.50:3000/v1（注意大多要带 /v1）');
      baseUrl = await ask('newapi 地址 baseUrl', 'http://192.168.1.50:3000/v1');
      apiKey = await ask('token / API Key', '');
      modelId = await ask('模型 ID（管理员给的，如 deepseek-v3）', '');
    } else {
      providerKey = 'ollama';
      line('');
      baseUrl = await ask('Ollama 地址（一般本机默认即可）', 'http://127.0.0.1:11434/v1');
      // Ollama 的 OpenAI 兼容端点在 /v1；自动补上
      if (!/\/v1\/?$/.test(baseUrl)) baseUrl = baseUrl.replace(/\/+$/, '') + '/v1';
      apiKey = 'ollama'; // 本地占位 key，任意值即可
      modelId = await ask('模型名（先用 ollama list 查，如 qwen2.5 / llama3.1）', 'qwen2.5');
    }

    if (!baseUrl || !modelId) { line(''); line('地址或模型 ID 为空，已取消。'); process.exitCode = 2; return; }

    // 读取并合并现有配置（保留 gateway 等），写前备份
    let config = {};
    if (existsSync(configPath)) {
      try { config = JSON.parse(readFileSync(configPath, 'utf8')); }
      catch { config = {}; }
      try { copyFileSync(configPath, configPath + '.bak'); } catch {}
    } else {
      try { mkdirSync(dirname(configPath), { recursive: true }); } catch {}
    }

    config.gateway ||= { mode: 'local', auth: { token: 'zclaw' } };
    config.models ||= {};
    config.models.mode = 'merge';
    config.models.providers ||= {};
    config.models.providers[providerKey] = {
      baseUrl,
      apiKey,
      api: 'openai-completions',
      models: [{ id: modelId, name: modelId }],
    };
    config.agents ||= {};
    config.agents.defaults ||= {};
    config.agents.defaults.model ||= {};
    config.agents.defaults.model.primary = `${providerKey}/${modelId}`;

    writeFileSync(configPath, JSON.stringify(config, null, 2), 'utf8');
    line('');
    line(`✓ 已写入配置：${configPath}`);
    line(`  provider=${providerKey}  baseUrl=${baseUrl}  model=${modelId}`);
    if (existsSync(configPath + '.bak')) line(`  （原配置已备份为 openclaw.json.bak）`);
    line('');

    // 当场实测
    line('正在实测：发一条对话给模型...');
    const r = await chatTest(baseUrl, apiKey, modelId);
    line('');
    if (r.ok) {
      line(`✓✓ 跑通了！模型回复 (${r.ms}ms)：${r.reply.slice(0, 120) || '(空回复但请求成功)'}`);
      line('');
      line('配置完成。现在双击 Windows-Start.bat 即可正常使用（对话可走 CLI 或 Dashboard）。');
    } else if (r.status) {
      line(`✗ 服务端 HTTP ${r.status} (${r.ms}ms)：${r.body}`);
      line('');
      if (r.status === 401 || r.status === 403) line('→ 网络通，但 token / key 不对（Ollama 可忽略鉴权，newapi 请核对 token）。');
      else if (r.status === 404) line('→ 网络通，但路径或模型 ID 不对（检查 baseUrl 是否要带 /v1、模型名是否正确）。');
      else line('→ 网络通，服务端报错，把上面内容发管理员。');
    } else {
      const host = (() => { try { return new URL(withScheme(baseUrl)).hostname; } catch { return baseUrl; } })();
      line(`✗ 连不上：${r.error} (${r.ms}ms)`);
      line('');
      if (providerKey === 'ollama') {
        line('→ 本机 Ollama 没连上，多半是 Ollama 没启动或模型没拉。请在本机执行：');
        line('    ollama serve            （启动服务，若已是后台服务可跳过）');
        line(`    ollama pull ${modelId}   （把模型拉到本地，离线需提前准备好）`);
        line('  然后重新运行本工具。');
      } else {
        line('→ 是地址错 / 内网不通 / 防火墙 / 模型服务没起。');
        line('  在这台机器上自测：');
        line(`    ping ${host}`);
        line('  让机房管理员确认 IP、端口、防火墙放行。');
      }
    }
  } finally {
    rl.close();
  }
}

main();
