<template>
  <div class="weekly-list">
    <div class="info-banner">
      <strong>📅 更新时间：</strong>{{ updateTime }}
    </div>
    
    <div v-if="loading" class="loading">
      加载中...
    </div>
    
    <div v-else-if="reports.length === 0" class="empty">
      暂无周报数据，请等待系统自动生成。
    </div>
    
    <div v-else>
      <p>共收集 {{ reports.length }} 份周报</p>
      
      <h2>📋 周报列表</h2>
      
      <div v-for="(report, index) in reports" :key="report.identifier" class="report-item">
        <h3>{{ index + 1 }}. {{ report.identifier }}</h3>
        <p><strong>时间范围：</strong>{{ report.dateRange }}</p>
        <p><strong>更新时间：</strong>{{ report.mtime }}</p>
        <a :href="report.link" class="report-link">📖 查看周报</a>
        <hr v-if="index < reports.length - 1" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const reports = ref([])
const loading = ref(true)
const updateTime = ref('')

// 获取周报列表
const fetchWeeklyReports = async () => {
  try {
    const reportList = []
    
    // 手动指定周报文件（实际部署时会由Python脚本生成）
    // 这里使用静态数据作为示例，实际项目中会自动生成
    const weeklyFiles = [
      '2026-W10'
    ]
    
    for (const identifier of weeklyFiles) {
      // 解析周标识符计算日期范围
      const [year, weekStr] = identifier.split('-W')
      const week = parseInt(weekStr)
      
      // 计算周的起始和结束日期（ISO标准）
      const jan1 = new Date(parseInt(year), 0, 1)
      const isoWeekday = jan1.getDay() || 7 // 将周日(0)转为7
      
      let weekStart
      if (isoWeekday !== 1) {
        const daysToMonday = isoWeekday - 1
        weekStart = new Date(jan1)
        weekStart.setDate(jan1.getDate() - daysToMonday)
      } else {
        weekStart = new Date(jan1)
      }
      
      weekStart.setDate(weekStart.getDate() + (week - 1) * 7)
      const weekEnd = new Date(weekStart)
      weekEnd.setDate(weekStart.getDate() + 6)
      
      const dateRange = `${formatDate(weekStart)} - ${formatDate(weekEnd)}`
      
      reportList.push({
        identifier,
        dateRange,
        link: `/ai-daily-dashboard/weekly/${identifier}.html`,
        mtime: new Date().toLocaleString('zh-CN')
      })
    }
    
    // 按标识符倒序排列（最新的在前）
    reportList.sort((a, b) => b.identifier.localeCompare(a.identifier))
    
    reports.value = reportList
    updateTime.value = new Date().toLocaleString('zh-CN')
  } catch (error) {
    console.error('获取周报列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 格式化日期
const formatDate = (date) => {
  const month = (date.getMonth() + 1).toString().padStart(2, '0')
  const day = date.getDate().toString().padStart(2, '0')
  return `${month}/${day}`
}

onMounted(() => {
  fetchWeeklyReports()
})
</script>

<style scoped>
.weekly-list {
  margin-top: 1rem;
}

.info-banner {
  background: var(--vp-c-bg-soft);
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.loading, .empty {
  text-align: center;
  padding: 2rem;
  color: var(--vp-c-text-2);
}

.report-item {
  margin: 1.5rem 0;
}

.report-item h3 {
  margin-bottom: 0.5rem;
}

.report-item p {
  margin: 0.25rem 0;
  color: var(--vp-c-text-2);
}

.report-link {
  display: inline-block;
  margin-top: 0.5rem;
  color: var(--vp-c-brand);
  text-decoration: none;
}

.report-link:hover {
  text-decoration: underline;
}

hr {
  border: none;
  border-top: 1px solid var(--vp-c-divider);
  margin: 1.5rem 0;
}
</style>
