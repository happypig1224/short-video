"""
内容安全与合规审查模块 (Content Moderation & Compliance Guard)
符合《生成式人工智能服务管理暂行办法》第十二条、第十五条之规定
在提交至大模型前对提示词进行合规检测与不良信息熔断拦截
"""

import re
from typing import Tuple, List

# 生产级合规敏感词汇规则集（涵盖涉政、涉暴、违禁品及不良低俗等核心大类）
PROHIBITED_KEYWORDS = [
    # 违规违法与暴恐极端
    "枪支", "弹药", "爆炸物", "炸药", "手枪", "步枪", "制毒", "贩毒", "毒品", "海洛因", "冰毒",
    "恐怖袭击", "自杀", "自残", "绝食", "暗杀", "暴乱", "偷渡", "黑客攻击", "木马病毒",
    # 低俗色情与涉黄
    "色情", "强奸", "幼女", "儿童色情", "露点", "生殖器", "裸体人像", "群交", "淫秽", "性交", "乱伦",
    # 虚假欺诈与伪造
    "伪造身份证", "伪造公章", "假钞", "洗钱", "高利贷", "传销", "赌博网站", "代开增值税发票"
]


def check_prompt_safety(prompt: str) -> Tuple[bool, str, List[str]]:
    """
    对用户输入的生图提示词进行合规审计
    :param prompt: 提示词文本
    :return: (is_safe, reason, hit_words)
    """
    if not prompt or not prompt.strip():
        return True, "通过", []

    text_lower = prompt.lower()
    hit_words = []

    for word in PROHIBITED_KEYWORDS:
        if word in text_lower:
            hit_words.append(word)

    if hit_words:
        masked_hits = [w[0] + "*" * (len(w) - 1) for w in hit_words]
        return False, f"提示词触及内容合规审计安全策略（敏感特征：{', '.join(masked_hits)}），已被合规引擎熔断拦截", hit_words

    return True, "通过", []
