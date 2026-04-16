import sys
import os
import io

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
    generate_ppt_from_file,
    generate_result_paragraph,
    generate_chart_description,
)
import config

# ─── 自定义样式 ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* 隐藏 Streamlit 右上角菜单和页脚 */
    #MainMenu { visibility: hidden; }
    header[data-testid="stHeader"] { background: transparent; }
    footer { visibility: hidden; }
    [data-testid="stToolbar"] { display: none; }
    [data-testid="stDecoration"] { display: none; }

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

    /* 隐私提示 */
    .privacy-note {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 6px;
        padding: 0.5rem 0.8rem;
        font-size: 0.75rem;
        color: #166534;
    }

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

    key_configured = bool(config.LLM_API_KEY)
    api_key = st.text_input(
        "API Key",
        value="",
        type="password",
        placeholder="已配置 ✓" if key_configured else "输入你的 API Key",
        help="支持 OpenAI / 通义千问 / DeepSeek / 智谱等",
    )
    base_url = st.text_input(
        "Base URL",
        value=config.LLM_BASE_URL,
        help="OpenAI 兼容接口地址",
    )
    model_name = st.text_input("模型名称", value=config.LLM_MODEL)

    if st.button("保存配置", use_container_width=True):
        if api_key.strip():
            config.LLM_API_KEY = api_key.strip()
        if base_url.strip():
            config.LLM_BASE_URL = base_url.strip()
        if model_name.strip():
            config.LLM_MODEL = model_name.strip()
        st.success("配置已更新")

    st.divider()
    st.markdown(
        '<div class="privacy-note">🔒 用户数据不留存，仅用于本次会话处理</div>',
        unsafe_allow_html=True,
    )
    st.caption("比赛作品 · ResearchPilot v1.0")


def _check_config() -> bool:
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
                with st.spinner("🤖 AI 正在解读文献，请稍候..."):
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
            with st.spinner("✨ 思考中，稍等一下～"):
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
        <p>上传数据，AI 推荐分析方法；或选择变量，即时生成可视化图表</p>
    </div>
    """, unsafe_allow_html=True)

    data_sub = st.segmented_control(
        "子模块切换",
        ["🔍 智能分析建议", "📈 变量可视化"],
        default="🔍 智能分析建议",
        label_visibility="collapsed",
    )

    # ══════════════════════════════════════════════════════════════════════════
    # 子模块 A：智能分析建议
    # ══════════════════════════════════════════════════════════════════════════
    if data_sub == "🔍 智能分析建议":
        col1, col2 = st.columns([1, 1], gap="large")

        with col1:
            st.markdown("#### 上传数据文件")
            uploaded_data = st.file_uploader(
                "上传数据（Excel / CSV）",
                type=["xlsx", "xls", "csv"],
                label_visibility="collapsed",
                key="data_uploader_analysis",
            )
            research_goal = st.text_area(
                "研究目的（可选）",
                placeholder="例如：探索哪些因素影响患者30天再入院率...",
                height=100,
                help="描述你的研究问题，AI 可给出更针对性的建议",
            )
            btn_data = st.button("🔍 开始分析", type="primary", use_container_width=True)

            if btn_data and _check_config():
                if not uploaded_data:
                    st.error("请先上传数据文件")
                else:
                    try:
                        with st.spinner("🧠 AI 正在分析数据结构，努力思考中..."):
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

                info = st.session_state["data_info"]
                if info:
                    type_counts: dict = {}
                    for vtype in info["variable_types"].values():
                        type_counts[vtype] = type_counts.get(vtype, 0) + 1
                    metric_cols = st.columns(min(len(type_counts), 4))
                    for i, (vtype, cnt) in enumerate(list(type_counts.items())[:4]):
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
                with st.spinner("✨ 思考中，稍等一下～"):
                    ans = ask_data_question(
                        st.session_state["data_info"],
                        st.session_state["data_advice"] or "",
                        data_q,
                    )
                st.markdown(f'<div class="result-box">{ans}</div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # 子模块 B：变量可视化
    # ══════════════════════════════════════════════════════════════════════════
    elif data_sub == "📈 变量可视化":

        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import seaborn as sns

        # 动态查找可用的中文字体（兼容本地 macOS 和云端 Linux）
        import matplotlib.font_manager as fm
        _cjk_candidates = [
            "Noto Sans CJK SC", "Noto Sans SC", "Noto Sans CJK",
            "WenQuanYi Micro Hei", "WenQuanYi Zen Hei",
            "Arial Unicode MS", "SimHei", "Microsoft YaHei",
        ]
        _available = {f.name for f in fm.fontManager.ttflist}
        _chosen = next((f for f in _cjk_candidates if f in _available), None)
        plt.rcParams["font.family"] = _chosen if _chosen else "DejaVu Sans"
        plt.rcParams["axes.unicode_minus"] = False

        # 若尚未上传数据，提示先去分析建议页上传
        if st.session_state["data_df"] is None:
            st.info("📂 请先在「🔍 智能分析建议」标签上传数据文件，再来这里画图。")
        else:
            df = st.session_state["data_df"]
            all_cols = list(df.columns)
            num_cols = [c for c in df.columns if str(df[c].dtype) in
                        ("float64", "float32", "int64", "int32")]
            cat_cols = [c for c in df.columns if str(df[c].dtype) == "object"
                        and df[c].nunique() <= 30]

            st.markdown(f"#### 当前数据：`{st.session_state['data_filename']}`  "
                        f"（{df.shape[0]} 行 × {df.shape[1]} 列）")

            ctrl_col, chart_col = st.columns([1, 2], gap="large")

            with ctrl_col:
                st.markdown("##### 图表设置")
                chart_type = st.selectbox(
                    "图表类型",
                    ["� 直方图（单变量分布）",
                     "🔵 散点图（两变量关系）",
                     "📦 箱线图（分组比较）",
                     "📋 柱状图（类别频次）",
                     "🔥 相关热力图（多变量）",
                     "📉 折线图（趋势）"],
                    key="viz_chart_type",
                )

                fig = None

                if chart_type == "📊 直方图（单变量分布）":
                    x_col = st.selectbox("选择变量", num_cols or all_cols, key="hist_x")
                    bins = st.slider("分组数", 5, 80, 20, key="hist_bins")
                    show_kde = st.checkbox("显示密度曲线", value=True, key="hist_kde")
                    if st.button("🎨 生成图表", type="primary", use_container_width=True, key="gen_hist"):
                        fig, ax = plt.subplots(figsize=(7, 4))
                        sns.histplot(df[x_col].dropna(), bins=bins, kde=show_kde,
                                     ax=ax, color="#0ea5e9", edgecolor="white")
                        ax.set_title(f"{x_col} 分布直方图", fontsize=13)
                        ax.set_xlabel(x_col)
                        ax.set_ylabel("频次")
                        plt.tight_layout()

                elif chart_type == "🔵 散点图（两变量关系）":
                    x_col = st.selectbox("X 轴变量", num_cols or all_cols, key="sc_x")
                    y_col = st.selectbox("Y 轴变量",
                                         [c for c in (num_cols or all_cols) if c != x_col] or all_cols,
                                         key="sc_y")
                    hue_col = st.selectbox("分组变量（可选）",
                                           ["（不分组）"] + cat_cols, key="sc_hue")
                    if st.button("🎨 生成图表", type="primary", use_container_width=True, key="gen_sc"):
                        fig, ax = plt.subplots(figsize=(7, 4))
                        hue = None if hue_col == "（不分组）" else hue_col
                        sns.scatterplot(data=df, x=x_col, y=y_col, hue=hue,
                                        ax=ax, alpha=0.7)
                        ax.set_title(f"{x_col} vs {y_col}", fontsize=13)
                        plt.tight_layout()

                elif chart_type == "📦 箱线图（分组比较）":
                    y_col = st.selectbox("数值变量（Y 轴）", num_cols or all_cols, key="box_y")
                    x_col = st.selectbox("分组变量（X 轴，可选）",
                                         ["（不分组）"] + cat_cols, key="box_x")
                    if st.button("🎨 生成图表", type="primary", use_container_width=True, key="gen_box"):
                        fig, ax = plt.subplots(figsize=(7, 4))
                        if x_col == "（不分组）":
                            sns.boxplot(y=df[y_col].dropna(), ax=ax, color="#6366f1")
                        else:
                            order = df[x_col].value_counts().index[:12].tolist()
                            sns.boxplot(data=df, x=x_col, y=y_col, ax=ax,
                                        order=order, palette="Set2")
                            plt.xticks(rotation=30, ha="right")
                        ax.set_title(f"{y_col} 箱线图", fontsize=13)
                        plt.tight_layout()

                elif chart_type == "📋 柱状图（类别频次）":
                    cat_col = st.selectbox("分类变量", cat_cols or all_cols, key="bar_cat")
                    top_n = st.slider("显示前 N 类", 3, 20, 10, key="bar_topn")
                    if st.button("🎨 生成图表", type="primary", use_container_width=True, key="gen_bar"):
                        vc = df[cat_col].value_counts().head(top_n)
                        fig, ax = plt.subplots(figsize=(7, 4))
                        vc.plot(kind="bar", ax=ax, color="#6366f1", edgecolor="white")
                        ax.set_title(f"{cat_col} 类别频次", fontsize=13)
                        ax.set_ylabel("频次")
                        plt.xticks(rotation=30, ha="right")
                        plt.tight_layout()

                elif chart_type == "🔥 相关热力图（多变量）":
                    corr_cols = st.multiselect(
                        "选择变量（建议 3-10 个）",
                        num_cols,
                        default=num_cols[:6],
                        key="corr_cols_viz",
                    )
                    if st.button("🎨 生成图表", type="primary", use_container_width=True, key="gen_corr"):
                        if len(corr_cols) < 2:
                            st.error("至少选择 2 个变量")
                        else:
                            corr = df[corr_cols].corr()
                            fig, ax = plt.subplots(
                                figsize=(max(5, len(corr_cols)), max(4, len(corr_cols) * 0.85))
                            )
                            sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm",
                                        ax=ax, linewidths=0.5, vmin=-1, vmax=1)
                            ax.set_title("Pearson 相关系数热力图", fontsize=13)
                            plt.tight_layout()

                elif chart_type == "📉 折线图（趋势）":
                    x_col = st.selectbox("X 轴变量（时间/序号）", all_cols, key="line_x")
                    y_cols = st.multiselect("Y 轴变量（可多选）", num_cols or all_cols,
                                            default=num_cols[:2] if num_cols else [],
                                            key="line_y")
                    if st.button("🎨 生成图表", type="primary", use_container_width=True, key="gen_line"):
                        if not y_cols:
                            st.error("请至少选择一个 Y 轴变量")
                        else:
                            fig, ax = plt.subplots(figsize=(8, 4))
                            for yc in y_cols:
                                ax.plot(df[x_col], df[yc], marker="o", markersize=3,
                                        linewidth=1.5, label=yc)
                            ax.set_title("折线图", fontsize=13)
                            ax.set_xlabel(x_col)
                            ax.legend()
                            plt.xticks(rotation=30, ha="right")
                            plt.tight_layout()

            with chart_col:
                st.markdown("##### 图表预览")
                if fig is not None:
                    st.pyplot(fig, use_container_width=True)
                    plt.close(fig)
                else:
                    st.markdown(
                        '<div class="feature-card" style="text-align:center;padding:3rem 1rem;">'
                        '在左侧选择变量和图表类型，点击「生成图表」</div>',
                        unsafe_allow_html=True,
                    )

            # ── 图表说明文字生成 ──────────────────────────────────────────────
            st.divider()
            st.markdown("#### 🖼️ 图表说明文字生成")
            st.caption("描述刚才画的图，AI 帮你写成规范的学术图注")
            desc_c1, desc_c2, desc_c3 = st.columns([1, 1, 1])
            with desc_c1:
                chart_type_sel = st.selectbox(
                    "图表类型",
                    ["直方图", "散点图", "箱线图", "柱状图", "相关热力图", "折线图",
                     "生存曲线", "ROC曲线", "火山图", "其他"],
                    key="desc_chart_type",
                )
            with desc_c2:
                chart_desc_text = st.text_area(
                    "图表内容描述", height=90,
                    placeholder="X轴为...，Y轴为...，展示了...",
                    key="desc_chart_desc",
                )
            with desc_c3:
                chart_findings = st.text_area(
                    "主要发现", height=90,
                    placeholder="图表揭示的核心结论...",
                    key="desc_chart_findings",
                )
            if st.button("✍️ 生成图注", use_container_width=True, key="gen_chart_desc"):
                if not chart_desc_text or not chart_findings:
                    st.error("请填写图表描述和主要发现")
                elif _check_config():
                    with st.spinner("🖊️ AI 正在撰写图注..."):
                        desc_result = generate_chart_description(
                            chart_type_sel, chart_desc_text, chart_findings
                        )
                    st.markdown(f'<div class="result-box">{desc_result}</div>',
                                unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# 页面 3：科研表达生成
# ══════════════════════════════════════════════════════════════════════════════
elif page == "✍️ 科研表达生成":
    st.markdown("""
    <div class="main-header">
        <h1>✍️ 科研表达生成</h1>
        <p>生成开题报告提纲、PPT 文件、论文结果段落，AI 全程辅助科研写作</p>
    </div>
    """, unsafe_allow_html=True)

    expr_type = st.segmented_control(
        "选择生成类型",
        ["📋 开题报告提纲", "🖥️ PPT 文件生成", "📝 论文结果段落"],
        default="📋 开题报告提纲",
    )

    col_form, col_result = st.columns([1, 1], gap="large")

    with col_form:
        result_text = ""
        pptx_bytes = None

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
                    with st.spinner("📝 AI 正在撰写提纲，请稍候..."):
                        result_text = generate_outline(topic, context)

        # ── PPT 文件生成 ──────────────────────────────────────────────────────
        elif expr_type == "🖥️ PPT 文件生成":
            st.markdown("#### PPT 文件生成")
            ppt_input = st.radio(
                "内容来源", ["上传文件（PDF / Word）", "手动输入主题"], horizontal=True
            )
            duration = st.slider("汇报时长（分钟）", 5, 30, 10)

            if ppt_input == "上传文件（PDF / Word）":
                ppt_file = st.file_uploader(
                    "上传文件", type=["pdf", "docx", "doc"],
                    label_visibility="collapsed",
                )
                if ppt_file:
                    st.info(f"已上传：{ppt_file.name}（{ppt_file.size // 1024} KB）")
                if st.button("🚀 生成 PPT", type="primary", use_container_width=True):
                    if not ppt_file:
                        st.error("请先上传文件")
                    elif _check_config():
                        with st.spinner("🎞️ AI 正在读取文件并生成 PPT，马上好～"):
                            try:
                                result_text, pptx_bytes = generate_ppt_from_file(
                                    ppt_file.read(), ppt_file.name, duration
                                )
                                st.success("✅ PPT 生成完成！")
                            except Exception as e:
                                st.error(f"生成失败：{e}")
            else:
                topic = st.text_input(
                    "汇报主题 *",
                    placeholder="例如：RNA-seq 差异表达分析结果汇报",
                )
                context = st.text_area(
                    "内容摘要（可选）",
                    placeholder="主要研究内容、核心发现...",
                    height=100,
                )
                if st.button("生成 PPT 框架", type="primary", use_container_width=True):
                    if not topic:
                        st.error("请填写汇报主题")
                    elif _check_config():
                        with st.spinner("🎞️ AI 正在规划幻灯片结构..."):
                            result_text = generate_ppt_structure(topic, context, duration)

        # ── 论文结果段落 ──────────────────────────────────────────────────────
        elif expr_type == "📝 论文结果段落":
            st.markdown("#### 论文结果段落生成")
            st.caption("输入统计分析数据，AI 自动生成符合期刊规范的结果章节段落")
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
                    with st.spinner("✍️ AI 正在撰写学术段落..."):
                        result_text = generate_result_paragraph(method, results, context)

    with col_result:
        st.markdown("#### 生成结果")
        if pptx_bytes:
            if result_text:
                with st.expander("查看 PPT 内容预览", expanded=False):
                    st.markdown(result_text)
            st.success("PPT 文件已就绪，点击下方按钮下载")
            st.download_button(
                "⬇️ 下载 PPT 文件（.pptx）",
                data=pptx_bytes,
                file_name="AI生成演示文稿.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                use_container_width=True,
                type="primary",
            )
        elif result_text:
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
