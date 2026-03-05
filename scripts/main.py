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
    template_path = os.path.join(project_root, "templates", "dashboard_template.md")
    with open(template_path, "r", encoding="utf-8") as f:
        template = Template(f.read())

    rendered_content = template.render(
        date=date_str,
        timestamp=timestamp,
        model_ranking=ranking_data,
        model_news=news_data,
        open_source_apps=open_source_data,
        successful_cases=successful_data,
    )

    # 目录设置：最新资讯与历史记录分开
    docs_dir = os.path.join(project_root, "docs")
    latest_dir = os.path.join(docs_dir, "latest")
    history_dir = os.path.join(docs_dir, "history")

    for d in (docs_dir, latest_dir, history_dir):
        if not os.path.exists(d):
            os.makedirs(d)

    # 1. 最新资讯：始终覆盖 docs/latest/index.md
    latest_file = os.path.join(latest_dir, "index.md")
    with open(latest_file, "w", encoding="utf-8") as f:
        f.write(rendered_content)
    print(f"最新资讯已写入: {latest_file}")

    # 2. 历史存档：按日期保存到 docs/history/YYYY-MM-DD.md
    history_file = os.path.join(history_dir, f"{date_str}.md")
    with open(history_file, "w", encoding="utf-8") as f:
        f.write(rendered_content)
    print(f"历史记录已写入: {history_file}")

    # 3. 额外备份到 output 目录
    output_dir = os.path.join(project_root, "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    backup_file = os.path.join(output_dir, f"{date_str}.md")
    with open(backup_file, "w", encoding="utf-8") as f:
        f.write(rendered_content)

    print(f"备份完成: {backup_file}")

    # 4. 根据 history 目录更新历史索引页面 docs/history/index.md
    update_archive(project_root)

    print("\n所有任务完成!")

def update_archive(project_root):
    """根据 docs/history 目录生成历史索引页面 docs/history/index.md"""
    history_dir = os.path.join(project_root, "docs", "history")

    files = sorted(
        [
            f
            for f in os.listdir(history_dir)
            if f.endswith(".md") and f != "index.md"
        ],
        reverse=True,
    )

    archive_content = "# 📅 历史记录\n\n"
    archive_content += "## 按日期查看\n\n"

    current_month = None
    for file in files:
        date_str = file.replace(".md", "")
        year_month = date_str[:7]  # YYYY-MM

        if year_month != current_month:
            if current_month:
                archive_content += "\n"
            current_month = year_month
            archive_content += f"### {year_month}\n\n"

        archive_content += f"- [{date_str}](./{date_str})\n"

    index_path = os.path.join(history_dir, "index.md")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(archive_content)

    print("历史记录索引 docs/history/index.md 更新完成")


def update_index(project_root: str, latest_date: str) -> None:
    """根据最新日期更新 docs/index.md"""
    docs_dir = os.path.join(project_root, "docs")
    index_path = os.path.join(docs_dir, "index.md")

    files = sorted(
        [
            f
            for f in os.listdir(docs_dir)
            if f.endswith(".md") and f not in ["index.md", "archive.md"]
        ],
        reverse=True,
    )

    recent_dates = [f.replace(".md", "") for f in files[:7]]
    if recent_dates:
        recent_list = "\n".join(
            f"- [{date}](./{date})" for date in recent_dates
        )
    else:
        recent_list = "- 暂无数据"

    index_template = """---
layout: home

hero:
  name: "AI每日资讯"
  text: "每日更新的AI资讯仪表盘"
  tagline: 追踪大模型发展，掌握AI前沿动态
  actions:
    - theme: brand
      text: 查看最新
      link: ./__LATEST_DATE__
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

__RECENT_LIST__

<script setup>
import { onMounted } from 'vue'

onMounted(() => {
  const features = document.querySelectorAll('.VPFeature')

  const links = [
    './__LATEST_DATE__#🏆-大模型综合评测榜单',
    './__LATEST_DATE__#📰-最新大模型相关资讯',
    './__LATEST_DATE__#🔥-开源社区热门ai应用',
    './__LATEST_DATE__#💡-ai创新'
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
"""

    index_content = index_template.replace("__LATEST_DATE__", latest_date)
    index_content = index_content.replace("__RECENT_LIST__", recent_list)

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_content)

    print("首页 index.md 已更新为最新日期")


def update_vitepress_config(project_root: str, latest_date: str) -> None:
    """将 .vitepress/config.mts 中的“今日资讯/今日内容”链接指向最新日期"""
    config_path = os.path.join(project_root, ".vitepress", "config.mts")
    if not os.path.exists(config_path):
        return

    with open(config_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 查找当前配置中使用的日期（如 ./2026-03-04）
    match = re.search(r"\./(\d{{4}}-\d{{2}}-\d{{2}})", content)
    if not match:
        # 如果没找到，就直接假设当前 latest_date 即为第一次配置日期，追加使用
        old_date = None
    else:
        old_date = match.group(1)

    if old_date == latest_date:
        print("VitePress 配置已是最新日期，无需更新")
        return

    if old_date:
        new_content = content.replace(f"./{old_date}", f"./{latest_date}")
    else:
        # 没有检测到旧日期时，不做复杂处理，只是提示一下
        print("未在 VitePress 配置中检测到旧日期链接，暂不自动修改。")
        return

    with open(config_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(".vitepress/config.mts 中的今日资讯链接已更新为最新日期")

if __name__ == "__main__":
    main()