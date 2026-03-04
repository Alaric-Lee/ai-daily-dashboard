import requests
import os

def get_open_source_apps():
    """抓取GitHub热门AI应用"""
    try:
        # GitHub API搜索热门AI项目
        # 使用GitHub Search API获取最近一周热门的AI相关项目
        url = "https://api.github.com/search/repositories"
        
        # 搜索关键词：AI、LLM、machine learning等
        params = {
            'q': 'AI OR LLM OR "machine learning" OR chatbot OR "large language model"',
            'sort': 'stars',
            'order': 'desc',
            'per_page': 20
        }
        
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'AI-Daily-Dashboard'
        }
        
        # 如果有GitHub Token，添加到headers
        github_token = os.getenv('GITHUB_TOKEN')
        if github_token:
            headers['Authorization'] = f'token {github_token}'
        
        response = requests.get(url, params=params, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            
            repo_list = []
            
            # 筛选出真正与AI相关的项目
            ai_keywords = ['ai', 'llm', 'chatgpt', 'deep learning', 'machine learning', 
                          'neural network', 'transformer', 'gpt', 'claude', 'gemini',
                          'stable diffusion', 'langchain', 'openai', 'anthropic']
            
            for repo in items[:10]:  # 取前10个
                description = (repo.get('description') or '').lower()
                name = repo.get('name', '').lower()
                
                # 检查是否包含AI相关关键词
                is_ai_related = any(keyword in description or keyword in name 
                                  for keyword in ai_keywords)
                
                if is_ai_related:
                    full_name = repo.get('full_name', 'Unknown')
                    stars = repo.get('stargazers_count', 0)
                    desc = repo.get('description') or '无描述'
                    html_url = repo.get('html_url', '')
                    language = repo.get('language') or '未知'
                    
                    repo_list.append(
                        f"- **{full_name}** ⭐{stars} ({language})：{desc} [链接]({html_url})"
                    )
            
            if repo_list:
                return "\n".join(repo_list)
            else:
                return "> 暂无热门AI应用数据\n"
        else:
            return f"> GitHub API请求失败，状态码：{response.status_code}\n"
            
    except Exception as e:
        return f"> GitHub数据抓取失败：{str(e)}\n"

if __name__ == "__main__":
    # 测试
    result = get_open_source_apps()
    print(result)