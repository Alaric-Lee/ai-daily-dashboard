import DefaultTheme from 'vitepress/theme'
import './custom.css'

// 导入自定义组件
import WeeklyList from '../../docs/.vitepress/theme/components/WeeklyList.vue'
import MonthlyList from '../../docs/.vitepress/theme/components/MonthlyList.vue'

export default {
  ...DefaultTheme,
  enhanceApp({ app }) {
    // 注册全局组件
    app.component('WeeklyList', WeeklyList)
    app.component('MonthlyList', MonthlyList)
  }
}
