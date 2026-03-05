<template>
  <div class="monthly-list">
    <div class="info-banner">
      <strong>📅 更新时间：</strong>{{ updateTime }}
    </div>
    
    <div v-if="loading" class="loading">
      加载中...
    </div>
    
    <div v-else-if="reports.length === 0" class="empty">
      暂无月报数据，请等待系统自动生成。
    </div>
    
    <div v-else>
      <p>共收集 {{ reports.length }} 份月报</p>
      
      <h2>📋 月报列表</h2>
      
      <div v-for="(report, index) in reports" :key="report.identifier" class="report-item">
        <h3>{{ index + 1 }}. {{ report.identifier }}</h3>
        <p><strong>月份：</strong>{{ report.monthName }}</p>
        <p><strong>更新时间：</strong>{{ report.mtime }}</p>
        <a :href="report.link" class="report-link">📖 查看月报</a>
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

// 获取月报列表
const fetchMonthlyReports = async () => {
  try {
    const reportList = []
    
    // 手动指定月报文件（实际部署时会由Python脚本生成）
    // 这里使用静态数据作为示例，实际项目中会自动生成
    const monthlyFiles = [
      '2026-03'
    ]
    
    for (const identifier of monthlyFiles) {
      // 解析月标识符
      const [year, month] = identifier.split('-')
      const monthName = `${year}年${parseInt(month)}月`
      
      reportList.push({
        identifier,
        monthName,
        link: `/ai-daily-dashboard/monthly/${identifier}.html`,
        mtime: new Date().toLocaleString('zh-CN')
      })
    }
    
    // 按标识符倒序排列（最新的在前）
    reportList.sort((a, b) => b.identifier.localeCompare(a.identifier))
    
    reports.value = reportList
    updateTime.value = new Date().toLocaleString('zh-CN')
  } catch (error) {
    console.error('获取月报列表失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchMonthlyReports()
})
</script>

<style scoped>
.monthly-list {
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
