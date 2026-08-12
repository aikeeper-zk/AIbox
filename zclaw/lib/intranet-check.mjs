// intranet-check.mjs — 内网一体化体检（代理 + 可达性 + 真发对话）
//
// 把"代理环境 / NO_PROXY 建议 / 直连可达 / 端到端发一条对话"全做在一个 Node 脚本里，
// 这样 .bat 只需一行 `node intranet-check.mjs <cfg>`，没有任何 cmd 解析坑（中文、for/f、
// 转义都不沾），最稳。所有中文提示由 Node 打印（chcp 65001 下正常显示）。
//
// 用法：node intranet-check.mjs <CONFIG_PATH>

import { readFileSync } from 'node:fs';
import http from 'node:http';
import https from 'node:https';

const REACH_TIMEOUT_MS = 8000;
const CHAT_TIMEOUT_MS = 30000;
const ALWAYS = ['localhost', '127.0.0.1', '::1'];
function line(s = '') { process.stdout.write(s + '\n'); }

function applyNoProxy(hosts) {
  const existing = (process.env.NO_PROXY || process.env.no_proxy || '')
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean);
  const merged = Array.from(new Set([...existing, ...ALWAYS, ...hosts]));
  process.env.NO_PROXY = merged.join(',');
  process.env.no_proxy = process.env.NO_PROXY;
  return merged;
}

function withScheme(raw) {
  return /^[a-z][a-z0-9+.-]*:\/\//i.test(raw) ? raw : `http://${raw}`;
}
function hostOf(raw) {
  try { return new URL(withScheme(String(raw).trim())).hostname || null; } catch { return null; }
}
function collectProviders(models) {
  const out = [];
  const providers = models?.providers;
  if (providers && typeof providers === 'object') {
    for (const [name, p] of Object.entries(providers)) {
      const baseUrl = p?.baseUrl || p?.baseURL;
      if (typeof baseUrl === 'string' && baseUrl.trim()) {
        out.push({ name, baseUrl: baseUrl.trim(), apiKey: typeof p?.apiKey === 'string' ? p.apiKey : '' });
      }
    }
  }
  return out;
}
function pickTarget(config, providers) {
  const primary = config?.agents?.defaults?.model?.primary;
  if (typeof primary === 'string' && primary.includes('/')) {
    const provName = primary.slice(0, primary.indexOf('/'));
    const modelId = primary.slice(primary.indexOf('/') + 1);
    const p = config?.models?.providers?.[provName];
    if (p?.baseUrl || p?.baseURL) {
      return { provName, modelId, baseUrl: (p.baseUrl || p.baseURL).trim(), apiKey: p.apiKey || '' };
    }
  }
  for (const pr of providers) {
    const p = config?.models?.providers?.[pr.name];
    const modelId = Array.isArray(p?.models) && p.models[0]?.id ? p.models[0].id : undefined;
    if (modelId) return { provName: pr.name, modelId, baseUrl: pr.baseUrl, apiKey: pr.apiKey };
  }
  return null;
}

async function reachProbe(baseUrl, apiKey) {
  const url = withScheme(baseUrl).replace(/\/+$/, '') + '/models';
  const started = Date.now();
  try {
    const res = await requestText(url, { headers: apiKey ? { Authorization: `Bearer ${apiKey}` } : {}, timeoutMs: REACH_TIMEOUT_MS });
    return { ok: true, status: res.status, ms: Date.now() - started };
  } catch (err) {
    const ms = Date.now() - started;
    if (err?.code === 'ETIMEDOUT') return { ok: false, error: `ETIMEDOUT(>${REACH_TIMEOUT_MS / 1000}s)`, ms };
    return { ok: false, error: err?.cause?.code || err?.code || err?.name || 'ERR', ms };
  }
}

async function chatProbe(t) {
  const url = withScheme(t.baseUrl).replace(/\/+$/, '') + '/chat/completions';
  const started = Date.now();
  try {
    const res = await requestText(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...(t.apiKey ? { Authorization: `Bearer ${t.apiKey}` } : {}) },
      body: JSON.stringify({ model: t.modelId, messages: [{ role: 'user', content: '请回复四个字：连接成功' }], max_tokens: 64, stream: false }),
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
  line('========================================');
  line('  Z-Claw 内网体检 / Intranet Check');
  line(`  Node ${process.version}`);
  line('========================================');
  line('');

  // 1) 代理环境
  line('【1】代理环境检查');
  const proxyKeys = ['HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'http_proxy', 'https_proxy', 'all_proxy'];
  const setProxies = proxyKeys.filter((k) => process.env[k]);
  if (setProxies.length) {
    for (const k of setProxies) line(`    ${k} = ${process.env[k]}`);
    line('    → 检测到系统代理。发往内网模型的请求可能被它劫持（最常见的内网故障源）。');
  } else {
    line('    （未检测到系统代理）');
  }
  line('');

  if (!configPath) { line('未提供配置路径，结束。'); return; }
  let config;
  try { config = JSON.parse(readFileSync(configPath, 'utf8')); }
  catch (e) { line(`读取配置失败：${e?.message || e}`); return; }

  const providers = collectProviders(config?.models);
  if (!providers.length) { line('配置里没有任何模型地址（baseUrl）。先配好模型再来跑。'); return; }

  // 2) NO_PROXY 建议
  const hosts = Array.from(new Set(providers.map((p) => hostOf(p.baseUrl)).filter(Boolean)));
  const noProxy = applyNoProxy(hosts);
  line('【2】建议的 NO_PROXY（让这些地址直连、绕开代理）');
  line(`    ${noProxy.join(',')}`);
  line('    （新版 Windows-Start.bat 已会自动设置，无需手动操作）');
  line('');

  // 3) 直连可达
  line('【3】直连测试（绕过代理，看能否摸到模型服务）');
  for (const p of providers) {
    const r = await reachProbe(p.baseUrl, p.apiKey);
    if (r.ok) line(`    [${p.name}] ${p.baseUrl}  →  ✓ 可达 HTTP ${r.status} (${r.ms}ms)`);
    else line(`    [${p.name}] ${p.baseUrl}  →  ✗ 失败 ${r.error} (${r.ms}ms)`);
  }
  line('');

  // 4) 端到端实测
  line('【4】实测：真发一条对话给模型');
  const t = pickTarget(config, providers);
  if (!t) { line('    找不到可测的模型 id，跳过。'); }
  else {
    line(`    模型：${t.provName} / ${t.modelId}`);
    line('    发送中，请稍候...');
    const c = await chatProbe(t);
    if (c.ok) {
      line('');
      line(`    ✓✓ 跑通了！模型回复 (${c.ms}ms)：${c.reply.slice(0, 120) || '(空回复但请求成功)'}`);
    } else if (c.status) {
      line('');
      line(`    ✗ 服务端 HTTP ${c.status} (${c.ms}ms)：${c.body}`);
    } else {
      line('');
      line(`    ✗ 直连失败：${c.error} (${c.ms}ms)`);
    }
  }
  line('');

  // 结论
  line('========================================');
  line('  怎么看结果：');
  line('  · 第4步「跑通了」      → 一切正常，以后双击 Windows-Start.bat 即可。');
  line('  · 第3步可达但程序里用不了 → 是系统代理在劫持，新版启动脚本已自动绕开（NO_PROXY）。');
  line('  · 第3步「直连失败/超时」 → 地址错 / 内网不通 / 防火墙 / 模型服务没起，找机房管理员。');
  line('  · 出现 401/403         → 网络是通的，只是 API Key 不对。');
  line('========================================');
}

main();
