import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import re


def _clean_html(text: str) -> str:
    """移除HTML标签和常见转义符，保证摘要在Markdown中安全展示。"""
    if not text:
        return ""
    cleaned = re.sub(r"<[^>]+>", "", text)
    cleaned = cleaned.replace("&nbsp;", " ")
    cleaned = cleaned.replace("&amp;", "&")
    cleaned = cleaned.replace("&lt;", "<")
    cleaned = cleaned.replace("&gt;", ">")
    return cleaned.strip()


def _parse_published(item) -> datetime | None:
    """从RSS/Atom条目中解析发布时间，尽量兼容多种字段。"""
    # 常见字段：pubDate、updated、published、dc:date
    candidates = [
        "pubDate",
        "updated",
        "published",
        "{http://purl.org/dc/elements/1.1/}date",
    ]

    for tag in candidates:
        elem = item.find(tag)
        if elem is not None and elem.text:
            text = elem.text.strip()
            # RSS 2.0 常用格式，可用 parsedate_to_datetime 解析
            try:
                return parsedate_to_datetime(text)
            except Exception:
                pass
            # 其他情况尝试用 datetime.fromisoformat
            try:
                return datetime.fromisoformat(text.replace("Z", "+00:00"))
            except Exception:
                continue

    return None


def get_model_news():
    """抓取最新大模型相关资讯（多数据源 + 近几天内的新内容优先）"""
    # 多个RSS源：国产媒体 + 国际AI媒体
    rss_urls = [
        "https://www.qbitai.com/feed",  # 量子位（中文AI资讯）
        "https://techcrunch.com/tag/artificial-intelligence/feed/",  # TechCrunch AI 专题
        "https://www.marktechpost.com/feed/",  # MarkTechPost（AI研究/应用）
    ]

    news_list = []
    seen_titles = set()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }

    now = datetime.now(timezone.utc)
    max_age = timedelta(days=3)  # 只保留最近3天内的新闻

    for url in rss_urls:
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.encoding = "utf-8"

            if not response.content or len(response.content) < 100:
                print(f"抓取 {url} 失败: 响应内容为空或过短")
                continue

            try:
                root = ET.fromstring(response.content)
            except ET.ParseError as e:
                print(f"解析 {url} 失败: XML解析错误 - {e}")
                continue

            items = root.findall(".//item")
            if not items:
                items = root.findall(".//{http://www.w3.org/2005/Atom}entry")

            if not items:
                print(f"抓取 {url} 失败: 未找到RSS条目")
                continue

            for item in items[:20]:  # 每个源最多看前20条
                try:
                    # 标题
                    title_elem = item.find("title")
                    if title_elem is None:
                        title_elem = item.find(".//{http://www.w3.org/2005/Atom}title")
                    title = title_elem.text.strip() if title_elem is not None else "无标题"

                    # 发布时间（统一为 UTC aware，便于与 now 比较和后续排序）
                    published = _parse_published(item)
                    published_utc = None
                    if published is not None:
                        published_utc = (
                            published.astimezone(timezone.utc)
                            if published.tzinfo
                            else published.replace(tzinfo=timezone.utc)
                        )
                        if now - published_utc > max_age:
                            continue

                    # 链接
                    link_elem = item.find("link")
                    if link_elem is None:
                        link_elem = item.find(".//{http://www.w3.org/2005/Atom}link")
                    link = link_elem.text if link_elem is not None else ""
                    if not link and link_elem is not None:
                        link = link_elem.get("href", "")

                    # 摘要
                    desc_elem = (
                        item.find("description")
                        or item.find("summary")
                        or item.find(".//{http://www.w3.org/2005/Atom}summary")
                    )

                    description = ""
                    if desc_elem is not None and desc_elem.text:
                        description = _clean_html(desc_elem.text)
                        description = (
                            description[:80] + "..."
                            if len(description) > 80
                            else description
                        )

                    # 来源域名
                    source = url.split("//")[1].split("/")[0].replace("www.", "")

                    # 去重（按标题）
                    if title and title not in seen_titles:
                        seen_titles.add(title)
                        news_list.append(
                            {
                                "title": title,
                                "source": source,
                                "description": description,
                                "link": link,
                                "published": published_utc,
                            }
                        )

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

    if not news_list:
        return "> 暂无最新资讯\n"

    # 先按发布时间（有时间的）倒序排，最近的在前（统一按 UTC aware 比较）
    _min = datetime.min.replace(tzinfo=timezone.utc)
    news_list.sort(
        key=lambda x: x["published"] or _min,
        reverse=True,
    )

    markdown_list = []
    for news in news_list[:10]:
        markdown_list.append(
            f"- **{news['title']}** ({news['source']})：{news['description']} [查看原文]({news['link']})"
        )

    return "\n".join(markdown_list)

if __name__ == "__main__":
    # 测试
    result = get_model_news()
    print(result)