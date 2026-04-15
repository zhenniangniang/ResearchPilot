from utils.llm_client import chat
from prompts.expression_prompts import (
    EXPRESSION_SYSTEM,
    OUTLINE_USER,
    PPT_USER,
    RESULT_PARAGRAPH_USER,
    CHART_DESCRIPTION_USER,
)


def generate_outline(topic: str, context: str = "") -> str:
    """生成开题报告提纲。"""
    user_prompt = OUTLINE_USER.format(topic=topic, context=context or "无")
    return chat(EXPRESSION_SYSTEM, user_prompt)


def generate_ppt_structure(topic: str, context: str = "", duration: int = 10) -> str:
    """生成 PPT 汇报结构框架。"""
    user_prompt = PPT_USER.format(topic=topic, context=context or "无", duration=duration)
    return chat(EXPRESSION_SYSTEM, user_prompt)


def generate_result_paragraph(method: str, results: str, context: str = "") -> str:
    """生成论文结果段落。"""
    user_prompt = RESULT_PARAGRAPH_USER.format(
        method=method, results=results, context=context or "无"
    )
    return chat(EXPRESSION_SYSTEM, user_prompt)


def generate_chart_description(chart_type: str, description: str, findings: str) -> str:
    """生成图表说明文字。"""
    user_prompt = CHART_DESCRIPTION_USER.format(
        chart_type=chart_type, description=description, findings=findings
    )
    return chat(EXPRESSION_SYSTEM, user_prompt)
