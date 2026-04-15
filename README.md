# ResearchPilot · AI 科研学习助手

面向数理学习科研场景的 AI 智能体应用，支持**文献智能解读、数据分析建议、科研表达生成**三大核心功能。

## 快速启动

### 1. 安装依赖

```bash
cd ResearchPilot
pip install -r requirements.txt
```

### 2. 配置 API Key

打开 `config.py`，填写你的 LLM API 信息：

```python
LLM_API_KEY  = "你的 API Key"
LLM_BASE_URL = "https://api.openai.com/v1"   # 或其他兼容接口
LLM_MODEL    = "gpt-4o-mini"
```

**支持的大模型服务：**

| 服务 | Base URL | 推荐模型 |
|------|----------|----------|
| OpenAI | `https://api.openai.com/v1` | `gpt-4o-mini` |
| 通义千问 | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-plus` |
| DeepSeek | `https://api.deepseek.com/v1` | `deepseek-chat` |
| 智谱 GLM | `https://open.bigmodel.cn/api/paas/v4` | `glm-4-flash` |

也可以通过**侧边栏**在运行时实时修改配置，无需重启。

### 3. 运行应用

```bash
streamlit run app.py
```

浏览器自动打开 `http://localhost:8501`

---

## 功能介绍

### 📄 文献智能解读
- 支持 **PDF 上传** 或 **文本粘贴**
- 自动输出：基本信息、研究目的、方法、结果、创新点、局限性、汇报要点
- 支持**追问**：针对文献内容进行任意提问

### 📊 数据分析建议
- 支持 **Excel / CSV** 上传
- 自动识别变量类型（连续/二分类/多分类/时间变量）
- 检测缺失值与异常值
- 推荐统计分析方法及完整分析流程
- 支持**追问**数据分析问题

### ✍️ 科研表达生成
- **开题报告提纲**：输入研究主题，自动生成完整提纲
- **PPT 汇报框架**：按时长生成分页结构
- **论文结果段落**：输入数据，生成符合学术规范的段落
- **图表说明文字**：生成图注文字

---

## 项目结构

```
ResearchPilot/
├── app.py                  # Streamlit 主程序入口
├── config.py               # API 配置
├── requirements.txt
├── modules/
│   ├── literature.py       # 文献解读模块
│   ├── data_analysis.py    # 数据分析建议模块
│   └── expression.py       # 科研表达生成模块
├── utils/
│   ├── llm_client.py       # LLM 调用封装
│   ├── pdf_parser.py       # PDF 解析工具
│   └── data_parser.py      # 数据处理工具
└── prompts/
    ├── literature_prompts.py
    ├── data_prompts.py
    └── expression_prompts.py
```
