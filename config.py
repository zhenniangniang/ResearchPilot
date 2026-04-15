import os

# ==================== LLM 配置 ====================
# 优先级：Streamlit Secrets（云端）> 环境变量 > 代码默认值
# 部署到 Streamlit Cloud 时，在 Advanced Settings > Secrets 中填写

def _get_secret(key: str, default: str = "") -> str:
    """兼容本地运行和 Streamlit Cloud 部署的配置读取。"""
    try:
        import streamlit as st
        val = st.secrets.get(key)
        if val:
            return val
    except Exception:
        pass
    return os.getenv(key, default)


LLM_API_KEY  = _get_secret("LLM_API_KEY",  "sk-0a7e47d980a44aefaf8e19157b4ad3fd")
LLM_BASE_URL = _get_secret("LLM_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
LLM_MODEL    = _get_secret("LLM_MODEL",    "qwen-plus")

# ==================== 文档解析配置 ====================
MAX_PDF_PAGES  = 30       # 最多解析 PDF 页数
MAX_TEXT_CHARS = 12000    # 送入 LLM 的最大字符数（避免超出上下文）

# ==================== 数据分析配置 ====================
MAX_ROWS_PREVIEW = 5      # 数据预览行数
MAX_COLS_SHOW    = 20     # 最多展示列数
