import io
from utils.llm_client import chat
from utils.pdf_parser import extract_text_from_pdf, truncate_text
from prompts.expression_prompts import (
    EXPRESSION_SYSTEM,
    OUTLINE_USER,
    PPT_USER,
    PPT_FROM_FILE_USER,
    RESULT_PARAGRAPH_USER,
    CHART_DESCRIPTION_USER,
)


def generate_outline(topic: str, context: str = "") -> str:
    """生成开题报告提纲。"""
    user_prompt = OUTLINE_USER.format(topic=topic, context=context or "无")
    return chat(EXPRESSION_SYSTEM, user_prompt)


def generate_ppt_structure(topic: str, context: str = "", duration: int = 10) -> str:
    """生成 PPT 汇报结构框架（Markdown 文本）。"""
    user_prompt = PPT_USER.format(topic=topic, context=context or "无", duration=duration)
    return chat(EXPRESSION_SYSTEM, user_prompt)


def generate_ppt_from_file(file_bytes: bytes, filename: str, duration: int = 10) -> tuple[str, bytes]:
    """
    读取 PDF / Word 文件，AI 生成结构化 PPT 内容，并输出真实 .pptx 文件。
    返回 (markdown_preview, pptx_bytes)
    """
    # ── 1. 提取文字 ──────────────────────────────────────────────────────────
    fname = filename.lower()
    if fname.endswith(".pdf"):
        raw_text = extract_text_from_pdf(file_bytes)
    elif fname.endswith((".docx", ".doc")):
        from docx import Document
        doc = Document(io.BytesIO(file_bytes))
        raw_text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    else:
        raise ValueError(f"不支持的文件格式：{filename}，请上传 PDF 或 Word 文件")

    raw_text = truncate_text(raw_text)

    # ── 2. AI 生成结构化 PPT 内容 ─────────────────────────────────────────────
    user_prompt = PPT_FROM_FILE_USER.format(text=raw_text, duration=duration)
    ai_output = chat(EXPRESSION_SYSTEM, user_prompt)

    # ── 3. 解析 AI 输出并生成 .pptx ──────────────────────────────────────────
    pptx_bytes = _build_pptx(ai_output)
    return ai_output, pptx_bytes


def _build_pptx(ai_output: str) -> bytes:
    """将 AI 生成的结构化文本转换为 .pptx 文件字节。"""
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor

    prs = Presentation()
    prs.slide_width  = Inches(13.33)
    prs.slide_height = Inches(7.5)

    blank_layout = prs.slide_layouts[6]  # 空白布局

    def _add_slide(title: str, bullets: list[str], is_title_slide: bool = False):
        slide = prs.slides.add_slide(blank_layout)

        # 背景色
        from pptx.oxml.ns import qn
        from lxml import etree
        bg = slide.background
        fill = bg.fill
        fill.solid()
        fill.fore_color.rgb = RGBColor(0x1a, 0x1a, 0x2e) if is_title_slide else RGBColor(0xFF, 0xFF, 0xFF)

        # 标题
        txBox = slide.shapes.add_textbox(Inches(0.5), Inches(0.6), Inches(12.3), Inches(1.4))
        tf = txBox.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(32 if is_title_slide else 26)
        p.font.bold = True
        p.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF) if is_title_slide else RGBColor(0x1a, 0x1a, 0x2e)

        # 要点
        if bullets:
            bBox = slide.shapes.add_textbox(Inches(0.7), Inches(2.2), Inches(11.9), Inches(4.8))
            btf = bBox.text_frame
            btf.word_wrap = True
            for i, bullet in enumerate(bullets):
                if not bullet.strip():
                    continue
                bp = btf.paragraphs[0] if i == 0 else btf.add_paragraph()
                bp.text = f"• {bullet.strip()}"
                bp.font.size = Pt(18 if is_title_slide else 16)
                bp.font.color.rgb = RGBColor(0xCC, 0xDD, 0xFF) if is_title_slide else RGBColor(0x33, 0x33, 0x33)
                bp.space_after = Pt(6)

    # ── 解析 AI 输出 ──────────────────────────────────────────────────────────
    # 支持格式：
    # SLIDE N | 标题
    # 要点内容（每行一条，或 - / • 开头）
    import re
    slides_raw = re.split(r'(?i)slide\s*\d+\s*[|｜]', ai_output)
    slide_titles_raw = re.findall(r'(?i)slide\s*\d+\s*[|｜]\s*(.+)', ai_output)

    if not slide_titles_raw:
        # fallback：按 ## 标题分割
        slides_raw = re.split(r'\n#{1,3}\s+', ai_output)
        slide_titles_raw = re.findall(r'\n#{1,3}\s+(.+)', "\n" + ai_output)

    for idx, (title_line, content) in enumerate(zip(slide_titles_raw, slides_raw[1:])):
        title = title_line.strip()
        lines = [
            l.lstrip("-•*·▶ ").strip()
            for l in content.strip().splitlines()
            if l.strip() and not re.match(r'(?i)slide\s*\d', l)
        ]
        bullets = [l for l in lines if l][:8]
        _add_slide(title, bullets, is_title_slide=(idx == 0))

    if len(prs.slides) == 0:
        _add_slide("演示文稿", [ai_output[:200]], is_title_slide=True)

    buf = io.BytesIO()
    prs.save(buf)
    return buf.getvalue()


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
