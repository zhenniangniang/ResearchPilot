import sys
import os

# 确保从项目根目录运行时模块可被正确导入
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st

# ─── 页面配置（必须是第一条 Streamlit 命令）───────────────────────────────────
st.set_page_config(
    page_title="ResearchPilot · AI科研助手",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── 模块导入 ──────────────────────────────────────────────────────────────────
from modules.literature import analyze_literature, analyze_pdf, ask_literature_question
from modules.data_analysis import load_and_analyze, ask_data_question
from modules.expression import (
    generate_outline,
    generate_ppt_structure,
    generate_result_paragraph,
    generate_chart_description,
)
import config

# ─── 自定义样式 ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* 主标题区 */
    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 2rem 2.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: white;
    }
    .main-header h1 { margin: 0; font-size: 2rem; }
    .main-header p  { margin: 0.4rem 0 0; opacity: 0.8; font-size: 1rem; }

    /* 功能卡片 */
    .feature-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 0.8rem;
    }

    /* 结果区域 */
    .result-box {
        background: #f0f9ff;
        border-left: 4px solid #0ea5e9;
        border-radius: 0 8px 8px 0;
        padding: 1rem 1.2rem;
    }

    /* 隐藏 Streamlit 默认底部 */
    footer { visibility: hidden; }

    /* 按钮美化 */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ─── Session State 初始化 ──────────────────────────────────────────────────────
for key in ["lit_text", "lit_result", "data_df", "data_info",
            "data_advice", "data_filename"]:
    if key not in st.session_state:
        st.session_state[key] = None


# ══════════════════════════════════════════════════════════════════════════════
# 侧边栏
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🔬 ResearchPilot")
    st.markdown("*面向科研学习场景的 AI 智能助手*")
    st.divider()

    page = st.radio(
        "功能导航",
        ["📄 文献智能解读", "📊 数据分析建议", "✍️ 科研表达生成"],
        label_visibility="collapsed",
    )

    st.divider()
    st.markdown("### ⚙️ 配置")
    api_key = st.text_input(
        "API Key",
        value=config.LLM_API_KEY if config.LLM_API_KEY != "your-api-key-here" else "",
        type="password",
        placeholder="输入你的 API Key",
        help="支持 OpenAI / 通义千问 / DeepSeek / 智谱等",
    )
    base_url = st.text_input(
        "Base URL",
        value=config.LLM_BASE_URL,
        help="OpenAI 兼容接口地址",
    )
    model_name = st.text_input("模型名称", value=config.LLM_MODEL)

    if st.button("保存配置", use_container_width=True):
        config.LLM_API_KEY = api_key
        config.LLM_BASE_URL = base_url
        config.LLM_MODEL = model_name
        st.success("配置已更新")

    st.divider()
    st.caption("比赛作品 · ResearchPilot v1.0")


def _check_config() -> bool:
    """检查 API Key 是否已配置。"""
    if not config.LLM_API_KEY or config.LLM_API_KEY == "your-api-key-here":
        st.warning("⚠️ 请先在左侧侧边栏填写 API Key 后再使用功能。")
        return False
    return True


# ══════════════════════════════════════════════════════════════════════════════
# 页面 1：文献智能解读
# ══════════════════════════════════════════════════════════════════════════════
if page == "📄 文献智能解读":
    st.markdown("""
    <div class="main-header">
        <h1>📄 文献智能解读</h1>
        <p>上传 PDF 或粘贴文本，AI 自动提取关键信息并生成结构化摘要</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("#### 输入文献内容")
        input_method = st.radio(
            "选择输入方式", ["上传 PDF 文件", "粘贴文本内容"], horizontal=True
        )

        raw_text = ""
        if input_method == "上传 PDF 文件":
            uploaded_file = st.file_uploader(
                "上传 PDF 文献", type=["pdf"], label_visibility="collapsed"
            )
            if uploaded_file:
                st.info(f"已上传：{uploaded_file.name}（{uploaded_file.size // 1024} KB）")
        else:
            raw_text = st.text_area(
                "粘贴文献全文或摘要",
                height=280,
                placeholder="将文献内容粘贴到此处...",
                label_visibility="collapsed",
            )

        btn_analyze = st.button("🚀 开始解读", type="primary", use_container_width=True)

        if btn_analyze and _check_config():
            try:
                with st.spinner("AI 正在解读文献，请稍候..."):
                    if input_method == "上传 PDF 文件":
                        if not uploaded_file:
                            st.error("请先上传 PDF 文件")
                            st.stop()
                        file_bytes = uploaded_file.read()
                        raw_text, result = analyze_pdf(file_bytes)
                    else:
                        if not raw_text.strip():
                            st.error("请输入文献内容")
                            st.stop()
                        result = analyze_literature(raw_text)

                    st.session_state["lit_text"] = raw_text
                    st.session_state["lit_result"] = result
                    st.success("✅ 解读完成！")
            except Exception as e:
                st.error(f"解读失败：{e}")

    with col2:
        st.markdown("#### 解读结果")
        if st.session_state["lit_result"]:
            st.markdown(st.session_state["lit_result"])
            st.download_button(
                "⬇️ 下载解读报告（Markdown）",
                data=st.session_state["lit_result"],
                file_name="文献解读报告.md",
                mime="text/markdown",
                use_container_width=True,
            )
        else:
            st.markdown(
                '<div class="feature-card">解读结果将在此处显示</div>',
                unsafe_allow_html=True,
            )

    # 追问区
    if st.session_state["lit_text"]:
        st.divider()
        st.markdown("#### 💬 追问文献")
        q_col, btn_col = st.columns([5, 1])
        with q_col:
            follow_q = st.text_input(
                "针对该文献提问",
                placeholder="例如：作者采用的是什么实验设计？样本量是多少？",
                label_visibility="collapsed",
            )
        with btn_col:
            ask_btn = st.button("提问", use_container_width=True)

        if ask_btn and follow_q and _check_config():
            with st.spinner("思考中..."):
                answer = ask_literature_question(st.session_state["lit_text"], follow_q)
            st.markdown(
                f'<div class="result-box">{answer}</div>', unsafe_allow_html=True
            )


# ══════════════════════════════════════════════════════════════════════════════
# 页面 2：数据分析建议
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📊 数据分析建议":
    st.markdown("""
    <div class="main-header">
        <h1>📊 数据分析建议</h1>
        <p>上传 Excel / CSV，AI 自动识别变量类型并推荐最适合的统计分析方法</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("#### 上传数据文件")
        uploaded_data = st.file_uploader(
            "上传数据（Excel / CSV）",
            type=["xlsx", "xls", "csv"],
            label_visibility="collapsed",
        )
        research_goal = st.text_area(
            "研究目的（可选）",
            placeholder="例如：探索哪些因素影响患者30天再入院率...",
            height=100,
            help="描述你的研究问题，AI 可给出更针对性的建议",
        )
        btn_data = st.button("🔍 分析数据", type="primary", use_container_width=True)

        if btn_data and _check_config():
            if not uploaded_data:
                st.error("请先上传数据文件")
            else:
                try:
                    with st.spinner("正在分析数据结构并生成建议..."):
                        file_bytes = uploaded_data.read()
                        df, info, advice = load_and_analyze(
                            file_bytes, uploaded_data.name, research_goal
                        )
                        st.session_state["data_df"] = df
                        st.session_state["data_info"] = info
                        st.session_state["data_advice"] = advice
                        st.session_state["data_filename"] = uploaded_data.name
                    st.success("✅ 分析完成！")
                except Exception as e:
                    st.error(f"分析失败：{e}")

        # 数据预览
        if st.session_state["data_df"] is not None:
            st.markdown("#### 数据预览")
            df = st.session_state["data_df"]
            st.caption(f"共 {df.shape[0]} 行 × {df.shape[1]} 列")
            from utils.data_parser import get_preview
            st.dataframe(get_preview(df), use_container_width=True)

            # 变量类型统计
            info = st.session_state["data_info"]
            if info:
                type_counts: dict = {}
                for vtype in info["variable_types"].values():
                    type_counts[vtype] = type_counts.get(vtype, 0) + 1
                metric_cols = st.columns(len(type_counts))
                for i, (vtype, cnt) in enumerate(type_counts.items()):
                    metric_cols[i].metric(vtype, cnt)

    with col2:
        st.markdown("#### AI 分析建议")
        if st.session_state["data_advice"]:
            st.markdown(st.session_state["data_advice"])
            st.download_button(
                "⬇️ 下载分析建议（Markdown）",
                data=st.session_state["data_advice"],
                file_name="数据分析建议.md",
                mime="text/markdown",
                use_container_width=True,
            )
        else:
            st.markdown(
                '<div class="feature-card">分析建议将在此处显示</div>',
                unsafe_allow_html=True,
            )

    # 追问区
    if st.session_state["data_info"]:
        st.divider()
        st.markdown("#### 💬 追问数据分析")
        q_col2, btn_col2 = st.columns([5, 1])
        with q_col2:
            data_q = st.text_input(
                "追问",
                placeholder="例如：如果结局变量是连续的，应该用什么方法检验两组差异？",
                label_visibility="collapsed",
            )
        with btn_col2:
            ask_data_btn = st.button("提问", key="ask_data", use_container_width=True)

        if ask_data_btn and data_q and _check_config():
            with st.spinner("思考中..."):
                ans = ask_data_question(
                    st.session_state["data_info"],
                    st.session_state["data_advice"] or "",
                    data_q,
                )
            st.markdown(f'<div class="result-box">{ans}</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# 页面 3：科研表达生成
# ══════════════════════════════════════════════════════════════════════════════
elif page == "✍️ 科研表达生成":
    st.markdown("""
    <div class="main-header">
        <h1>✍️ 科研表达生成</h1>
        <p>输入研究内容，AI 自动生成开题报告提纲、PPT框架、论文段落及图表说明</p>
    </div>
    """, unsafe_allow_html=True)

    expr_type = st.segmented_control(
        "选择生成类型",
        ["📋 开题报告提纲", "🖥️ PPT 汇报结构", "📝 论文结果段落", "🖼️ 图表说明文字"],
        default="📋 开题报告提纲",
    )

    col_form, col_result = st.columns([1, 1], gap="large")

    with col_form:
        result_text = ""

        # ── 开题报告提纲 ──────────────────────────────────────────────────────
        if expr_type == "📋 开题报告提纲":
            st.markdown("#### 开题报告提纲生成")
            topic = st.text_input(
                "研究主题 *",
                placeholder="例如：基于深度学习的胸部 CT 肺结节自动检测研究",
            )
            context = st.text_area(
                "补充说明（可选）",
                placeholder="研究背景、数据来源、目标人群等...",
                height=120,
            )
            if st.button("生成提纲", type="primary", use_container_width=True):
                if not topic:
                    st.error("请填写研究主题")
                elif _check_config():
                    with st.spinner("生成中..."):
                        result_text = generate_outline(topic, context)

        # ── PPT 汇报结构 ──────────────────────────────────────────────────────
        elif expr_type == "🖥️ PPT 汇报结构":
            st.markdown("#### PPT 汇报框架生成")
            topic = st.text_input(
                "汇报主题 *",
                placeholder="例如：RNA-seq 差异表达分析结果汇报",
            )
            context = st.text_area(
                "内容摘要（可选）",
                placeholder="主要研究内容、核心发现...",
                height=100,
            )
            duration = st.slider("汇报时长（分钟）", 5, 30, 10)
            if st.button("生成 PPT 框架", type="primary", use_container_width=True):
                if not topic:
                    st.error("请填写汇报主题")
                elif _check_config():
                    with st.spinner("生成中..."):
                        result_text = generate_ppt_structure(topic, context, duration)

        # ── 论文结果段落 ──────────────────────────────────────────────────────
        elif expr_type == "📝 论文结果段落":
            st.markdown("#### 论文结果段落生成")
            method = st.text_input(
                "分析方法 *",
                placeholder="例如：多因素 Logistic 回归分析",
            )
            results = st.text_area(
                "关键数据/结果 *",
                placeholder="例如：年龄（OR=1.05, 95%CI 1.02-1.08, P<0.001）、\n高血压（OR=2.3, 95%CI 1.4-3.7, P=0.001）...",
                height=140,
            )
            context = st.text_area(
                "补充说明（可选）",
                placeholder="研究背景或样本信息...",
                height=80,
            )
            if st.button("生成段落", type="primary", use_container_width=True):
                if not method or not results:
                    st.error("请填写分析方法和关键结果")
                elif _check_config():
                    with st.spinner("生成中..."):
                        result_text = generate_result_paragraph(method, results, context)

        # ── 图表说明文字 ──────────────────────────────────────────────────────
        elif expr_type == "🖼️ 图表说明文字":
            st.markdown("#### 图表说明文字生成")
            chart_type = st.selectbox(
                "图表类型 *",
                ["折线图", "柱状图", "散点图", "箱线图", "热图", "生存曲线", "ROC曲线",
                 "火山图", "流程图", "其他"],
            )
            description = st.text_area(
                "图表内容描述 *",
                placeholder="描述图表展示的内容，如：X轴为时间，Y轴为累积生存率，展示了治疗组与对照组的生存曲线...",
                height=120,
            )
            findings = st.text_area(
                "主要发现 *",
                placeholder="图表揭示的核心结论...",
                height=80,
            )
            if st.button("生成图注", type="primary", use_container_width=True):
                if not description or not findings:
                    st.error("请填写图表描述和主要发现")
                elif _check_config():
                    with st.spinner("生成中..."):
                        result_text = generate_chart_description(
                            chart_type, description, findings
                        )

    with col_result:
        st.markdown("#### 生成结果")
        if result_text:
            st.markdown(result_text)
            st.download_button(
                "⬇️ 下载结果（Markdown）",
                data=result_text,
                file_name="科研表达生成结果.md",
                mime="text/markdown",
                use_container_width=True,
            )
        else:
            st.markdown(
                '<div class="feature-card">生成结果将在此处显示</div>',
                unsafe_allow_html=True,
            )
