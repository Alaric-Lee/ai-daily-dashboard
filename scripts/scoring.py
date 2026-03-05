"""
评分算法模块 - 为AI资讯计算重要性评分
"""
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple


class NewsScorer:
    """新闻评分器"""
    
    # 来源权重配置
    SOURCE_WEIGHTS = {
        # 顶级AI公司
        'OpenAI': 30,
        'Google': 28,
        'Anthropic': 28,
        'DeepMind': 28,
        'Meta': 25,
        'Microsoft': 25,
        
        # 学术和开源平台
        'arXiv': 25,
        'Hugging Face': 22,
        'GitHub': 20,
        'Papers With Code': 20,
        
        # 中文科技媒体
        '机器之心': 18,
        '量子位': 18,
        'InfoQ': 15,
        '雷锋网': 15,
        '36氪': 14,
        
        # 国际科技媒体
        'TechCrunch': 16,
        'The Verge': 16,
        'VentureBeat': 15,
        
        # 默认
        'default': 10
    }
    
    # 重要关键词及其权重
    KEYWORDS = {
        # 大模型名称
        'GPT-5': 8, 'GPT-4': 6, 'GPT-3': 4,
        'Claude': 7, 'Claude 3': 8,
        'Gemini': 7, 'Gemini Ultra': 8,
        'LLaMA': 6, 'LLaMA 3': 8,
        'Mistral': 6, 'Mixtral': 7,
        'Qwen': 6, 'ChatGLM': 5,
        
        # 技术突破
        'SOTA': 8, 'state of the art': 8,
        '突破': 7, '重大突破': 9,
        '里程碑': 8,
        '首次': 6,
        '超越': 6, '击败': 6,
        
        # 发布和开源
        '发布': 5, '正式发布': 7,
        '开源': 6, '全面开源': 8,
        '免费': 5,
        
        # 技术趋势
        '多模态': 6, '多模态AI': 7,
        'AI Agent': 7, '智能体': 6,
        'RAG': 5,
        '微调': 4, 'Fine-tuning': 4,
        'RLHF': 5,
        '向量数据库': 4,
        
        # 应用场景
        '代码生成': 5,
        '图像生成': 5,
        '视频生成': 6,
        '语音识别': 4,
        '自动驾驶': 5,
        
        # 商业动态
        '融资': 5, '估值': 5,
        '收购': 6, '并购': 6,
        '合作': 4,
        '战略': 4,
        
        # 安全和伦理
        'AI安全': 6,
        '对齐': 5,
        '幻觉': 4,
        '监管': 5,
    }
    
    @classmethod
    def calculate_score(cls, news_item: Dict[str, Any], reference_date: datetime = None) -> float:
        """
        计算单条新闻的评分
        
        Args:
            news_item: 新闻数据字典
            reference_date: 参考日期（用于计算时效性），默认为今天
        
        Returns:
            评分 (0-100)
        """
        if reference_date is None:
            reference_date = datetime.now()
        
        score = 0.0
        title = news_item.get('title', '')
        content = news_item.get('description', '') + news_item.get('content', '')
        source = news_item.get('source', '')
        news_date = news_item.get('date', '')
        
        title_lower = title.lower()
        content_lower = content.lower()
        
        # 1. 来源权重 (0-30分)
        source_score = 0
        for src, weight in cls.SOURCE_WEIGHTS.items():
            if src.lower() in source.lower():
                source_score = weight
                break
        if source_score == 0:
            source_score = cls.SOURCE_WEIGHTS['default']
        score += source_score
        
        # 2. 时效性 (0-25分)
        timeliness_score = 25
        if news_date:
            try:
                if isinstance(news_date, str):
                    news_date_obj = datetime.strptime(news_date, '%Y-%m-%d')
                else:
                    news_date_obj = news_date
                
                days_old = (reference_date - news_date_obj).days
                # 越新的新闻分数越高，超过7天分数为0
                timeliness_score = max(0, 25 - days_old * 3.5)
            except:
                pass
        score += timeliness_score
        
        # 3. 关键词匹配 (0-30分)
        keyword_score = 0
        matched_keywords = []
        
        for keyword, weight in cls.KEYWORDS.items():
            keyword_lower = keyword.lower()
            # 标题匹配权重更高
            if keyword_lower in title_lower:
                keyword_score += weight * 1.5
                matched_keywords.append(f"{keyword}(标题)")
            elif keyword_lower in content_lower:
                keyword_score += weight * 0.8
                matched_keywords.append(keyword)
        
        score += min(30, keyword_score)
        
        # 4. 内容质量 (0-15分)
        content_length = len(content)
        if content_length > 1000:
            content_score = 15
        elif content_length > 500:
            content_score = 12
        elif content_length > 200:
            content_score = 8
        elif content_length > 100:
            content_score = 5
        else:
            content_score = 2
        score += content_score
        
        # 5. 特殊标记加分 (0-10分)
        bonus_score = 0
        
        # 包含数字和具体数据
        if re.search(r'\d+%', title) or re.search(r'\d+倍', title):
            bonus_score += 3
        
        # 包含知名公司或产品
        major_companies = ['openai', 'google', 'anthropic', 'meta', 'microsoft', 'nvidia']
        for company in major_companies:
            if company in title_lower:
                bonus_score += 2
                break
        
        # 标题长度适中（太短可能信息量不足，太长可能不够精炼）
        title_length = len(title)
        if 20 <= title_length <= 60:
            bonus_score += 2
        
        score += min(10, bonus_score)
        
        # 确保分数在0-100之间
        final_score = min(100, max(0, score))
        
        # 添加调试信息（开发时使用）
        news_item['_score_details'] = {
            'source_score': source_score,
            'timeliness_score': timeliness_score,
            'keyword_score': min(30, keyword_score),
            'content_score': content_score,
            'bonus_score': min(10, bonus_score),
            'matched_keywords': matched_keywords[:5],  # 只保留前5个匹配的关键词
            'final_score': final_score
        }
        
        return final_score
    
    @classmethod
    def rank_news(cls, news_list: List[Dict[str, Any]], 
                  reference_date: datetime = None,
                  top_n: int = None) -> List[Dict[str, Any]]:
        """
        对新闻列表进行评分和排序
        
        Args:
            news_list: 新闻列表
            reference_date: 参考日期
            top_n: 只返回前N条，None表示返回全部
        
        Returns:
            按评分排序的新闻列表（高分在前）
        """
        # 为每条新闻计算评分
        scored_news = []
        for news in news_list:
            score = cls.calculate_score(news, reference_date)
            news['_score'] = score
            scored_news.append(news)
        
        # 按评分排序（高分在前）
        scored_news.sort(key=lambda x: x['_score'], reverse=True)
        
        # 去重（基于标题相似度）
        unique_news = []
        seen_titles = set()
        
        for news in scored_news:
            title = news.get('title', '').lower()
            # 简化的标题去重（取前20个字符作为指纹）
            title_fingerprint = title[:20]
            
            is_duplicate = False
            for seen in seen_titles:
                # 如果标题相似度超过80%，认为是重复
                if cls._title_similarity(title_fingerprint, seen) > 0.8:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                seen_titles.add(title_fingerprint)
                unique_news.append(news)
        
        # 返回前N条
        if top_n and len(unique_news) > top_n:
            return unique_news[:top_n]
        
        return unique_news
    
    @staticmethod
    def _title_similarity(title1: str, title2: str) -> float:
        """
        计算两个标题的相似度（简化版）
        
        Args:
            title1: 标题1
            title2: 标题2
        
        Returns:
            相似度 (0-1)
        """
        if not title1 or not title2:
            return 0.0
        
        # 使用简单的字符重叠率
        set1 = set(title1)
        set2 = set(title2)
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        if union == 0:
            return 0.0
        
        return intersection / union


if __name__ == '__main__':
    # 测试评分算法
    test_news = [
        {
            'title': 'OpenAI发布GPT-5：全新多模态能力震撼业界，性能提升300%',
            'description': 'OpenAI今日发布GPT-5，具备更强的多模态理解能力和更长的上下文窗口，在多项基准测试中超越前代产品。',
            'source': 'OpenAI',
            'date': '2026-03-04'
        },
        {
            'title': '某小公司发布新AI产品',
            'description': '这是一个普通的产品发布。',
            'source': '未知来源',
            'date': '2026-03-01'
        },
        {
            'title': 'Google DeepMind突破：AI首次在数学奥林匹克竞赛中获得金牌',
            'description': 'Google DeepMind的最新研究成果显示，其开发的AI系统在国际数学奥林匹克竞赛中表现出色，解决了多道高难度题目。',
            'source': 'Google',
            'date': '2026-03-04'
        }
    ]
    
    print("测试评分算法：\n")
    
    for news in test_news:
        score = NewsScorer.calculate_score(news)
        details = news['_score_details']
        print(f"标题: {news['title']}")
        print(f"来源: {news['source']}")
        print(f"总分: {score:.2f}")
        print(f"评分详情: {details}")
        print("-" * 50)
    
    # 测试排序
    print("\n排序后的新闻：")
    ranked = NewsScorer.rank_news(test_news, top_n=2)
    for i, news in enumerate(ranked, 1):
        print(f"{i}. [{news['_score']:.2f}] {news['title']}")
