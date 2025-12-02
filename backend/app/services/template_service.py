import json
import uuid
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.text.paragraph import Paragraph
from fastapi import UploadFile

from .utils import docx_format_utils


class TemplateService:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def save_template(self, upload: UploadFile, session_id: str) -> str:
        """
        保存模板并生成规则库
        
        Args:
            upload: 上传的模板文件
            session_id: 用户会话ID，用于标识模板所有者
        """
        template_id = uuid.uuid4().hex
        template_dir = self.base_dir / template_id
        template_dir.mkdir(parents=True, exist_ok=True)

        template_path = template_dir / "template.docx"
        content = await upload.read()
        template_path.write_bytes(content)

        document = Document(template_path)
        rules, default_style = self._extract_rules(document)

        metadata = {
            "template_id": template_id,
            "name": upload.filename,
            "session_id": session_id,  # 记录模板所有者
            "styles": rules,
            "default_style": default_style,
            "created_at": datetime.utcnow().isoformat(),
        }

        metadata_path = template_dir / "metadata.json"
        metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
        return template_id

    def get_template_metadata(self, template_id: str) -> Dict:
        metadata_path = self.base_dir / template_id / "metadata.json"
        if not metadata_path.exists():
            return {}
        return json.loads(metadata_path.read_text(encoding="utf-8"))
    
    def get_user_templates(self, session_id: str) -> list[Dict]:
        """
        获取指定用户的所有模板列表
        
        Args:
            session_id: 用户会话ID
            
        Returns:
            模板列表，每个模板包含 template_id, name, created_at
        """
        templates = []
        
        if not self.base_dir.exists():
            return templates
        
        # 遍历所有模板目录
        for template_dir in self.base_dir.iterdir():
            if not template_dir.is_dir():
                continue
            
            metadata_path = template_dir / "metadata.json"
            if not metadata_path.exists():
                continue
            
            try:
                metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
                # 只返回属于当前用户的模板
                if metadata.get("session_id") == session_id:
                    template_name = metadata.get("name", "未命名模板")
                    # 只保留名称中包含"大学"的模板
                    if "大学" in template_name:
                        templates.append({
                            "template_id": metadata.get("template_id"),
                            "name": template_name,
                            "created_at": metadata.get("created_at"),
                        })
            except (json.JSONDecodeError, KeyError):
                continue
        
        # 按创建时间倒序排列（最新的在前）
        templates.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        # 同名模板去重：只保留每个名称最新的一个（忽略括号内的编号）
        seen_names = {}
        unique_templates = []
        
        for template in templates:
            # 提取模板名称（去掉文件扩展名和括号内容）
            template_name = template.get("name", "未命名模板")
            # 去掉 .docx 扩展名
            if template_name.lower().endswith(".docx"):
                template_name = template_name[:-5]
            
            # 如果这个名称还没有出现过，或者当前模板更新，则保留
            if template_name not in seen_names:
                seen_names[template_name] = template
                unique_templates.append(template)
            else:
                # 如果已存在同名模板，比较创建时间，保留最新的
                existing = seen_names[template_name]
                existing_time = existing.get("created_at", "")
                current_time = template.get("created_at", "")
                if current_time > existing_time:
                    # 替换为更新的模板
                    unique_templates.remove(existing)
                    seen_names[template_name] = template
                    unique_templates.append(template)
        
        # 只返回最新的10个模板，避免列表过长
        return unique_templates[:10]
    
    def is_template_owner(self, template_id: str, session_id: str) -> bool:
        """
        检查模板是否属于指定用户
        
        Args:
            template_id: 模板ID
            session_id: 用户会话ID
            
        Returns:
            True 如果模板属于该用户，否则 False
        """
        metadata = self.get_template_metadata(template_id)
        return metadata.get("session_id") == session_id

    def _extract_rules(self, document: Document) -> tuple[Dict[str, Dict], Optional[str]]:
        rules: Dict[str, Dict] = {}
        style_counter: Counter[str] = Counter()

        for paragraph in document.paragraphs:
            style_name = paragraph.style.name if paragraph.style else "Normal"
            style_counter[style_name] += 1
            if style_name not in rules:
                rules[style_name] = self._serialize_paragraph_format(paragraph)

        default_style = self._select_default_style(style_counter)
        return rules, default_style

    def _serialize_paragraph_format(self, paragraph: Paragraph) -> Dict:
        data: Dict[str, Optional[float | str | bool]] = {}

        run_rule = docx_format_utils.extract_run_format(paragraph)
        data.update(run_rule)

        pf = paragraph.paragraph_format

        alignment_map = {
            WD_ALIGN_PARAGRAPH.LEFT: "left",
            WD_ALIGN_PARAGRAPH.CENTER: "center",
            WD_ALIGN_PARAGRAPH.RIGHT: "right",
            WD_ALIGN_PARAGRAPH.JUSTIFY: "justify",
            WD_ALIGN_PARAGRAPH.DISTRIBUTE: "distribute",
        }
        if paragraph.alignment in alignment_map:
            data["alignment"] = alignment_map[paragraph.alignment]

        data.update(docx_format_utils.extract_spacing(pf))
        data.update(docx_format_utils.extract_indents(pf))

        return {k: v for k, v in data.items() if v is not None}

    def _select_default_style(self, style_counter: Counter[str]) -> Optional[str]:
        if not style_counter:
            return None

        sorted_styles = sorted(
            style_counter.items(),
            key=lambda item: (item[0] and "标题" in item[0], -item[1]),
        )
        for style_name, _ in sorted_styles:
            if not style_name:
                continue
            if "标题" in style_name or style_name.lower().startswith("heading"):
                continue
            return style_name

        # fallback: most common
        return style_counter.most_common(1)[0][0]

