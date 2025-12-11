#!/usr/bin/env python3
"""
诊断 Word 文档字体提取和应用问题
"""

from docx import Document
from docx.oxml.ns import qn
from pathlib import Path
import sys

def extract_run_font(run):
    """提取单个 run 的字体信息"""
    font_info = {
        "text": run.text[:50] if run.text else "",
        "font_name": None,
        "font_size": None,
    }
    
    # 方法1: 从 run.font.name 获取
    if run.font and run.font.name:
        font_info["font_name"] = run.font.name
        font_info["font_size"] = run.font.size.pt if run.font.size else None
    
    # 方法2: 从 XML 中获取（更准确）
    try:
        r_pr = run._element.get_or_add_rPr()
        r_fonts = r_pr.rFonts
        if r_fonts is not None:
            east_asia = r_fonts.get(qn("w:eastAsia"))
            ascii_font = r_fonts.get(qn("w:ascii"))
            h_ansi = r_fonts.get(qn("w:hAnsi"))
            
            # 优先使用 eastAsia（中文字体）
            font_info["font_name"] = east_asia or ascii_font or h_ansi or font_info["font_name"]
            
            # 从 XML 中获取字号
            if not font_info["font_size"]:
                sz = r_pr.find(qn("w:sz"))
                if sz is not None:
                    sz_val = sz.get(qn("w:val"))
                    if sz_val:
                        font_info["font_size"] = int(sz_val) / 2  # Word 中字号是半磅单位
    except Exception as e:
        pass
    
    return font_info

def diagnose_document(docx_path):
    """诊断文档中的字体使用情况"""
    print(f"正在分析文档: {docx_path}")
    print("=" * 80)
    
    doc = Document(docx_path)
    
    all_fonts = set()
    paragraph_fonts = []
    
    for para_idx, paragraph in enumerate(doc.paragraphs):
        if not paragraph.text.strip():
            continue
        
        para_fonts = []
        for run_idx, run in enumerate(paragraph.runs):
            if not run.text.strip():
                continue
            
            font_info = extract_run_font(run)
            if font_info["font_name"]:
                all_fonts.add(font_info["font_name"])
                para_fonts.append(font_info["font_name"])
            
            # 显示前几个 run 的详细信息
            if para_idx < 5 and run_idx < 3:
                print(f"\n段落 {para_idx}, Run {run_idx}:")
                print(f"  文本: {font_info['text']}")
                print(f"  字体: {font_info['font_name']}")
                print(f"  字号: {font_info['font_size']}")
        
        if para_fonts:
            unique_fonts = set(para_fonts)
            paragraph_fonts.append({
                "para_idx": para_idx,
                "text": paragraph.text[:50],
                "fonts": unique_fonts,
                "font_count": len(unique_fonts)
            })
    
    print("\n" + "=" * 80)
    print("统计信息:")
    print(f"文档中使用的所有字体: {sorted(all_fonts)}")
    print(f"总段落数: {len(paragraph_fonts)}")
    
    # 统计有多字体的段落
    multi_font_paras = [p for p in paragraph_fonts if p["font_count"] > 1]
    print(f"包含多种字体的段落数: {len(multi_font_paras)}")
    
    if multi_font_paras:
        print("\n包含多种字体的段落:")
        for p in multi_font_paras[:10]:  # 只显示前10个
            print(f"  段落 {p['para_idx']}: {p['fonts']} - {p['text']}")
    
    # 统计每种字体的使用情况
    font_usage = {}
    for p in paragraph_fonts:
        for font in p["fonts"]:
            font_usage[font] = font_usage.get(font, 0) + 1
    
    print("\n字体使用统计:")
    for font, count in sorted(font_usage.items(), key=lambda x: -x[1]):
        print(f"  {font}: {count} 个段落")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python 诊断字体问题.py <word文档路径>")
        sys.exit(1)
    
    docx_path = Path(sys.argv[1])
    if not docx_path.exists():
        print(f"错误: 文件不存在: {docx_path}")
        sys.exit(1)
    
    diagnose_document(docx_path)

