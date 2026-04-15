import pandas as pd
from utils.llm_client import chat
from utils.data_parser import analyze_dataframe, load_dataframe, format_analysis_for_llm
from prompts.data_prompts import (
    DATA_SYSTEM,
    DATA_USER,
    DATA_FOLLOW_UP_SYSTEM,
    DATA_FOLLOW_UP_USER,
)


def analyze_data(df: pd.DataFrame, research_goal: str = "") -> tuple[dict, str]:
    """
    分析数据并获取 LLM 的统计方法建议。
    返回 (data_info_dict, advice_markdown)
    """
    info = analyze_dataframe(df)
    data_summary = format_analysis_for_llm(info)
    user_prompt = DATA_USER.format(
        data_summary=data_summary,
        research_goal=research_goal.strip() if research_goal else "未指定",
    )
    advice = chat(DATA_SYSTEM, user_prompt)
    return info, advice


def load_and_analyze(file_bytes: bytes, filename: str, research_goal: str = "") -> tuple[pd.DataFrame, dict, str]:
    """
    加载文件、分析数据、获取建议。
    返回 (dataframe, info_dict, advice_markdown)
    """
    df = load_dataframe(file_bytes, filename)
    info, advice = analyze_data(df, research_goal)
    return df, info, advice


def ask_data_question(info: dict, previous_advice: str, question: str) -> str:
    """针对数据分析结果进行追问。"""
    data_summary = format_analysis_for_llm(info)
    user_prompt = DATA_FOLLOW_UP_USER.format(
        data_summary=data_summary,
        previous_advice=previous_advice,
        question=question,
    )
    return chat(DATA_FOLLOW_UP_SYSTEM, user_prompt)
