// resolve-no-proxy.mjs — 让"内网/自建模型地址"绕开系统代理
//
// 背景（内网环境最大的坑）：
//   很多公司/机房的机器设置了 HTTP_PROXY / HTTPS_PROXY 环境变量（为了上外网）。
//   OpenClaw 启动时若检测到这两个变量，会 setGlobalDispatcher(new EnvHttpProxyAgent())，
//   于是"所有" fetch——包括调用用户自己填的模型 baseUrl——都被塞进公司代理。
//   当模型部署在内网（如 http://10.x / 192.168.x / 某机房 IP）时，代理够不着那台机器，
//   请求直接失败。表现：互联网能连公网模型、reasonix/copilot 也能连内网，唯独本程序连不上。
//   见 openclaw dist/auth-profiles-*.js 的 ensureGlobalUndiciEnvProxyDispatcher()。
//
// 方案：undici 的 EnvHttpProxyAgent 认 NO_PROXY。把用户配置里所有模型 baseUrl 的主机名
//   （IP 或域名）+ 本机回环地址，统一写进 NO_PROXY，让这些地址"直连不走代理"。
//   纯增量、绝对安全：自建/内网模型本就不该走代理；没设代理时 NO_PROXY 也无副作用。
//
// 设计原则：静默失败。任何一步出错就不输出，启动照常（只是少了这层保护）。
//
// CLI 用法（供 .bat / .command source）：
//   node resolve-no-proxy.mjs <CONFIG_PATH>
// 输出（无代理需要保护时不输出任何内容）：
//   zclaw_NO_PROXY=localhost,127.0.0.1,::1,15.151.114.142,...

import { readFileSync } from 'node:fs';

// 始终直连的本机地址。
const ALWAYS = ['localhost', '127.0.0.1', '::1'];

// 从一个 baseUrl 字符串里抽出主机名（IP 或域名）。容错：解析不了就忽略。
function hostOf(raw) {
  if (typeof raw !== 'string') return null;
  const trimmed = raw.trim();
  if (!trimmed) return null;
  try {
    // 补协议，URL() 才能解析 "host:port/v1" 这种缺协议的写法。
    const withScheme = /^[a-z][a-z0-9+.-]*:\/\//i.test(trimmed) ? trimmed : `http://${trimmed}`;
    const host = new URL(withScheme).hostname; // 自动去掉 IPv6 的方括号
    return host || null;
  } catch {
    return null;
  }
}

// 递归收集对象里所有 baseUrl 字段的主机名（providers 可能嵌套/命名各异，宽松收集最稳）。
function collectHosts(node, out) {
  if (!node || typeof node !== 'object') return;
  if (Array.isArray(node)) {
    for (const item of node) collectHosts(item, out);
    return;
  }
  for (const [key, value] of Object.entries(node)) {
    if (key === 'baseUrl' || key === 'baseURL') {
      const h = hostOf(value);
      if (h) out.add(h);
    } else if (value && typeof value === 'object') {
      collectHosts(value, out);
    }
  }
}

function main() {
  const configPath = process.argv[2] || process.env.OPENCLAW_CONFIG_PATH;
  if (!configPath) return;

  let config;
  try {
    config = JSON.parse(readFileSync(configPath, 'utf8'));
  } catch {
    return; // 配置不存在/坏了：不输出，启动照常
  }

  const hosts = new Set();
  collectHosts(config?.models, hosts);

  // 合并已有的 NO_PROXY，避免覆盖用户/系统已有设置。
  const existing = (process.env.NO_PROXY || process.env.no_proxy || '')
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean);

  const merged = Array.from(new Set([...existing, ...ALWAYS, ...hosts]));
  // 没有任何模型主机、又没有已有 NO_PROXY 时，只剩本机回环，输出也无害——但为简洁，
  // 仅当收集到了真实模型主机时才输出（本机回环本就不会被代理误伤到业务）。
  if (hosts.size === 0 && existing.length === 0) return;

  process.stdout.write(`zclaw_NO_PROXY=${merged.join(',')}\n`);
}

main();
