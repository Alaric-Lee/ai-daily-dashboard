---
layout: home

hero:
  name: "AI每日资讯"
  text: "每日更新的AI资讯仪表盘"
  tagline: 追踪大模型发展，掌握AI前沿动态
  actions:
    - theme: brand
      text: 查看最新
      link: ./2026-03-04
    - theme: alt
      text: 历史记录
      link: ./archive

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

- [2026-03-04](./2026-03-04)

<script setup>
import { onMounted } from 'vue'

onMounted(() => {
  // 获取所有feature卡片
  const features = document.querySelectorAll('.VPFeature')

  // 定义跳转链接（使用相对路径，锚点需要匹配标题的emoji前缀）
  const links = [
    './2026-03-04#🏆-大模型综合评测榜单',
    './2026-03-04#📰-最新大模型相关资讯',
    './2026-03-04#🔥-开源社区热门ai应用',
    './2026-03-04#💡-ai创新'
  ]

  // 为每个卡片添加点击事件
  features.forEach((feature, index) => {
    if (links[index]) {
      feature.style.cursor = 'pointer'
      feature.addEventListener('click', () => {
        window.location.href = links[index]
      })

      // 添加悬停效果
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
