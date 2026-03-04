from datetime import datetime

def get_model_ranking():
    """获取大模型综合评测榜单（直接链接形式）"""
    
    content = "以下是当前主流大模型的权威评测榜单，点击链接查看最新排名：\n\n"
    
    # 1. Hugging Face Open LLM Leaderboard
    content += "### 1. Hugging Face Open LLM Leaderboard\n\n"
    content += "开源大模型综合评测榜单，涵盖多项基准测试：\n\n"
    content += "- **链接**：[https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard](https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard)\n"
    content += "- **特点**：包含MMLU、HumanEval、GSM8K等多项基准测试，支持多种模型对比\n\n"
    
    # 2. LMSYS Chatbot Arena
    content += "### 2. LMSYS Chatbot Arena\n\n"
    content += "基于用户投票的大模型对战评测榜单：\n\n"
    content += "- **链接**：[https://arena.ai/leaderboard](https://arena.ai/leaderboard)\n"
    content += "- **特点**：通过真实用户对战投票，反映模型在实际使用中的表现\n\n"
    
    # 3. OpenCompass 司南评测榜单
    content += "### 3. OpenCompass 司南评测榜单\n\n"
    content += "上海人工智能实验室推出的大模型评测体系：\n\n"
    content += "- **链接**：[https://rank.opencompass.org.cn/home](https://rank.opencompass.org.cn/home)\n"
    content += "- **特点**：中国自主研发的评测体系，覆盖多语言和多任务场景\n\n"
    
    today = datetime.now().strftime("%Y-%m-%d")
    content += f"> 📅 数据更新时间：{today}\n"
    content += "> 💡 提示：点击上述链接查看最新的大模型评测排名。\n"
    
    return content

if __name__ == "__main__":
    # 测试
    result = get_model_ranking()
    print(result)