import { defineConfig } from 'vitepress'

export default defineConfig({
  title: "AI Daily",
  description: "每日更新的AI资讯仪表盘",
  base: '/ai-daily-dashboard/',
  srcDir: 'docs',
  lang: 'zh-CN',
  
  head: [
    ['meta', { name: 'theme-color', content: '#6366f1' }],
    ['meta', { name: 'og:type', content: 'website' }],
    ['meta', { name: 'og:title', content: 'AI Daily - 每日AI资讯仪表盘' }],
    ['meta', { name: 'og:description', content: '追踪大模型发展，掌握AI前沿动态' }],
  ],
  
  themeConfig: {
    logo: '/logo.svg',
    siteTitle: 'AI Daily',
    
    nav: [
      { text: '🏠 首页', link: '/' },
      { text: '📰 今日资讯', link: '/2026-03-04' },
      { text: '📅 历史记录', link: '/archive' }
    ],

    sidebar: {
      '/': [
        {
          text: '📊 导航',
          items: [
            { text: '🏠 首页', link: '/' },
            { text: '📰 今日资讯', link: '/2026-03-04' },
            { text: '📅 历史记录', link: '/archive' }
          ]
        },
        {
          text: '📋 今日内容',
          items: [
            { text: '🏆 大模型评测榜单', link: '/2026-03-04#大模型综合评测榜单' },
            { text: '📰 最新资讯', link: '/2026-03-04#最新大模型相关资讯' },
            { text: '🔥 开源项目', link: '/2026-03-04#开源社区热门ai应用' },
            { text: '💡 成功案例', link: '/2026-03-04#ai创新' }
          ]
        }
      ]
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/Alaric-Lee/ai-daily-dashboard' }
    ],
    
    footer: {
      message: '基于 VitePress 构建，每日自动更新',
      copyright: 'Copyright © 2026 AI Daily. All rights reserved.'
    },
    
    editLink: {
      pattern: 'https://github.com/Alaric-Lee/ai-daily-dashboard/edit/main/docs/:path',
      text: '在 GitHub 上编辑此页'
    },
    
    lastUpdated: {
      text: '最后更新于',
      formatOptions: {
        dateStyle: 'full',
        timeStyle: 'short'
      }
    },
    
    docFooter: {
      prev: '上一页',
      next: '下一页'
    },
    
    outline: {
      label: '页面导航',
      level: [2, 3]
    },
    
    returnToTopLabel: '返回顶部',
    sidebarMenuLabel: '菜单',
    darkModeSwitchLabel: '主题',
    lightModeSwitchTitle: '切换到浅色模式',
    darkModeSwitchTitle: '切换到深色模式'
  },
  
  markdown: {
    theme: {
      light: 'github-light',
      dark: 'github-dark'
    },
    lineNumbers: false
  }
})