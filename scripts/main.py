"""
主程序 - 整合日报、周报、月报生成功能
"""
import os
import sys
import argparse
from datetime import datetime, timedelta

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
    
    # 简化处理，返回文本内容
    return [{'content': markdown_text, 'date': datetime.now().strftime('%Y-%m-%d')}]


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
    
    # 生成Markdown报告（使用现有的vitepress_generator）
    try:
        from vitepress_generator import VitePressGenerator
        vp_generator = VitePressGenerator(project_root)
        vp_generator.generate()
        print(f"\n日报生成完成: {date_str}")
    except Exception as e:
        print(f"生成Markdown报告失败: {e}")
    
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
