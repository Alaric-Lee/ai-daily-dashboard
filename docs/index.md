---
layout: home

hero:
  name: "AI每日资讯"
  text: "每日更新的AI资讯仪表盘"
  tagline: 追踪大模型发展，掌握AI前沿动态
  actions:
    - theme: brand
      text: 查看最新
      link: ./latest/
    - theme: alt
      text: 历史记录
      link: ./history/

features:
  - title: 大模型评测榜单
    details: 实时获取LMSYS Arena等权威评测数据
  - title: 最新AI资讯
    details: 聚合机器之心、量子位等科技媒体动态
  - title: 开源项目追踪
    details: 发现GitHub上热门的AI应用和工具
  - title: AI创新
    details: 了解AI的最新创新方向
---

## 最近更新

- [今日最新](./latest/)
- [历史记录](./history/)

<script setup>
import { onMounted } from 'vue'

onMounted(() => {
  const features = document.querySelectorAll('.VPFeature')

  const links = [
    '/ai-daily-dashboard/latest/#🏆-大模型综合评测榜单',
    '/ai-daily-dashboard/latest/#📰-最新大模型相关资讯',
    '/ai-daily-dashboard/latest/#🔥-开源社区热门ai应用',
    '/ai-daily-dashboard/latest/#💡-ai创新'
  ]

  features.forEach((feature, index) => {
    if (links[index]) {
      feature.style.cursor = 'pointer'
      feature.addEventListener('click', () => {
        window.location.href = links[index]
      })

      feature.addEventListener('mouseenter', () => {
        feature.style.transform = 'translateY(-2px)'
        feature.style.transition = 'transform 0.2s ease'
      })

      feature.addEventListener('mouseleave', () => {
        feature.style.transform = 'translateY(0)'
      })
    }
  })
})
</script>
