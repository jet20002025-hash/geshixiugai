"""
毕业论文格式标准配置
基于杭州电子科技大学毕业设计（论文）写作规范和参考格式
"""

# 页面设置标准
PAGE_SETTINGS = {
    "paper_size": "A4",
    "margins": {
        "top": 3.0,      # 上：3厘米
        "bottom": 2.0,   # 下：2厘米
        "left": 3.0,     # 左：3厘米
        "right": 2.0,    # 右：2厘米
        "gutter": 1.0,   # 装订线：1厘米
    },
    "header_distance": 2.0,  # 页眉距边界：2厘米
    "footer_distance": 1.0,  # 页脚距边界：1厘米
}

# 页眉设置
HEADER_SETTINGS = {
    "text": "杭州电子科技大学本科毕业论文",  # 或 "杭州电子科技大学本科毕业设计"
    "font_name": "宋体",
    "font_size": 10.5,  # 五号字
    "alignment": "center",
}

# 字体字号标准（根据文档要求）
FONT_STANDARDS = {
    # 标题格式
    "title_level_1": {
        "font_name": "黑体",
        "font_size": 16,  # 三号字
        "bold": True,
        "alignment": "center",
        "space_before": 24,  # 段前2行（12pt * 2）
        "space_after": 24,  # 段后2行
        "line_spacing": "single",  # 单倍行距
    },
    "title_level_2": {
        "font_name": "黑体",
        "font_size": 14,  # 四号字
        "bold": True,
        "alignment": "left",
    },
    "title_level_3": {
        "font_name": "黑体",
        "font_size": 12,  # 小四号字
        "bold": True,
        "alignment": "left",
    },
    # 正文格式
    "body_text": {
        "font_name": "宋体",
        "font_size": 12,  # 小四号字
        "bold": False,
        "alignment": "left",
        "line_spacing": 20,  # 20磅固定行距
        "first_line_indent": 24,  # 首行缩进2字符（12pt * 2）
    },
    # 摘要格式
    "abstract_title": {
        "font_name": "黑体",
        "font_size": 16,  # 三号字
        "bold": True,
        "alignment": "center",
        "space_before": 24,
        "space_after": 24,
    },
    "abstract_content": {
        "font_name": "宋体",
        "font_size": 12,  # 小四号字
        "bold": False,
        "alignment": "left",
        "line_spacing": 20,  # 20磅
    },
    "keywords_label": {
        "font_name": "黑体",
        "font_size": 12,  # 小四号字
        "bold": True,
    },
    "keywords_content": {
        "font_name": "宋体",
        "font_size": 12,  # 小四号字
        "bold": False,
    },
    # 英文摘要格式
    "abstract_title_en": {
        "font_name": "黑体",  # 改为黑体，与中文摘要标题一致
        "font_size": 16,  # 三号字
        "bold": True,
        "alignment": "center",
        "space_before": 24,
        "space_after": 24,
    },
    "abstract_content_en": {
        "font_name": "Times New Roman",
        "font_size": 12,  # 小四号字
        "bold": False,
        "alignment": "left",
        "line_spacing": 20,  # 20磅
    },
    "keywords_label_en": {
        "font_name": "Times New Roman",
        "font_size": 12,  # 小四号字
        "bold": True,
    },
    "keywords_content_en": {
        "font_name": "Times New Roman",
        "font_size": 12,  # 小四号字
        "bold": False,
    },
    # 目录格式
    "toc_title": {
        "font_name": "黑体",
        "font_size": 16,  # 三号字
        "bold": True,
        "alignment": "center",
        "space_before": 24,
        "space_after": 24,
    },
    "toc_content": {
        "font_name": "宋体",
        "font_size": 12,  # 小四号字
        "bold": False,
        "alignment": "left",
    },
    # 图题格式
    "figure_caption": {
        "font_name": "宋体",
        "font_size": 10.5,  # 五号字
        "bold": False,
        "alignment": "center",
    },
    # 表题格式
    "table_caption": {
        "font_name": "宋体",
        "font_size": 10.5,  # 五号字
        "bold": False,
        "alignment": "center",
    },
    # 公式格式
    "formula": {
        "font_name": "宋体",
        "font_size": 10.5,  # 五号字
        "bold": False,
        "alignment": "center",
    },
    # 参考文献格式
    "reference_title": {
        "font_name": "黑体",
        "font_size": 16,  # 三号字
        "bold": True,
        "alignment": "center",
        "space_before": 24,
        "space_after": 24,
    },
    "reference_content": {
        "font_name": "宋体",
        "font_size": 12,  # 小四号字
        "bold": False,
        "alignment": "left",
        "line_spacing": 20,  # 20磅
        "left_indent": 0,  # 居左顶格
    },
    # 致谢格式
    "acknowledgment_title": {
        "font_name": "黑体",
        "font_size": 16,  # 三号字
        "bold": True,
        "alignment": "center",
        "space_before": 24,
        "space_after": 24,
    },
    "acknowledgment_content": {
        "font_name": "宋体",
        "font_size": 12,  # 小四号字
        "bold": False,
        "alignment": "left",
        "line_spacing": 20,  # 20磅
    },
}

# 样式映射规则（根据段落内容自动识别样式）
STYLE_MAPPING_RULES = [
    {
        "pattern": r"^(摘要|ABSTRACT)",
        "style": "abstract_title",
    },
    {
        "pattern": r"^(目录|Contents)",
        "style": "toc_title",
    },
    {
        "pattern": r"^(致谢|Acknowledgement)",
        "style": "acknowledgment_title",
    },
    {
        "pattern": r"^(参考文献|References)",
        "style": "reference_title",
    },
    {
        "pattern": r"^关键词|Keywords",
        "style": "keywords_label",
    },
    {
        "pattern": r"^图\s*\d+",
        "style": "figure_caption",
    },
    {
        "pattern": r"^表\s*\d+",
        "style": "table_caption",
    },
    # 注意：章节标题的检测在 _detect_paragraph_style 中有更严格的逻辑
    # 这里只保留简单的模式匹配，实际检测会检查段落长度和内容
    {
        "pattern": r"^(第[一二三四五六七八九十\d]+章|第\d+章|Chapter\s+\d+)([，,。.：:；;]?)$",
        "style": "title_level_1",
    },
    {
        "pattern": r"^(\d+\.\d+|第[一二三四五六七八九十\d]+节)([，,。.：:；;]?)$",
        "style": "title_level_2",
    },
    {
        "pattern": r"^(\d+\.\d+\.\d+)([，,。.：:；;]?)$",
        "style": "title_level_3",
    },
]

# 默认样式（正文）
DEFAULT_STYLE = "body_text"

# 参考文献要求
REFERENCE_REQUIREMENTS = {
    "min_total": 10,  # 最少10篇
    "min_foreign": 2,  # 外文文献不少于2篇
    "min_journal": 4,  # 期刊论文不少于4篇
}

# 注释格式要求
NOTE_FORMAT = {
    "style": "footnote",  # 页末注或篇末注
    "number_format": "circled",  # ①、②、③格式（不是[1]、[2]）
}

# 页码格式
PAGE_NUMBER_FORMAT = {
    "exclude_sections": ["封面", "封底", "中文摘要", "ABSTRACT", "目录"],
    "format": "arabic",  # 阿拉伯数字
    "font_name": "Times New Roman",
    "font_size": 10.5,  # 五号字
    "alignment": "center",
}

