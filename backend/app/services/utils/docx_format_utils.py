from __future__ import annotations

import re
from typing import Dict, Optional

from docx.enum.text import WD_PARAGRAPH_ALIGNMENT, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.oxml.shared import OxmlElement
from docx.shared import Length, Pt
from docx.text.paragraph import Paragraph


def extract_run_format(paragraph: Paragraph) -> Dict[str, Optional[str | float | bool]]:
    for run in paragraph.runs:
        if not run.text.strip():
            continue
        font = run.font
        font_name = font.name
        font_size = font.size.pt if font.size else None
        if not font_name:
            r_pr = run._element.get_or_add_rPr()
            r_fonts = r_pr.rFonts
            if r_fonts is not None:
                font_name = r_fonts.get(qn("w:eastAsia")) or r_fonts.get(qn("w:ascii"))

        return {
            "font_name": font_name,
            "font_size": font_size,
            "bold": font.bold,
        }
    return {
        "font_name": None,
        "font_size": None,
        "bold": None,
    }


def extract_spacing(pf) -> Dict[str, Optional[float]]:
    data: Dict[str, Optional[float]] = {
        "line_spacing": _length_to_pt(pf.line_spacing),
        "space_before": _length_to_pt(pf.space_before),
        "space_after": _length_to_pt(pf.space_after),
    }
    return data


def extract_indents(pf) -> Dict[str, Optional[float]]:
    return {
        "first_line_indent": _length_to_pt(pf.first_line_indent),
        "left_indent": _length_to_pt(pf.left_indent),
        "right_indent": _length_to_pt(pf.right_indent),
    }


def extract_paragraph_format(paragraph: Paragraph) -> Dict[str, Optional[str | float | bool]]:
    """提取段落的完整格式信息"""
    pf = paragraph.paragraph_format
    run_format = extract_run_format(paragraph)
    spacing = extract_spacing(pf)
    indents = extract_indents(pf)
    
    alignment_map = {
        WD_PARAGRAPH_ALIGNMENT.LEFT: "left",
        WD_PARAGRAPH_ALIGNMENT.CENTER: "center",
        WD_PARAGRAPH_ALIGNMENT.RIGHT: "right",
        WD_PARAGRAPH_ALIGNMENT.JUSTIFY: "justify",
        WD_PARAGRAPH_ALIGNMENT.DISTRIBUTE: "distribute",
    }
    
    return {
        "font_name": run_format.get("font_name"),
        "font_size": run_format.get("font_size"),
        "bold": run_format.get("bold"),
        "alignment": alignment_map.get(paragraph.alignment),
        "line_spacing": spacing.get("line_spacing"),
        "space_before": spacing.get("space_before"),
        "space_after": spacing.get("space_after"),
        "first_line_indent": indents.get("first_line_indent"),
        "left_indent": indents.get("left_indent"),
        "right_indent": indents.get("right_indent"),
    }


def apply_paragraph_rule(paragraph: Paragraph, rule: Dict[str, Optional[str | float | bool]]) -> None:
    pf = paragraph.paragraph_format

    alignment_map = {
        "left": WD_PARAGRAPH_ALIGNMENT.LEFT,
        "center": WD_PARAGRAPH_ALIGNMENT.CENTER,
        "right": WD_PARAGRAPH_ALIGNMENT.RIGHT,
        "justify": WD_PARAGRAPH_ALIGNMENT.JUSTIFY,
        "distribute": WD_PARAGRAPH_ALIGNMENT.DISTRIBUTE,
    }
    
    # 智能对齐逻辑：标题、图片说明可以居中，正文保持左对齐
    paragraph_text = paragraph.text.strip() if paragraph.text else ""
    
    # 判断是否是"摘要"、"ABSTRACT"或"目录"标题（需要强制居中）
    # 匹配"摘要"、"ABSTRACT"、"目录"及其变体，包括中间有空格的变体（如"摘 要"、"目 录"）
    # 使用更灵活的匹配：去除所有空格和标点后检查是否等于"摘要"、"ABSTRACT"或"目录"
    is_abstract_title = False
    is_toc_title = False
    if paragraph_text:
        # 去除所有空格、标点符号和空白字符，只保留字母和汉字
        # 去除所有空格、标点符号（包括中文和英文标点）
        cleaned_text = re.sub(r'[\s\u3000：:，,。.；;！!？?、]', '', paragraph_text)
        # 转换为大写以便匹配（对于英文）
        cleaned_text_upper = cleaned_text.upper()
        
        # 检查去除空格和标点后是否等于"摘要"或"ABSTRACT"
        if cleaned_text == "摘要" or cleaned_text_upper == "ABSTRACT":
            is_abstract_title = True
        # 检查去除空格和标点后是否等于"目录"或"Contents"（支持中间最多5个空格）
        elif cleaned_text == "目录" or cleaned_text_upper == "CONTENTS":
            is_toc_title = True
        # 如果去除空格后的文本较短，也检查是否包含这些关键词（支持中间有空格）
        # 对于"目录"，允许中间最多5个空格，所以原始文本长度可能达到 2 + 5 + 标点 = 约10个字符
        elif len(cleaned_text) <= 15:  # 放宽限制，基于去除空格后的长度
            # 检查是否包含"摘"和"要"（允许中间有空格或其他字符）
            if "摘" in paragraph_text and "要" in paragraph_text:
                # 进一步验证：去除空格和标点后是否等于"摘要"
                if cleaned_text == "摘要":
                    is_abstract_title = True
            # 检查是否包含"目"和"录"（允许中间最多5个空格）
            elif "目" in paragraph_text and "录" in paragraph_text:
                # 进一步验证：去除空格和标点后是否等于"目录"
                # 检查"目"和"录"之间的字符是否只有空格（最多5个）
                # 找到"目"和"录"的位置
                mu_pos = paragraph_text.find("目")
                lu_pos = paragraph_text.find("录")
                if mu_pos >= 0 and lu_pos > mu_pos:
                    # 检查"目"和"录"之间的字符
                    between_text = paragraph_text[mu_pos + 1:lu_pos]
                    # 如果中间只有空格（最多5个），或者是空字符串，认为是目录标题
                    if len(between_text) <= 5 and all(c in ' \t\u3000' for c in between_text):
                        if cleaned_text == "目录":
                            is_toc_title = True
                    # 如果中间没有字符或只有空格，也认为是目录标题
                    elif len(between_text) == 0:
                        if cleaned_text == "目录":
                            is_toc_title = True
            # 检查是否包含"ABSTRACT"（不区分大小写）
            elif "ABSTRACT" in cleaned_text_upper or "abstract" in paragraph_text.lower():
                # 进一步验证：去除空格和标点后是否等于"ABSTRACT"
                if cleaned_text_upper == "ABSTRACT":
                    is_abstract_title = True
            # 检查是否包含"Contents"（不区分大小写）
            elif "CONTENTS" in cleaned_text_upper or "contents" in paragraph_text.lower():
                # 进一步验证：去除空格和标点后是否等于"CONTENTS"
                if cleaned_text_upper == "CONTENTS":
                    is_toc_title = True
    
    # 如果是"摘要"、"ABSTRACT"或"目录"标题，强制居中，无论规则如何设置
    if is_abstract_title or is_toc_title:
        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        # 直接返回，不执行后续的对齐逻辑，确保不会被覆盖
        # 但继续执行其他格式设置（字体、行距等）
    elif alignment := rule.get("alignment"):
        # 判断是否是图片或表格说明（包含"图"或"表"字，且通常较短）
        is_figure_caption = (
            ("图" in paragraph_text or "表" in paragraph_text) and
            len(paragraph_text) < 100 and
            (paragraph_text.startswith("图") or paragraph_text.startswith("表"))
        )
        
        # 判断是否是其他标题（目录、绪论、概述等）
        is_title = (
            paragraph_text == "目录" or paragraph_text.startswith("目录") or
            paragraph_text == "Contents" or paragraph_text.startswith("Contents") or
            paragraph_text == "绪论" or paragraph_text == "概述" or
            paragraph_text.startswith("1 绪论") or paragraph_text.startswith("1 概述") or
            paragraph_text.startswith("参考文献") or paragraph_text.startswith("致谢") or
            paragraph_text.startswith("References") or paragraph_text.startswith("Acknowledgement")
        )
        
        # 如果是图片说明或标题，且规则要求居中，则应用居中
        if (is_figure_caption or is_title) and alignment == "center":
            paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        # 如果是普通正文，且规则要求居中，则强制改为左对齐（避免正文被错误居中）
        elif not is_figure_caption and not is_title and alignment == "center":
            # 只有当前不是左对齐时才修改，避免不必要的修改记录
            if paragraph.alignment != WD_PARAGRAPH_ALIGNMENT.LEFT:
                paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
        # 其他情况按规则应用（左对齐、右对齐、两端对齐等）
        else:
            paragraph.alignment = alignment_map.get(alignment, paragraph.alignment)

    if (line_spacing := rule.get("line_spacing")) is not None:
        # 处理行距设置
        # 如果 line_spacing 是字符串 "single"，设置为单倍行距
        if line_spacing == "single" or line_spacing == 1.0:
            # 单倍行距：使用 WD_LINE_SPACING.SINGLE
            pf.line_spacing_rule = WD_LINE_SPACING.SINGLE
            # 不设置 line_spacing 值，让Word使用默认
        elif isinstance(line_spacing, (int, float)) and line_spacing > 1.0:
            # 固定行距（exact spacing），单位为磅
            # 使用 Pt() 会自动设置为固定值，而不是倍数
            pf.line_spacing = Pt(line_spacing)
        else:
            # 其他情况（如倍数行距），使用默认处理
            # 如果值小于等于1.0且不是"single"，可能是误设置，使用单倍行距
            pf.line_spacing_rule = WD_LINE_SPACING.SINGLE
    if (space_before := rule.get("space_before")) is not None:
        pf.space_before = Pt(space_before)
    if (space_after := rule.get("space_after")) is not None:
        pf.space_after = Pt(space_after)
    if (first_line_indent := rule.get("first_line_indent")) is not None:
        pf.first_line_indent = Pt(first_line_indent)
    if (left_indent := rule.get("left_indent")) is not None:
        pf.left_indent = Pt(left_indent)
    if (right_indent := rule.get("right_indent")) is not None:
        pf.right_indent = Pt(right_indent)

    # 强制统一字体大小：确保所有runs都应用相同的字体大小
    font_size = rule.get("font_size")
    font_name = rule.get("font_name")
    bold_value = rule.get("bold")
    
    # 如果规则中指定了字体大小，强制应用到所有runs，确保段落内字体大小一致
    if font_size is not None:
        for run in paragraph.runs:
            font = run.font
            # 强制设置字体大小，覆盖原有的任何设置
            font.size = Pt(font_size)
            
            # 应用字体名称
            if font_name:
                font.name = font_name
                r_pr = run._element.get_or_add_rPr()
                r_fonts = r_pr.rFonts
                if r_fonts is None:
                    r_fonts = OxmlElement("w:rFonts")
                    r_pr.append(r_fonts)
                r_fonts.set(qn("w:ascii"), font_name)
                r_fonts.set(qn("w:eastAsia"), font_name)
                r_fonts.set(qn("w:hAnsi"), font_name)
            
            # 应用加粗设置
            if bold_value is not None:
                font.bold = bool(bold_value)
    else:
        # 如果没有指定字体大小，确保段落内所有runs的字体大小一致
        # 提取段落中最常见的字体大小，然后统一应用到所有runs
        font_sizes = []
        for run in paragraph.runs:
            if run.font.size:
                font_sizes.append(run.font.size.pt)
        
        # 如果有字体大小，使用最常见的（或第一个）
        unified_font_size = font_sizes[0] if font_sizes else None
        
        for run in paragraph.runs:
            font = run.font
            
            # 如果找到了统一的字体大小，应用到所有runs
            if unified_font_size is not None:
                font.size = Pt(unified_font_size)
            
            # 应用字体名称
            if font_name:
                font.name = font_name
                r_pr = run._element.get_or_add_rPr()
                r_fonts = r_pr.rFonts
                if r_fonts is None:
                    r_fonts = OxmlElement("w:rFonts")
                    r_pr.append(r_fonts)
                r_fonts.set(qn("w:ascii"), font_name)
                r_fonts.set(qn("w:eastAsia"), font_name)
                r_fonts.set(qn("w:hAnsi"), font_name)
            
            # 应用加粗设置
            if bold_value is not None:
                font.bold = bool(bold_value)
    
    # 最后再次检查：确保"摘要"、"ABSTRACT"和"目录"标题始终居中（防止被其他逻辑覆盖）
    paragraph_text_final = paragraph.text.strip() if paragraph.text else ""
    if paragraph_text_final:
        # 使用相同的判断逻辑
        cleaned_text_final = re.sub(r'[\s\u3000：:，,。.；;！!？?、]', '', paragraph_text_final)
        cleaned_text_final_upper = cleaned_text_final.upper()
        
        is_abstract_title_final = False
        is_toc_title_final = False
        if cleaned_text_final == "摘要" or cleaned_text_final_upper == "ABSTRACT":
            is_abstract_title_final = True
        elif cleaned_text_final == "目录" or cleaned_text_final_upper == "CONTENTS":
            is_toc_title_final = True
        elif len(cleaned_text_final) <= 15:  # 基于去除空格后的长度
            if "摘" in paragraph_text_final and "要" in paragraph_text_final:
                if cleaned_text_final == "摘要":
                    is_abstract_title_final = True
            elif "目" in paragraph_text_final and "录" in paragraph_text_final:
                # 检查"目"和"录"之间的字符是否只有空格（最多5个）
                mu_pos = paragraph_text_final.find("目")
                lu_pos = paragraph_text_final.find("录")
                if mu_pos >= 0 and lu_pos > mu_pos:
                    between_text = paragraph_text_final[mu_pos + 1:lu_pos]
                    # 如果中间只有空格（最多5个），或者是空字符串，认为是目录标题
                    if len(between_text) <= 5 and all(c in ' \t\u3000' for c in between_text):
                        if cleaned_text_final == "目录":
                            is_toc_title_final = True
                    elif len(between_text) == 0:
                        if cleaned_text_final == "目录":
                            is_toc_title_final = True
            elif "ABSTRACT" in cleaned_text_final_upper or "abstract" in paragraph_text_final.lower():
                if cleaned_text_final_upper == "ABSTRACT":
                    is_abstract_title_final = True
            elif "CONTENTS" in cleaned_text_final_upper or "contents" in paragraph_text_final.lower():
                if cleaned_text_final_upper == "CONTENTS":
                    is_toc_title_final = True
        
        if is_abstract_title_final or is_toc_title_final:
            paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER


def _length_to_pt(value) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, Length):
        return value.pt
    if isinstance(value, (float, int)):
        return float(value)
    return None

