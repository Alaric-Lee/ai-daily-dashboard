import requests
import xml.etree.ElementTree as ET
from datetime import datetime

def get_model_news():
    """抓取最新大模型相关资讯"""
    # 使用可靠的RSS源
    rss_urls = [
        "https://www.qbitai.com/feed",     # 量子位（主要源）
    ]
    
    news_list = []
    seen_titles = set()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
    }
    
    for url in rss_urls:
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.encoding = 'utf-8'
            
            # 检查响应内容
            if not response.content or len(response.content) < 100:
                print(f"抓取 {url} 失败: 响应内容为空或过短")
                continue
            
            # 解析RSS
            try:
                root = ET.fromstring(response.content)
            except ET.ParseError as e:
                print(f"解析 {url} 失败: XML解析错误 - {e}")
                continue
            
            # 处理不同格式的RSS
            items = root.findall('.//item')
            if not items:
                items = root.findall('.//{http://www.w3.org/2005/Atom}entry')
            
            if not items:
                print(f"抓取 {url} 失败: 未找到RSS条目")
                continue
                
            for item in items[:10]:  # 每个源取前10条
                try:
                    # 获取标题
                    title_elem = item.find('title')
                    if title_elem is None:
                        title_elem = item.find('.//{http://www.w3.org/2005/Atom}title')
                    title = title_elem.text if title_elem is not None else "无标题"
                    
                    # 获取链接
                    link_elem = item.find('link')
                    if link_elem is None:
                        link_elem = item.find('.//{http://www.w3.org/2005/Atom}link')
                    link = link_elem.text if link_elem is not None else ""
                    if not link and link_elem is not None:
                        link = link_elem.get('href', '')
                    
                    # 获取摘要
                    desc_elem = item.find('description')
                    if desc_elem is None:
                        desc_elem = item.find('summary')
                    if desc_elem is None:
                        desc_elem = item.find('.//{http://www.w3.org/2005/Atom}summary')
                    
                    description = ""
                    if desc_elem is not None and desc_elem.text:
                        # 去除HTML标签
                        import re
                        description = re.sub('<[^<]+?>', '', desc_elem.text)
                        description = re.sub('&nbsp;', ' ', description)
                        description = description.strip()
                        description = description[:80] + "..." if len(description) > 80 else description
                    
                    # 获取来源
                    source = url.split("//")[1].split("/")[0].replace("www.", "")
                    
                    # 去重
                    if title and title not in seen_titles:
                        seen_titles.add(title)
                        news_list.append({
                            'title': title,
                            'source': source,
                            'description': description,
                            'link': link
                        })
                        
                except Exception as e:
                    print(f"处理条目失败: {e}")
                    continue
            
            print(f"成功抓取 {url}: 获取了 {len(items)} 条资讯")
                    
        except requests.exceptions.RequestException as e:
            print(f"抓取 {url} 失败: 网络请求错误 - {str(e)}")
            continue
        except ET.ParseError as e:
            print(f"解析 {url} 失败: XML解析错误 - {str(e)}")
            continue
        except Exception as e:
            print(f"抓取 {url} 失败: {str(e)}")
            continue
    
    # 生成Markdown列表
    if not news_list:
        return "> 暂无最新资讯\n"
    
    markdown_list = []
    for news in news_list[:10]:  # 保留前10条
        markdown_list.append(f"- **{news['title']}** ({news['source']})：{news['description']} [查看原文]({news['link']})")
    
    return "\n".join(markdown_list)

if __name__ == "__main__":
    # 测试
    result = get_model_news()
    print(result)