import os
import re
from datetime import datetime

class VitePressGenerator:
    def __init__(self, project_root):
        self.project_root = project_root
        self.docs_dir = os.path.join(project_root, 'docs')
        self.output_dir = os.path.join(project_root, 'output')
        self.ensure_dirs()
        
    def ensure_dirs(self):
        """确保必要的目录存在"""
        os.makedirs(self.docs_dir, exist_ok=True)
        os.makedirs(os.path.join(self.docs_dir, '.vitepress'), exist_ok=True)
        
    def generate_index(self):
        """生成VitePress首页"""
        # 获取所有生成的Markdown文件
        files = sorted([f for f in os.listdir(self.output_dir) if f.endswith('.md')], reverse=True)
        
        if not files:
            return
            
        # 读取最新的文件内容作为首页
        latest_file = files[0]
        latest_path = os.path.join(self.output_dir, latest_file)
        
        with open(latest_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 生成首页
        index_content = f"""---
layout: home

hero:
  name: "AI每日资讯"
  text: "每日更新的AI资讯仪表盘"
  tagline: 追踪大模型发展，掌握AI前沿动态
  actions:
    - theme: brand
      text: 查看最新
      link: /{latest_file.replace('.md', '')}
    - theme: alt
      text: 历史记录
      link: /archive

features:
  - title: 大模型评测榜单
    details: 实时获取LMSYS Arena等权威评测数据
  - title: 最新AI资讯
    details: 聚合机器之心、量子位等科技媒体动态
  - title: 开源项目追踪
    details: 发现GitHub上热门的AI应用和工具
  - title: 成功案例
    details: 了解AI在各行业的最佳实践
---

## 最近更新

"""
        
        # 添加最近7天的链接
        for file in files[:7]:
            date_str = file.replace('.md', '')
            index_content += f"- [{date_str}]({date_str})\n"
            
        # 保存首页
        index_path = os.path.join(self.docs_dir, 'index.md')
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_content)
            
        print(f"首页生成完成: {index_path}")
        
    def generate_archive(self):
        """生成历史记录页面"""
        files = sorted([f for f in os.listdir(self.output_dir) if f.endswith('.md')], reverse=True)
        
        archive_content = "# 历史记录\n\n"
        archive_content += "## 按日期查看\n\n"
        
        # 按月份分组
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
            
        # 保存历史记录页面
        archive_path = os.path.join(self.docs_dir, 'archive.md')
        with open(archive_path, 'w', encoding='utf-8') as f:
            f.write(archive_content)
            
        print(f"历史记录页面生成完成: {archive_path}")
        
    def copy_daily_files(self):
        """将生成的Markdown文件复制到docs目录"""
        files = [f for f in os.listdir(self.output_dir) if f.endswith('.md')]
        
        for file in files:
            src_path = os.path.join(self.output_dir, file)
            dst_path = os.path.join(self.docs_dir, file)
            
            with open(src_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            with open(dst_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
        print(f"复制了 {len(files)} 个文件到docs目录")
        
    def generate(self):
        """生成完整的VitePress站点"""
        print("开始生成VitePress站点...")
        self.copy_daily_files()
        self.generate_index()
        self.generate_archive()
        print("VitePress站点生成完成!")

if __name__ == "__main__":
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    generator = VitePressGenerator(project_root)
    generator.generate()