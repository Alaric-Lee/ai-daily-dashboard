import os
import datetime
from jinja2 import Template

# 导入数据获取模块
import model_ranking
import model_news
import open_source_apps
import successful_cases

def main():
    # 获取当前日期
    today = datetime.date.today()
    date_str = today.strftime("%Y-%m-%d")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 获取项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 获取数据
    print("获取大模型综合评测榜单...")
    ranking_data = model_ranking.get_model_ranking()
    
    print("获取最新大模型相关资讯...")
    news_data = model_news.get_model_news()
    
    print("获取开源社区热门AI应用...")
    open_source_data = open_source_apps.get_open_source_apps()
    
    print("获取AI创新...")
    successful_data = successful_cases.get_successful_cases()
    
    # 渲染模板
    template_path = os.path.join(project_root, 'templates', 'dashboard_template.md')
    with open(template_path, 'r', encoding='utf-8') as f:
        template = Template(f.read())
    
    rendered_content = template.render(
        date=date_str,
        timestamp=timestamp,
        model_ranking=ranking_data,
        model_news=news_data,
        open_source_apps=open_source_data,
        successful_cases=successful_data
    )
    
    # 保存生成的Markdown文件到docs目录
    docs_dir = os.path.join(project_root, 'docs')
    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir)
    
    output_file = os.path.join(docs_dir, f'{date_str}.md')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(rendered_content)
    
    print(f"生成完成: {output_file}")
    
    # 保存到output目录作为备份
    output_dir = os.path.join(project_root, 'output')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    backup_file = os.path.join(output_dir, f'{date_str}.md')
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(rendered_content)
    
    print(f"备份完成: {backup_file}")
    
    # 更新历史记录
    update_archive(project_root)
    
    print("\n所有任务完成!")

def update_archive(project_root):
    """更新历史记录"""
    docs_dir = os.path.join(project_root, 'docs')
    files = sorted([f for f in os.listdir(docs_dir) if f.endswith('.md') and f not in ['index.md', 'archive.md']], reverse=True)
    
    # 更新历史记录
    archive_content = "# 📅 历史记录\n\n"
    archive_content += "## 按日期查看\n\n"
    
    current_month = None
    for file in files:
        date_str = file.replace('.md', '')
        year_month = date_str[:7]  # YYYY-MM
        
        if year_month != current_month:
            if current_month:
                archive_content += "\n"
            current_month = year_month
            archive_content += f"### {year_month}\n\n"
            
        archive_content += f"- [{date_str}]({date_str})\n"
    
    archive_path = os.path.join(docs_dir, 'archive.md')
    with open(archive_path, 'w', encoding='utf-8') as f:
        f.write(archive_content)
    
    print("历史记录更新完成")

if __name__ == "__main__":
    main()