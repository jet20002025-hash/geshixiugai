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

    async def save_template(self, upload: UploadFile) -> str:
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

