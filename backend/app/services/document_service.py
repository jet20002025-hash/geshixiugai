from __future__ import annotations

import io
import json
import os
import re
import shutil
import uuid
import xml.sax.saxutils
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple, Optional

from docx import Document
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.oxml import parse_xml
from docx.shared import RGBColor, Pt
from docx.oxml.ns import qn
from docx.oxml.shared import OxmlElement
from fastapi import UploadFile

from .utils import docx_format_utils
from .storage_factory import get_storage
from .thesis_format_standard import (
    FONT_STANDARDS,
    STYLE_MAPPING_RULES,
    DEFAULT_STYLE,
    PAGE_SETTINGS,
    HEADER_SETTINGS,
    PAGE_NUMBER_FORMAT,
)
import re


class DocumentService:
    def __init__(self, document_dir: Path, template_dir: Path) -> None:
        self.document_dir = document_dir
        self.template_dir = template_dir
        self.document_dir.mkdir(parents=True, exist_ok=True)
        # 获取存储实例（如果可用）
        self.storage = get_storage()
        self.use_storage = self.storage is not None

    async def process_document(self, template_id: str, upload: UploadFile) -> Tuple[str, Dict]:
        if not upload.filename or not upload.filename.lower().endswith(".docx"):
            raise ValueError("仅支持 docx 文档")

        template_metadata = self._load_template(template_id)
        document_id = uuid.uuid4().hex
        # 生成唯一的下载 token，用于验证用户身份
        download_token = uuid.uuid4().hex
        task_dir = self.document_dir / document_id
        task_dir.mkdir(parents=True, exist_ok=True)

        original_path = task_dir / "original.docx"
        original_path.write_bytes(await upload.read())

        # 加载文档
        document = Document(original_path)
        
        # 应用页面设置（优先使用标准）
        self._apply_page_settings(document)
        
        # 应用页眉页脚（优先使用标准）
        self._apply_header_footer(document)
        
        # 合并模板规则和标准规则（标准优先）
        template_rules = template_metadata.get("styles", {})
        merged_rules = self._merge_rules_with_standard(template_rules)
        
        final_doc, stats = self._apply_rules(
            document=document,
            rules=merged_rules,
            default_style=template_metadata.get("default_style") or DEFAULT_STYLE,
        )
        
        # 检测图片并检查图题
        figure_issues = self._check_figure_captions(final_doc)
        if figure_issues:
            stats["figure_issues"] = figure_issues
        
        # 检测参考文献引用标注
        reference_issues = self._check_reference_citations(final_doc)
        if reference_issues:
            stats["reference_issues"] = reference_issues
        
        # 检测大段空白
        blank_issues = self._check_excessive_blanks(final_doc)
        if blank_issues:
            stats["blank_issues"] = blank_issues

        final_path = task_dir / "final.docx"
        final_doc.save(final_path)

        preview_path = task_dir / "preview.docx"
        self._generate_watermarked_preview(final_path, preview_path)
        html_path = preview_path.with_suffix('.html')
        self._generate_html_preview(preview_path, html_path, stats)

        report_data = {
            "document_id": document_id,
            "template_id": template_id,
            "summary": stats,
        }

        report_path = task_dir / "report.json"
        report_path.write_text(json.dumps(report_data, ensure_ascii=False, indent=2), encoding="utf-8")

        # 如果使用云存储，将文件上传到云存储
        if self.use_storage:
            self._save_to_storage(document_id, {
                "original": original_path,
                "final": final_path,
                "preview": preview_path,
                "html": html_path,
                "report": report_path,
            })

        metadata = {
            "document_id": document_id,
            "template_id": template_id,
            "status": "completed",
            "paid": False,
            "download_token": download_token,  # 下载验证 token
            "summary": stats,
            "report_path": str(report_path),
            "preview_path": str(preview_path),
            "preview_html_path": str(html_path),
            "final_path": str(final_path),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }

        metadata_path = task_dir / "metadata.json"
        metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
        
        # 如果使用云存储，也上传 metadata
        if self.use_storage:
            self._save_file_to_storage(f"documents/{document_id}/metadata.json", metadata_path.read_bytes())
        
        return document_id, stats

    def get_document_metadata(self, document_id: str) -> Dict:
        # 优先从云存储读取
        if self.use_storage:
            metadata_key = f"documents/{document_id}/metadata.json"
            if self.storage.file_exists(metadata_key):
                content = self.storage.download_file(metadata_key)
                if content:
                    return json.loads(content.decode("utf-8"))
        
        # 回退到本地文件系统
        metadata_path = self.document_dir / document_id / "metadata.json"
        if not metadata_path.exists():
            return {}
        return json.loads(metadata_path.read_text(encoding="utf-8"))

    def update_metadata(self, document_id: str, **kwargs) -> Dict:
        # 先加载 metadata（优先从存储）
        data = self.get_document_metadata(document_id)
        if not data:
            raise FileNotFoundError("metadata not found")
        
        # 更新数据
        data.update(kwargs)
        data["updated_at"] = datetime.utcnow().isoformat()
        
        # 保存到本地和存储
        task_dir = self.document_dir / document_id
        task_dir.mkdir(parents=True, exist_ok=True)
        metadata_path = task_dir / "metadata.json"
        metadata_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        
        # 如果使用云存储，也更新存储中的 metadata
        if self.use_storage:
            metadata_key = f"documents/{document_id}/metadata.json"
            content = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
            self._save_file_to_storage(metadata_key, content)
        
        return data

    def _load_template(self, template_id: str) -> Dict:
        metadata_path = self.template_dir / template_id / "metadata.json"
        if not metadata_path.exists():
            raise FileNotFoundError("template not found")
        return json.loads(metadata_path.read_text(encoding="utf-8"))

    def _paragraph_has_image_or_equation(self, paragraph) -> bool:
        """判断段落是否包含图片或公式"""
        # 检查是否包含图片
        has_image = False
        try:
            # 方法1: 检查段落中的runs是否包含图片
            for run in paragraph.runs:
                if not hasattr(run, 'element'):
                    continue
                run_xml = str(run.element.xml)
                # 排除VML形状的水印
                if 'v:shape' in run_xml.lower() and 'textpath' in run_xml.lower():
                    continue
                # 检查是否包含真正的图片元素
                if ('pic:pic' in run_xml or 'a:blip' in run_xml) and ('r:embed' in run_xml or 'r:link' in run_xml or 'a:blip' in run_xml):
                    has_image = True
                    break
        except:
            pass
        
        # 方法2: 检查段落元素中是否包含图片
        if not has_image:
            try:
                para_xml = str(paragraph._element.xml)
                if 'v:shape' in para_xml.lower() and 'textpath' in para_xml.lower():
                    pass  # 这是水印，跳过
                elif ('pic:pic' in para_xml or 'a:blip' in para_xml) and ('r:embed' in para_xml or 'r:link' in para_xml or 'a:blip' in para_xml):
                    has_image = True
            except:
                pass
        
        # 方法3: 使用xpath查找drawing元素
        if not has_image:
            try:
                from docx.oxml.ns import qn
                drawings = paragraph._element.xpath('.//w:drawing', namespaces={
                    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
                    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
                    'pic': 'http://schemas.openxmlformats.org/drawingml/2006/picture',
                    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
                })
                if drawings:
                    for drawing in drawings:
                        drawing_xml = str(drawing.xml)
                        if 'v:shape' in drawing_xml.lower() and 'textpath' in drawing_xml.lower():
                            continue
                        if ('pic:pic' in drawing_xml or 'a:blip' in drawing_xml) and ('r:embed' in drawing_xml or 'r:link' in drawing_xml or 'a:blip' in drawing_xml):
                            has_image = True
                            break
            except:
                pass
        
        # 检查是否包含公式（Office Math 或 MathType）
        has_equation = False
        try:
            para_xml = str(paragraph._element.xml)
            # 检查Office Math (oMath)
            if 'm:oMath' in para_xml or 'm:oMathPara' in para_xml:
                has_equation = True
            # 检查MathType公式（通常包含object标签）
            elif 'object' in para_xml.lower() and ('mathtype' in para_xml.lower() or 'equation' in para_xml.lower()):
                has_equation = True
            # 检查段落中的runs是否包含公式
            if not has_equation:
                for run in paragraph.runs:
                    if not hasattr(run, 'element'):
                        continue
                    run_xml = str(run.element.xml)
                    if 'm:oMath' in run_xml or 'm:oMathPara' in run_xml:
                        has_equation = True
                        break
        except:
            pass
        
        return has_image or has_equation

    def _apply_page_settings(self, document: Document) -> None:
        """应用页面设置（页边距等）"""
        margins = PAGE_SETTINGS["margins"]
        for section in document.sections:
            # 设置页边距（单位：厘米转磅，1厘米=28.35磅）
            section.top_margin = Pt(margins["top"] * 28.35)
            section.bottom_margin = Pt(margins["bottom"] * 28.35)
            section.left_margin = Pt(margins["left"] * 28.35)
            section.right_margin = Pt(margins["right"] * 28.35)
            section.gutter = Pt(margins["gutter"] * 28.35)
            section.header_distance = Pt(PAGE_SETTINGS["header_distance"] * 28.35)
            section.footer_distance = Pt(PAGE_SETTINGS["footer_distance"] * 28.35)
    
    def _apply_header_footer(self, document: Document) -> None:
        """应用页眉页脚设置"""
        header_text = HEADER_SETTINGS["text"]
        for section in document.sections:
            header = section.header
            if header.is_linked_to_previous:
                header.is_linked_to_previous = False
            
            # 清空现有页眉内容
            for para in header.paragraphs:
                para.clear()
            
            # 添加标准页眉
            para = header.add_paragraph()
            para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            run = para.add_run(header_text)
            run.font.name = HEADER_SETTINGS["font_name"]
            run.font.size = Pt(HEADER_SETTINGS["font_size"])
    
    def _merge_rules_with_standard(self, template_rules: Dict[str, Dict]) -> Dict[str, Dict]:
        """
        合并模板规则和标准规则
        优先级：标准规则 > 模板规则
        如果模板规则中有标准规则没有的样式，保留模板规则
        """
        merged = {}
        
        # 首先添加标准规则
        for style_name, style_config in FONT_STANDARDS.items():
            merged[style_name] = style_config.copy()
        
        # 然后添加模板规则（如果模板规则中的样式名不在标准中，则添加）
        for style_name, style_config in template_rules.items():
            # 如果模板样式名不在标准中，保留模板样式
            if style_name not in merged:
                merged[style_name] = style_config.copy()
            else:
                # 如果模板样式在标准中，但标准中没有某些字段，则补充模板的字段
                standard_style = merged[style_name]
                for key, value in style_config.items():
                    if key not in standard_style or standard_style[key] is None:
                        standard_style[key] = value
        
        return merged
    
    def _detect_paragraph_style(self, paragraph: Paragraph) -> str:
        """
        根据段落内容自动检测应该应用的样式
        返回样式名称（对应FONT_STANDARDS中的key）
        """
        text = paragraph.text.strip() if paragraph.text else ""
        if not text:
            return DEFAULT_STYLE
        
        # 根据样式映射规则检测
        for rule in STYLE_MAPPING_RULES:
            if re.match(rule["pattern"], text, re.IGNORECASE):
                return rule["style"]
        
        # 检查是否是标题
        style_name = paragraph.style.name if paragraph.style else None
        if style_name:
            style_lower = style_name.lower()
            if "标题" in style_name or "heading" in style_lower:
                # 根据标题级别判断
                if "1" in style_name or "一" in style_name or "heading 1" in style_lower:
                    return "title_level_1"
                elif "2" in style_name or "二" in style_name or "heading 2" in style_lower:
                    return "title_level_2"
                elif "3" in style_name or "三" in style_name or "heading 3" in style_lower:
                    return "title_level_3"
        
        # 检查段落内容特征
        if text.startswith("图") and len(text) < 100:
            return "figure_caption"
        if text.startswith("表") and len(text) < 100:
            return "table_caption"
        if re.match(r"^第[一二三四五六七八九十\d]+章|^第\d+章|^Chapter\s+\d+", text):
            return "title_level_1"
        if re.match(r"^\d+\.\d+|^第[一二三四五六七八九十\d]+节", text):
            return "title_level_2"
        if re.match(r"^\d+\.\d+\.\d+", text):
            return "title_level_3"
        
        # 默认返回正文样式
        return DEFAULT_STYLE

    def _apply_rules(
        self,
        document: Document,
        rules: Dict[str, Dict],
        default_style: str | None,
    ) -> Tuple[Document, Dict]:
        total_paragraphs = len(document.paragraphs)
        adjusted_paragraphs = 0
        used_styles: set[str] = set()
        changes_log = []  # 记录详细修改日志

        default_rule = rules.get(default_style) if default_style else None

        for idx, paragraph in enumerate(document.paragraphs):
            style_name = paragraph.style.name if paragraph.style else None
            rule = None
            applied_rule_name = None
            
            # 优先使用标准格式检测
            detected_style = self._detect_paragraph_style(paragraph)
            if detected_style in rules:
                rule = rules[detected_style].copy()
                applied_rule_name = detected_style
            # 如果标准格式中没有，尝试使用模板中的样式名
            elif style_name and style_name in rules:
                rule = rules[style_name].copy()
                applied_rule_name = style_name
            # 如果都没有，使用默认规则
            elif default_rule:
                rule = default_rule.copy()
                applied_rule_name = default_style or "默认样式"
            
            # 如果仍然没有规则，使用标准默认样式
            if not rule:
                if DEFAULT_STYLE in rules:
                    rule = rules[DEFAULT_STYLE].copy()
                    applied_rule_name = DEFAULT_STYLE
                elif default_rule:
                    rule = default_rule.copy()
                    applied_rule_name = default_style or "默认样式"
            
            # 强制统一正文段落格式：毕业论文正文固定为小四（12pt）宋体，固定行距20磅
            if rule:
                paragraph_text = paragraph.text.strip() if paragraph.text else ""
                # 判断是否是标题（包含"标题"字样，或以数字开头且较短，或是居中对齐的短文本）
                is_heading = (
                    (style_name and ("标题" in style_name.lower() or "heading" in style_name.lower())) or
                    (paragraph.alignment == WD_PARAGRAPH_ALIGNMENT.CENTER and len(paragraph_text) < 50) or
                    (paragraph_text and paragraph_text[0].isdigit() and len(paragraph_text) < 30)
                )
                
                # 判断是否包含图片或公式
                has_image_or_equation = self._paragraph_has_image_or_equation(paragraph)
                
                # 对于正文段落（非标题、非图片、非公式），如果使用的是标准默认样式，确保格式正确
                if not is_heading and not has_image_or_equation:
                    # 如果使用的是标准默认样式，确保格式符合标准
                    if applied_rule_name == DEFAULT_STYLE or applied_rule_name == "body_text":
                        if DEFAULT_STYLE in FONT_STANDARDS:
                            standard_body = FONT_STANDARDS[DEFAULT_STYLE]
                            rule["font_size"] = standard_body.get("font_size", 12)
                            rule["font_name"] = standard_body.get("font_name", "宋体")
                            rule["bold"] = standard_body.get("bold", False)
                            rule["line_spacing"] = standard_body.get("line_spacing", 20)
                            rule["first_line_indent"] = standard_body.get("first_line_indent", 24)
                # 对于标题，如果当前规则没有字体大小，也使用默认规则的字体大小
                elif default_rule:
                    if rule.get("font_size") is None and default_rule.get("font_size") is not None:
                        rule["font_size"] = default_rule["font_size"]
                    if rule.get("font_name") is None and default_rule.get("font_name") is not None:
                        rule["font_name"] = default_rule["font_name"]

            if rule:
                # 记录修改前的格式
                before_format = docx_format_utils.extract_paragraph_format(paragraph)
                paragraph_text = paragraph.text[:50] + "..." if len(paragraph.text) > 50 else paragraph.text
                
                # 应用规则
                docx_format_utils.apply_paragraph_rule(paragraph, rule)
                
                # 记录修改后的格式
                after_format = docx_format_utils.extract_paragraph_format(paragraph)
                
                # 找出实际修改的字段
                changed_fields = []
                for key in before_format:
                    before_val = before_format.get(key)
                    after_val = after_format.get(key)
                    if before_val != after_val:
                        changed_fields.append({
                            "field": key,
                            "before": before_val,
                            "after": after_val
                        })
                
                if changed_fields:
                    adjusted_paragraphs += 1
                    changes_log.append({
                        "paragraph_index": idx,
                        "paragraph_preview": paragraph_text.strip() or "(空段落)",
                        "style_name": style_name,
                        "applied_rule": applied_rule_name,
                        "changes": changed_fields
                    })
                    if style_name:
                        used_styles.add(style_name)

        # 统计修改类型
        change_summary = {}
        for change in changes_log:
            for field_change in change["changes"]:
                field_name = field_change["field"]
                if field_name not in change_summary:
                    change_summary[field_name] = 0
                change_summary[field_name] += 1

        stats = {
            "paragraphs_total": total_paragraphs,
            "paragraphs_adjusted": adjusted_paragraphs,
            "styles_applied": sorted(list(used_styles)),
            "changes_summary": change_summary,
            "changes_detail": changes_log[:50],  # 只保留前50条详细记录，避免报告过大
        }

        return document, stats

    def _find_body_start_index(self, document: Document) -> int:
        """找到正文开始的段落索引，跳过封面、目录等前置部分"""
        # 正文开始的标志关键词（按优先级排序）
        # 高优先级：明确的章节标题
        chapter_keywords = [
            "第一章", "第二章", "第三章", "第四章", "第五章", "第六章", "第七章", "第八章", "第九章", "第十章",
            "第1章", "第2章", "第3章", "第4章", "第5章", "第6章", "第7章", "第8章", "第9章", "第10章",
        ]
        
        # 中优先级：章节关键词
        section_keywords = [
            "引言", "绪论", "前言", "概述", "正文", "正文部分",
        ]
        
        # 低优先级：带编号的章节（需要更严格的匹配）
        numbered_sections = [
            "1 引言", "1 绪论", "1 概述", "1 前言",
            "1.1", "1.2", "2.1", "2.2",  # 小节编号
        ]
        
        # 方法1: 查找明确的章节标题（最高优先级）
        for idx, paragraph in enumerate(document.paragraphs):
            paragraph_text = paragraph.text.strip() if paragraph.text else ""
            if not paragraph_text:
                continue
            
            # 检查是否是明确的章节标题
            for keyword in chapter_keywords:
                if keyword in paragraph_text:
                    # 确保不是目录中的引用（目录通常较短且包含"目录"字样）
                    if "目录" not in paragraph_text:
                        # 章节标题通常较短，或者段落开头就是章节标题
                        if len(paragraph_text) < 100 or paragraph_text.startswith(keyword):
                            return idx
        
        # 方法2: 查找章节关键词（中优先级）
        for idx, paragraph in enumerate(document.paragraphs):
            paragraph_text = paragraph.text.strip() if paragraph.text else ""
            if not paragraph_text:
                continue
            
            # 检查是否是章节关键词，且段落开头包含关键词（避免匹配到正文中的引用）
            for keyword in section_keywords:
                if paragraph_text.startswith(keyword) or (keyword in paragraph_text and len(paragraph_text) > 50):
                    # 确保不是目录中的引用
                    if "目录" not in paragraph_text and len(paragraph_text) > 20:
                        return idx
        
        # 方法3: 查找带编号的章节（需要更严格的匹配）
        for idx, paragraph in enumerate(document.paragraphs):
            paragraph_text = paragraph.text.strip() if paragraph.text else ""
            if not paragraph_text:
                continue
            
            # 检查是否是带编号的章节（段落开头必须是编号）
            for keyword in numbered_sections:
                if paragraph_text.startswith(keyword):
                    # 确保不是目录中的引用
                    if "目录" not in paragraph_text and len(paragraph_text) > 20:
                        return idx
        
        # 方法4: 如果找不到关键词，跳过前N个段落（通常是封面和目录）
        # 跳过前20个段落，或者文档总段落数的10%（取较大值）
        skip_count = max(20, len(document.paragraphs) // 10)
        return min(skip_count, len(document.paragraphs) - 1)

    def _check_figure_captions(self, document: Document) -> list:
        """检测文档中的图片，检查是否有图题，返回缺失图题的图片列表，并在文档中标记错误
        注意：只从正文开始检测，跳过封面、目录等前置部分"""
        issues = []
        missing_caption_indices = []  # 记录缺少图题的图片段落索引
        
        # 找到正文开始的段落索引
        body_start_idx = self._find_body_start_index(document)
        
        # 只从正文开始检测图片
        for idx, paragraph in enumerate(document.paragraphs):
            # 跳过正文之前的段落
            if idx < body_start_idx:
                continue
            # 检查段落中是否包含图片
            has_image = False
            paragraph_text = paragraph.text.strip() if paragraph.text else ""
            
            # 跳过明显不是图片的段落（比如纯文本段落、标题等）
            # 如果段落有大量文字且没有drawing相关标签，不太可能是图片段落
            # 但不要完全跳过，因为图片段落可能包含一些文字说明
            # 先检查是否有drawing相关标签，如果没有且文字很多，才跳过
            if len(paragraph_text) > 200:
                para_xml_preview = str(paragraph._element.xml)[:500] if hasattr(paragraph, '_element') else ""
                if 'drawing' not in para_xml_preview.lower() and 'pic:pic' not in para_xml_preview and 'a:blip' not in para_xml_preview:
                    continue
            
            # 方法1: 检查段落中的runs是否包含真正的图片（必须包含pic:pic或a:blip）
            try:
                for run in paragraph.runs:
                    if not hasattr(run, 'element'):
                        continue
                    run_xml = str(run.element.xml)
                    # 排除明显是VML形状的水印（通过检查是否有textpath等特征）
                    if 'v:shape' in run_xml.lower() and 'textpath' in run_xml.lower():
                        continue  # 这是水印，跳过
                    # 必须包含pic:pic或a:blip，这些才是真正的图片元素
                    # 同时需要验证有图片引用（r:embed或r:link）
                    if ('pic:pic' in run_xml or 'a:blip' in run_xml) and ('r:embed' in run_xml or 'r:link' in run_xml or 'a:blip' in run_xml):
                        has_image = True
                        break
            except:
                pass
            
            # 方法2: 检查段落元素中是否包含真正的图片
            if not has_image:
                try:
                    para_xml = str(paragraph._element.xml)
                    # 排除VML形状的水印
                    if 'v:shape' in para_xml.lower() and 'textpath' in para_xml.lower():
                        pass  # 这是水印，跳过
                    # 必须包含pic:pic或a:blip，且需要验证有图片引用
                    elif ('pic:pic' in para_xml or 'a:blip' in para_xml) and ('r:embed' in para_xml or 'r:link' in para_xml or 'a:blip' in para_xml):
                        has_image = True
                except:
                    pass
            
            # 方法3: 使用xpath查找drawing元素，并验证包含真正的图片
            if not has_image:
                try:
                    from docx.oxml.ns import qn
                    # 查找drawing元素
                    drawings = paragraph._element.xpath('.//w:drawing', namespaces={
                        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
                        'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
                        'pic': 'http://schemas.openxmlformats.org/drawingml/2006/picture',
                        'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
                    })
                    if drawings:
                        # 检查drawing中是否包含真正的图片（pic:pic或a:blip）
                        for drawing in drawings:
                            drawing_xml = str(drawing.xml)
                            # 排除VML形状的水印
                            if 'v:shape' in drawing_xml.lower() and 'textpath' in drawing_xml.lower():
                                continue
                            # 必须包含pic:pic或a:blip，且需要验证有图片引用
                            if ('pic:pic' in drawing_xml or 'a:blip' in drawing_xml) and ('r:embed' in drawing_xml or 'r:link' in drawing_xml or 'a:blip' in drawing_xml):
                                has_image = True
                                break
                except:
                    pass
            
            # 如果找到图片，还需要验证段落确实包含图片（不能只是文字说明）
            # 如果段落只有文字且没有图片元素，跳过
            if has_image:
                # 再次验证：如果段落只有文字说明（如"如下图所示"），但没有实际图片，则跳过
                # 检查段落中是否有实际的图片元素，而不仅仅是文字
                has_actual_image_element = False
                try:
                    para_xml_full = str(paragraph._element.xml)
                    # 必须包含pic:pic元素（这是真正的图片元素）
                    if 'pic:pic' in para_xml_full:
                        # 进一步验证：pic:pic中应该包含blip（图片数据）
                        # 或者包含embed/link引用
                        if 'a:blip' in para_xml_full or 'r:embed' in para_xml_full or 'r:link' in para_xml_full:
                            has_actual_image_element = True
                    # 或者直接包含a:blip且有引用
                    elif 'a:blip' in para_xml_full and ('r:embed' in para_xml_full or 'r:link' in para_xml_full):
                        has_actual_image_element = True
                except:
                    pass
                
                # 如果没有实际的图片元素，只是误判，跳过
                if not has_actual_image_element:
                    has_image = False
            
            # 如果找到图片，强制设置段落对齐为居中
            if has_image:
                paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            
            # 如果找到图片，检查后面几个段落是否有图题
            if has_image:
                # 检查当前段落及后面最多5个段落是否有图题
                is_caption = False
                caption_paragraph_idx = None
                
                # 检查范围：当前段落 + 后面5个段落
                check_range = min(6, len(document.paragraphs) - idx)
                for offset in range(check_range):
                    check_idx = idx + offset
                    if check_idx >= len(document.paragraphs):
                        break
                    check_para = document.paragraphs[check_idx]
                    check_text = check_para.text.strip() if check_para.text else ""
                    
                    # 判断是否是图题：以"图"开头，且包含数字（如"图1-1"、"图2.1"等）
                    if check_text and check_text.startswith("图") and len(check_text) < 100:
                        # 检查是否包含图号格式（图X-X、图X.X等）
                        if re.search(r'图\s*\d+[\.\-]\d+', check_text) or re.search(r'图\s*\d+', check_text):
                            is_caption = True
                            caption_paragraph_idx = check_idx
                            break
                    
                    # 如果检查的段落已经有大量文字，说明图题不太可能在更后面了
                    if offset > 0 and len(check_text) > 50 and not check_text.startswith("图"):
                        break
                
                # 如果没有找到图题，记录问题
                if not is_caption:
                    # 获取图片所在位置的上下文（前后各一段）
                    context_before = ""
                    context_after = ""
                    if idx > 0:
                        context_before = document.paragraphs[idx - 1].text.strip()[:50]
                    if idx + 1 < len(document.paragraphs):
                        context_after = document.paragraphs[idx + 1].text.strip()[:50]
                    
                    issues.append({
                        "paragraph_index": idx,
                        "type": "missing_figure_caption",
                        "message": "图片后缺少图题说明",
                        "context_before": context_before,
                        "context_after": context_after,
                        "suggestion": "请在图片后添加图题，格式如：图X-X 图片说明"
                    })
                    missing_caption_indices.append(idx)
        
        # 在文档中标记缺少图题的位置（从后往前插入，避免索引变化）
        for img_idx in reversed(missing_caption_indices):
            # 找到图片段落
            img_paragraph = document.paragraphs[img_idx]
            
            # 创建完整的标记段落XML（包含段落属性、run、文本、颜色、高亮等）
            marker_text = "⚠️ 【缺少图题】请在图片后添加图题，格式如：图X-X 图片说明"
            # 转义XML特殊字符
            escaped_text = xml.sax.saxutils.escape(marker_text)
            
            new_para_xml = f'''<w:p xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
                <w:pPr>
                    <w:jc w:val="left"/>
                </w:pPr>
                <w:r>
                    <w:rPr>
                        <w:b/>
                        <w:color w:val="FF0000"/>
                        <w:highlight w:val="yellow"/>
                    </w:rPr>
                    <w:t xml:space="preserve">{escaped_text}</w:t>
                </w:r>
            </w:p>'''
            
            # 解析并插入新段落
            new_para_element = parse_xml(new_para_xml)
            img_paragraph._element.addnext(new_para_element)
        
        return issues

    def _check_reference_citations(self, document: Document) -> list:
        """检测参考文献引用标注，检查正文中是否有引用标注，返回缺失引用的问题列表"""
        issues = []
        
        # 1. 找到参考文献部分的起始位置
        reference_start_idx = None
        reference_section_text = ""
        
        for idx, paragraph in enumerate(document.paragraphs):
            para_text = paragraph.text.strip() if paragraph.text else ""
            # 检测参考文献标题（可能包含"参考文献"、"References"、"参考书目"等）
            if re.search(r'参考(文献|书目)', para_text) or para_text.lower().startswith('references') or para_text.lower().startswith('bibliography'):
                reference_start_idx = idx
                # 收集参考文献部分的内容（最多收集50个段落）
                ref_paragraphs = []
                for i in range(idx, min(idx + 50, len(document.paragraphs))):
                    ref_paragraphs.append(document.paragraphs[i].text.strip() if document.paragraphs[i].text else "")
                reference_section_text = "\n".join(ref_paragraphs)
                break
        
        # 如果没有找到参考文献部分，提示用户
        if reference_start_idx is None:
            issues.append({
                "type": "no_reference_section",
                "message": "未找到参考文献部分",
                "suggestion": "请在文档末尾添加参考文献部分，标题为'参考文献'"
            })
            return issues
        
        # 2. 提取参考文献列表（通常以数字编号开头，如 [1]、1. 等）
        reference_items = []
        reference_patterns = [
            r'^\[\d+\]',  # [1] 格式
            r'^\d+\.',    # 1. 格式
            r'^\(\d+\)',  # (1) 格式
        ]
        
        for idx in range(reference_start_idx + 1, min(reference_start_idx + 100, len(document.paragraphs))):
            para = document.paragraphs[idx]
            para_text = para.text.strip() if para.text else ""
            
            # 如果遇到新的章节标题，停止收集
            if len(para_text) < 50 and (para_text.startswith("第") or para_text.startswith("Chapter") or 
                                         para_text.startswith("附录") or para_text.startswith("Appendix")):
                break
            
            # 检查是否符合参考文献格式
            is_reference = False
            for pattern in reference_patterns:
                if re.match(pattern, para_text):
                    is_reference = True
                    break
            
            # 如果段落较长且包含作者、年份等信息，也可能是参考文献
            if not is_reference and len(para_text) > 20:
                # 检查是否包含常见的参考文献特征（作者名、年份、期刊名等）
                if re.search(r'\d{4}', para_text) and (len(para_text) > 30):  # 包含年份且较长
                    is_reference = True
            
            if is_reference:
                reference_items.append({
                    "index": len(reference_items) + 1,
                    "text": para_text[:100],  # 只保存前100个字符
                    "paragraph_index": idx
                })
        
        # 如果没有找到参考文献条目，提示
        if not reference_items:
            issues.append({
                "type": "no_reference_items",
                "message": "参考文献部分为空或格式不正确",
                "suggestion": "请确保参考文献部分包含编号的参考文献条目"
            })
            return issues
        
        # 3. 检查正文中是否有引用标注
        # 正文部分：从文档开始到参考文献部分之前
        body_text = ""
        body_paragraphs = []
        for idx in range(min(100, reference_start_idx)):  # 只检查前100个段落和参考文献之前的部分
            para = document.paragraphs[idx]
            para_text = para.text.strip() if para.text else ""
            # 只检查较长的段落（正文），跳过标题、目录等短段落
            if len(para_text) > 50:  # 只检查较长的段落（正文）
                body_text += para_text + " "
                body_paragraphs.append((idx, para_text))
        
        # 检测引用标注的常见格式
        citation_patterns = [
            r'\[\d+\]',           # [1] 格式
            r'\[\d+[,\-\s]+\d+\]', # [1,2,3] 或 [1-5] 格式
            r'\(\d{4}[a-z]?\)',   # (2020) 或 (2020a) 格式
            r'（\d{4}[a-z]?）',   # （2020）格式
        ]
        
        has_citation = False
        citation_matches = []
        for pattern in citation_patterns:
            matches = re.finditer(pattern, body_text)
            for match in matches:
                has_citation = True
                citation_matches.append(match.group())
        
        # 如果没有找到引用标注，提示用户
        if not has_citation and len(reference_items) > 0:
            # 找到正文段落中可能缺少引用的位置
            missing_citation_paragraphs = []
            for para_idx, para_text in body_paragraphs:
                # 如果段落较长（可能是正文），但没有引用标注，记录
                if len(para_text) > 100 and not any(re.search(pattern, para_text) for pattern in citation_patterns):
                    # 检查段落是否包含可能引用的内容（如"研究"、"文献"、"表明"等学术词汇）
                    academic_keywords = ['研究', '文献', '表明', '发现', '提出', '分析', '方法', '理论', '模型']
                    if any(keyword in para_text for keyword in academic_keywords):
                        missing_citation_paragraphs.append({
                            "paragraph_index": para_idx,
                            "text_preview": para_text[:80] + "..."
                        })
            
            if missing_citation_paragraphs:
                issues.append({
                    "type": "missing_citations",
                    "message": f"正文中缺少参考文献引用标注（发现 {len(reference_items)} 条参考文献，但正文中未找到引用标注）",
                    "suggestion": "请在正文中添加引用标注，格式如：[1] 或 [1,2,3] 或 (作者, 年份)",
                    "reference_count": len(reference_items),
                    "missing_citation_paragraphs": missing_citation_paragraphs[:10]  # 只显示前10个
                })
            else:
                issues.append({
                    "type": "missing_citations",
                    "message": f"正文中缺少参考文献引用标注（发现 {len(reference_items)} 条参考文献，但正文中未找到引用标注）",
                    "suggestion": "请在正文中添加引用标注，格式如：[1] 或 [1,2,3] 或 (作者, 年份)",
                    "reference_count": len(reference_items)
                })
        
        return issues

    def _check_excessive_blanks(self, document: Document) -> list:
        """
        检测文档中的大段空白
        
        规则：
        - 只检测从正文开始到参考文献结束之间的内容
        - 其他部分（封面、目录、摘要等）不需要检测空白行
        - 两个章节之间允许有大段空白
        - 在同一章节内，不允许有大段空白（连续2个以上空白段落）
        
        Returns:
            问题列表
        """
        issues = []
        blank_paragraph_indices = []  # 记录需要标记的空白段落索引
        
        # 1. 找到正文开始位置
        body_start_idx = None
        body_start_patterns = [
            r'^正文',
            r'^第[一二三四五六七八九十\d]+章',  # 第一章、第二章等
            r'^第\d+章',  # 第1章、第2章等
            r'^Chapter\s+\d+',  # Chapter 1、Chapter 2等
            r'^1\s+',  # 以"1 "开头的标题（第一章）
            r'^1\.',  # 以"1."开头的标题
        ]
        
        for idx, paragraph in enumerate(document.paragraphs):
            para_text = paragraph.text.strip() if paragraph.text else ""
            # 检查是否符合正文开始模式
            for pattern in body_start_patterns:
                if re.match(pattern, para_text):
                    body_start_idx = idx
                    break
            if body_start_idx is not None:
                break
        
        # 如果没有找到明确的正文开始标记，尝试找第一个较长的段落（可能是正文开始）
        if body_start_idx is None:
            for idx, paragraph in enumerate(document.paragraphs):
                para_text = paragraph.text.strip() if paragraph.text else ""
                # 跳过明显的非正文部分（摘要、目录等）
                if re.search(r'^(摘要|Abstract|目录|Contents|致谢|Acknowledgement)', para_text, re.IGNORECASE):
                    continue
                # 如果段落较长（可能是正文），且不是标题样式，认为是正文开始
                if len(para_text) > 100:
                    style_name = paragraph.style.name if paragraph.style else ""
                    if '标题' not in style_name and 'Heading' not in style_name.lower():
                        body_start_idx = idx
                        break
        
        # 如果仍然找不到，从第10个段落开始（跳过封面、目录等）
        if body_start_idx is None:
            body_start_idx = min(10, len(document.paragraphs))
        
        # 2. 找到参考文献结束位置
        reference_end_idx = len(document.paragraphs)  # 默认到文档末尾
        
        # 先找到参考文献开始位置
        reference_start_idx = None
        for idx, paragraph in enumerate(document.paragraphs):
            para_text = paragraph.text.strip() if paragraph.text else ""
            if re.search(r'参考(文献|书目)', para_text) or para_text.lower().startswith('references') or para_text.lower().startswith('bibliography'):
                reference_start_idx = idx
                break
        
        if reference_start_idx is not None:
            # 从参考文献开始位置向后查找，找到参考文献结束位置
            # 参考文献结束的标志：遇到"致谢"、"附录"等，或者连续多个非参考文献格式的段落
            non_ref_count = 0
            for idx in range(reference_start_idx + 1, len(document.paragraphs)):
                para = document.paragraphs[idx]
                para_text = para.text.strip() if para.text else ""
                
                # 如果遇到新的章节（致谢、附录等），参考文献结束
                if re.search(r'^(致谢|附录|Acknowledgement|Appendix)', para_text, re.IGNORECASE):
                    reference_end_idx = idx
                    break
                
                # 检查是否是参考文献格式（编号开头）
                is_reference = False
                if re.match(r'^\[\d+\]', para_text) or re.match(r'^\d+\.', para_text) or re.match(r'^\(\d+\)', para_text):
                    is_reference = True
                
                # 如果连续多个段落都不是参考文献格式，认为参考文献结束
                if not is_reference and len(para_text) > 20:
                    non_ref_count += 1
                    if non_ref_count >= 3:  # 连续3个非参考文献段落，认为参考文献结束
                        reference_end_idx = idx - 2  # 回到第一个非参考文献段落之前
                        break
                else:
                    non_ref_count = 0
        
        # 3. 确定检测范围：从正文开始到参考文献结束
        check_start_idx = body_start_idx
        check_end_idx = reference_end_idx
        
        # 如果正文开始位置在参考文献之后，不检测
        if check_start_idx >= check_end_idx:
            return issues
        
        # 识别章节边界的模式
        chapter_patterns = [
            r'^第[一二三四五六七八九十\d]+章',  # 第一章、第二章等
            r'^第[一二三四五六七八九十\d]+节',  # 第一节、第二节等
            r'^\d+\.\d+',  # 1.1、2.1 等
            r'^第\d+章',  # 第1章、第2章等
            r'^Chapter\s+\d+',  # Chapter 1、Chapter 2等
            r'^附录[一二三四五六七八九十\d]',  # 附录一、附录二
        ]
        
        # 判断段落是否为章节标题
        def is_chapter_title(paragraph) -> bool:
            para_text = paragraph.text.strip() if paragraph.text else ""
            if not para_text:
                return False
            
            # 检查是否符合章节标题模式
            for pattern in chapter_patterns:
                if re.match(pattern, para_text):
                    return True
            
            # 检查是否为标题样式（通常标题样式名称包含"标题"或"Heading"）
            style_name = paragraph.style.name if paragraph.style else ""
            if '标题' in style_name or 'Heading' in style_name.lower():
                # 进一步验证：标题通常较短且格式特殊
                if len(para_text) < 50:  # 标题通常较短
                    return True
            
            return False
        
        # 判断段落是否为空（空白段落）
        def is_blank_paragraph(paragraph) -> bool:
            para_text = paragraph.text.strip() if paragraph.text else ""
            # 空白段落：文本为空或只有空白字符
            return len(para_text) == 0
        
        # 4. 只在检测范围内遍历段落，识别章节和空白
        current_chapter_start = check_start_idx  # 当前章节的起始段落索引
        consecutive_blanks = 0  # 连续空白段落计数
        blank_start_idx = None  # 连续空白段的起始索引
        
        for idx in range(check_start_idx, check_end_idx):
            paragraph = document.paragraphs[idx]
            # 检查是否为章节标题
            if is_chapter_title(paragraph):
                # 遇到新章节标题
                # 如果之前有连续空白，检查这些空白是否在章节标题后（允许）还是在章节内（需要标记）
                if consecutive_blanks >= 2 and blank_start_idx is not None:
                    # 检查空白段之前是否有章节标题
                    is_after_chapter = False
                    if blank_start_idx > 0:
                        prev_para = document.paragraphs[blank_start_idx - 1]
                        if is_chapter_title(prev_para):
                            # 空白段紧跟在章节标题后，这是章节间的空白，允许
                            is_after_chapter = True
                    
                    # 如果空白段不在章节标题后，而是在章节内，标记为问题
                    if not is_after_chapter:
                        issues.append({
                            "type": "excessive_blanks_in_chapter",
                            "message": f"第 {blank_start_idx + 1} 段到第 {blank_start_idx + consecutive_blanks} 段之间存在 {consecutive_blanks} 个连续空白段落（正文章节内）",
                            "suggestion": "请删除章节内的多余空白，章节之间可以保留适当空白",
                            "chapter_start": current_chapter_start,
                            "blank_start": blank_start_idx,
                            "blank_count": consecutive_blanks,
                            "paragraph_indices": list(range(blank_start_idx, blank_start_idx + consecutive_blanks))
                        })
                        # 记录需要标记的段落
                        blank_paragraph_indices.extend(range(blank_start_idx, blank_start_idx + consecutive_blanks))
                
                # 开始新章节，重置计数（章节标题后的空白是允许的）
                current_chapter_start = idx
                consecutive_blanks = 0
                blank_start_idx = None
            else:
                # 检查是否为空白段落
                if is_blank_paragraph(paragraph):
                    if consecutive_blanks == 0:
                        # 开始新的连续空白段
                        blank_start_idx = idx
                    consecutive_blanks += 1
                else:
                    # 遇到非空白段落
                    # 如果之前有连续空白且在同一章节内，检查是否需要标记
                    if consecutive_blanks >= 2 and blank_start_idx is not None:
                        # 在同一章节内（不是章节边界），标记为问题
                        # 检查空白段之前是否有章节标题（如果空白段紧跟在章节标题后，可能是章节间的空白，允许）
                        is_after_chapter = False
                        if blank_start_idx > 0:
                            prev_para = document.paragraphs[blank_start_idx - 1]
                            if is_chapter_title(prev_para):
                                is_after_chapter = True
                        
                        # 如果空白段不在章节标题后，且在同一章节内，标记为问题
                        if not is_after_chapter:
                            issues.append({
                                "type": "excessive_blanks_in_chapter",
                                "message": f"第 {blank_start_idx + 1} 段到第 {blank_start_idx + consecutive_blanks} 段之间存在 {consecutive_blanks} 个连续空白段落（正文章节内）",
                                "suggestion": "请删除章节内的多余空白，章节之间可以保留适当空白",
                                "chapter_start": current_chapter_start,
                                "blank_start": blank_start_idx,
                                "blank_count": consecutive_blanks,
                                "paragraph_indices": list(range(blank_start_idx, blank_start_idx + consecutive_blanks))
                            })
                            # 记录需要标记的段落
                            blank_paragraph_indices.extend(range(blank_start_idx, blank_start_idx + consecutive_blanks))
                    
                    # 重置计数
                    consecutive_blanks = 0
                    blank_start_idx = None
        
        # 处理文档末尾的连续空白
        if consecutive_blanks >= 2 and blank_start_idx is not None:
            # 检查是否在章节标题后
            is_after_chapter = False
            if blank_start_idx > 0:
                prev_para = document.paragraphs[blank_start_idx - 1]
                if is_chapter_title(prev_para):
                    is_after_chapter = True
            
            if not is_after_chapter:
                issues.append({
                    "type": "excessive_blanks_in_chapter",
                    "message": f"正文末尾第 {blank_start_idx + 1} 段到第 {blank_start_idx + consecutive_blanks} 段之间存在 {consecutive_blanks} 个连续空白段落",
                    "suggestion": "请删除正文末尾的多余空白",
                    "chapter_start": current_chapter_start,
                    "blank_start": blank_start_idx,
                    "blank_count": consecutive_blanks,
                    "paragraph_indices": list(range(blank_start_idx, blank_start_idx + consecutive_blanks))
                })
                blank_paragraph_indices.extend(range(blank_start_idx, blank_start_idx + consecutive_blanks))
        
        # 在文档中标记问题（从后往前插入，避免索引变化）
        for blank_idx in sorted(set(blank_paragraph_indices), reverse=True):
            blank_paragraph = document.paragraphs[blank_idx]
            
            # 创建标记文本
            marker_text = "⚠️ 【正文章节内多余空白】请删除此空白段落"
            escaped_text = xml.sax.saxutils.escape(marker_text)
            
            # 创建标记段落（插入在空白段落之后，这样更容易看到）
            new_para_xml = f'''<w:p xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
                <w:pPr>
                    <w:jc w:val="left"/>
                </w:pPr>
                <w:r>
                    <w:rPr>
                        <w:b/>
                        <w:color w:val="FF0000"/>
                        <w:highlight w:val="yellow"/>
                    </w:rPr>
                    <w:t xml:space="preserve">{escaped_text}</w:t>
                </w:r>
            </w:p>'''
            
            # 解析并插入新段落（在空白段落之后）
            new_para_element = parse_xml(new_para_xml)
            blank_paragraph._element.addnext(new_para_element)
        
        return issues

    def _save_file_to_storage(self, key: str, content: bytes) -> bool:
        """
        保存文件到云存储
        
        Args:
            key: 存储键（路径）
            content: 文件内容（字节）
        
        Returns:
            是否成功
        """
        if not self.use_storage:
            return False
        try:
            file_obj = io.BytesIO(content)
            return self.storage.upload_file(key, file_obj)
        except Exception as e:
            print(f"[Storage] Failed to save {key}: {e}")
            return False

    def _load_file_from_storage(self, key: str) -> Optional[bytes]:
        """
        从云存储加载文件
        
        Args:
            key: 存储键（路径）
        
        Returns:
            文件内容（字节），如果不存在则返回 None
        """
        if not self.use_storage:
            return None
        try:
            return self.storage.download_file(key)
        except Exception as e:
            print(f"[Storage] Failed to load {key}: {e}")
            return None

    def _save_to_storage(self, document_id: str, files: Dict[str, Path]) -> None:
        """
        将文档文件保存到云存储
        
        Args:
            document_id: 文档ID
            files: 文件路径字典
        """
        if not self.use_storage:
            return
        
        prefix = f"documents/{document_id}"
        
        # 保存所有文件
        for file_type, file_path in files.items():
            if file_path.exists():
                key = f"{prefix}/{file_type}.{file_path.suffix[1:]}"  # 去掉点号
                content = file_path.read_bytes()
                if self._save_file_to_storage(key, content):
                    print(f"[Storage] Saved {key}")
                else:
                    print(f"[Storage] Failed to save {key}")

    def _get_file_from_storage_or_local(self, document_id: str, file_type: str, extension: str, local_path: Path) -> Optional[Path]:
        """
        从云存储或本地文件系统获取文件
        
        Args:
            document_id: 文档ID
            file_type: 文件类型（original, final, preview, html, report）
            extension: 文件扩展名（docx, html, json）
            local_path: 本地文件路径（用于回退）
        
        Returns:
            文件路径（如果找到），否则返回 None
        """
        # 优先从云存储读取
        if self.use_storage:
            key = f"documents/{document_id}/{file_type}.{extension}"
            if self.storage.file_exists(key):
                content = self._load_file_from_storage(key)
                if content:
                    # 确保本地目录存在
                    local_path.parent.mkdir(parents=True, exist_ok=True)
                    # 写入本地临时文件
                    local_path.write_bytes(content)
                    print(f"[Storage] Loaded {key} to {local_path}")
                    return local_path
        
        # 回退到本地文件系统
        if local_path.exists():
            return local_path
        
        return None

    def _generate_watermarked_preview(self, final_path: Path, preview_path: Path) -> None:
        shutil.copy2(final_path, preview_path)
        document = Document(preview_path)
        watermark_text = "预览版 仅供查看"
        
        # 创建VML水印形状，设置为背景层，难以删除
        ns = (
            'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
            'xmlns:v="urn:schemas-microsoft-com:vml" '
            'xmlns:o="urn:schemas-microsoft-com:office:office"'
        )
        shape_template = (
            f'<w:pict {ns}>'
            '<v:shape id="watermark" o:spid="_x0000_s1025" type="#_x0000_t136" '
            'style="position:absolute;margin-left:0;margin-top:0;width:468pt;height:600pt;'
            'rotation:315;opacity:0.15;z-index:-251654144;mso-position-horizontal:center;'
            'mso-position-vertical:center;mso-wrap-style:none;mso-wrap-distance-left:0;'
            'mso-wrap-distance-right:0;mso-wrap-distance-top:0;mso-wrap-distance-bottom:0;">'
            '<v:fill opacity="0"/>'
            '<v:stroke color="#d10f0f"/>'
            f'<v:textpath style="font-family:微软雅黑;font-size:72pt;font-weight:bold" string="{watermark_text}"/>'
            '<o:lock v:ext="edit" rotation="t" text="t" aspectratio="t"/>'
            '</v:shape>'
            '</w:pict>'
        )
        
        # 方法1: 在页眉中添加水印（覆盖所有页面）
        for section in document.sections:
            header = section.header
            if header.is_linked_to_previous:
                header.is_linked_to_previous = False
            # 清空现有页眉内容
            for para in header.paragraphs:
                para.clear()
            paragraph = header.add_paragraph()
            paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            run = paragraph.add_run()
            run._r.append(parse_xml(shape_template))
        
        # 方法2: 在正文的每个段落中嵌入水印（作为背景层）
        # 每隔几个段落插入一次，避免文档过大
        watermark_interval = max(1, len(document.paragraphs) // 20)  # 大约20个水印
        for i, paragraph in enumerate(document.paragraphs):
            # 跳过空段落和标题段落
            if not paragraph.text.strip() or len(paragraph.text.strip()) < 3:
                continue
            # 每隔一定间隔插入水印
            if i % watermark_interval == 0:
                # 在段落开头插入水印形状
                run = paragraph.runs[0] if paragraph.runs else paragraph.add_run()
                # 创建独立的水印形状，位置相对于段落
                para_shape = (
                    f'<w:pict {ns}>'
                    '<v:shape id="watermark_para" o:spid="_x0000_s1026" type="#_x0000_t136" '
                    'style="position:absolute;margin-left:0;margin-top:0;width:400pt;height:400pt;'
                    'rotation:315;opacity:0.12;z-index:-251654144;mso-position-horizontal:center;'
                    'mso-position-vertical:center;mso-wrap-style:none;">'
                    '<v:fill opacity="0"/>'
                    '<v:stroke color="#d10f0f"/>'
                    f'<v:textpath style="font-family:微软雅黑;font-size:60pt;font-weight:bold" string="{watermark_text}"/>'
                    '<o:lock v:ext="edit" rotation="t" text="t" aspectratio="t"/>'
                    '</v:shape>'
                    '</w:pict>'
                )
                run._r.append(parse_xml(para_shape))
        
        document.save(preview_path)
    
    def _generate_html_preview(self, docx_path: Path, html_path: Path, stats: Dict) -> None:
        """将Word文档转换为HTML预览"""
        document = Document(docx_path)
        
        # 生成修改摘要HTML
        changes_summary_html = ""
        if stats.get("changes_summary"):
            field_names = {
                "font_name": "字体",
                "font_size": "字号",
                "bold": "加粗",
                "alignment": "对齐方式",
                "line_spacing": "行距",
                "space_before": "段前间距",
                "space_after": "段后间距",
                "first_line_indent": "首行缩进",
                "left_indent": "左缩进",
                "right_indent": "右缩进",
            }
            changes_summary_html = '<div class="changes-summary"><h3>📝 格式修改摘要</h3><ul>'
            for field, count in sorted(stats["changes_summary"].items(), key=lambda x: x[1], reverse=True):
                field_name = field_names.get(field, field)
                changes_summary_html += f'<li><strong>{field_name}</strong>: 修改了 <strong>{count}</strong> 处</li>'
            changes_summary_html += f'</ul><p>总计修改了 <strong>{stats.get("paragraphs_adjusted", 0)}</strong> 个段落</p></div>'
        
        # 生成图片检测结果HTML
        figure_issues_html = ""
        if stats.get("figure_issues"):
            issues = stats["figure_issues"]
            figure_issues_html = '<div class="figure-issues" style="background: #fff3cd; border: 2px solid #ffc107; border-radius: 8px; padding: 20px; margin-bottom: 30px; position: relative; z-index: 2;"><h3 style="margin-top: 0; color: #856404;">⚠️ 图片检测结果</h3>'
            figure_issues_html += f'<p style="color: #856404; font-weight: bold;">发现 <strong>{len(issues)}</strong> 处图片缺少图题：</p><ul style="list-style: none; padding-left: 0;">'
            for issue in issues[:10]:  # 最多显示10个问题
                figure_issues_html += f'<li style="padding: 10px 0; border-bottom: 1px solid #ffc107;"><strong>第 {issue["paragraph_index"] + 1} 段</strong>: {issue["message"]}<br><small style="color: #666;">{issue["suggestion"]}</small></li>'
            if len(issues) > 10:
                figure_issues_html += f'<li style="padding: 10px 0; color: #666;">... 还有 {len(issues) - 10} 处问题未显示</li>'
            figure_issues_html += '</ul></div>'
        
        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>文档预览 - 预览版</title>
    <style>
        body {{
            font-family: "SimSun", "宋体", "Times New Roman", serif;
            max-width: 210mm;
            margin: 20px auto;
            padding: 20px;
            background: #f5f5f5;
            line-height: 1.6;
        }}
        .document-container {{
            background: white;
            padding: 40px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            min-height: 297mm;
        }}
        .watermark {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) rotate(-45deg);
            font-size: 72px;
            color: rgba(209, 15, 15, 0.15);
            font-weight: bold;
            pointer-events: none;
            z-index: 1;
            white-space: nowrap;
        }}
        .changes-summary {{
            background: #e7f3ff;
            border: 2px solid #2196F3;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
            position: relative;
            z-index: 2;
        }}
        .changes-summary h3 {{
            margin-top: 0;
            color: #1976D2;
            font-size: 18px;
        }}
        .changes-summary ul {{
            list-style: none;
            padding-left: 0;
        }}
        .changes-summary li {{
            padding: 8px 0;
            border-bottom: 1px solid #BBDEFB;
        }}
        .changes-summary li:last-child {{
            border-bottom: none;
        }}
        .changes-summary p {{
            margin-top: 15px;
            font-size: 16px;
            color: #1976D2;
            font-weight: bold;
        }}
        p {{
            margin: 12px 0;
            text-indent: 2em;
            position: relative;
            z-index: 2;
        }}
        h1, h2, h3, h4, h5, h6 {{
            margin: 20px 0 10px 0;
            position: relative;
            z-index: 2;
        }}
        h1 {{ font-size: 18pt; font-weight: bold; text-align: center; }}
        h2 {{ font-size: 16pt; font-weight: bold; }}
        h3 {{ font-size: 14pt; font-weight: bold; }}
        .center {{ text-align: center; }}
        .bold {{ font-weight: bold; }}
        .no-indent {{ text-indent: 0; }}
        .warning {{
            background: #fff3cd;
            border: 1px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
            text-align: center;
            font-weight: bold;
            color: #856404;
        }}
        @media print {{
            body {{ background: white; }}
            .document-container {{ box-shadow: none; }}
        }}
    </style>
</head>
<body>
    <div class="watermark">预览版 仅供查看</div>
    <div class="document-container">
        {changes_summary_html}
        {figure_issues_html}
"""
        
        for paragraph in document.paragraphs:
            text = paragraph.text.strip()
            if not text:
                html_content += "<p>&nbsp;</p>\n"
                continue
            
            # 判断段落样式
            style_name = paragraph.style.name if paragraph.style else "Normal"
            alignment = paragraph.alignment
            
            # 构建样式
            style_attrs = []
            classes = []
            
            if "Heading" in style_name or "标题" in style_name:
                level = 1
                if "1" in style_name or "一" in style_name:
                    level = 1
                elif "2" in style_name or "二" in style_name:
                    level = 2
                elif "3" in style_name or "三" in style_name:
                    level = 3
                else:
                    level = 2
                html_content += f"<h{level}>{text}</h{level}>\n"
            else:
                # 普通段落
                if alignment == WD_PARAGRAPH_ALIGNMENT.CENTER:
                    classes.append("center")
                if alignment == WD_PARAGRAPH_ALIGNMENT.RIGHT:
                    style_attrs.append("text-align: right;")
                
                # 检查首行缩进
                if paragraph.paragraph_format.first_line_indent and paragraph.paragraph_format.first_line_indent.pt > 0:
                    classes.append("no-indent")
                
                # 检查加粗
                is_bold = any(run.bold for run in paragraph.runs if run.bold)
                if is_bold:
                    classes.append("bold")
                
                class_attr = f' class="{" ".join(classes)}"' if classes else ""
                style_attr = f' style="{" ".join(style_attrs)}"' if style_attrs else ""
                
                # 处理文本中的特殊字符
                text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                
                html_content += f'<p{class_attr}{style_attr}>{text}</p>\n'
        
        html_content += """    </div>
    <div class="warning">
        ⚠️ 这是预览版本，仅供查看。如需下载正式版，请完成支付。
    </div>
</body>
</html>"""
        
        html_path.write_text(html_content, encoding="utf-8")

