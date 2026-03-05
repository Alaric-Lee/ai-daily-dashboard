import requests
import json
import feedparser
import time
import re
from datetime import datetime, timedelta
import hashlib
from collections import Counter


class AIInnovationCollector:
    def __init__(self):
        self.innovations = []
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        self.sources = {
            'arxiv': 'http://export.arxiv.org/api/query?search_query=cat:cs.AI+OR+cat:cs.LG+OR+cat:cs.CL&sortBy=submittedDate&sortOrder=descending&max_results=30',
            'huggingface': 'https://huggingface.co/api/daily_papers',
            'reddit_ml': 'https://www.reddit.com/r/MachineLearning/hot/.json?limit=25',
            'reddit_ai': 'https://www.reddit.com/r/artificial/hot/.json?limit=25',
            'techcrunch': 'https://techcrunch.com/category/artificial-intelligence/feed/',
            'medium': 'https://medium.com/feed/tag/ai',
            'github_trending': 'https://api.github.com/search/repositories',
        }
        
    def clean_html(self, text: str) -> str:
        """移除HTML标签和常见转义符，防止Markdown中出现不完整的HTML片段"""
        if not text:
            return ""
        # 去掉所有HTML标签
        cleaned = re.sub(r"<[^>]+>", "", text)
        # 处理常见HTML实体
        cleaned = cleaned.replace("&nbsp;", " ")
        cleaned = cleaned.replace("&amp;", "&")
        cleaned = cleaned.replace("&lt;", "<")
        cleaned = cleaned.replace("&gt;", ">")
        return cleaned.strip()

    def fetch_arxiv_papers(self):
        """获取arXiv最新AI论文"""
        print("📚 正在获取arXiv论文...")
        innovations = []
        
        try:
            response = requests.get(self.sources['arxiv'], timeout=15)
            if response.status_code == 200:
                feed = feedparser.parse(response.text)
                
                for entry in feed.entries[:10]:
                    title = entry.title
                    raw_summary = getattr(entry, "summary", "") or ""
                    summary = self.clean_html(raw_summary)
                    summary = (summary[:200] + "...") if len(summary) > 200 else summary
                    
                    # 提取创新点
                    innovation_score = self.calculate_innovation_score(title + " " + summary)
                    
                    innovations.append({
                        'title': title,
                        'source': 'arXiv',
                        'type': '学术论文',
                        'summary': summary,
                        'url': entry.link,
                        'published': entry.published,
                        'innovation_score': innovation_score,
                        'tags': self.extract_tags(title + " " + summary)
                    })
        except Exception as e:
            print(f"arXiv获取失败: {e}")
        
        return innovations

    def fetch_huggingface_papers(self):
        """获取HuggingFace每日论文"""
        print("🤗 正在获取HuggingFace论文...")
        innovations = []
        
        try:
            response = requests.get(self.sources['huggingface'], timeout=15)
            if response.status_code == 200:
                papers = response.json()
                
                for paper in papers[:10]:
                    innovations.append({
                        'title': paper.get('title', ''),
                        'source': 'HuggingFace',
                        'type': 'AI论文/模型',
                        'summary': paper.get('summary', ''),
                        'url': f"https://huggingface.co/papers/{paper.get('id', '')}",
                        'published': datetime.now().isoformat(),
                        'innovation_score': paper.get('upvotes', 0) / 100,
                        'tags': paper.get('tags', [])
                    })
        except Exception as e:
            print(f"HuggingFace获取失败: {e}")
        
        return innovations

    def fetch_reddit_innovations(self):
        """从Reddit获取AI创新讨论"""
        print("👥 正在获取Reddit热门讨论...")
        innovations = []
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        for subreddit, url in [('ml', self.sources['reddit_ml']), ('ai', self.sources['reddit_ai'])]:
            try:
                response = requests.get(url, headers=headers, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    posts = data.get('data', {}).get('children', [])
                    
                    for post in posts[:5]:
                        post_data = post['data']
                        title = post_data['title']
                        score = post_data['score']
                        
                        # 创新关键词检测
                        innovation_keywords = ['new', 'novel', 'breakthrough', 'SOTA', 'state-of-the-art', 
                                              'innovation', 'revolutionary', '前沿', '突破', '创新']
                        has_innovation = any(keyword in title.lower() for keyword in innovation_keywords)

                        if has_innovation or score > 100:
                            summary_raw = (post_data.get("selftext", "") or "")[:200]
                            summary = self.clean_html(summary_raw)

                            innovations.append(
                                {
                                    "title": title,
                                    "source": f"Reddit r/{subreddit}",
                                    "type": "社区讨论",
                                    "summary": summary,
                                    "url": f"https://reddit.com{post_data['permalink']}",
                                    "published": datetime.fromtimestamp(
                                        post_data["created_utc"]
                                    ).isoformat(),
                                    "innovation_score": score / 1000,
                                    "tags": ["社区热点", "创新讨论"],
                                }
                            )
            except Exception as e:
                print(f"Reddit {subreddit}获取失败: {e}")
        
        return innovations

    def fetch_techcrunch_news(self):
        """从TechCrunch获取AI创新新闻"""
        print("📰 正在获取TechCrunch AI新闻...")
        innovations = []
        
        try:
            response = requests.get(self.sources['techcrunch'], timeout=15)
            if response.status_code == 200:
                feed = feedparser.parse(response.text)
                
                for entry in feed.entries[:5]:
                    title = entry.title
                    raw_summary = entry.get("summary", "") or ""
                    summary = self.clean_html(raw_summary)
                    summary = (summary[:200] + "...") if len(summary) > 200 else summary

                    innovations.append(
                        {
                            "title": title,
                            "source": "TechCrunch",
                            "type": "科技新闻",
                            "summary": summary,
                            "url": entry.link,
                            "published": entry.get(
                                "published", datetime.now().isoformat()
                            ),
                            "innovation_score": 0.5,
                            "tags": ["科技新闻", "AI应用"],
                        }
                    )
        except Exception as e:
            print(f"TechCrunch获取失败: {e}")
        
        return innovations

    def fetch_github_innovations(self):
        """从GitHub获取创新AI项目"""
        print("⭐ 正在获取GitHub创新项目...")
        innovations = []
        
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'AI-Innovation-Collector'
        }
        
        # 多个搜索查询以覆盖更多创新项目
        queries = [
            'AI+innovation+OR+breakthrough',
            'created:>2024-01-01+AI',
            'LLM+OR+large-language-model',
            'multimodal+AI',
            'AI-agent+OR+autonomous'
        ]
        
        for query in queries:
            try:
                params = {
                    'q': query,
                    'sort': 'stars',
                    'order': 'desc',
                    'per_page': 5
                }
                
                response = requests.get(self.sources['github_trending'], 
                                      params=params, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for item in data.get('items', [])[:3]:
                        name = item['full_name']
                        description = item.get('description', '')
                        stars = item['stargazers_count']
                        created_at = item['created_at']
                        
                        # 计算创新分数（基于新近度和热度）
                        days_old = (datetime.now() - datetime.fromisoformat(created_at.replace('Z', '+00:00'))).days
                        innovation_score = (stars / 1000) * (30 / max(days_old, 1))
                        
                        innovations.append({
                            'title': f"{name}: {description[:100]}",
                            'source': 'GitHub',
                            'type': '开源项目',
                            'summary': description or '创新AI项目',
                            'url': item['html_url'],
                            'published': created_at,
                            'innovation_score': innovation_score,
                            'tags': [item.get('language', 'Unknown'), '开源', '创新'],
                            'stars': stars
                        })
            except Exception as e:
                print(f"GitHub查询'{query}'失败: {e}")
                continue
        
        return innovations

    def fetch_medium_articles(self):
        """从Medium获取AI创新文章"""
        print("📝 正在获取Medium AI文章...")
        innovations = []
        
        try:
            response = requests.get(self.sources['medium'], timeout=15)
            if response.status_code == 200:
                feed = feedparser.parse(response.text)
                
                for entry in feed.entries[:8]:
                    title = entry.title

                    # 创新关键词过滤
                    innovation_indicators = [
                        "new",
                        "novel",
                        "breakthrough",
                        "state-of-the-art",
                        "前沿",
                        "突破",
                        "创新",
                        "革命性",
                    ]

                    if any(keyword in title.lower() for keyword in innovation_indicators):
                        raw_summary = entry.get("summary", "") or ""
                        summary = self.clean_html(raw_summary)
                        summary = (summary[:200] + "...") if len(summary) > 200 else summary

                        innovations.append(
                            {
                                "title": title,
                                "source": "Medium",
                                "type": "技术博客",
                                "summary": summary,
                                "url": entry.link,
                                "published": entry.get(
                                    "published", datetime.now().isoformat()
                                ),
                                "innovation_score": 0.6,
                                "tags": ["技术博客", "AI实践"],
                            }
                        )
        except Exception as e:
            print(f"Medium获取失败: {e}")
        
        return innovations

    def fetch_youtube_innovations(self):
        """模拟YouTube AI创新内容（实际需要通过YouTube API）"""
        print("🎥 正在获取YouTube创新内容（模拟）...")
        
        # 模拟数据，实际应用中需要YouTube Data API
        mock_innovations = [
            {
                'title': '突破性多模态AI模型发布：能同时理解文本、图像和音频',
                'source': 'YouTube',
                'type': '视频内容',
                'summary': '新模型在多项任务上超越GPT-4V，实现真正的多模态理解',
                'url': 'https://youtube.com/watch?v=mock1',
                'published': datetime.now().isoformat(),
                'innovation_score': 0.95,
                'tags': ['多模态', '模型创新', '视频'],
                'views': '50k+'
            },
            {
                'title': 'AI Agent新范式：自主学习与决策系统',
                'source': 'YouTube',
                'type': '视频内容',
                'summary': '介绍最新的AI Agent框架，能够自主学习和决策',
                'url': 'https://youtube.com/watch?v=mock2',
                'published': (datetime.now() - timedelta(days=1)).isoformat(),
                'innovation_score': 0.88,
                'tags': ['AI Agent', '自主学习', '视频'],
                'views': '35k+'
            },
            {
                'title': '开源模型突破：在手机上运行100B参数模型',
                'source': 'YouTube',
                'type': '视频内容',
                'summary': '新技术使大型语言模型可以在手机上运行，推理速度提升10倍',
                'url': 'https://youtube.com/watch?v=mock3',
                'published': (datetime.now() - timedelta(days=2)).isoformat(),
                'innovation_score': 0.92,
                'tags': ['模型压缩', '移动端AI', '视频'],
                'views': '80k+'
            }
        ]
        
        return mock_innovations

    def calculate_innovation_score(self, text):
        """计算内容的创新分数"""
        innovation_keywords = {
            '突破': 0.3, '创新': 0.3, '首次': 0.2, '革命性': 0.3,
            'SOTA': 0.4, 'state-of-the-art': 0.4, 'novel': 0.3,
            '前沿': 0.25, '新范式': 0.35, '颠覆': 0.35,
            'breakthrough': 0.4, 'innovation': 0.3, 'first-ever': 0.25,
            '开创新': 0.3, '重大进展': 0.2, '里程碑': 0.3
        }
        
        score = 0.2
        text_lower = text.lower()
        
        for keyword, weight in innovation_keywords.items():
            if keyword.lower() in text_lower:
                score += weight
        
        return min(score, 1.0)

    def extract_tags(self, text):
        """从文本中提取标签"""
        common_tags = [
            'LLM', '多模态', 'AI Agent', '模型优化', 'AI应用',
            '深度学习', '计算机视觉', 'NLP', '强化学习', '生成式AI',
            'RAG', '模型压缩', 'AI安全', '边缘计算', '自动驾驶'
        ]
        
        found_tags = []
        text_lower = text.lower()
        
        for tag in common_tags:
            if tag.lower() in text_lower:
                found_tags.append(tag)
        
        return found_tags[:3]

    def deduplicate_innovations(self):
        """去重并合并相似内容"""
        seen_titles = set()
        unique_innovations = []
        
        for innovation in self.innovations:
            # 创建标题的简单哈希用于去重
            title_hash = hashlib.md5(innovation['title'].lower().encode()).hexdigest()
            
            if title_hash not in seen_titles:
                seen_titles.add(title_hash)
                unique_innovations.append(innovation)
        
        self.innovations = unique_innovations

    def rank_innovations(self):
        """对创新内容进行排名"""
        # 计算综合得分
        for innovation in self.innovations:
            base_score = innovation.get('innovation_score', 0.5)
            
            # 根据来源加权
            source_weights = {
                'arXiv': 1.2,
                'HuggingFace': 1.15,
                'GitHub': 1.1,
                'TechCrunch': 1.0,
                'Reddit': 0.9,
                'Medium': 0.95,
                'YouTube': 1.05
            }
            
            source_weight = source_weights.get(innovation.get('source', ''), 1.0)
            
            # 新鲜度加权（越新越高）
            try:
                pub_date = datetime.fromisoformat(innovation.get('published', datetime.now().isoformat()).replace('Z', '+00:00'))
                days_old = (datetime.now() - pub_date).days
                freshness = max(0, 1 - days_old * 0.02)
            except:
                freshness = 0.8
            
            final_score = base_score * source_weight * freshness
            innovation['final_score'] = round(final_score, 3)
        
        # 按最终得分排序
        self.innovations.sort(key=lambda x: x.get('final_score', 0), reverse=True)

    def collect_all(self):
        """收集所有创新内容"""
        all_innovations = []
        
        # 并行或顺序收集
        collectors = [
            self.fetch_arxiv_papers,
            self.fetch_huggingface_papers,
            self.fetch_reddit_innovations,
            self.fetch_techcrunch_news,
            self.fetch_github_innovations,
            self.fetch_medium_articles,
            self.fetch_youtube_innovations
        ]
        
        for collector in collectors:
            try:
                innovations = collector()
                all_innovations.extend(innovations)
                time.sleep(1)
            except Exception as e:
                print(f"收集器{collector.__name__}执行失败: {e}")
        
        self.innovations = all_innovations
        self.deduplicate_innovations()
        self.rank_innovations()
        
        return self.innovations[:20]


def get_successful_cases():
    """获取AI创新资讯（从多个来源获取top20）"""
    print("🔍 正在收集AI创新信息...\n")
    
    collector = AIInnovationCollector()
    innovations = collector.collect_all()
    
    # 格式化输出
    formatted_cases = []
    for i, innovation in enumerate(innovations[:20], 1):
        formatted_case = f"""{i}. **{innovation['title']}**
   - 领域：{innovation['type']}
   - 来源：{innovation['source']}
   - 创新指数：{innovation.get('final_score', 0):.2f}
   - 描述：{innovation['summary']}
   - 链接：{innovation['url']}"""
        formatted_cases.append(formatted_case)
    
    return "\n\n".join(formatted_cases)


if __name__ == "__main__":
    # 测试
    result = get_successful_cases()
    print(result)
