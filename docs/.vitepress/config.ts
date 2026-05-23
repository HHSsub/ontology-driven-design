import { defineConfig } from 'vitepress'

export default defineConfig({
  base: '/ontology-driven-design/',
  title: 'ODD',
  description: 'Ontology Driven Design — Purpose-driven AI workflows for Claude Code',

  locales: {
    root: {
      label: '한국어',
      lang: 'ko',
      title: 'ODD — Ontology Driven Design',
      description: '목적 중심 AI 워크플로우 — Claude Code 플러그인',
      themeConfig: {
        nav: [
          { text: '홈', link: '/' },
          { text: '시작하기', link: '/guide/getting-started' },
          { text: '스킬', link: '/skills/' },
          { text: '철학', link: '/philosophy' },
        ],
        sidebar: {
          '/guide/': [
            {
              text: '가이드',
              items: [
                { text: '시작하기', link: '/guide/getting-started' },
                { text: '설치', link: '/guide/installation' },
              ]
            }
          ],
          '/skills/': [
            {
              text: '스킬',
              items: [
                { text: '전체 목록', link: '/skills/' },
                { text: 'pyramid-ontology', link: '/skills/pyramid-ontology' },
                { text: 'ontology-detach', link: '/skills/ontology-detach' },
                { text: 'ontology-rebuild', link: '/skills/ontology-rebuild' },
                { text: 'pyramid-label', link: '/skills/pyramid-label' },
                { text: 'pyramid-topology', link: '/skills/pyramid-topology' },
                { text: 'ontology-review-gate', link: '/skills/ontology-review-gate' },
              ]
            }
          ]
        },
        footer: {
          copyright: 'Copyright © 2026 황회선 (Hwang Hoe Sun) · <a href="https://knowgram.vercel.app">KnowGram</a>'
        },
        socialLinks: [
          { icon: 'github', link: 'https://github.com/HHSsub/ontology-driven-design' }
        ]
      }
    },
    en: {
      label: 'English',
      lang: 'en',
      link: '/en/',
      title: 'ODD — Ontology Driven Design',
      description: 'Purpose-driven AI workflows for Claude Code',
      themeConfig: {
        nav: [
          { text: 'Home', link: '/en/' },
          { text: 'Getting Started', link: '/en/guide/getting-started' },
          { text: 'Skills', link: '/en/skills/' },
          { text: 'Philosophy', link: '/en/philosophy' },
        ],
        sidebar: {
          '/en/guide/': [
            {
              text: 'Guide',
              items: [
                { text: 'Getting Started', link: '/en/guide/getting-started' },
                { text: 'Installation', link: '/en/guide/installation' },
              ]
            }
          ],
          '/en/skills/': [
            {
              text: 'Skills',
              items: [
                { text: 'All Skills', link: '/en/skills/' },
                { text: 'pyramid-ontology', link: '/en/skills/pyramid-ontology' },
                { text: 'ontology-detach', link: '/en/skills/ontology-detach' },
                { text: 'ontology-rebuild', link: '/en/skills/ontology-rebuild' },
                { text: 'pyramid-label', link: '/en/skills/pyramid-label' },
                { text: 'pyramid-topology', link: '/en/skills/pyramid-topology' },
                { text: 'ontology-review-gate', link: '/en/skills/ontology-review-gate' },
              ]
            }
          ]
        },
        footer: {
          copyright: 'Copyright © 2026 Hwang Hoe Sun (황회선) · <a href="https://knowgram.vercel.app">KnowGram</a>'
        },
        socialLinks: [
          { icon: 'github', link: 'https://github.com/HHSsub/ontology-driven-design' }
        ]
      }
    }
  },

  themeConfig: {
    search: { provider: 'local' },
  },

  head: [
    ['link', { rel: 'icon', href: '/favicon.ico' }],
    ['meta', { name: 'og:type', content: 'website' }],
    ['meta', { name: 'og:title', content: 'ODD — Ontology Driven Design' }],
    ['meta', { name: 'og:description', content: 'Purpose-driven AI workflows for Claude Code' }],
    ['meta', { name: 'naver-site-verification', content: 'NAVER_VERIFICATION_CODE' }],
  ],

  sitemap: {
    hostname: 'https://HHSsub.github.io/ontology-driven-design'
  }
})
