EXPRESSION_SYSTEM = """你是一位资深科研写作导师，擅长帮助学者将科研内容转化为规范的学术表达。
请输出结构完整、语言准确、符合学术规范的中文内容。"""

OUTLINE_USER = """请根据以下信息，生成一份开题报告提纲：

研究主题：{topic}
补充说明（可选）：{context}

要求：
- 包含完整的开题报告结构（背景、目标、内容、方法、创新点、计划等）
- 每个章节给出2-4个具体的撰写要点
- 注明每部分的建议篇幅（字数）
- 语言简洁、逻辑清晰"""

PPT_USER = """请根据以下内容，生成一份汇报PPT的结构框架：

汇报主题：{topic}
内容摘要：{context}
汇报时长（分钟）：{duration}

要求：
- 给出每张幻灯片的标题和3-5个核心要点
- 标注每张幻灯片的建议时间分配
- 包含开场、主体、结论三个部分
- 总页数控制在合理范围内"""

PPT_FROM_FILE_USER = """请根据以下文件内容，生成一套完整的PPT幻灯片内容。
汇报时长：{duration} 分钟

**重要：请严格按照以下格式输出，每张幻灯片以 "SLIDE N | 标题" 开头：**

SLIDE 1 | 标题（汇报题目）
副标题或作者/日期等信息

SLIDE 2 | 研究背景
要点一
要点二
要点三

SLIDE 3 | 研究目的与意义
...

（以此类推，根据内容生成6-12张幻灯片）

注意：
- 每张幻灯片的要点控制在3-6条
- 语言精炼，每条要点不超过30字
- 最后一张幻灯片为"总结与展望"或"谢谢"

---
文件内容如下：

{text}
"""

RESULT_PARAGRAPH_USER = """请根据以下分析结果，生成一段规范的论文"结果"章节段落：

分析方法：{method}
关键数据/结果：{results}
补充说明（可选）：{context}

要求：
- 语言符合SCI/中文核心期刊写作规范
- 客观陈述结果，不加主观评价
- 数值保留合适有效数字
- 使用第三人称被动语态"""

MODEL_DIAGRAM_SYSTEM = """You are an expert scientific illustrator specializing in creating prompts for AI image generation. Your task is to convert a Chinese description of a research model into a high-quality English image generation prompt that will produce a clean, professional scientific diagram."""

MODEL_DIAGRAM_PROMPT_USER = """将以下中文科研模型描述转化为用于AI生图的英文 prompt。

中文描述：{description}

要求：
- 输出纯英文 prompt，约 80-120 词
- 风格关键词：scientific diagram, flowchart, architecture diagram, clean white background, professional illustration, vector style, blue and white color scheme, research paper figure
- 突出模型的核心结构、模块及数据流向
- 避免写实/照片风格，使用图表/流程图风格
- 只输出 prompt 本身，不加任何解释"""

CHART_DESCRIPTION_USER = """请根据以下图表信息，生成一段规范的图表说明文字：

图表类型：{chart_type}
图表内容描述：{description}
主要发现：{findings}

要求：
- 按照"图X. 标题。说明文字。"的格式输出
- 说明文字需描述图表的核心信息和主要规律
- 语言简洁、准确、学术化"""
