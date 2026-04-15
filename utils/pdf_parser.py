import io
from config import MAX_PDF_PAGES, MAX_TEXT_CHARS


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """从 PDF 字节流中提取纯文本，最多处理 MAX_PDF_PAGES 页。"""
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages = pdf.pages[:MAX_PDF_PAGES]
            texts = []
            for page in pages:
                t = page.extract_text()
                if t:
                    texts.append(t)
            return "\n".join(texts)[:MAX_TEXT_CHARS]
    except ImportError:
        pass

    # fallback: PyPDF2
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        texts = []
        for page in reader.pages[:MAX_PDF_PAGES]:
            t = page.extract_text()
            if t:
                texts.append(t)
        return "\n".join(texts)[:MAX_TEXT_CHARS]
    except Exception as e:
        raise RuntimeError(f"PDF 解析失败：{e}")


def truncate_text(text: str) -> str:
    """截断文本以适配 LLM 上下文窗口。"""
    if len(text) > MAX_TEXT_CHARS:
        return text[:MAX_TEXT_CHARS] + "\n\n[...文本已截断，仅展示前部分内容...]"
    return text
