/**
 * L0: ODD 플러그인의 구조적 무결성을 자동으로 검증한다
 * L1: 필수 파일 존재 확인 + hooks.json 등록-파일 일관성 체크
 * L2: existsSync로 파일 체크, hooks.json 파싱으로 훅 수 비교
 * L3: Node.js ESM — node verify.js 로 실행
 */
import { existsSync, readFileSync, readdirSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

// ─── 1. 필수 파일 존재 확인 ────────────────────────────────────────────────
const requiredFiles = [
  'docs/.vitepress/config.ts',
  'CLAUDE.md',
  'README.md',
  'skills/pyramid-ontology/SKILL.md',
  'skills/ontology-detach/SKILL.md',
  '.github/workflows/deploy.yml',
  'hooks/hooks.json',
  'tests/test_hooks.py',
  '.github/workflows/test.yml',
];

let hasError = false;

console.log('=== ODD Plugin Verification ===\n');
console.log('── Required files ──');
for (const f of requiredFiles) {
  const full = resolve(__dirname, f);
  if (!existsSync(full)) {
    console.error(`✗ MISSING: ${f}`);
    hasError = true;
  } else {
    console.log(`✓ ${f}`);
  }
}

// ─── 2. hooks.json 등록-파일 일관성 체크 ───────────────────────────────────
console.log('\n── Hook registry consistency ──');

const hooksJsonPath = resolve(__dirname, 'hooks', 'hooks.json');
const hooksDirPath  = resolve(__dirname, 'hooks');

if (!existsSync(hooksJsonPath)) {
  console.error('✗ hooks/hooks.json 없음 — 훅 레지스트리 없음');
  hasError = true;
} else {
  let hooksData;
  try {
    hooksData = JSON.parse(readFileSync(hooksJsonPath, 'utf-8'));
  } catch (e) {
    console.error(`✗ hooks/hooks.json 파싱 실패: ${e.message}`);
    hasError = true;
    hooksData = null;
  }

  if (hooksData) {
    // 등록된 훅 파일명 추출
    const registered = new Set();
    const HOOK_PY_RE = /hooks[\\/](\w+\.py)/;

    for (const phaseHooks of Object.values(hooksData.hooks || {})) {
      if (!Array.isArray(phaseHooks)) continue;
      for (const entry of phaseHooks) {
        if (!entry || typeof entry !== 'object') continue;
        for (const h of entry.hooks || []) {
          const cmd = h.command || '';
          const m   = HOOK_PY_RE.exec(cmd);
          if (m) registered.add(m[1]);
        }
      }
    }

    // hooks/ 폴더의 실제 .py 파일 목록
    let pyFiles;
    try {
      pyFiles = readdirSync(hooksDirPath).filter(f => f.endsWith('.py'));
    } catch (e) {
      console.error(`✗ hooks/ 폴더 읽기 실패: ${e.message}`);
      pyFiles = [];
      hasError = true;
    }
    const pyFileSet = new Set(pyFiles);

    // 등록됐지만 파일 없는 것
    const missingFiles = [...registered].filter(name => !pyFileSet.has(name));
    // 파일은 있지만 등록 안 된 것 (참고용 — 경고만)
    const unregistered = pyFiles.filter(name => !registered.has(name));

    console.log(`  hooks.json 등록 훅: ${registered.size}개`);
    console.log(`  hooks/*.py 파일:    ${pyFiles.length}개`);

    for (const name of [...registered].sort()) {
      const exists = pyFileSet.has(name);
      console.log(`  ${exists ? '✓' : '✗'} ${name}${exists ? '' : ' ← 파일 없음!'}`);
      if (!exists) hasError = true;
    }

    if (unregistered.length > 0) {
      console.log(`\n  참고 — 파일은 있지만 hooks.json 미등록 (비활성 훅):`);
      for (const name of unregistered.sort()) {
        console.log(`    - ${name}`);
      }
    }

    if (missingFiles.length === 0) {
      console.log('\n  ✓ 등록-파일 일관성 OK');
    } else {
      console.error(`\n  ✗ 등록됐지만 파일 없는 훅 ${missingFiles.length}개: ${missingFiles.join(', ')}`);
    }
  }
}

// ─── 3. 테스트 실행 안내 ────────────────────────────────────────────────────
console.log('\n── Test execution ──');
console.log('  Run hook tests:  python tests/test_hooks.py');
console.log('  Run with pytest: python -m pytest tests/test_hooks.py -v');

// ─── 4. 최종 결과 ─────────────────────────────────────────────────────────
console.log('');
if (hasError) {
  console.error('✗ Verification FAILED — fix the issues above.');
  process.exit(1);
} else {
  console.log('✓ All verification checks passed.');
}
