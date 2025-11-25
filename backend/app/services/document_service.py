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
from docx.text.paragraph import Paragraph
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
        
        # 检测页眉（不修改，只检测）
        # 不再自动应用页眉，只检测是否存在
        
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
        
        # 检测页眉
        header_issues = self._check_header(final_doc)
        if header_issues:
            stats["header_issues"] = header_issues

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
    
    def _paragraph_has_flowchart(self, paragraph) -> bool:
        """判断段落是否包含流程图（由多个形状组成的流程图）"""
        try:
            para_xml = str(paragraph._element.xml)
            
            # 方法1: 检测 Word Processing Shapes (wps:wsp) - 现代 Word 文档中的形状
            # 流程图通常包含多个形状，如果段落中有多个 wps:wsp 元素，可能是流程图
            if 'wps:wsp' in para_xml:
                # 计算形状数量
                shape_count = para_xml.count('wps:wsp')
                # 如果包含多个形状（至少2个），可能是流程图
                if shape_count >= 2:
                    return True
            
            # 方法2: 检测 VML Shapes (v:shape) - 旧版 Word 文档中的形状
            # 排除水印（包含 textpath 的 v:shape 通常是水印）
            vml_shapes = []
            if 'v:shape' in para_xml.lower():
                # 检查是否有多个非水印的形状
                # 简单判断：如果包含 v:shape 但不包含 textpath，可能是流程图的一部分
                vml_count = para_xml.lower().count('v:shape')
                textpath_count = para_xml.lower().count('textpath')
                # 如果有形状且不是水印，可能是流程图
                if vml_count > textpath_count and vml_count >= 2:
                    return True
            
            # 方法3: 检测 SmartArt 流程图
            # SmartArt 在 XML 中通常包含 'smartart' 或特定的命名空间
            if 'smartart' in para_xml.lower() or 'dgm:' in para_xml:
                return True
            
            # 方法4: 检测 drawing 元素中的多个形状
            # 使用 xpath 查找 drawing 元素，检查是否包含多个形状
            try:
                from docx.oxml.ns import qn
                drawings = paragraph._element.xpath('.//w:drawing', namespaces={
                    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
                    'wps': 'http://schemas.microsoft.com/office/word/2010/wordprocessingShape',
                    'v': 'urn:schemas-microsoft-com:vml'
                })
                if drawings:
                    # 检查每个 drawing 元素中是否包含多个形状
                    for drawing in drawings:
                        drawing_xml = str(drawing.xml)
                        # 计算形状数量
                        wps_count = drawing_xml.count('wps:wsp')
                        vml_count = drawing_xml.lower().count('v:shape') - drawing_xml.lower().count('textpath')
                        # 如果包含多个形状，可能是流程图
                        if wps_count >= 2 or (vml_count >= 2 and vml_count > 0):
                            return True
            except:
                pass
            
            # 方法5: 检测段落中的 runs 是否包含形状
            try:
                shape_count = 0
                for run in paragraph.runs:
                    if not hasattr(run, 'element'):
                        continue
                    run_xml = str(run.element.xml)
                    # 排除水印
                    if 'v:shape' in run_xml.lower() and 'textpath' in run_xml.lower():
                        continue
                    # 检查是否包含形状
                    if 'wps:wsp' in run_xml or ('v:shape' in run_xml.lower() and 'textpath' not in run_xml.lower()):
                        shape_count += 1
                # 如果包含多个形状，可能是流程图
                if shape_count >= 2:
                    return True
            except:
                pass
            
        except:
            pass
        
        return False

    def _apply_page_settings(self, document: Document) -> None:
        """应用页面设置（页边距等），但不修改任何页边距，保持文档原始页边距"""
        # 不修改任何 section 的页边距，保持文档原始页边距
        # 封面页和后续页面的页边距都不修改
        pass
    
    def _check_header(self, document: Document) -> list:
        """检测页眉是否存在，如果不存在则提示添加"""
        issues = []
        
        # 检查所有节的页眉
        has_header = False
        for section in document.sections:
            header = section.header
            # 检查页眉是否有内容
            for para in header.paragraphs:
                if para.text and para.text.strip():
                    has_header = True
                    break
            if has_header:
                break
        
        # 如果没有任何页眉，添加提示
        if not has_header:
            issues.append({
                "type": "missing_header",
                "severity": "warning",
                "message": "文档缺少页眉",
                "suggestion": f"请在文档中添加页眉，建议内容：{HEADER_SETTINGS['text']}"
            })
        
        return issues
    
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
        
        # 优先检测特殊标题：摘要、ABSTRACT、目录、绪论、概述
        # 这些标题需要设置为黑体、三号字、加粗、居中
        if text == "摘要" or text.startswith("摘要"):
            return "abstract_title"
        if text == "ABSTRACT" or text.startswith("ABSTRACT"):
            return "abstract_title_en"
        if text == "目录" or text.startswith("目录") or text == "Contents" or text.startswith("Contents"):
            return "toc_title"
        if text == "绪论" or text == "概述" or text.startswith("1 绪论") or text.startswith("1 概述"):
            # 如果是独立的"绪论"或"概述"，且段落较短，则认为是标题
            if len(text) < 50:
                return "title_level_1"
        
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
        
        # 章节标题检测：必须是独立的、较短的段落
        # 避免将正文中的"第二章的方案"等误识别为标题
        chapter_match = re.match(r"^(第[一二三四五六七八九十\d]+章|第\d+章|Chapter\s+\d+)([，,。.：:；;]?)$", text)
        if chapter_match:
            # 如果匹配到章节标题，且段落较短（标题通常是独立的短段落）
            # 或者后面只有标点符号，则认为是标题
            remaining_text = text[len(chapter_match.group(0)):].strip()
            if len(text) < 50 or (len(remaining_text) == 0 or remaining_text in ["，", "。", "：", "；", ",", ".", ":", ";"]):
                return "title_level_1"
        
        # 二级标题检测：必须是独立的、较短的段落
        # 标题格式：数字.数字 或 数字.数字 后跟标点符号，且后面没有其他文字内容
        section_match = re.match(r"^(\d+\.\d+|第[一二三四五六七八九十\d]+节)([，,。.：:；;]?)$", text)
        if section_match:
            remaining_text = text[len(section_match.group(0)):].strip()
            # 只有当剩余文本为空或只有标点符号时，才认为是标题
            # 如果后面还有文字内容，则不是标题（是正文中的编号引用）
            if len(remaining_text) == 0 or remaining_text in ["，", "。", "：", "；", ",", ".", ":", ";"]:
                return "title_level_2"
        
        # 三级标题检测：必须是独立的、较短的段落
        # 标题格式：数字.数字.数字 或 数字.数字.数字 后跟标点符号，且后面没有其他文字内容
        subsection_match = re.match(r"^(\d+\.\d+\.\d+)([，,。.：:；;]?)$", text)
        if subsection_match:
            remaining_text = text[len(subsection_match.group(0)):].strip()
            # 只有当剩余文本为空或只有标点符号时，才认为是标题
            # 如果后面还有文字内容（如"3.2.4 12864 液晶显示屏"），则不是标题，是正文
            if len(remaining_text) == 0 or remaining_text in ["，", "。", "：", "；", ",", ".", ":", ";"]:
                return "title_level_3"
        
        # 默认返回正文样式
        return DEFAULT_STYLE

    def _find_cover_end_index(self, document: Document) -> int:
        """找到封面结束的段落索引，跳过封面部分"""
        # 封面的结束标志：通常是"摘要"、"目录"、"引言"、"第一章"等
        cover_end_keywords = [
            "摘要", "ABSTRACT", "目录", "Contents", 
            "引言", "绪论", "前言", "第一章", "第1章", "Chapter 1",
            "1 引言", "1 绪论", "1 概述"
        ]
        
        # 从前往后查找，找到第一个封面结束标志
        for idx, paragraph in enumerate(document.paragraphs):
            para_text = paragraph.text.strip() if paragraph.text else ""
            if not para_text:
                continue
            
            # 检查是否是封面结束标志
            for keyword in cover_end_keywords:
                if para_text.startswith(keyword) or keyword in para_text:
                    # 确保不是封面中的文字（封面通常较短）
                    if len(para_text) < 200:  # 封面中的文字通常较短
                        return idx
        
        # 如果找不到，跳过前20个段落（通常是封面）
        return min(20, len(document.paragraphs) - 1)
    
    def _find_section_ranges(self, document: Document) -> Dict[str, Tuple[int, int]]:
        """
        识别文档各个部分的段落范围
        返回: {
            "cover": (0, cover_end),
            "abstract_zh": (start, end),  # 中文摘要
            "abstract_en": (start, end),  # 英文摘要
            "toc": (start, end),  # 目录
            "body": (start, end),  # 正文
        }
        """
        ranges = {}
        cover_end = self._find_cover_end_index(document)
        ranges["cover"] = (0, cover_end)
        
        abstract_zh_start = None
        abstract_zh_end = None
        abstract_en_start = None
        abstract_en_end = None
        toc_start = None
        toc_end = None
        body_start = None
        
        # 查找中文摘要
        for idx in range(cover_end, len(document.paragraphs)):
            para_text = document.paragraphs[idx].text.strip() if document.paragraphs[idx].text else ""
            if para_text.startswith("摘要") and abstract_zh_start is None:
                abstract_zh_start = idx
            elif abstract_zh_start is not None and (para_text.startswith("关键词") or para_text.startswith("ABSTRACT") or para_text.startswith("目录")):
                abstract_zh_end = idx
                break
        
        # 如果没找到结束标志，假设摘要到"ABSTRACT"或"目录"之前
        if abstract_zh_start is not None and abstract_zh_end is None:
            for idx in range(abstract_zh_start + 1, len(document.paragraphs)):
                para_text = document.paragraphs[idx].text.strip() if document.paragraphs[idx].text else ""
                if para_text.startswith("ABSTRACT") or para_text.startswith("目录"):
                    abstract_zh_end = idx
                    break
        
        # 查找英文摘要
        for idx in range(cover_end, len(document.paragraphs)):
            para_text = document.paragraphs[idx].text.strip() if document.paragraphs[idx].text else ""
            if para_text.startswith("ABSTRACT") and abstract_en_start is None:
                abstract_en_start = idx
            elif abstract_en_start is not None and (para_text.startswith("Keywords") or para_text.startswith("目录") or para_text.startswith("Contents") or para_text.startswith("第一章") or para_text.startswith("第1章")):
                abstract_en_end = idx
                break
        
        # 查找目录
        for idx in range(cover_end, len(document.paragraphs)):
            para_text = document.paragraphs[idx].text.strip() if document.paragraphs[idx].text else ""
            if (para_text.startswith("目录") or para_text.startswith("Contents")) and toc_start is None:
                toc_start = idx
            elif toc_start is not None and (para_text.startswith("第一章") or para_text.startswith("第1章") or para_text.startswith("Chapter 1") or para_text.startswith("1 引言") or para_text.startswith("1 绪论")):
                toc_end = idx
                break
        
        # 查找正文开始（从"绪论"或"概述"开始）
        for idx in range(cover_end, len(document.paragraphs)):
            para_text = document.paragraphs[idx].text.strip() if document.paragraphs[idx].text else ""
            if (para_text.startswith("第一章") or para_text.startswith("第1章") or para_text.startswith("Chapter 1") or 
                para_text.startswith("1 引言") or para_text.startswith("1 绪论") or para_text.startswith("1 概述") or
                para_text == "绪论" or para_text == "概述" or para_text.startswith("绪论") or para_text.startswith("概述")):
                body_start = idx
                break
        
        if abstract_zh_start is not None:
            ranges["abstract_zh"] = (abstract_zh_start, abstract_zh_end if abstract_zh_end else (abstract_en_start if abstract_en_start else (toc_start if toc_start else len(document.paragraphs))))
        if abstract_en_start is not None:
            ranges["abstract_en"] = (abstract_en_start, abstract_en_end if abstract_en_end else (toc_start if toc_start else (body_start if body_start else len(document.paragraphs))))
        if toc_start is not None:
            ranges["toc"] = (toc_start, toc_end if toc_end else (body_start if body_start else len(document.paragraphs)))
        if body_start is not None:
            ranges["body"] = (body_start, len(document.paragraphs))
        
        return ranges

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
        
        # 找到封面结束位置，跳过封面部分
        cover_end_idx = self._find_cover_end_index(document)
        
        # 识别各个部分的段落范围
        section_ranges = self._find_section_ranges(document)

        for idx, paragraph in enumerate(document.paragraphs):
            # 跳过封面部分，不修改封面内容
            if idx < cover_end_idx:
                continue
            style_name = paragraph.style.name if paragraph.style else None
            rule = None
            applied_rule_name = None
            paragraph_text = paragraph.text.strip() if paragraph.text else ""
            
            # 判断当前段落属于哪个部分
            current_section = None
            if "abstract_zh" in section_ranges:
                start, end = section_ranges["abstract_zh"]
                if start <= idx < end:
                    current_section = "abstract_zh"
            if current_section is None and "abstract_en" in section_ranges:
                start, end = section_ranges["abstract_en"]
                if start <= idx < end:
                    current_section = "abstract_en"
            if current_section is None and "toc" in section_ranges:
                start, end = section_ranges["toc"]
                if start <= idx < end:
                    current_section = "toc"
            if current_section is None and "body" in section_ranges:
                start, end = section_ranges["body"]
                if start <= idx < end:
                    current_section = "body"
            
            # 根据当前部分应用特定格式规则
            # 处理中文摘要部分
            if current_section == "abstract_zh":
                # 摘要标题
                if paragraph_text.startswith("摘要"):
                    if "abstract_title" in rules:
                        rule = rules["abstract_title"].copy()
                        applied_rule_name = "abstract_title"
                    else:
                        rule = FONT_STANDARDS.get("abstract_title", {}).copy()
                        applied_rule_name = "abstract_title"
                    # 强制确保摘要标题居中对齐
                    rule["alignment"] = "center"
                # 关键词标签
                elif paragraph_text.startswith("关键词"):
                    if "keywords_label" in rules:
                        rule = rules["keywords_label"].copy()
                        applied_rule_name = "keywords_label"
                    else:
                        rule = FONT_STANDARDS.get("keywords_label", {}).copy()
                        applied_rule_name = "keywords_label"
                # 摘要正文内容
                else:
                    if "abstract_content" in rules:
                        rule = rules["abstract_content"].copy()
                        applied_rule_name = "abstract_content"
                    else:
                        rule = FONT_STANDARDS.get("abstract_content", {}).copy()
                        applied_rule_name = "abstract_content"
                    # 确保摘要正文：宋体小四（12pt），行距20磅
                    rule["font_name"] = "宋体"
                    rule["font_size"] = 12
                    rule["line_spacing"] = 20
            
            # 处理英文摘要部分
            elif current_section == "abstract_en":
                # 英文摘要标题
                if paragraph_text.startswith("ABSTRACT"):
                    if "abstract_title_en" in rules:
                        rule = rules["abstract_title_en"].copy()
                        applied_rule_name = "abstract_title_en"
                    else:
                        rule = FONT_STANDARDS.get("abstract_title_en", {}).copy()
                        applied_rule_name = "abstract_title_en"
                    # 强制确保ABSTRACT标题居中对齐
                    rule["alignment"] = "center"
                # 关键词标签
                elif paragraph_text.startswith("Keywords") or paragraph_text.startswith("Key words"):
                    if "keywords_label_en" in rules:
                        rule = rules["keywords_label_en"].copy()
                        applied_rule_name = "keywords_label_en"
                    else:
                        rule = FONT_STANDARDS.get("keywords_label_en", {}).copy()
                        applied_rule_name = "keywords_label_en"
                # 英文摘要正文内容
                else:
                    if "abstract_content_en" in rules:
                        rule = rules["abstract_content_en"].copy()
                        applied_rule_name = "abstract_content_en"
                    else:
                        rule = FONT_STANDARDS.get("abstract_content_en", {}).copy()
                        applied_rule_name = "abstract_content_en"
                    # 确保英文摘要正文：Times New Roman小四（12pt）
                    rule["font_name"] = "Times New Roman"
                    rule["font_size"] = 12
            
            # 处理目录部分
            elif current_section == "toc":
                # 目录标题（支持中间最多5个空格的变体，如"目 录"、"目  录"、"目    录"等）
                # 检查是否包含"目"和"录"（允许中间最多5个空格）
                is_toc_title_para = False
                if "目" in paragraph_text and "录" in paragraph_text:
                    # 去除空格和标点后检查是否等于"目录"
                    cleaned_toc_text = re.sub(r'[\s\u3000：:，,。.；;！!？?、]', '', paragraph_text)
                    if cleaned_toc_text == "目录":
                        # 检查"目"和"录"之间的字符是否只有空格（最多5个）
                        mu_pos = paragraph_text.find("目")
                        lu_pos = paragraph_text.find("录")
                        if mu_pos >= 0 and lu_pos > mu_pos:
                            between_text = paragraph_text[mu_pos + 1:lu_pos]
                            # 如果中间只有空格（最多5个），或者是空字符串，认为是目录标题
                            if len(between_text) <= 5 and all(c in ' \t\u3000' for c in between_text):
                                is_toc_title_para = True
                            elif len(between_text) == 0:
                                is_toc_title_para = True
                elif paragraph_text.startswith("Contents") or paragraph_text.startswith("contents"):
                    cleaned_toc_text = re.sub(r'[\s\u3000：:，,。.；;！!？?、]', '', paragraph_text).upper()
                    if cleaned_toc_text == "CONTENTS":
                        is_toc_title_para = True
                
                if is_toc_title_para:
                    if "toc_title" in rules:
                        rule = rules["toc_title"].copy()
                        applied_rule_name = "toc_title"
                    else:
                        rule = FONT_STANDARDS.get("toc_title", {}).copy()
                        applied_rule_name = "toc_title"
                    # 强制确保目录标题居中对齐
                    rule["alignment"] = "center"
                # 目录内容
                else:
                    if "toc_content" in rules:
                        rule = rules["toc_content"].copy()
                        applied_rule_name = "toc_content"
                    else:
                        rule = FONT_STANDARDS.get("toc_content", {}).copy()
                        applied_rule_name = "toc_content"
                    # 确保目录内容：宋体小四（12pt），行距20磅
                    rule["font_name"] = "宋体"
                    rule["font_size"] = 12
                    rule["line_spacing"] = 20
            
            # 处理正文部分（使用原有逻辑）
            else:
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
                # 判断是否是标题
                # 优先使用检测到的样式来判断
                is_heading = False
                if applied_rule_name:
                    # 如果应用的规则是标题样式，则认为是标题
                    if applied_rule_name in ["title_level_1", "title_level_2", "title_level_3", "abstract_title", "toc_title", "reference_title", "acknowledgment_title"]:
                        is_heading = True
                    # 或者检查样式名称
                    elif style_name and ("标题" in style_name.lower() or "heading" in style_name.lower()):
                        is_heading = True
                    # 或者检查段落内容特征（居中对齐的短文本，或"绪论"、"概述"等）
                    elif paragraph.alignment == WD_PARAGRAPH_ALIGNMENT.CENTER and len(paragraph_text) < 50:
                        is_heading = True
                    # 或者检查是否是"绪论"、"概述"等标题
                    elif paragraph_text == "绪论" or paragraph_text == "概述" or paragraph_text.startswith("1 绪论") or paragraph_text.startswith("1 概述"):
                        is_heading = True
                    # 或者检查是否以数字开头且较短（但需要更严格的判断，避免误判正文）
                    elif paragraph_text and paragraph_text[0].isdigit() and len(paragraph_text) < 30:
                        # 更严格的判断：只有纯数字编号格式（如"3.2.4"、"3.2"等）才认为是标题
                        # 如果包含其他文字内容，则不是标题
                        if re.match(r'^(\d+\.\d+\.\d+|\d+\.\d+|\d+)([，,。.：:；;]?)$', paragraph_text):
                            is_heading = True
                # 如果没有应用规则名称，使用备用判断逻辑
                if not is_heading:
                    is_heading = (
                        (style_name and ("标题" in style_name.lower() or "heading" in style_name.lower())) or
                        (paragraph.alignment == WD_PARAGRAPH_ALIGNMENT.CENTER and len(paragraph_text) < 50) or
                        # 更严格的判断：只有纯数字编号格式才认为是标题
                        (paragraph_text and paragraph_text[0].isdigit() and len(paragraph_text) < 30 and 
                         re.match(r'^(\d+\.\d+\.\d+|\d+\.\d+|\d+)([，,。.：:；;]?)$', paragraph_text)) or
                        (paragraph_text == "绪论" or paragraph_text == "概述" or paragraph_text.startswith("1 绪论") or paragraph_text.startswith("1 概述"))
                    )
                
                # 判断是否包含图片、公式或流程图
                has_image_or_equation = self._paragraph_has_image_or_equation(paragraph)
                has_flowchart = self._paragraph_has_flowchart(paragraph)
                
                # 对于标题，移除行距设置，保持标题的原始行距
                if is_heading:
                    rule.pop("line_spacing", None)
                
                # 对于包含图片、公式或流程图的段落，移除行距设置，避免被压缩看不见
                if has_image_or_equation or has_flowchart:
                    # 移除行距设置，保持图片/流程图段落的原始行距
                    rule.pop("line_spacing", None)
                    # 也移除首行缩进，图片/流程图段落通常不需要缩进
                    rule.pop("first_line_indent", None)
                
                # 对于正文段落（非标题、非图片、非公式、非流程图），如果使用的是标准默认样式，确保格式正确
                if not is_heading and not has_image_or_equation and not has_flowchart:
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
                
                # 再次确认：如果段落包含流程图，确保行距不被修改
                # 流程图视为图片，不修改行距
                if has_flowchart:
                    # 确保规则中不包含行距设置
                    rule.pop("line_spacing", None)
                    rule.pop("first_line_indent", None)
                
                # 应用规则
                docx_format_utils.apply_paragraph_rule(paragraph, rule)
                
                # 最终检查：确保"摘要"、"ABSTRACT"和"目录"标题始终居中（防止被其他逻辑覆盖）
                para_text_check = paragraph.text.strip() if paragraph.text else ""
                if para_text_check:
                    # 去除所有空格、标点符号和空白字符，只保留字母和汉字
                    cleaned_text_check = re.sub(r'[\s\u3000：:，,。.；;！!？?、]', '', para_text_check)
                    cleaned_text_check_upper = cleaned_text_check.upper()
                    
                    is_abstract_title_check = False
                    is_toc_title_check = False
                    # 检查去除空格和标点后是否等于"摘要"、"ABSTRACT"或"目录"
                    if cleaned_text_check == "摘要" or cleaned_text_check_upper == "ABSTRACT":
                        is_abstract_title_check = True
                    elif cleaned_text_check == "目录" or cleaned_text_check_upper == "CONTENTS":
                        is_toc_title_check = True
                    # 如果去除空格后的文本较短，也检查是否包含这些关键词
                    elif len(cleaned_text_check) <= 15:  # 基于去除空格后的长度
                        # 检查是否包含"摘"和"要"（允许中间有空格或其他字符）
                        if "摘" in para_text_check and "要" in para_text_check:
                            if cleaned_text_check == "摘要":
                                is_abstract_title_check = True
                        # 检查是否包含"目"和"录"（允许中间最多5个空格）
                        elif "目" in para_text_check and "录" in para_text_check:
                            # 检查"目"和"录"之间的字符是否只有空格（最多5个）
                            mu_pos = para_text_check.find("目")
                            lu_pos = para_text_check.find("录")
                            if mu_pos >= 0 and lu_pos > mu_pos:
                                between_text = para_text_check[mu_pos + 1:lu_pos]
                                # 如果中间只有空格（最多5个），或者是空字符串，认为是目录标题
                                if len(between_text) <= 5 and all(c in ' \t\u3000' for c in between_text):
                                    if cleaned_text_check == "目录":
                                        is_toc_title_check = True
                                elif len(between_text) == 0:
                                    if cleaned_text_check == "目录":
                                        is_toc_title_check = True
                        # 检查是否包含"ABSTRACT"（不区分大小写）
                        elif "ABSTRACT" in cleaned_text_check_upper or "abstract" in para_text_check.lower():
                            if cleaned_text_check_upper == "ABSTRACT":
                                is_abstract_title_check = True
                        # 检查是否包含"Contents"（不区分大小写）
                        elif "CONTENTS" in cleaned_text_check_upper or "contents" in para_text_check.lower():
                            if cleaned_text_check_upper == "CONTENTS":
                                is_toc_title_check = True
                    
                    if is_abstract_title_check or is_toc_title_check:
                        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                
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
                    # 或者以"流程图"开头（如"流程图1-1"、"流程图2.1"等）
                    if check_text and len(check_text) < 100:
                        # 检查是否包含图号格式（图X-X、图X.X等）
                        if (check_text.startswith("图") and (re.search(r'图\s*\d+[\.\-]\d+', check_text) or re.search(r'图\s*\d+', check_text))):
                            is_caption = True
                            caption_paragraph_idx = check_idx
                            break
                        # 检查是否是流程图标题（流程图X-X、流程图X.X等）
                        elif (check_text.startswith("流程图") and (re.search(r'流程图\s*\d+[\.\-]\d+', check_text) or re.search(r'流程图\s*\d+', check_text))):
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
        """检测参考文献引用标注，检查正文中是否有引用标注，返回缺失引用的问题列表
        同时标记未被引用的参考文献（标红并添加提示）
        """
        issues = []
        
        # 1. 找到参考文献部分的起始位置（从后往前查找，找到最后一个"参考文献"标题）
        reference_start_idx = None
        reference_section_text = ""
        
        # 从后往前查找，找到最后一个"参考文献"标题（避免匹配到目录中的"参考文献"）
        for idx in range(len(document.paragraphs) - 1, -1, -1):
            paragraph = document.paragraphs[idx]
            para_text = paragraph.text.strip() if paragraph.text else ""
            # 检测参考文献标题（可能包含"参考文献"、"References"、"参考书目"等）
            if re.search(r'参考(文献|书目)', para_text) or para_text.lower().startswith('references') or para_text.lower().startswith('bibliography'):
                # 确保是标题格式（通常较短，且可能是居中或单独一行）
                if len(para_text) < 50 or para_text in ["参考文献", "References", "参考书目", "Bibliography"]:
                    reference_start_idx = idx
                    # 收集参考文献部分的内容（最多收集100个段落）
                    ref_paragraphs = []
                    for i in range(idx, min(idx + 100, len(document.paragraphs))):
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
            # 获取原始文本，不strip，以便检查开头格式
            para_text_raw = para.text if para.text else ""
            para_text = para_text_raw.strip()
            
            # 如果遇到新的章节标题，停止收集
            if len(para_text) < 50 and (para_text.startswith("第") or para_text.startswith("Chapter") or 
                                         para_text.startswith("附录") or para_text.startswith("Appendix")):
                break
            
            # 排除章节标题（如"1.2"、"1.2.1"、"第一章"等）
            is_section_title = False
            # 检查是否是章节标题格式
            if re.match(r'^\d+\.\d+', para_text) or re.match(r'^\d+\.\d+\.\d+', para_text):  # 1.2 或 1.2.1 格式
                # 如果段落较短（通常是标题），且不包含参考文献特征，则不是参考文献
                if len(para_text) < 100:
                    is_section_title = True
            # 检查是否是章节标题（如"第一章"、"第1章"等）
            if re.match(r'^第[一二三四五六七八九十\d]+章|^第\d+章|^Chapter\s+\d+', para_text):
                is_section_title = True
            # 检查是否是标题样式
            if para.style and ("标题" in para.style.name or "heading" in para.style.name.lower()):
                is_section_title = True
            
            # 如果确定是章节标题，跳过
            if is_section_title:
                continue
            
            # 检查是否符合参考文献格式
            is_reference = False
            ref_number = None
            
            # 首先尝试从段落开头提取编号（更准确）
            # 检查常见的参考文献编号格式
            # 注意：参考文献格式可能是 [1]  作者名...（[1]后面有多个空格）
            # 改进：使用 search 而不是 match，允许前面有少量空格
            number_match = None
            
            # 检查 [数字] 格式（优先检查，因为这是最常见的格式）
            # 支持半角方括号 [数字] 和全角方括号 ［数字］
            # 使用 search 查找，但检查是否在段落开头（允许前面有少量空格）
            bracket_match = None
            # 先尝试半角方括号
            bracket_match = re.search(r'\[(\d+)\]', para_text)
            if not bracket_match:
                # 如果没找到半角方括号，尝试全角方括号
                bracket_match = re.search(r'［(\d+)］', para_text)
            
            if bracket_match:
                # 检查 [数字] 或 ［数字］ 是否在段落开头（允许前面有少量空格）
                bracket_pos = para_text.find(bracket_match.group(0))
                # 改进：允许 [数字] 在段落开头10个字符内，提高容错性
                if bracket_pos <= 10:  # [数字] 在段落开头10个字符内
                    # 进一步验证：确保 [数字] 后面有内容（不是单独的 [2]）
                    bracket_end = bracket_pos + len(bracket_match.group(0))
                    remaining_after_bracket = para_text[bracket_end:].strip()
                    # 如果 [数字] 后面有内容（至少5个字符），认为是参考文献
                    if len(remaining_after_bracket) >= 5:
                        is_reference = True
                        ref_number = int(bracket_match.group(1))
                        bracket_type = "半角" if "[" in bracket_match.group(0) else "全角"
                        print(f"[DocumentService] 通过 {bracket_type}方括号 [数字] 格式识别参考文献: {ref_number} (位置: {bracket_pos}, 后续文本长度: {len(remaining_after_bracket)})")
            
            # 如果还没有识别，继续检查其他格式
            if not is_reference:
                if re.match(r'^\d+\.', para_text):  # 1. 格式
                    number_match = re.search(r'^\d+', para_text)
                    if number_match:
                        is_reference = True
                        ref_number = int(number_match.group())
                        print(f"[DocumentService] 通过 数字. 格式识别参考文献: {ref_number}")
                elif re.match(r'^\(\d+\)', para_text):  # (1) 格式
                    number_match = re.search(r'\d+', para_text)
                    if number_match:
                        is_reference = True
                        ref_number = int(number_match.group())
                        print(f"[DocumentService] 通过 (数字) 格式识别参考文献: {ref_number}")
                else:
                    # 尝试其他格式：可能是空格分隔的编号，如 "1 作者名..."
                    number_match = re.match(r'^(\d+)\s+', para_text)
                    if number_match:
                        # 检查后面是否有参考文献特征
                        remaining_text = para_text[len(number_match.group(0)):].strip()
                        # 如果后面有作者名、年份等特征，可能是参考文献
                        has_year = re.search(r'\d{4}', remaining_text)
                        has_author = re.search(r'[，,]\s*\d{4}|[A-Z][a-z]+\s+[A-Z]', remaining_text)
                        if has_year or (has_author and len(remaining_text) > 20):
                            is_reference = True
                            ref_number = int(number_match.group(1))
                            print(f"[DocumentService] 通过 数字空格 格式识别参考文献: {ref_number}")
            
            # 如果还没有识别为参考文献，但段落较长且包含作者、年份等信息，也可能是参考文献
            # 但必须排除章节标题
            if not is_reference and len(para_text) > 20:
                # 检查是否包含常见的参考文献特征（作者名、年份、期刊名等）
                # 参考文献通常包含：作者、年份、期刊名、出版社等
                # 改进：支持更多年份格式（中文和英文）
                has_author_pattern_cn = re.search(r'[，,]\s*\d{4}[，,]', para_text)  # 中文格式：年份前后有逗号
                has_author_pattern_en = re.search(r'[A-Z][a-z]+\.[A-Z]', para_text)  # 英文格式：作者名（如 A. I.）
                has_journal_pattern = re.search(r'\[[JC]\]|期刊|学报|Journal|Conference', para_text, re.IGNORECASE)  # 期刊标识 [J] 或 [C]
                has_publisher_pattern = re.search(r'出版社|Press|Publishing', para_text, re.IGNORECASE)  # 出版社
                has_year = re.search(r'\d{4}', para_text)  # 年份（4位数字）
                
                # 改进识别逻辑：支持英文参考文献格式
                # 参考文献必须同时满足：有年份，且（有作者模式或期刊标识或出版社），且段落较长
                # 或者：有 [数字] 格式在开头，且有年份和期刊标识
                # 支持半角和全角方括号
                has_bracket_at_start = False
                bracket_match_at_start = re.search(r'\[(\d+)\]', para_text)
                if not bracket_match_at_start:
                    bracket_match_at_start = re.search(r'［(\d+)］', para_text)
                if bracket_match_at_start:
                    bracket_pos = para_text.find(bracket_match_at_start.group(0))
                    if bracket_pos <= 10:  # [数字] 在段落开头10个字符内
                        has_bracket_at_start = True
                
                # 如果段落开头有 [数字] 格式，且有年份和期刊标识，认为是参考文献
                if has_bracket_at_start and has_year and has_journal_pattern:
                    is_reference = True
                    ref_number = int(bracket_match_at_start.group(1))
                    print(f"[DocumentService] 通过 [数字]+年份+期刊标识 识别参考文献: {ref_number}")
                # 或者满足传统的识别条件
                elif has_year and (has_author_pattern_cn or has_author_pattern_en or has_journal_pattern or has_publisher_pattern) and len(para_text) > 30:
                    is_reference = True
                    # 尝试从段落开头提取编号（更宽松的匹配）
                    # 可能格式：数字开头，后面跟空格或标点，或者 [数字] 格式
                    # 先尝试 [数字] 格式（支持半角和全角方括号）
                    bracket_match = re.search(r'\[(\d+)\]', para_text)
                    if not bracket_match:
                        bracket_match = re.search(r'［(\d+)］', para_text)
                    if bracket_match:
                        bracket_pos = para_text.find(bracket_match.group(0))
                        if bracket_pos <= 10:  # 在段落开头10个字符内
                            ref_number = int(bracket_match.group(1))
                    else:
                        # 尝试数字开头格式
                        number_match = re.search(r'^(\d+)', para_text)
                        if number_match:
                            ref_number = int(number_match.group(1))
                        else:
                            # 如果没有找到编号，使用序号（但这种情况应该很少）
                            ref_number = len(reference_items) + 1
                    print(f"[DocumentService] 通过内容特征识别参考文献: {ref_number} (年份: {has_year is not None}, 期刊: {has_journal_pattern is not None}, 作者: {has_author_pattern_cn is not None or has_author_pattern_en is not None})")
            
            if is_reference:
                # 如果还是没有编号，尝试从段落开头提取（更宽松的匹配）
                if ref_number is None:
                    # 尝试匹配：数字开头，后面跟空格、点、方括号、圆括号等
                    number_match = re.match(r'^(\d+)', para_text)
                    if number_match:
                        ref_number = int(number_match.group(1))
                    else:
                        # 如果还是没有，使用序号（确保每个参考文献都有编号）
                        ref_number = len(reference_items) + 1
                        print(f"[DocumentService] 警告：参考文献没有明确编号，使用序号 {ref_number}: {para_text[:50]}")
                
                reference_items.append({
                    "index": ref_number,
                    "number": ref_number,  # 确保编号一致
                    "text": para_text[:100],  # 只保存前100个字符
                    "paragraph_index": idx,
                    "paragraph": para,  # 保存段落对象，用于后续修改
                })
                print(f"[DocumentService] 识别参考文献 {ref_number}: {para_text[:50]}")
        
        # 如果没有找到参考文献条目，提示
        if not reference_items:
            issues.append({
                "type": "no_reference_items",
                "message": "参考文献部分为空或格式不正确",
                "suggestion": "请确保参考文献部分包含编号的参考文献条目"
            })
            return issues
        
        # 3. 检查正文中是否有引用标注，并找出被引用的参考文献编号
        # 正文部分：从封面结束到参考文献部分之前
        body_start_idx = self._find_body_start_index(document)
        print(f"[DocumentService] 正文开始位置: {body_start_idx}, 参考文献开始位置: {reference_start_idx}")
        
        body_text = ""
        body_paragraphs = []
        # 记录每个引用所在的段落索引（用于计算页码）
        citation_locations = {}  # {ref_number: [paragraph_index1, paragraph_index2, ...]}
        
        # 从正文开始到参考文献之前的所有段落（包括短段落，因为引用可能在图片说明等短段落中）
        # 改进：确保能正确提取段落文本，包括所有 runs 的文本
        for idx in range(body_start_idx, reference_start_idx):
            para = document.paragraphs[idx]
            # 方法1：使用 para.text（这是最可靠的方法，会自动合并所有 runs）
            para_text = para.text.strip() if para.text else ""
            
            # 方法2：如果 para.text 为空，尝试手动合并所有 runs 的文本
            if not para_text:
                para_text = "".join([run.text for run in para.runs if run.text]).strip()
            
            # 方法3：如果还是为空，尝试从 XML 中提取文本（最后的手段）
            if not para_text:
                try:
                    para_xml = str(para._element.xml)
                    # 提取所有文本节点
                    import xml.etree.ElementTree as ET
                    root = ET.fromstring(para_xml)
                    texts = []
                    for elem in root.iter():
                        if elem.text:
                            texts.append(elem.text)
                    para_text = "".join(texts).strip()
                except:
                    pass
            
            # 检查所有段落（包括短段落），因为引用可能在图片说明、表格说明等短段落中
            if len(para_text) > 0:  # 只要有内容就检查
                body_text += para_text + " "
                body_paragraphs.append((idx, para_text))
                
                # 在当前段落中检测引用，并记录段落索引
                # 检测半角方括号 [数字]
                for match in re.finditer(r'\[(\d+)\]', para_text):
                    try:
                        num = int(match.group(1))
                        if 1 <= num <= 1000:
                            if num not in citation_locations:
                                citation_locations[num] = []
                            citation_locations[num].append(idx)
                    except ValueError:
                        pass
                
                # 检测全角方括号 ［数字］
                for match in re.finditer(r'［(\d+)］', para_text):
                    try:
                        num = int(match.group(1))
                        if 1 <= num <= 1000:
                            if num not in citation_locations:
                                citation_locations[num] = []
                            citation_locations[num].append(idx)
                    except ValueError:
                        pass
                
                # 检测多个编号格式 [1,2,3] 或 [1-5]
                for match in re.finditer(r'\[(\d+(?:[,\s]+\d+)+)\]', para_text):
                    try:
                        numbers_str = match.group(1)
                        numbers = re.findall(r'\d+', numbers_str)
                        for num_str in numbers:
                            num = int(num_str.strip())
                            if 1 <= num <= 1000:
                                if num not in citation_locations:
                                    citation_locations[num] = []
                                citation_locations[num].append(idx)
                    except ValueError:
                        pass
                
                # 检测全角方括号多个编号格式 ［1,2,3］
                for match in re.finditer(r'［(\d+(?:[,\s]+\d+)+)］', para_text):
                    try:
                        numbers_str = match.group(1)
                        numbers = re.findall(r'\d+', numbers_str)
                        for num_str in numbers:
                            num = int(num_str.strip())
                            if 1 <= num <= 1000:
                                if num not in citation_locations:
                                    citation_locations[num] = []
                                citation_locations[num].append(idx)
                    except ValueError:
                        pass
                
                # 检测范围格式 [1-5]
                for match in re.finditer(r'\[(\d+)[\-\s]+(\d+)\]', para_text):
                    try:
                        start = int(match.group(1))
                        end = int(match.group(2))
                        if 1 <= start <= end <= 1000:
                            for num in range(start, end + 1):
                                if num not in citation_locations:
                                    citation_locations[num] = []
                                citation_locations[num].append(idx)
                    except ValueError:
                        pass
                
                # 调试：如果段落包含 [4] 或 [5]，打印详细信息
                if '[4]' in para_text or '[5]' in para_text:
                    print(f"[DocumentService] 调试：段落 {idx} 包含引用")
                    print(f"[DocumentService] 段落文本: {para_text}")
                    print(f"[DocumentService] para.text: {para.text if para.text else 'None'}")
                    print(f"[DocumentService] runs数量: {len(para.runs)}")
                    for run_idx, run in enumerate(para.runs):
                        print(f"[DocumentService]   run {run_idx}: '{run.text}' (上标: {run.font.superscript if run.font else 'N/A'})")
        
        # 调试：检查 body_text 中是否包含 [4] 和 [5]
        print(f"[DocumentService] 正文文本总长度: {len(body_text)} 字符")
        if '[4]' in body_text:
            # 找到所有 [4] 的位置
            positions = []
            start = 0
            while True:
                pos = body_text.find('[4]', start)
                if pos == -1:
                    break
                positions.append(pos)
                start = pos + 1
            print(f"[DocumentService] 在正文中找到 {len(positions)} 个 [4]，位置: {positions}")
            for pos in positions[:3]:  # 只显示前3个
                context = body_text[max(0, pos-30):min(len(body_text), pos+30)]
                print(f"[DocumentService]   [4] 上下文: ...{context}...")
        else:
            print(f"[DocumentService] 警告：正文文本中未找到 [4]")
        
        if '[5]' in body_text:
            # 找到所有 [5] 的位置
            positions = []
            start = 0
            while True:
                pos = body_text.find('[5]', start)
                if pos == -1:
                    break
                positions.append(pos)
                start = pos + 1
            print(f"[DocumentService] 在正文中找到 {len(positions)} 个 [5]，位置: {positions}")
            for pos in positions[:3]:  # 只显示前3个
                context = body_text[max(0, pos-30):min(len(body_text), pos+30)]
                print(f"[DocumentService]   [5] 上下文: ...{context}...")
        else:
            print(f"[DocumentService] 警告：正文文本中未找到 [5]")
        
        # 检测引用标注的常见格式，并提取被引用的参考文献编号
        # 改进：支持更多格式，包括多个编号的完整提取
        citation_patterns = [
            (r'\[(\d+)\]', 'single'),                    # [1] 格式
            (r'\[(\d+)[,\s]+(\d+)\]', 'range_comma'),   # [1,2,3] 格式（逗号分隔，但只匹配两个数字）
            (r'\[(\d+)[\-\s]+(\d+)\]', 'range_dash'),   # [1-5] 或 [1 5] 格式（连字符或空格分隔）
            (r'\((\d+)\)', 'paren_single'),              # (1) 格式（圆括号）
            (r'（(\d+)）', 'paren_single_cn'),          # （1）格式（中文圆括号）
            (r'\((\d+)[,\s]+(\d+)\)', 'paren_range'),  # (1,2,3) 格式
            (r'（(\d+)[,\s]+(\d+)）', 'paren_range_cn'), # （1,2,3）格式
            # 注意：年份格式 (2020) 不提取为参考文献编号，因为可能是作者-年份引用格式
        ]
        
        cited_reference_numbers = set()  # 被引用的参考文献编号集合
        
        # 改进：先检测单个编号格式 [1], [2], [3], [4], [5] 等
        # 这样可以确保单个引用不会被多个编号的模式遗漏
        # 使用更简单直接的方法：直接搜索所有 [数字] 格式
        print(f"[DocumentService] 开始检测引用，正文文本长度: {len(body_text)}")
        
        # 方法1：使用正则表达式搜索所有 [数字] 格式（支持半角和全角方括号）
        # 先检测半角方括号
        single_citation_pattern = r'\[(\d+)\]'
        single_matches = list(re.finditer(single_citation_pattern, body_text))
        print(f"[DocumentService] 正则表达式找到 {len(single_matches)} 个 [数字] 格式的匹配（半角）")
        
        for match in single_matches:
            try:
                num = int(match.group(1))
                if 1 <= num <= 1000:
                    cited_reference_numbers.add(num)
                    # 记录引用位置（在body_text中的位置，需要转换为段落索引）
                    # 由于body_text是合并后的文本，我们需要找到对应的段落
                    match_start = match.start()
                    # 通过累积文本长度找到对应的段落索引
                    current_pos = 0
                    for para_idx, para_text in body_paragraphs:
                        para_len = len(para_text) + 1  # +1 for space
                        if current_pos <= match_start < current_pos + para_len:
                            if num not in citation_locations:
                                citation_locations[num] = []
                            citation_locations[num].append(para_idx)
                            break
                        current_pos += para_len
                    # 获取匹配的上下文（前后各30个字符），便于调试
                    match_end = match.end()
                    context_start = max(0, match_start - 30)
                    context_end = min(len(body_text), match_end + 30)
                    context = body_text[context_start:context_end].replace('\n', ' ').replace('\r', ' ')
                    print(f"[DocumentService] 从单个编号格式中检测到引用: [{num}] (位置: {match_start}, 上下文: ...{context}...)")
            except ValueError as e:
                print(f"[DocumentService] 提取编号失败: {e}")
        
        # 检测全角方括号 ［数字］
        fullwidth_citation_pattern = r'［(\d+)］'
        fullwidth_matches = list(re.finditer(fullwidth_citation_pattern, body_text))
        print(f"[DocumentService] 正则表达式找到 {len(fullwidth_matches)} 个 ［数字］ 格式的匹配（全角）")
        
        for match in fullwidth_matches:
            try:
                num = int(match.group(1))
                if 1 <= num <= 1000:
                    cited_reference_numbers.add(num)
                    # 记录引用位置
                    match_start = match.start()
                    current_pos = 0
                    for para_idx, para_text in body_paragraphs:
                        para_len = len(para_text) + 1
                        if current_pos <= match_start < current_pos + para_len:
                            if num not in citation_locations:
                                citation_locations[num] = []
                            citation_locations[num].append(para_idx)
                            break
                        current_pos += para_len
                    # 获取匹配的上下文（前后各30个字符），便于调试
                    match_end = match.end()
                    context_start = max(0, match_start - 30)
                    context_end = min(len(body_text), match_end + 30)
                    context = body_text[context_start:context_end].replace('\n', ' ').replace('\r', ' ')
                    print(f"[DocumentService] 从单个编号格式中检测到引用: ［{num}］ (位置: {match_start}, 上下文: ...{context}...)")
            except ValueError as e:
                print(f"[DocumentService] 提取编号失败: {e}")
        
        # 方法2：直接使用字符串搜索作为备用（更可靠，支持半角和全角）
        for num in range(1, 1001):
            # 搜索半角方括号
            search_str = f'[{num}]'
            if search_str in body_text:
                if num not in cited_reference_numbers:
                    cited_reference_numbers.add(num)
                    # 找到所有位置
                    positions = []
                    start = 0
                    while True:
                        pos = body_text.find(search_str, start)
                        if pos == -1:
                            break
                        positions.append(pos)
                        start = pos + 1
                    print(f"[DocumentService] 通过字符串搜索检测到引用: [{num}] (找到 {len(positions)} 处)")
                    # 记录引用位置
                    for pos in positions:
                        current_pos = 0
                        for para_idx, para_text in body_paragraphs:
                            para_len = len(para_text) + 1
                            if current_pos <= pos < current_pos + para_len:
                                if num not in citation_locations:
                                    citation_locations[num] = []
                                citation_locations[num].append(para_idx)
                                break
                            current_pos += para_len
                    for pos in positions[:2]:  # 只显示前2个
                        context = body_text[max(0, pos-30):min(len(body_text), pos+30)].replace('\n', ' ').replace('\r', ' ')
                        print(f"[DocumentService]   位置 {pos}: ...{context}...")
            
            # 搜索全角方括号
            search_str_fullwidth = f'［{num}］'
            if search_str_fullwidth in body_text:
                if num not in cited_reference_numbers:
                    cited_reference_numbers.add(num)
                    # 找到所有位置
                    positions = []
                    start = 0
                    while True:
                        pos = body_text.find(search_str_fullwidth, start)
                        if pos == -1:
                            break
                        positions.append(pos)
                        start = pos + 1
                    print(f"[DocumentService] 通过字符串搜索检测到引用: ［{num}］ (找到 {len(positions)} 处)")
                    # 记录引用位置
                    for pos in positions:
                        current_pos = 0
                        for para_idx, para_text in body_paragraphs:
                            para_len = len(para_text) + 1
                            if current_pos <= pos < current_pos + para_len:
                                if num not in citation_locations:
                                    citation_locations[num] = []
                                citation_locations[num].append(para_idx)
                                break
                            current_pos += para_len
                    for pos in positions[:2]:  # 只显示前2个
                        context = body_text[max(0, pos-30):min(len(body_text), pos+30)].replace('\n', ' ').replace('\r', ' ')
                        print(f"[DocumentService]   位置 {pos}: ...{context}...")
        
        # 然后检测多个编号的格式 [1,2,3,4,5]（改进：支持任意数量的编号，支持全角方括号）
        # 改进：使用更宽松的模式，确保能匹配 [4,5] 等格式
        # 模式说明：\[(\d+(?:[,\s]+\d+)+)\] 要求至少两个数字，但可能遗漏某些格式
        # 改用更全面的检测：先检测所有 [数字,数字] 或 [数字 数字] 格式
        multi_citation_patterns = [
            r'\[(\d+(?:[,\s]+\d+)+)\]',  # [1,2,3,4,5] 或 [1 2 3] 格式（至少两个数字，半角）
            r'［(\d+(?:[,\s]+\d+)+)］',  # ［1,2,3,4,5］ 或 ［1 2 3］ 格式（至少两个数字，全角）
            r'\[(\d+)[,\s]+(\d+)\]',     # [4,5] 或 [4 5] 格式（两个数字，半角）
            r'［(\d+)[,\s]+(\d+)］',     # ［4,5］ 或 ［4 5］ 格式（两个数字，全角）
        ]
        for pattern in multi_citation_patterns:
            multi_matches = re.finditer(pattern, body_text)
            for match in multi_matches:
                # 提取所有数字
                if len(match.groups()) == 1:
                    # 单个组，包含所有数字（可能用逗号或空格分隔）
                    numbers_str = match.group(1)
                    numbers = re.findall(r'\d+', numbers_str)
                else:
                    # 多个组，每个组是一个数字
                    numbers = [g for g in match.groups() if g]
                
                # 记录匹配位置，用于确定段落索引
                match_start = match.start()
                current_pos = 0
                para_idx = None
                for idx, para_text in body_paragraphs:
                    para_len = len(para_text) + 1
                    if current_pos <= match_start < current_pos + para_len:
                        para_idx = idx
                        break
                    current_pos += para_len
                
                for num_str in numbers:
                    try:
                        num = int(num_str.strip())
                        if 1 <= num <= 1000:
                            cited_reference_numbers.add(num)
                            # 记录引用位置
                            if para_idx is not None:
                                if num not in citation_locations:
                                    citation_locations[num] = []
                                citation_locations[num].append(para_idx)
                            print(f"[DocumentService] 从多个编号格式中检测到引用: {num} (模式: {pattern})")
                    except ValueError:
                        pass
        
        # 然后检测其他格式（圆括号格式等）
        # 注意：单个 [数字] 格式已经在上面检测过了，这里只检测其他格式
        for pattern, pattern_type in citation_patterns:
            # 跳过单个 [数字] 格式，因为已经在上面检测过了
            if pattern_type == 'single':
                continue
                
            matches = re.finditer(pattern, body_text)
            for match in matches:
                # 记录匹配位置，用于确定段落索引
                match_start = match.start()
                current_pos = 0
                para_idx = None
                for idx, para_text in body_paragraphs:
                    para_len = len(para_text) + 1
                    if current_pos <= match_start < current_pos + para_len:
                        para_idx = idx
                        break
                    current_pos += para_len
                
                if pattern_type == 'paren_single':
                    # (1) 格式，提取单个编号
                    num = int(match.group(1))
                    cited_reference_numbers.add(num)
                    # 记录引用位置
                    if para_idx is not None:
                        if num not in citation_locations:
                            citation_locations[num] = []
                        citation_locations[num].append(para_idx)
                    print(f"[DocumentService] 检测到单个引用: ({num})")
                elif pattern_type == 'paren_single_cn':
                    # （1）格式，提取单个编号
                    num = int(match.group(1))
                    cited_reference_numbers.add(num)
                    # 记录引用位置
                    if para_idx is not None:
                        if num not in citation_locations:
                            citation_locations[num] = []
                        citation_locations[num].append(para_idx)
                    print(f"[DocumentService] 检测到单个引用: （{num}）")
                elif pattern_type in ['range_comma', 'range_dash', 'paren_range', 'paren_range_cn']:
                    # [1,2,3] 或 [1-5] 或 (1,2,3) 格式，提取所有编号
                    numbers_str = match.group(0).strip('[]()（）')
                    # 处理逗号分隔的编号（改进：支持多个编号）
                    if ',' in numbers_str:
                        for num_str in numbers_str.split(','):
                            try:
                                num = int(num_str.strip())
                                if 1 <= num <= 1000:  # 合理的参考文献编号范围
                                    cited_reference_numbers.add(num)
                                    # 记录引用位置
                                    if para_idx is not None:
                                        if num not in citation_locations:
                                            citation_locations[num] = []
                                        citation_locations[num].append(para_idx)
                                    print(f"[DocumentService] 从逗号分隔格式中检测到引用: {num}")
                            except ValueError:
                                pass
                    # 处理连字符或空格分隔的编号范围
                    elif '-' in numbers_str or ' ' in numbers_str:
                        separator = '-' if '-' in numbers_str else ' '
                        parts = numbers_str.split(separator, 1)
                        if len(parts) == 2:
                            try:
                                start = int(parts[0].strip())
                                end = int(parts[1].strip())
                                # 限制范围，避免误匹配
                                if 1 <= start <= end <= 1000:
                                    for num in range(start, end + 1):
                                        cited_reference_numbers.add(num)
                                        # 记录引用位置
                                        if para_idx is not None:
                                            if num not in citation_locations:
                                                citation_locations[num] = []
                                            citation_locations[num].append(para_idx)
                                    print(f"[DocumentService] 从范围格式中检测到引用: {start}-{end}")
                            except ValueError:
                                pass
                    else:
                        # 单个数字
                        try:
                            num = int(numbers_str.strip())
                            if 1 <= num <= 1000:
                                cited_reference_numbers.add(num)
                                # 记录引用位置
                                if para_idx is not None:
                                    if num not in citation_locations:
                                        citation_locations[num] = []
                                    citation_locations[num].append(para_idx)
                                print(f"[DocumentService] 从格式中检测到引用: {num}")
                        except ValueError:
                            pass
        
        # 额外检查：检测Word中的上标格式引用（通过检查runs的格式）
        # 毕业论文中，引用通常是在文字上方加入 [1], [2] 这种格式，通常是上标格式
        for idx in range(body_start_idx, reference_start_idx):
            para = document.paragraphs[idx]
            for run in para.runs:
                run_text = run.text.strip() if run.text else ""
                if not run_text:
                    continue
                
                # 检查是否是上标格式（可能是引用标注）
                if run.font.superscript:
                    # 上标格式的引用可能是：
                    # 1. 纯数字：1, 2, 3
                    # 2. 方括号数字：[1], [2], [3]
                    # 3. 多个数字：[1,2,3] 或 [1-5]
                    
                    # 检查方括号格式的上标引用 [1], [2] 等（支持半角和全角）
                    # 先检测半角方括号
                    bracket_matches = re.finditer(r'\[(\d+)\]', run_text)
                    for match in bracket_matches:
                        try:
                            num = int(match.group(1))
                            if 1 <= num <= 1000:
                                cited_reference_numbers.add(num)
                                # 记录引用位置
                                if num not in citation_locations:
                                    citation_locations[num] = []
                                citation_locations[num].append(idx)
                                print(f"[DocumentService] 检测到上标格式引用 [{num}]")
                        except ValueError:
                            pass
                    
                    # 检测全角方括号 ［1］, ［2］ 等
                    fullwidth_bracket_matches = re.finditer(r'［(\d+)］', run_text)
                    for match in fullwidth_bracket_matches:
                        try:
                            num = int(match.group(1))
                            if 1 <= num <= 1000:
                                cited_reference_numbers.add(num)
                                # 记录引用位置
                                if num not in citation_locations:
                                    citation_locations[num] = []
                                citation_locations[num].append(idx)
                                print(f"[DocumentService] 检测到上标格式引用 [{num}]")
                        except ValueError:
                            pass
                    
                    # 检查多个编号的上标引用 [1,2,3,4,5] 或 [1-5]（改进：支持任意数量的编号，支持全角方括号）
                    # 先检测多个编号格式 [1,2,3,4,5]（半角）
                    multi_bracket_pattern = r'\[(\d+(?:[,\s]+\d+)+)\]'
                    multi_matches = re.finditer(multi_bracket_pattern, run_text)
                    for match in multi_matches:
                        try:
                            numbers_str = match.group(1)  # 提取括号内的内容
                            # 提取所有数字
                            numbers = re.findall(r'\d+', numbers_str)
                            for num_str in numbers:
                                num = int(num_str.strip())
                                if 1 <= num <= 1000:
                                    cited_reference_numbers.add(num)
                                    # 记录引用位置
                                    if num not in citation_locations:
                                        citation_locations[num] = []
                                    citation_locations[num].append(idx)
                                    print(f"[DocumentService] 检测到上标格式多个编号引用 [{num}]")
                        except ValueError:
                            pass
                    
                    # 检测全角方括号多个编号格式 ［1,2,3,4,5］
                    fullwidth_multi_pattern = r'［(\d+(?:[,\s]+\d+)+)］'
                    fullwidth_multi_matches = re.finditer(fullwidth_multi_pattern, run_text)
                    for match in fullwidth_multi_matches:
                        try:
                            numbers_str = match.group(1)  # 提取括号内的内容
                            # 提取所有数字
                            numbers = re.findall(r'\d+', numbers_str)
                            for num_str in numbers:
                                num = int(num_str.strip())
                                if 1 <= num <= 1000:
                                    cited_reference_numbers.add(num)
                                    # 记录引用位置
                                    if num not in citation_locations:
                                        citation_locations[num] = []
                                    citation_locations[num].append(idx)
                                    print(f"[DocumentService] 检测到上标格式多个编号引用 ［{num}］")
                        except ValueError:
                            pass
                    
                    # 再检测范围格式 [1-5] 或两个编号 [1,2]（半角）
                    range_matches = re.finditer(r'\[(\d+)[,\-\s]+(\d+)\]', run_text)
                    for match in range_matches:
                        try:
                            # 提取所有数字
                            numbers_str = match.group(0).strip('[]')
                            if ',' in numbers_str:
                                # 逗号分隔：[1,2] 或 [1,2,3]
                                for num_str in numbers_str.split(','):
                                    num = int(num_str.strip())
                                    if 1 <= num <= 1000:
                                        cited_reference_numbers.add(num)
                                        # 记录引用位置
                                        if num not in citation_locations:
                                            citation_locations[num] = []
                                        citation_locations[num].append(idx)
                                        print(f"[DocumentService] 检测到上标格式逗号分隔引用 [{num}]")
                            elif '-' in numbers_str:
                                # 连字符分隔：[1-5]
                                parts = numbers_str.split('-')
                                if len(parts) == 2:
                                    start = int(parts[0].strip())
                                    end = int(parts[1].strip())
                                    if 1 <= start <= end <= 1000:
                                        for num in range(start, end + 1):
                                            cited_reference_numbers.add(num)
                                            # 记录引用位置
                                            if num not in citation_locations:
                                                citation_locations[num] = []
                                            citation_locations[num].append(idx)
                                        print(f"[DocumentService] 检测到上标格式范围引用 [{start}-{end}]")
                        except ValueError:
                            pass
                    
                    # 检测全角方括号范围格式 ［1-5］ 或 ［1,2］
                    fullwidth_range_matches = re.finditer(r'［(\d+)[,\-\s]+(\d+)］', run_text)
                    for match in fullwidth_range_matches:
                        try:
                            # 提取所有数字
                            numbers_str = match.group(0).strip('［］')
                            if ',' in numbers_str:
                                # 逗号分隔：［1,2］ 或 ［1,2,3］
                                for num_str in numbers_str.split(','):
                                    num = int(num_str.strip())
                                    if 1 <= num <= 1000:
                                        cited_reference_numbers.add(num)
                                        # 记录引用位置
                                        if num not in citation_locations:
                                            citation_locations[num] = []
                                        citation_locations[num].append(idx)
                                        print(f"[DocumentService] 检测到上标格式逗号分隔引用 ［{num}］")
                            elif '-' in numbers_str:
                                # 连字符分隔：［1-5］
                                parts = numbers_str.split('-')
                                if len(parts) == 2:
                                    start = int(parts[0].strip())
                                    end = int(parts[1].strip())
                                    if 1 <= start <= end <= 1000:
                                        for num in range(start, end + 1):
                                            cited_reference_numbers.add(num)
                                            # 记录引用位置
                                            if num not in citation_locations:
                                                citation_locations[num] = []
                                            citation_locations[num].append(idx)
                                        print(f"[DocumentService] 检测到上标格式范围引用 ［{start}-{end}］")
                        except ValueError:
                            pass
                    
                    # 检查纯数字格式的上标引用（如果还没有匹配到方括号格式）
                    if not re.search(r'\[', run_text):
                        # 纯数字：1, 2, 3 或 1,2,3
                        if re.match(r'^\d+([,\-\s]+\d+)*$', run_text):
                            numbers = re.findall(r'\d+', run_text)
                            for num_str in numbers:
                                try:
                                    num = int(num_str)
                                    if 1 <= num <= 1000:
                                        cited_reference_numbers.add(num)
                                        # 记录引用位置
                                        if num not in citation_locations:
                                            citation_locations[num] = []
                                        citation_locations[num].append(idx)
                                        print(f"[DocumentService] 检测到上标格式引用 {num}")
                                except ValueError:
                                    pass
                
                # 也检查普通文本中的引用格式（非上标，但可能是引用）
                # 检查是否包含 [数字] 或 (数字) 格式（支持半角和全角方括号）
                for pattern in [r'\[(\d+)\]', r'［(\d+)］', r'\((\d+)\)', r'（(\d+)）']:
                    matches = re.finditer(pattern, run_text)
                    for match in matches:
                        try:
                            num = int(match.group(1))
                            if 1 <= num <= 1000:
                                cited_reference_numbers.add(num)
                                # 记录引用位置
                                if num not in citation_locations:
                                    citation_locations[num] = []
                                citation_locations[num].append(idx)
                                print(f"[DocumentService] 从普通文本中检测到引用: {num} (格式: {pattern})")
                        except ValueError:
                            pass
                
                # 额外检查：检测普通文本中的多个编号格式 [4,5]（非上标，支持全角方括号）
                multi_patterns = [
                    r'\[(\d+(?:[,\s]+\d+)+)\]',  # [4,5,6] 格式（半角）
                    r'［(\d+(?:[,\s]+\d+)+)］',  # ［4,5,6］ 格式（全角）
                    r'\[(\d+)[,\s]+(\d+)\]',     # [4,5] 格式（半角）
                    r'［(\d+)[,\s]+(\d+)］',     # ［4,5］ 格式（全角）
                ]
                for pattern in multi_patterns:
                    matches = re.finditer(pattern, run_text)
                    for match in matches:
                        try:
                            if len(match.groups()) == 1:
                                numbers_str = match.group(1)
                                numbers = re.findall(r'\d+', numbers_str)
                            else:
                                numbers = [g for g in match.groups() if g]
                            
                            for num_str in numbers:
                                num = int(num_str.strip())
                                if 1 <= num <= 1000:
                                    cited_reference_numbers.add(num)
                                    # 记录引用位置
                                    if num not in citation_locations:
                                        citation_locations[num] = []
                                    citation_locations[num].append(idx)
                                    print(f"[DocumentService] 从普通文本多个编号格式中检测到引用: {num}")
                        except ValueError:
                            pass
        
        # 4. 找出未被引用的参考文献
        # 调试信息：打印检测到的参考文献编号和引用编号
        print(f"[DocumentService] 检测到 {len(reference_items)} 条参考文献")
        print(f"[DocumentService] 参考文献编号: {[ref['number'] for ref in reference_items]}")
        print(f"[DocumentService] 正文中引用的编号: {sorted(cited_reference_numbers)}")
        print(f"[DocumentService] 正文文本长度: {len(body_text)} 字符")
        print(f"[DocumentService] 正文段落数量: {len(body_paragraphs)}")
        
        # 额外调试：检查正文中是否包含 [4] 和 [5]
        if '[4]' in body_text:
            print(f"[DocumentService] 调试：正文中包含 [4]")
        if '[5]' in body_text:
            print(f"[DocumentService] 调试：正文中包含 [5]")
        if '[4,5]' in body_text or '[4, 5]' in body_text:
            print(f"[DocumentService] 调试：正文中包含 [4,5] 格式")
        
        uncited_references = []
        for ref_item in reference_items:
            ref_num = ref_item["number"]
            # 检查是否真正被引用：必须在 cited_reference_numbers 中，并且有位置记录
            # 如果不在引用集合中，或者没有位置记录，都统一标记为未引用
            locations = citation_locations.get(ref_num, [])
            if ref_num not in cited_reference_numbers or not locations:
                uncited_references.append(ref_item)
                print(f"[DocumentService] 未引用的参考文献: {ref_num} - {ref_item['text'][:50]}")
        
        print(f"[DocumentService] 未引用的参考文献数量: {len(uncited_references)}")
        print(f"[DocumentService] 引用位置记录: {citation_locations}")
        
        # 5. 在参考文献段落中标记引用信息
        # 逻辑：把文献分为两类
        # 1. 找到标注页码的：把页码放在文献后面
        # 2. 未找到标注页码的：显示"未找到标注页"
        for ref_item in reference_items:
            ref_num = ref_item["number"]
            para = ref_item["paragraph"]
            
            # 获取引用位置（段落索引列表）
            locations = citation_locations.get(ref_num, [])
            
            # 检查是否找到了页码：必须在 cited_reference_numbers 中，并且有位置记录
            if ref_num in cited_reference_numbers and locations:
                # 找到了页码，在文献后面添加页码信息
                try:
                    # 尝试估算页码（假设每页约25个段落，从正文开始计算）
                    pages = []
                    for para_idx in sorted(set(locations)):
                        # 估算页码：正文开始位置 + 段落索引 / 每页段落数
                        estimated_page = max(1, (para_idx - body_start_idx) // 25 + 1)
                        pages.append(estimated_page)
                    
                    # 去重并排序页码
                    unique_pages = sorted(set(pages))
                    if unique_pages:
                        page_info = "、".join([str(p) for p in unique_pages])
                        marker_text = f"（引用页码：{page_info}）"
                        
                        # 在段落末尾添加页码信息
                        new_run = para.add_run(marker_text)
                        new_run.font.color.rgb = RGBColor(0, 128, 0)  # 绿色
                        new_run.font.bold = False
                        print(f"[DocumentService] 为参考文献 {ref_num} 添加引用页码: {page_info}")
                except Exception as e:
                    print(f"[DocumentService] 添加引用页码失败: {e}")
            else:
                # 未找到标注页码，标记为"未找到标注页"
                try:
                    # 将参考文献段落标红
                    if para.runs:
                        # 如果段落有 runs，直接设置颜色
                        for run in para.runs:
                            run.font.color.rgb = RGBColor(255, 0, 0)  # 红色
                            run.font.bold = True  # 加粗
                    else:
                        # 如果段落没有 runs，尝试添加一个 run（处理空段落或特殊格式）
                        para_text = para.text if para.text else ""
                        if para_text:
                            # 清空段落内容，然后添加带格式的 run
                            para.clear()
                            run = para.add_run(para_text)
                        else:
                            run = para.add_run("")
                        run.font.color.rgb = RGBColor(255, 0, 0)  # 红色
                        run.font.bold = True  # 加粗
                    
                    # 在参考文献文本后添加提示
                    marker_text = "（未找到标注页）"
                    # 在段落末尾添加红色提示文本
                    new_run = para.add_run(marker_text)
                    new_run.font.color.rgb = RGBColor(255, 0, 0)  # 红色
                    new_run.font.bold = True  # 加粗
                    print(f"[DocumentService] 参考文献 {ref_num} 未找到标注页")
                except Exception as e:
                    # 如果处理失败，记录错误但不中断流程
                    print(f"[DocumentService] 标记参考文献失败: {e}")
        
        # 6. 生成问题报告
        # 统计未找到标注页的参考文献数量
        uncited_refs = [ref for ref in reference_items 
                       if ref["number"] not in cited_reference_numbers 
                       or not citation_locations.get(ref["number"], [])]
        if uncited_refs:
            issues.append({
                "type": "uncited_references",
                "message": f"发现 {len(uncited_refs)} 条参考文献未找到标注页",
                "suggestion": "请在正文中添加引用标注，或删除未被引用的参考文献",
                "uncited_count": len(uncited_refs),
                "uncited_references": [
                    {
                        "number": ref["number"],
                        "text_preview": ref["text"][:80] + "..."
                    }
                    for ref in uncited_refs[:10]  # 只显示前10个
                ]
            })
        
        # 如果没有找到引用标注，提示用户
        if not cited_reference_numbers and len(reference_items) > 0:
            # 找到正文段落中可能缺少引用的位置
            missing_citation_paragraphs = []
            for para_idx, para_text in body_paragraphs:
                # 如果段落较长（可能是正文），但没有引用标注，记录
                if len(para_text) > 100:
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
        
        # 1. 找到正文开始位置（从"绪论"或"概述"开始）
        body_start_idx = None
        body_start_patterns = [
            r'^正文',
            r'^第[一二三四五六七八九十\d]+章',  # 第一章、第二章等
            r'^第\d+章',  # 第1章、第2章等
            r'^Chapter\s+\d+',  # Chapter 1、Chapter 2等
            r'^1\s+',  # 以"1 "开头的标题（第一章）
            r'^1\.',  # 以"1."开头的标题
            r'^绪论$',  # 绪论（精确匹配）
            r'^概述$',  # 概述（精确匹配）
            r'^绪论',  # 以"绪论"开头
            r'^概述',  # 以"概述"开头
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
        
        # 1.5. 找到目录页的范围（用于排除目录页末尾的空白行）
        toc_start_idx = None
        toc_end_idx = None
        for idx, paragraph in enumerate(document.paragraphs):
            para_text = paragraph.text.strip() if paragraph.text else ""
            if (para_text.startswith("目录") or para_text.startswith("Contents")) and toc_start_idx is None:
                toc_start_idx = idx
            elif toc_start_idx is not None and (
                para_text.startswith("第一章") or para_text.startswith("第1章") or 
                para_text.startswith("Chapter 1") or para_text.startswith("1 引言") or 
                para_text.startswith("1 绪论") or para_text.startswith("1 概述") or
                para_text == "绪论" or para_text == "概述"
            ):
                toc_end_idx = idx
                break
        
        # 如果没找到目录结束位置，假设目录到正文开始之前
        if toc_start_idx is not None and toc_end_idx is None:
            toc_end_idx = body_start_idx if body_start_idx is not None else len(document.paragraphs)
        
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
            r'^绪论$',  # 绪论（精确匹配）
            r'^概述$',  # 概述（精确匹配）
            r'^1\s+绪论',  # 1 绪论
            r'^1\s+概述',  # 1 概述
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
            
            # 检查"绪论"或"概述"（精确匹配或独立出现）
            if para_text == "绪论" or para_text == "概述":
                return True
            if para_text.startswith("1 绪论") or para_text.startswith("1 概述"):
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
                # 如果之前有连续空白，检查这些空白是否在章节标题前或后（都允许）
                if consecutive_blanks >= 2 and blank_start_idx is not None:
                    # 空白段在章节标题前，这是章节间的空白，允许（不标记）
                    # 空白段在章节标题后，也是允许的
                    # 所以遇到章节标题时，直接清除之前的空白计数，不标记
                    pass
                
                # 开始新章节，重置计数（章节标题前后的空白都是允许的）
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
                    # 如果之前有连续空白，检查是否需要标记
                    if consecutive_blanks >= 2 and blank_start_idx is not None:
                        # 检查空白段是否在目录页范围内（目录页末尾的空白行允许）
                        is_in_toc = False
                        if toc_start_idx is not None and toc_end_idx is not None:
                            # 如果空白段的起始位置在目录页范围内，或者是目录页结束后的空白（目录页和正文开始之间），都允许
                            if blank_start_idx >= toc_start_idx and blank_start_idx < toc_end_idx:
                                is_in_toc = True
                            # 如果空白段位于目录页结束和正文开始之间，也允许（这是章节间的空白）
                            elif toc_end_idx is not None and body_start_idx is not None:
                                if blank_start_idx >= toc_end_idx and blank_start_idx < body_start_idx:
                                    is_in_toc = True
                        
                        # 检查空白段之后是否有章节标题（如果空白段后面是章节标题，这是章节间的空白，允许）
                        is_before_chapter = False
                        # 扩大检查范围：检查空白段之后是否有章节标题（最多检查20个段落，以覆盖目录和第一章之间的情况）
                        for next_idx in range(blank_start_idx + consecutive_blanks, min(blank_start_idx + consecutive_blanks + 20, check_end_idx, len(document.paragraphs))):
                            if next_idx < len(document.paragraphs):
                                next_para = document.paragraphs[next_idx]
                                if is_chapter_title(next_para):
                                    # 空白段后面是章节标题，这是章节间的空白，允许
                                    is_before_chapter = True
                                    break
                        
                        # 检查空白段之前是否有章节标题（如果空白段紧跟在章节标题后，也是允许的）
                        # 扩大检查范围：不仅检查前一个段落，还要检查前面是否有章节标题（比如目录结束）
                        is_after_chapter = False
                        # 向前检查最多10个段落，查找章节标题
                        for prev_idx in range(max(0, blank_start_idx - 10), blank_start_idx):
                            if prev_idx < len(document.paragraphs):
                                prev_para = document.paragraphs[prev_idx]
                                if is_chapter_title(prev_para):
                                    # 空白段前面有章节标题，这是章节间的空白，允许
                                    is_after_chapter = True
                                    break
                        
                        # 特别检查：如果空白段位于目录结束和正文开始之间，也允许（这是章节间的空白）
                        if not is_after_chapter and toc_end_idx is not None and body_start_idx is not None:
                            if blank_start_idx >= toc_end_idx and blank_start_idx < body_start_idx:
                                is_after_chapter = True
                        
                        # 只有当空白段既不在目录页范围内，也不在章节标题前，也不在章节标题后，且在同一章节内时，才标记为问题
                        if not is_in_toc and not is_before_chapter and not is_after_chapter:
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
            # 检查空白段是否在目录页范围内（目录页末尾的空白行允许）
            is_in_toc = False
            if toc_start_idx is not None and toc_end_idx is not None:
                # 如果空白段的起始位置在目录页范围内，或者是目录页结束后的空白（目录页和正文开始之间），都允许
                if blank_start_idx >= toc_start_idx and blank_start_idx < toc_end_idx:
                    is_in_toc = True
                # 如果空白段位于目录页结束和正文开始之间，也允许（这是章节间的空白）
                elif toc_end_idx is not None and body_start_idx is not None:
                    if blank_start_idx >= toc_end_idx and blank_start_idx < body_start_idx:
                        is_in_toc = True
            
            # 检查是否在章节标题后（扩大检查范围）
            is_after_chapter = False
            # 向前检查最多10个段落，查找章节标题
            for prev_idx in range(max(0, blank_start_idx - 10), blank_start_idx):
                if prev_idx < len(document.paragraphs):
                    prev_para = document.paragraphs[prev_idx]
                    if is_chapter_title(prev_para):
                        # 空白段前面有章节标题，这是章节间的空白，允许
                        is_after_chapter = True
                        break
            
            # 特别检查：如果空白段位于目录结束和正文开始之间，也允许（这是章节间的空白）
            if not is_after_chapter and toc_end_idx is not None and body_start_idx is not None:
                if blank_start_idx >= toc_end_idx and blank_start_idx < body_start_idx:
                    is_after_chapter = True
            
            # 检查空白段之后是否有章节标题（虽然已经到文档末尾，但也要检查）
            is_before_chapter = False
            # 扩大检查范围：检查空白段之后是否有章节标题（最多检查20个段落）
            for next_idx in range(blank_start_idx + consecutive_blanks, min(blank_start_idx + consecutive_blanks + 20, len(document.paragraphs))):
                if next_idx < len(document.paragraphs):
                    next_para = document.paragraphs[next_idx]
                    if is_chapter_title(next_para):
                        is_before_chapter = True
                        break
            
            # 只有当空白段既不在目录页范围内，也不在章节标题前，也不在章节标题后时，才标记为问题
            if not is_in_toc and not is_after_chapter and not is_before_chapter:
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

