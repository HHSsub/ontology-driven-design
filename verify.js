import { existsSync } from 'fs';
const files = [
  'docs/.vitepress/config.ts',
  'CLAUDE.md', 'README.md',
  'skills/pyramid-ontology/SKILL.md',
  'skills/ontology-detach/SKILL.md',
  '.github/workflows/deploy.yml'
];
files.forEach(f => {
  if (!existsSync(f)) throw new Error(`Missing: ${f}`);
  console.log('✓', f);
});
console.log('All required files present.');
