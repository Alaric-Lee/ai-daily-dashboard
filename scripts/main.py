"""
主程序 - 整合日报、周报、月报生成功能
"""
import os
import sys
import argparse
from datetime import datetime, timedelta
from jinja2 import Template

# 添加脚本目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_storage import DataStorage
from scoring import NewsScorer
from weekly_report import WeeklyReportGenerator
from monthly_report import MonthlyReportGenerator

# 导入数据获取模块
try:
    import model_ranking
    import model_news
    import open_source_apps
    import successful_cases
except ImportError as e:
    print(f"警告: 部分数据获取模块导入失败: {e}")
    # 使用模拟数据
    model_ranking = None
    model_news = None
    open_source_apps = None
    successful_cases = None


def get_mock_data():
    """获取模拟数据（用于测试）"""
    return {
        'model_ranking': {
            'huggingface': 'https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard',
            'lmsys': 'https://arena.ai/leaderboard',
            'opencompass': 'https://rank.opencompass.org.cn/home'
        },
        'model_news': [
            {
                'title': 'OpenAI发布GPT-5：全新多模态能力震撼业界',
                'description': 'OpenAI今日发布GPT-5，具备更强的多模态理解能力和更长的上下文窗口...',
                'source': 'OpenAI',
                'link': 'https://openai.com',
                'date': datetime.now().strftime('%Y-%m-%d')
            },
            {
                'title': 'Anthropic推出Claude 4：超越GPT-4的性能',
                'description': 'Anthropic发布Claude 4，在多项基准测试中超越GPT-4...',
                'source': 'Anthropic',
                'link': 'https://anthropic.com',
                'date': datetime.now().strftime('%Y-%m-%d')
            }
        ],
        'open_source_apps': [
            {
                'name': 'LangChain',
                'description': '构建LLM应用的框架',
                'stars': 150000,
                'language': 'Python',
                'date': datetime.now().strftime('%Y-%m-%d')
            }
        ],
        'successful_cases': [
            {
                'title': '突破性多模态AI模型发布',
                'summary': '新模型在多项任务上超越GPT-4V',
                'source': 'arXiv',
                'final_score': 0.95,
                'date': datetime.now().strftime('%Y-%m-%d')
            }
        ]
    }


def fetch_daily_data():
    """获取每日数据"""
    print("开始获取每日数据...")
    
    data = {}
    
    # 获取大模型评测榜单
    print("获取大模型综合评测榜单...")
    if model_ranking:
        try:
            data['model_ranking'] = model_ranking.get_model_ranking()
        except Exception as e:
            print(f"获取榜单失败: {e}")
            data['model_ranking'] = {}
    else:
        data['model_ranking'] = {}
    
    # 获取最新大模型相关资讯
    print("获取最新大模型相关资讯...")
    if model_news:
        try:
            news = model_news.get_model_news()
            # 解析Markdown列表为结构化数据
            data['model_news'] = parse_news_from_markdown(news)
        except Exception as e:
            print(f"获取资讯失败: {e}")
            data['model_news'] = []
    else:
        data['model_news'] = []
    
    # 获取开源社区热门AI应用
    print("获取开源社区热门AI应用...")
    if open_source_apps:
        try:
            apps = open_source_apps.get_open_source_apps()
            data['open_source_apps'] = parse_apps_from_markdown(apps)
        except Exception as e:
            print(f"获取开源项目失败: {e}")
            data['open_source_apps'] = []
    else:
        data['open_source_apps'] = []
    
    # 获取AI创新
    print("获取AI创新...")
    if successful_cases:
        try:
            cases = successful_cases.get_successful_cases()
            data['successful_cases'] = parse_cases_from_markdown(cases)
        except Exception as e:
            print(f"获取创新案例失败: {e}")
            data['successful_cases'] = []
    else:
        data['successful_cases'] = []
    
    return data


def parse_news_from_markdown(markdown_text):
    """从Markdown文本解析新闻列表"""
    news_list = []
    if not markdown_text:
        return news_list
    
    import re
    # 匹配 Markdown 列表项
    pattern = r'- \*\*(.+?)\*\*\s*\((.+?)\)\s*：(.+?)\s*\[查看原文\]\((.+?)\)'
    matches = re.findall(pattern, markdown_text)
    
    for match in matches:
        title, source, description, link = match
        news_list.append({
            'title': title.strip(),
            'source': source.strip(),
            'description': description.strip(),
            'link': link.strip(),
            'date': datetime.now().strftime('%Y-%m-%d')
        })
    
    return news_list


def parse_apps_from_markdown(markdown_text):
    """从Markdown文本解析开源应用列表"""
    apps_list = []
    if not markdown_text:
        return apps_list
    
    import re
    # 匹配开源项目列表项
    pattern = r'- \*\*(.+?)\*\*\s*⭐(\d+)\s*\((.+?)\)：(.+?)\s*\[链接\]\((.+?)\)'
    matches = re.findall(pattern, markdown_text)
    
    for match in matches:
        full_name, stars, language, description, link = match
        # 提取项目名称（去掉用户名部分）
        name = full_name.split('/')[-1] if '/' in full_name else full_name
        apps_list.append({
            'name': name.strip(),
            'full_name': full_name.strip(),
            'stars': int(stars.strip()),
            'language': language.strip(),
            'description': description.strip(),
            'link': link.strip(),
            'date': datetime.now().strftime('%Y-%m-%d')
        })
    
    return apps_list


def parse_cases_from_markdown(markdown_text):
    """从Markdown文本解析创新案例列表"""
    cases_list = []
    if not markdown_text:
        return cases_list
    
    import re
    # 匹配编号列表项
    pattern = r'\d+\. \*\*(.+?)\*\*\s*- 领域：(.+?)\s*- 来源：(.+?)\s*- 创新指数：([\d.]+)\s*- 描述：(.+?)\s*- 链接：(.+?)(?=\n\n|\Z)'
    matches = re.findall(pattern, markdown_text, re.DOTALL)
    
    for match in matches:
        title, type_, source, score, summary, url = match
        cases_list.append({
            'title': title.strip(),
            'type': type_.strip(),
            'source': source.strip(),
            'final_score': float(score.strip()),
            'summary': summary.strip(),
            'url': url.strip(),
            'date': datetime.now().strftime('%Y-%m-%d')
        })
    
    return cases_list


def render_daily_report(data: dict, date_str: str) -> str:
    """渲染日报内容为Markdown格式"""
    template_str = """---
title: AI每日资讯 - {{ date_str }}
---

> 📅 **更新日期**：{{ date_str }}  
> ⏰ **生成时间**：{{ generated_at }}

## 🏆 大模型综合评测榜单

以下是当前主流大模型的权威评测榜单，点击链接查看最新排名：

### 1. Hugging Face Open LLM Leaderboard

开源大模型综合评测榜单，涵盖多项基准测试：

- **链接**：[https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard](https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard)
- **特点**：包含MMLU、HumanEval、GSM8K等多项基准测试，支持多种模型对比

### 2. LMSYS Chatbot Arena

基于用户投票的大模型对战评测榜单：

- **链接**：[https://arena.ai/leaderboard](https://arena.ai/leaderboard)
- **特点**：通过真实用户对战投票，反映模型在实际使用中的表现

### 3. OpenCompass 司南评测榜单

上海人工智能实验室推出的大模型评测体系：

- **链接**：[https://rank.opencompass.org.cn/home](https://rank.opencompass.org.cn/home)
- **特点**：中国自主研发的评测体系，覆盖多语言和多任务场景

> 📅 数据更新时间：{{ date_str }}
> 💡 提示：点击上述链接查看最新的大模型评测排名。


---

## 📰 最新大模型相关资讯

{% for news in model_news %}
- **{{ news.title }}** ({{ news.source }})： {{ news.description }} [查看原文]({{ news.link }})
{% endfor %}

---

## 🔥 开源社区热门AI应用

{% for app in open_source_apps %}
- **{{ app.full_name }}** ⭐{{ app.stars }} ({{ app.language }})：{{ app.description }} [链接]({{ app.link }})
{% endfor %}

---

## 💡 AI创新

{% for case in successful_cases %}
{{ loop.index }}. **{{ case.title }}**
   - 领域：{{ case.type }}
   - 来源：{{ case.source }}
   - 创新指数：{{ "%.2f"|format(case.final_score) }}
   - 描述：{{ case.summary }}
   - 链接：{{ case.url }}

{% endfor %}

---

**📌 提示**：本页面每日自动更新，数据来源于多个权威平台。  

**🔗 相关链接**：
- [Hugging Face](https://huggingface.co)
- [LMSYS Arena](https://lmarena.ai)
- [OpenCompass](https://opencompass.org.cn)
"""
    
    template = Template(template_str)
    return template.render(
        date_str=date_str,
        generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        **data
    )


def update_archive(project_root):
    """根据 docs/history 目录生成历史索引页面 docs/history/index.md"""
    history_dir = os.path.join(project_root, 'docs', 'history')
    
    files = sorted(
        [
            f
            for f in os.listdir(history_dir)
            if f.endswith('.md') and f != 'index.md'
        ],
        reverse=True,
    )
    
    archive_content = '# 📅 历史记录\n\n'
    archive_content += '## 按日期查看\n\n'
    
    current_month = None
    for file in files:
        date_str = file.replace('.md', '')
        year_month = date_str[:7]  # YYYY-MM
        
        if year_month != current_month:
            if current_month:
                archive_content += '\n'
            current_month = year_month
            archive_content += f'### {year_month}\n\n'
        
        archive_content += f'- [{date_str}](./{date_str})\n'
    
    index_path = os.path.join(history_dir, 'index.md')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(archive_content)
    
    print('历史记录索引 docs/history/index.md 更新完成')


def update_index(project_root: str, latest_date: str) -> None:
    """根据最新日期更新 docs/index.md"""
    docs_dir = os.path.join(project_root, 'docs')
    index_path = os.path.join(docs_dir, 'index.md')
    
    # 读取历史目录获取所有日期
    history_dir = os.path.join(docs_dir, 'history')
    files = sorted(
        [
            f
            for f in os.listdir(history_dir)
            if f.endswith('.md') and f != 'index.md'
        ],
        reverse=True,
    )
    
    # 生成首页内容
    index_content = """---
layout: home

hero:
  name: "AI每日资讯"
  text: "每日更新的AI资讯仪表盘"
  tagline: 追踪大模型发展，掌握AI前沿动态
  actions:
    - theme: brand
      text: 查看最新
      link: ./latest
    - theme: alt
      text: 历史记录
      link: ./history

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

"""
    
    # 添加最近7天的链接
    for file in files[:7]:
        date_str = file.replace('.md', '')
        index_content += f'- [{date_str}](./history/{date_str})\n'
    
    # 添加脚本，使feature卡片可点击
    index_content += """
<script setup>
import { onMounted } from 'vue'

onMounted(() => {
  // 获取所有feature卡片
  const features = document.querySelectorAll('.VPFeature')

  // 定义跳转链接（使用相对路径，锚点需要匹配标题的emoji前缀）
  const links = [
    './latest#🏆-大模型综合评测榜单',
    './latest#📰-最新大模型相关资讯',
    './latest#🔥-开源社区热门ai应用',
    './latest#💡-ai创新'
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
"""
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    print(f'首页 docs/index.md 更新完成')


def generate_daily_report(project_root: str, date_str: str = None, storage: DataStorage = None):
    """
    生成日报
    
    Args:
        project_root: 项目根目录
        date_str: 日期字符串，默认为今天
        storage: 数据存储实例
    
    Returns:
        生成的文件路径
    """
    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    if storage is None:
        storage = DataStorage(project_root)
    
    print(f"\n{'='*50}")
    print(f"开始生成日报: {date_str}")
    print(f"{'='*50}\n")
    
    # 获取数据
    data = fetch_daily_data()
    
    # 保存原始数据
    storage.save_daily_data(date_str, data)
    
    # 渲染日报内容为Markdown格式
    rendered_content = render_daily_report(data, date_str)
    
    # 目录设置：最新资讯与历史记录分开
    docs_dir = os.path.join(project_root, 'docs')
    latest_dir = os.path.join(docs_dir, 'latest')
    history_dir = os.path.join(docs_dir, 'history')
    
    for d in (docs_dir, latest_dir, history_dir):
        if not os.path.exists(d):
            os.makedirs(d)
    
    # 1. 最新资讯：始终覆盖 docs/latest/index.md
    latest_file = os.path.join(latest_dir, 'index.md')
    with open(latest_file, 'w', encoding='utf-8') as f:
        f.write(rendered_content)
    print(f"最新资讯已写入: {latest_file}")
    
    # 2. 历史存档：按日期保存到 docs/history/YYYY-MM-DD.md
    history_file = os.path.join(history_dir, f'{date_str}.md')
    with open(history_file, 'w', encoding='utf-8') as f:
        f.write(rendered_content)
    print(f"历史记录已写入: {history_file}")
    
    # 3. 额外备份到 output 目录
    output_dir = os.path.join(project_root, 'output')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    backup_file = os.path.join(output_dir, f'{date_str}.md')
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(rendered_content)
    
    print(f"备份完成: {backup_file}")
    
    # 4. 根据 history 目录更新历史索引页面 docs/history/index.md
    update_archive(project_root)
    
    # 5. 更新首页 docs/index.md
    update_index(project_root, date_str)
    
    print(f"\n日报生成完成: {date_str}")
    
    return date_str


def generate_weekly_report(project_root: str, year: int = None, week: int = None, 
                           check_exists: bool = True) -> str:
    """
    生成周报
    
    Args:
        project_root: 项目根目录
        year: 年份，默认为当前年
        week: 周数，默认为当前周
        check_exists: 是否检查已存在
    
    Returns:
        生成的文件路径
    """
    generator = WeeklyReportGenerator(project_root)
    
    if year is None or week is None:
        now = datetime.now()
        year = now.year
        week = now.isocalendar()[1]
    
    week_identifier = f'{year}-W{week:02d}'
    
    print(f"\n{'='*50}")
    print(f"开始生成周报: {week_identifier}")
    print(f"{'='*50}\n")
    
    if check_exists and generator.check_weekly_report_exists(week_identifier):
        print(f"周报 {week_identifier} 已存在，跳过生成")
        return None
    
    result = generator.generate_weekly_report(year, week)
    
    if result:
        print(f"\n周报生成完成: {result}")
    else:
        print(f"\n周报生成失败或无数据")
    
    return result


def generate_monthly_report(project_root: str, year: int = None, month: int = None,
                            check_exists: bool = True) -> str:
    """
    生成月报
    
    Args:
        project_root: 项目根目录
        year: 年份，默认为当前年
        month: 月份，默认为当前月
        check_exists: 是否检查已存在
    
    Returns:
        生成的文件路径
    """
    generator = MonthlyReportGenerator(project_root)
    
    if year is None or month is None:
        now = datetime.now()
        year = now.year
        month = now.month
    
    month_identifier = f'{year}-{month:02d}'
    
    print(f"\n{'='*50}")
    print(f"开始生成月报: {month_identifier}")
    print(f"{'='*50}\n")
    
    if check_exists and generator.check_monthly_report_exists(month_identifier):
        print(f"月报 {month_identifier} 已存在，跳过生成")
        return None
    
    result = generator.generate_monthly_report(year, month)
    
    if result:
        print(f"\n月报生成完成: {result}")
    else:
        print(f"\n月报生成失败或无数据")
    
    return result


def run_daily_task(project_root: str):
    """
    运行每日任务
    - 生成日报
    - 检查并生成周报（如果不存在）
    - 检查并生成月报（如果不存在）
    """
    print(f"\n{'#'*60}")
    print(f"# 开始执行每日任务")
    print(f"# 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*60}\n")
    
    # 1. 生成日报
    storage = DataStorage(project_root)
    date_str = datetime.now().strftime('%Y-%m-%d')
    generate_daily_report(project_root, date_str, storage)
    
    # 2. 检查并生成周报
    print("\n检查周报...")
    generate_weekly_report(project_root, check_exists=True)
    
    # 3. 检查并生成月报
    print("\n检查月报...")
    generate_monthly_report(project_root, check_exists=True)
    
    print(f"\n{'#'*60}")
    print(f"# 每日任务执行完成")
    print(f"{'#'*60}\n")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='AI Daily 数据生成工具')
    parser.add_argument('--mode', choices=['daily', 'weekly', 'monthly', 'all'], 
                        default='all',
                        help='生成模式: daily=日报, weekly=周报, monthly=月报, all=全部')
    parser.add_argument('--date', help='指定日期 (YYYY-MM-DD)，仅daily模式有效')
    parser.add_argument('--week', type=int, help='指定周数，仅weekly模式有效')
    parser.add_argument('--month', type=int, help='指定月份，仅monthly模式有效')
    parser.add_argument('--year', type=int, help='指定年份')
    parser.add_argument('--force', action='store_true', 
                        help='强制生成，即使已存在')
    
    args = parser.parse_args()
    
    # 获取项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    if args.mode == 'daily':
        # 生成日报
        generate_daily_report(project_root, args.date)
    
    elif args.mode == 'weekly':
        # 生成周报
        year = args.year or datetime.now().year
        week = args.week or datetime.now().isocalendar()[1]
        generate_weekly_report(project_root, year, week, check_exists=not args.force)
    
    elif args.mode == 'monthly':
        # 生成月报
        year = args.year or datetime.now().year
        month = args.month or datetime.now().month
        generate_monthly_report(project_root, year, month, check_exists=not args.force)
    
    else:  # all
        # 运行每日任务（包含日报、周报检查、月报检查）
        run_daily_task(project_root)


if __name__ == '__main__':
    main()
