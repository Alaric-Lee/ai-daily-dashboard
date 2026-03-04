# VitePress 安装与配置指南

## 一、安装 Node.js 和 npm

VitePress 需要 Node.js 16.0.0 或更高版本。请按照以下步骤安装：

### Windows 系统

1. **下载 Node.js 安装包**
   - 访问 [Node.js 官网](https://nodejs.org/)
   - 下载最新的 LTS 版本（推荐）
   - 运行安装程序，按照提示完成安装

2. **验证安装**
   打开命令提示符或 PowerShell，运行：
   ```bash
   node --version
   npm --version
   ```
   应该显示版本号，说明安装成功。

### macOS 系统

1. **使用 Homebrew 安装**
   ```bash
   brew install node
   ```

2. **或直接下载安装包**
   - 访问 [Node.js 官网](https://nodejs.org/)
   - 下载最新的 LTS 版本
   - 运行安装程序

3. **验证安装**
   ```bash
   node --version
   npm --version
   ```

### Linux 系统

1. **使用包管理器安装**
   - Ubuntu/Debian：
     ```bash
     sudo apt update
     sudo apt install nodejs npm
     ```
   - CentOS/RHEL：
     ```bash
     sudo dnf install nodejs npm
     ```

2. **或使用 nvm 安装**
   ```bash
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
   nvm install --lts
   ```

3. **验证安装**
   ```bash
   node --version
   npm --version
   ```

## 二、在项目中安装 VitePress

### 1. 初始化 npm 项目

在项目根目录运行：

```bash
npm init -y
```

### 2. 安装 VitePress

```bash
npm install -D vitepress
```

### 3. 初始化 VitePress 项目

```bash
npx vitepress init
```

按照提示进行配置：
- 选择 "docs" 作为文档目录
- 选择适合的主题和配置

## 三、配置 VitePress

### 1. 更新 `docs/.vitepress/config.js`

```javascript
export default {
  title: 'AI每日资讯',
  description: '每日更新的AI资讯仪表盘',
  base: '/ai-daily-dashboard/',
  themeConfig: {
    nav: [
      { text: '首页', link: '/' },
      { text: '历史记录', link: '/archive' }
    ],
    sidebar: {
      '/': [
        {
          text: '今日资讯',
          items: [
            { text: '大模型评测榜单', link: '/#大模型综合评测榜单' },
            { text: '最新资讯', link: '/#最新大模型相关资讯' },
            { text: '开源项目', link: '/#开源社区热门AI应用' },
            { text: '成功案例', link: '/#AI应用最成功方案' }
          ]
        }
      ]
    },
    socialLinks: [
      { icon: 'github', link: 'https://github.com/yourusername/ai-daily-dashboard' }
    ]
  }
}
```

### 2. 更新首页内容 `docs/index.md`

```markdown
---
layout: home

hero:
  name: "AI每日资讯"
  text: "每日更新的AI资讯仪表盘"
  tagline: 追踪大模型发展，掌握AI前沿动态
  actions:
    - theme: brand
      text: 查看最新
      link: /2026-03-04
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

- [2026-03-04](2026-03-04)
```

### 3. 创建历史记录页面 `docs/archive.md`

```markdown
# 历史记录

## 按日期查看

### 2026-03

- [2026-03-04](2026-03-04)
```

## 四、更新数据获取脚本

### 1. 修改 `scripts/main.py`

更新脚本以生成符合 VitePress 格式的文件：

```python
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
    
    print("获取AI应用最成功方案...")
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
    
    # 保存生成的Markdown文件到docs目录（VitePress使用）
    docs_dir = os.path.join(project_root, 'docs')
    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir)
    
    output_file = os.path.join(docs_dir, f'{date_str}.md')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(rendered_content)
    
    print(f"生成完成: {output_file}")
    
    # 更新首页和历史记录
    update_index(project_root)

def update_index(project_root):
    """更新首页和历史记录"""
    docs_dir = os.path.join(project_root, 'docs')
    files = sorted([f for f in os.listdir(docs_dir) if f.endswith('.md') and f not in ['index.md', 'archive.md']], reverse=True)
    
    # 更新首页
    index_content = """---
layout: home

hero:
  name: "AI每日资讯"
  text: "每日更新的AI资讯仪表盘"
  tagline: 追踪大模型发展，掌握AI前沿动态
  actions:
    - theme: brand
      text: 查看最新
      link: /{latest_file}
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
    
    if files:
        latest_file = files[0].replace('.md', '')
        index_content = index_content.replace('{latest_file}', latest_file)
        
        for file in files[:7]:
            date_str = file.replace('.md', '')
            index_content += f"- [{date_str}]({date_str})\n"
    
    index_path = os.path.join(docs_dir, 'index.md')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    # 更新历史记录
    archive_content = "# 历史记录\n\n"
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
    
    print("首页和历史记录更新完成")

if __name__ == "__main__":
    main()
```

## 五、更新 GitHub Actions 工作流

### 更新 `.github/workflows/daily-update.yml`

```yaml
name: Daily AI Dashboard Update

on:
  schedule:
    - cron: '0 0 * * *'  # 每天凌晨执行
  workflow_dispatch:  # 允许手动触发
  push:
    branches:
      - main  # 推送到main分支时也触发

jobs:
  update-dashboard:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pages: write
      id-token: write
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      
      - name: Install Python dependencies
        run: |
          python -m pip install --upgrade pip
          pip install requests beautifulsoup4 lxml jinja2
      
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
      
      - name: Install VitePress
        run: npm install -D vitepress
      
      - name: Run data collection script
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: python scripts/main.py
      
      - name: Build VitePress site
        run: npx vitepress build docs
      
      - name: Setup Pages
        uses: actions/configure-pages@v4
      
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: docs/.vitepress/dist
      
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
      
      - name: Commit and push changes
        run: |
          git config --global user.name 'GitHub Actions'
          git config --global user.email 'actions@github.com'
          git add .
          if git diff --staged --quiet; then
            echo "No changes to commit"
          else
            git commit -m 'Update AI dashboard data - $(date +%Y-%m-%d)'
            git push
          fi
```

## 六、运行和预览

### 本地预览

```bash
npx vitepress dev docs
```

然后在浏览器中访问 `http://localhost:5173/ai-daily-dashboard/`

### 构建生产版本

```bash
npx vitepress build docs
```

构建后的文件会在 `docs/.vitepress/dist` 目录中。

## 七、部署到 GitHub Pages

1. **推送到 GitHub 仓库**
   ```bash
   git add .
   git commit -m "Setup VitePress"
   git push
   ```

2. **配置 GitHub Pages**
   - 进入仓库 Settings > Pages
   - 选择 "GitHub Actions" 作为构建和部署源
   - 保存设置

3. **触发工作流**
   - 进入 Actions 标签页
   - 找到 "Daily AI Dashboard Update" 工作流
   - 点击 "Run workflow" 手动触发一次

4. **访问网站**
   - 部署完成后，会显示网站 URL
   - 格式：`https://yourusername.github.io/ai-daily-dashboard/`

## 八、注意事项

1. **环境变量**
   - 如果需要 GitHub Token 来提高 API 访问限制，在仓库 Settings > Secrets and variables > Actions 中添加 `GITHUB_TOKEN` 变量

2. **数据抓取**
   - LMSYS Arena API 可能会有访问限制，请确保你的请求频率合理
   - 其他数据源也可能有访问限制，建议添加适当的错误处理和重试机制

3. **性能优化**
   - 对于大型项目，建议添加缓存机制，避免重复抓取数据
   - 考虑使用增量更新，只在必要时更新数据

4. **安全**
   - 不要在代码中硬编码敏感信息
   - 使用 GitHub Secrets 管理敏感配置

5. **维护**
   - 定期检查数据源是否可用
   - 及时更新依赖包，确保系统安全

## 九、常见问题

### 1. npm 安装失败

- 检查网络连接
- 尝试使用 npm 镜像：
  ```bash
  npm config set registry https://registry.npmmirror.com
  ```

### 2. VitePress 构建失败

- 检查 Markdown 文件格式是否正确
- 确保所有依赖都已正确安装
- 查看构建日志，定位具体错误

### 3. 数据抓取失败

- 检查网络连接
- 确认 API 端点是否可用
- 查看错误日志，分析具体原因
- 考虑添加代理或更换数据源

### 4. GitHub Pages 部署失败

- 检查工作流配置是否正确
- 确认权限设置是否完整
- 查看 Actions 日志，定位具体错误

---

按照以上步骤操作，你就可以成功使用 VitePress 来展示 AI 每日资讯仪表盘了！