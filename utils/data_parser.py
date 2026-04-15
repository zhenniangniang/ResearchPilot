import io
import pandas as pd
from config import MAX_ROWS_PREVIEW, MAX_COLS_SHOW


def load_dataframe(file_bytes: bytes, filename: str) -> pd.DataFrame:
    """从上传文件字节中加载 DataFrame，支持 xlsx / xls / csv。"""
    fname = filename.lower()
    if fname.endswith(".csv"):
        try:
            df = pd.read_csv(io.BytesIO(file_bytes), encoding="utf-8")
        except UnicodeDecodeError:
            df = pd.read_csv(io.BytesIO(file_bytes), encoding="gbk")
    elif fname.endswith((".xlsx", ".xls")):
        df = pd.read_excel(io.BytesIO(file_bytes))
    else:
        raise ValueError(f"不支持的文件格式：{filename}，请上传 CSV 或 Excel 文件")
    return df


def analyze_dataframe(df: pd.DataFrame) -> dict:
    """
    自动分析 DataFrame，返回结构化统计摘要，供 LLM 决策分析方法。
    """
    info = {
        "shape": df.shape,
        "columns": list(df.columns[:MAX_COLS_SHOW]),
        "dtypes": {},
        "missing": {},
        "variable_types": {},
        "numeric_stats": {},
        "categorical_stats": {},
    }

    for col in df.columns[:MAX_COLS_SHOW]:
        dtype = str(df[col].dtype)
        info["dtypes"][col] = dtype
        missing_count = int(df[col].isna().sum())
        missing_pct = round(missing_count / len(df) * 100, 1)
        info["missing"][col] = {"count": missing_count, "pct": missing_pct}

        nunique = df[col].nunique()

        # 变量类型判断
        if dtype in ("float64", "float32", "int64", "int32"):
            if nunique == 2:
                info["variable_types"][col] = "二分类"
            elif nunique <= 10:
                info["variable_types"][col] = "有序分类/多分类"
            else:
                info["variable_types"][col] = "连续变量"
            try:
                info["numeric_stats"][col] = {
                    "mean": round(float(df[col].mean()), 4),
                    "std": round(float(df[col].std()), 4),
                    "min": round(float(df[col].min()), 4),
                    "max": round(float(df[col].max()), 4),
                    "nunique": nunique,
                }
            except Exception:
                pass
        elif dtype == "object" or dtype == "category":
            if nunique == 2:
                info["variable_types"][col] = "二分类"
            elif nunique <= 20:
                info["variable_types"][col] = "分类变量"
            else:
                info["variable_types"][col] = "文本/高基数"
            top_vals = df[col].value_counts().head(5).to_dict()
            info["categorical_stats"][col] = {
                "nunique": nunique,
                "top_values": {str(k): int(v) for k, v in top_vals.items()},
            }
        elif "datetime" in dtype:
            info["variable_types"][col] = "时间变量"
        else:
            info["variable_types"][col] = "其他"

    return info


def get_preview(df: pd.DataFrame) -> pd.DataFrame:
    """返回数据预览（前 N 行，最多 MAX_COLS_SHOW 列）。"""
    return df.iloc[:MAX_ROWS_PREVIEW, :MAX_COLS_SHOW]


def format_analysis_for_llm(info: dict) -> str:
    """将数据分析结果格式化为适合 LLM 阅读的字符串。"""
    lines = [
        f"数据集规模：{info['shape'][0]} 行 × {info['shape'][1]} 列",
        f"展示前 {len(info['columns'])} 列：{', '.join(info['columns'])}",
        "",
        "各变量信息：",
    ]
    for col in info["columns"]:
        vtype = info["variable_types"].get(col, "未知")
        missing = info["missing"].get(col, {})
        m_str = f"缺失 {missing.get('count', 0)} 个（{missing.get('pct', 0)}%）"
        stat = ""
        if col in info["numeric_stats"]:
            s = info["numeric_stats"][col]
            stat = f"  均值={s['mean']}, 标准差={s['std']}, 范围=[{s['min']}, {s['max']}]"
        elif col in info["categorical_stats"]:
            s = info["categorical_stats"][col]
            top = list(s["top_values"].keys())[:3]
            stat = f"  唯一值={s['nunique']}, 高频类别={top}"
        lines.append(f"  - {col}：{vtype}，{m_str}{stat}")
    return "\n".join(lines)
