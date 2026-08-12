// 发版辅助：生成 latest.json 用于上传到阿里云 OSS
//
// 用法（在仓库根目录跑）：
//   node portable/lib/publish-latest.mjs
//   node portable/lib/publish-latest.mjs --notes "修复了 xxx"
//
// 输出：
//   - dist/latest.json — 你手动（或 ossutil）上传到 OSS 的同一个路径
//
// 上传命令示例（自己装 ossutil 后用）：
//   ossutil cp dist/latest.json oss://Z-Claw-oss/Z-Claw-open/latest.json
//
// 这个脚本不直接调 OSS，避免硬编码 access key。把生成 + 上传分开，发版人自己负责上传。

import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(__dirname, '../..');

// 默认 OSS 路径前缀（你可以改成自己的 bucket / domain）
const DEFAULT_OSS_BASE = 'https://Z-Claw-oss.56chat.cn/Z-Claw-open';
const GH_RELEASES_BASE = 'https://github.com/aikeeper-zk/AIbox';

function parseArgs(argv) {
  const args = { notes: '', ossBase: DEFAULT_OSS_BASE };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--notes' || a === '-n') args.notes = argv[++i] || '';
    else if (a === '--oss-base') args.ossBase = argv[++i] || DEFAULT_OSS_BASE;
    else if (a === '--help' || a === '-h') {
      process.stdout.write([
        'Usage: node portable/lib/publish-latest.mjs [options]',
        '  --notes "<text>"      Release notes (single line)',
        '  --oss-base <url>      OSS public URL prefix (default: ' + DEFAULT_OSS_BASE + ')',
        '  --help                Show this help',
        '',
        'Output: dist/latest.json — upload it to <oss-base>/latest.json',
      ].join('\n') + '\n');
      process.exit(0);
    }
  }
  return args;
}

function readVersion() {
  const versionFile = resolve(REPO_ROOT, 'OPENCLAW_VERSION');
  if (!existsSync(versionFile)) {
    throw new Error(`OPENCLAW_VERSION file not found at ${versionFile}`);
  }
  const v = readFileSync(versionFile, 'utf8').trim();
  if (!v) throw new Error('OPENCLAW_VERSION is empty');
  return v;
}

function todayIso() {
  const d = new Date();
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd}`;
}

function main() {
  const args = parseArgs(process.argv);
  const version = readVersion();
  const tag = `v${version}`;

  // Naming convention matches release.yml:
  // dist/Z-Claw-portable-${tag_name}.zip
  const zipName = `Z-Claw-portable-${tag}.zip`;
  const downloadUrl = `${args.ossBase}/${zipName}`;
  const releasePageUrl = `${GH_RELEASES_BASE}/tag/${tag}`;

  const manifest = {
    version,
    releaseDate: todayIso(),
    downloadUrl,
    releasePageUrl,
    notes: args.notes || '',
    // Mirror fallback if user wants — check-update.mjs only looks at the top-level fields
    mirrors: {
      oss: downloadUrl,
      github: `${releasePageUrl}/${zipName}`,
    },
  };

  const distDir = resolve(REPO_ROOT, 'dist');
  if (!existsSync(distDir)) mkdirSync(distDir, { recursive: true });
  const outFile = resolve(distDir, 'latest.json');
  writeFileSync(outFile, JSON.stringify(manifest, null, 2) + '\n', 'utf8');

  process.stdout.write(`\nGenerated: ${outFile}\n`);
  process.stdout.write(`Version:   ${version}\n`);
  process.stdout.write(`Download:  ${downloadUrl}\n`);
  process.stdout.write('\nNext steps (manual):\n');
  process.stdout.write(`  1. Upload portable zip to OSS: ${args.ossBase}/${zipName}\n`);
  process.stdout.write(`  2. Upload latest.json to OSS:  ${args.ossBase}/latest.json\n`);
  process.stdout.write('\nExample (with ossutil):\n');
  process.stdout.write(`  ossutil cp dist/${zipName} oss://<your-bucket>/Z-Claw-open/${zipName}\n`);
  process.stdout.write(`  ossutil cp dist/latest.json oss://<your-bucket>/Z-Claw-open/latest.json\n`);
  process.stdout.write('\nVerify after upload:\n');
  process.stdout.write(`  curl -s ${args.ossBase}/latest.json | head -20\n\n`);
}

try {
  main();
} catch (err) {
  process.stderr.write(`publish-latest error: ${err.message}\n`);
  process.exit(1);
}
