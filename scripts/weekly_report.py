"""
周报生成器 - 汇总本周数据并生成周报
"""
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
from jinja2 import Template

from data_storage import DataStorage
from scoring import NewsScorer


class WeeklyReportGenerator:
    """周报生成器"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.storage = DataStorage(project_root)
        self.docs_dir = os.path.join(project_root, 'docs')
        self.weekly_dir = os.path.join(self.docs_dir, 'weekly')
        
        # 确保目录存在
        os.makedirs(self.weekly_dir, exist_ok=True)
    
    def get_week_identifier(self, date: datetime) -> str:
        """
        获取周标识符 (YYYY-WXX)
        
        Args:
            date: 日期
        
        Returns:
            周标识符
        """
        year = date.year
        week = date.isocalendar()[1]
        return f'{year}-W{week:02d}'
    
    def get_week_date_range(self, year: int, week: int) -> tuple:
        """
        获取指定周的起始和结束日期
        
        Args:
            year: 年份
            week: 周数，使用ISO标准
        
        Returns:
            (开始日期, 结束日期) 元组
        """
        # 使用ISO标准计算周的起始和结束日期
        # ISO周从周一开始
        jan1 = datetime(year, 1, 1)
        
        # 获取1月1日所在的ISO周
        iso_year, iso_week, iso_weekday = jan1.isocalendar()
        
        # 计算目标周的起始日期（周一）
        if iso_weekday != 1:
            # 1月1日不是周一，计算当前周的第一天
            days_to_monday = iso_weekday - 1
            week_start = jan1 - timedelta(days=days_to_monday)
        else:
            week_start = jan1
        
        # 计算指定周的起始日期
        week_start = week_start + timedelta(weeks=week-1)
        week_end = week_start + timedelta(days=6)
        
        return week_start, week_end
    
    def check_weekly_report_exists(self, week_identifier: str) -> bool:
        """
        检查周报是否已存在
        
        Args:
            week_identifier: 周标识符
        
        Returns:
            是否存在
        """
        filepath = os.path.join(self.weekly_dir, f'{week_identifier}.md')
        return os.path.exists(filepath)
    
    def aggregate_weekly_data(self, year: int, week: int) -> Dict[str, Any]:
        """
        汇总本周数据
        
        Args:
            year: 年份
            week: 周数
        
        Returns:
            汇总后的数据
        """
        # 获取本周的所有数据
        week_data = self.storage.get_week_data(year, week)
        
        if not week_data:
            return None
        
        # 获取日期范围
        week_start, week_end = self.get_week_date_range(year, week)
        
        # 收集所有新闻
        all_news = []
        all_open_source = []
        all_innovations = []
        
        for daily_data in week_data:
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
                if isinstance(item, dict):
                    item['date'] = date
                    all_open_source.append(item)
            
            # 收集创新案例
            innovations = data.get('successful_cases', [])
            for item in innovations:
                if isinstance(item, dict):
                    item['date'] = date
                    all_innovations.append(item)
        
        # 对新闻进行评分和排序，保留Top 30
        reference_date = week_end
        ranked_news = NewsScorer.rank_news(all_news, reference_date, top_n=30)
        
        # 对开源项目进行简单排序（按star数或时间）
        ranked_open_source = sorted(
            all_open_source,
            key=lambda x: x.get('stars', 0) if isinstance(x, dict) else 0,
            reverse=True
        )[:20]  # 保留Top 20
        
        # 对创新案例进行排序
        ranked_innovations = sorted(
            all_innovations,
            key=lambda x: x.get('final_score', 0) if isinstance(x, dict) else 0,
            reverse=True
        )[:20]  # 保留Top 20
        
        return {
            'week_identifier': f'{year}-W{week:02d}',
            'week_start': week_start.strftime('%Y-%m-%d'),
            'week_end': week_end.strftime('%Y-%m-%d'),
            'news_count': len(all_news),
            'top_news': ranked_news,
            'open_source_count': len(all_open_source),
            'top_open_source': ranked_open_source,
            'innovation_count': len(all_innovations),
            'top_innovations': ranked_innovations,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def generate_weekly_report(self, year: int = None, week: int = None) -> str:
        """
        生成周报
        
        Args:
            year: 年份，默认为当前年
            week: 周数，默认为当前周
        
        Returns:
            生成的文件路径
        """
        if year is None or week is None:
            now = datetime.now()
            year = now.year
            week = now.isocalendar()[1]
        
        week_identifier = f'{year}-W{week:02d}'
        
        # 检查是否已存在
        if self.check_weekly_report_exists(week_identifier):
            print(f"周报 {week_identifier} 已存在，跳过生成")
            return None
        
        # 汇总数据
        data = self.aggregate_weekly_data(year, week)
        
        if not data:
            print(f"本周 ({week_identifier}) 暂无数据，无法生成周报")
            return None
        
        # 渲染模板
        template_str = """---
title: AI每周精选 - {{ week_identifier }}
description: {{ week_start }} 至 {{ week_end }} 的AI资讯精选
---

# 📊 AI每周精选 - {{ week_identifier }}

<div class="info-banner">
  <strong>📅 时间范围：</strong>{{ week_start }} 至 {{ week_end }} | 
  <strong>📝 生成时间：</strong>{{ generated_at }}
</div>

## 📰 本周热门资讯 (Top {{ top_news|length }})

本周共收集 {{ news_count }} 条AI资讯，精选 Top {{ top_news|length }} 条：

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

## 🔥 本周热门开源项目 (Top {{ top_open_source|length }})

本周共发现 {{ open_source_count }} 个开源项目，精选 Top {{ top_open_source|length }} 个：

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

## 💡 本周AI创新 (Top {{ top_innovations|length }})

本周共收集 {{ innovation_count }} 个AI创新案例，精选 Top {{ top_innovations|length }} 个：

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

## 📈 本周趋势总结

本周AI领域的主要趋势：

{% if top_news %}
{% set first_news = top_news[0] %}
- **最热门：** {{ first_news.title }} (评分: {{ "%.1f"|format(first_news._score) }})
{% endif %}

- **资讯数量：** 共 {{ news_count }} 条
- **开源项目：** 共 {{ open_source_count }} 个
- **创新案例：** 共 {{ innovation_count }} 个

---

*本报告由AI Daily自动生成*
"""
        
        template = Template(template_str)
        content = template.render(**data)
        
        # 保存文件
        filepath = os.path.join(self.weekly_dir, f'{week_identifier}.md')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"周报生成完成: {filepath}")
        return filepath
    
    def generate_current_week(self) -> str:
        """
        生成当前周的周报
        
        Returns:
            生成的文件路径
        """
        now = datetime.now()
        return self.generate_weekly_report(now.year, now.isocalendar()[1])
    
    def generate_if_not_exists(self, date: datetime = None) -> str:
        """
        如果周报不存在则生成（用于每日检查时调用）
        
        Args:
            date: 日期，默认为今天
        
        Returns:
            生成的文件路径，如果已存在则返回None
        """
        if date is None:
            date = datetime.now()
        
        year = date.year
        week = date.isocalendar()[1]
        week_identifier = f'{year}-W{week:02d}'
        
        if self.check_weekly_report_exists(week_identifier):
            return None
        
        return self.generate_weekly_report(year, week)


if __name__ == '__main__':
    # 测试代码
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    generator = WeeklyReportGenerator(project_root)
    
    # 测试生成当前周的周报
    result = generator.generate_current_week()
    if result:
        print(f"生成成功: {result}")
    else:
        print("生成失败或已存在")
