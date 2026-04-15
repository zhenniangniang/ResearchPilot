from utils.llm_client import chat
from utils.pdf_parser import extract_text_from_pdf, truncate_text
from prompts.literature_prompts import (
    LITERATURE_SYSTEM,
    LITERATURE_USER,
    LITERATURE_QA_SYSTEM,
    LITERATURE_QA_USER,
)


def analyze_literature(text: str) -> str:
    """对文献文本进行结构化解析，返回 Markdown 格式结果。"""
    text = truncate_text(text)
    user_prompt = LITERATURE_USER.format(text=text)
    return chat(LITERATURE_SYSTEM, user_prompt)


def analyze_pdf(file_bytes: bytes) -> tuple[str, str]:
    """
    解析 PDF 文件并进行文献分析。
    返回 (extracted_text, analysis_result)
    """
    raw_text = extract_text_from_pdf(file_bytes)
    if not raw_text.strip():
        raise ValueError("无法从 PDF 中提取文字，请检查文件是否为扫描件或加密文件。")
    result = analyze_literature(raw_text)
    return raw_text, result


def ask_literature_question(text: str, question: str) -> str:
    """针对文献内容进行追问。"""
    text = truncate_text(text)
    user_prompt = LITERATURE_QA_USER.format(text=text, question=question)
    return chat(LITERATURE_QA_SYSTEM, user_prompt)
