"""
月报生成器 - 汇总本月数据并生成月报
"""
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
from jinja2 import Template

from data_storage import DataStorage
from scoring import NewsScorer


class MonthlyReportGenerator:
    """月报生成器"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.storage = DataStorage(project_root)
        self.docs_dir = os.path.join(project_root, 'docs')
        self.monthly_dir = os.path.join(self.docs_dir, 'monthly')
        
        # 确保目录存在
        os.makedirs(self.monthly_dir, exist_ok=True)
    
    def get_month_identifier(self, year: int, month: int) -> str:
        """
        获取月标识符 (YYYY-MM)
        
        Args:
            year: 年份
            month: 月份
        
        Returns:
            月标识符
        """
        return f'{year}-{month:02d}'
    
    def get_month_date_range(self, year: int, month: int) -> tuple:
        """
        获取指定月的起始和结束日期
        
        Args:
            year: 年份
            month: 月份
        
        Returns:
            (开始日期, 结束日期) 元组
        """
        month_start = datetime(year, month, 1)
        if month == 12:
            month_end = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = datetime(year, month + 1, 1) - timedelta(days=1)
        
        return month_start, month_end
    
    def check_monthly_report_exists(self, month_identifier: str) -> bool:
        """
        检查月报是否已存在
        
        Args:
            month_identifier: 月标识符
        
        Returns:
            是否存在
        """
        filepath = os.path.join(self.monthly_dir, f'{month_identifier}.md')
        return os.path.exists(filepath)
    
    def aggregate_monthly_data(self, year: int, month: int) -> Dict[str, Any]:
        """
        汇总本月数据
        
        Args:
            year: 年份
            month: 月份
        
        Returns:
            汇总后的数据
        """
        # 获取本月的所有数据
        month_data = self.storage.get_month_data(year, month)
        
        if not month_data:
            return None
        
        # 获取日期范围
        month_start, month_end = self.get_month_date_range(year, month)
        
        # 收集所有新闻
        all_news = []
        all_open_source = []
        all_innovations = []
        
        for daily_data in month_data:
            data = daily_data.get('data', {})
            date = daily_data.get('date', '')
            
            # 收集新闻
            news_list = data.get('model_news', [])
            for news in news_list:
                if isinstance(news, dict):
                    news['date'] = date
                    all_news.append(news)
            
            # 收集开源项目
            open_source = data.get('open_source_apps', [])
            for item in open_source:
                if isinstance(item, dict) and 'name' in item and 'stars' in item:
                    # 确保项目有基本字段
                    item['date'] = date
                    all_open_source.append(item)
            
            # 收集创新案例
            innovations = data.get('successful_cases', [])
            for item in innovations:
                if isinstance(item, dict):
                    item['date'] = date
                    all_innovations.append(item)
        
        # 对新闻进行评分和排序，保留Top 50
        reference_date = month_end
        ranked_news = NewsScorer.rank_news(all_news, reference_date, top_n=50)
        
        # 对开源项目进行排序
        ranked_open_source = sorted(
            all_open_source,
            key=lambda x: x.get('stars', 0) if isinstance(x, dict) else 0,
            reverse=True
        )[:30]  # 保留Top 30
        
        # 对创新案例进行排序
        ranked_innovations = sorted(
            all_innovations,
            key=lambda x: x.get('final_score', 0) if isinstance(x, dict) else 0,
            reverse=True
        )[:30]  # 保留Top 30
        
        # 统计每周的数据量
        weekly_stats = {}
        for daily_data in month_data:
            date_str = daily_data.get('date', '')
            if date_str:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                week_num = date_obj.isocalendar()[1]
                week_key = f'第{week_num}周'
                if week_key not in weekly_stats:
                    weekly_stats[week_key] = 0
                weekly_stats[week_key] += 1
        
        return {
            'month_identifier': f'{year}-{month:02d}',
            'year': year,
            'month': month,
            'month_start': month_start.strftime('%Y-%m-%d'),
            'month_end': month_end.strftime('%Y-%m-%d'),
            'news_count': len(all_news),
            'top_news': ranked_news,
            'open_source_count': len(all_open_source),
            'top_open_source': ranked_open_source,
            'innovation_count': len(all_innovations),
            'top_innovations': ranked_innovations,
            'weekly_stats': weekly_stats,
            'daily_count': len(month_data),
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def generate_monthly_report(self, year: int = None, month: int = None) -> str:
        """
        生成月报
        
        Args:
            year: 年份，默认为当前年
            month: 月份，默认为当前月
        
        Returns:
            生成的文件路径
        """
        if year is None or month is None:
            now = datetime.now()
            year = now.year
            month = now.month
        
        month_identifier = f'{year}-{month:02d}'
        
        # 检查是否已存在
        if self.check_monthly_report_exists(month_identifier):
            print(f"月报 {month_identifier} 已存在，跳过生成")
            return None
        
        # 汇总数据
        data = self.aggregate_monthly_data(year, month)
        
        if not data:
            print(f"本月 ({month_identifier}) 暂无数据，无法生成月报")
            return None
        
        # 渲染模板
        template_str = """---
title: AI每月精选 - {{ month_identifier }}
description: {{ year }}年{{ month }}月的AI资讯精选
---

# 📊 AI每月精选 - {{ month_identifier }}

<div class="info-banner">
  <strong>📅 时间范围：</strong>{{ month_start }} 至 {{ month_end }} | 
  <strong>📊 数据天数：</strong>{{ daily_count }} 天 |
  <strong>📝 生成时间：</strong>{{ generated_at }}
</div>

## 📈 本月概览

| 指标 | 数量 | 精选 |
|------|------|------|
| 📰 资讯 | {{ news_count }} | Top {{ top_news|length }} |
| 🔥 开源项目 | {{ open_source_count }} | Top {{ top_open_source|length }} |
| 💡 创新案例 | {{ innovation_count }} | Top {{ top_innovations|length }} |

### 每周数据分布

{% for week, count in weekly_stats.items() %}
- **{{ week }}：** {{ count }} 天
{% endfor %}

---

## 📰 本月热门资讯 (Top {{ top_news|length }})

本月共收集 {{ news_count }} 条AI资讯，精选 Top {{ top_news|length }} 条：

{% for news in top_news %}
### {{ loop.index }}. {{ news.title }} 

**评分：** ⭐ {{ "%.1f"|format(news._score) }}/100

{% if news._score_details and news._score_details.matched_keywords %}
**关键词：** {{ news._score_details.matched_keywords | join(', ') }}
{% endif %}

{{ news.description }}

{% if news.source %}
**来源：** {{ news.source }}
{% endif %}
{% if news.date %}
**日期：** {{ news.date }}
{% endif %}
{% if news.link %}
**链接：** [查看原文]({{ news.link }})
{% endif %}

---

{% endfor %}

## 🔥 本月热门开源项目 (Top {{ top_open_source|length }})

本月共发现 {{ open_source_count }} 个开源项目，精选 Top {{ top_open_source|length }} 个：

{% for project in top_open_source %}
### {{ loop.index }}. {{ project.name if project.name is defined else project }}

{% if project.description is defined %}
{{ project.description }}
{% endif %}
{% if project.stars is defined %}
**⭐ Stars：** {{ project.stars }}
{% endif %}
{% if project.language is defined %}
**语言：** {{ project.language }}
{% endif %}
{% if project.date %}
**日期：** {{ project.date }}
{% endif %}

---

{% endfor %}

## 💡 本月AI创新 (Top {{ top_innovations|length }})

本月共收集 {{ innovation_count }} 个AI创新案例，精选 Top {{ top_innovations|length }} 个：

{% for innovation in top_innovations %}
### {{ loop.index }}. {{ innovation.title if innovation.title is defined else innovation }}

{% if innovation.summary is defined %}
{{ innovation.summary }}
{% endif %}
{% if innovation.final_score is defined %}
**创新指数：** {{ "%.2f"|format(innovation.final_score) }}
{% endif %}
{% if innovation.source is defined %}
**来源：** {{ innovation.source }}
{% endif %}
{% if innovation.date %}
**日期：** {{ innovation.date }}
{% endif %}

---

{% endfor %}

## 🎯 本月重点回顾

### Top 3 重要资讯

{% for news in top_news[:3] %}
{{ loop.index }}. **{{ news.title }}** (评分: {{ "%.1f"|format(news._score) }})
{% endfor %}

### 趋势分析

基于本月 {{ news_count }} 条资讯的分析：

- **总资讯数：** {{ news_count }} 条
- **日均资讯：** {{ "%.1f"|format(news_count / daily_count) }} 条
- **覆盖天数：** {{ daily_count }} 天
- **热门来源：** 
  {% if top_news %}
    {% set sources = {} %}
    {% for news in top_news %}
      {% if news.source %}
        {% set _ = sources.update({news.source: sources.get(news.source, 0) + 1}) %}
      {% endif %}
    {% endfor %}
    {{ sources | dictsort(by='value') | reverse | map(attribute='0') | list | join(', ') }}
  {% endif %}

---

*本报告由AI Daily自动生成*
"""
        
        template = Template(template_str)
        content = template.render(**data)
        
        # 保存文件
        filepath = os.path.join(self.monthly_dir, f'{month_identifier}.md')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"月报生成完成: {filepath}")
        return filepath
    
    def generate_current_month(self) -> str:
        """
        生成当前月的月报
        
        Returns:
            生成的文件路径
        """
        now = datetime.now()
        return self.generate_monthly_report(now.year, now.month)
    
    def generate_if_not_exists(self, date: datetime = None) -> str:
        """
        如果月报不存在则生成（用于每日检查时调用）
        
        Args:
            date: 日期，默认为今天
        
        Returns:
            生成的文件路径，如果已存在则返回None
        """
        if date is None:
            date = datetime.now()
        
        year = date.year
        month = date.month
        month_identifier = f'{year}-{month:02d}'
        
        if self.check_monthly_report_exists(month_identifier):
            return None
        
        return self.generate_monthly_report(year, month)


if __name__ == '__main__':
    # 测试代码
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    generator = MonthlyReportGenerator(project_root)
    
    # 测试生成当前月的月报
    result = generator.generate_current_month()
    if result:
        print(f"生成成功: {result}")
    else:
        print("生成失败或已存在")
