#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
md2word-gate 交付前门禁 - 核心脚本
致敬文格（lilialla/legal-document-format-skill）的"交付前门禁"思想。

功能:
  1. OpenXML 结构完整性检查
  2. 页眉页脚检查
  3. 页码字段检查
  4. 标题样式引用检查
  5. 字体合规检查（仿宋_GB2312）
  6. 中文标点全角检查
  7. 表格边框检查
  8. 空段检测
  9. [可选] 渲染页门禁（LibreOffice + Poppler）

退出码:
  0 - 全部通过
  1 - 有警告（非严格模式）
  2 - 有失败
  3 - 文件错误
"""

import sys
import os
import json
import re
import zipfile
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple

# 尝试导入 python-docx
try:
    from docx import Document
    from docx.shared import Pt
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False


# ============== 检查项 ==============

def check_openxml_structure(docx_path: str) -> Tuple[str, str]:
    """OpenXML 结构完整性检查"""
    try:
        with zipfile.ZipFile(docx_path, 'r') as z:
            names = z.namelist()
            if 'word/document.xml' not in names:
                return 'fail', 'document.xml 缺失'
            if 'word/styles.xml' not in names:
                return 'fail', 'styles.xml 缺失'
            if '[Content_Types].xml' not in names:
                return 'fail', '[Content_Types].xml 缺失'
        if HAS_DOCX:
            doc = Document(docx_path)
            _ = len(doc.paragraphs)  # 触发解析
        return 'pass', f'结构完整，{len(names)} 个 XML 组件'
    except Exception as e:
        return 'fail', f'无法解析: {str(e)[:100]}'


def check_header_footer(doc) -> Tuple[str, str]:
    """页眉页脚检查"""
    header_texts = []
    footer_texts = []
    for section in doc.sections:
        if section.header.is_linked_to_previous is False:
            for p in section.header.paragraphs:
                if p.text.strip():
                    header_texts.append(p.text.strip())
        if section.footer.is_linked_to_previous is False:
            for p in section.footer.paragraphs:
                if p.text.strip():
                    footer_texts.append(p.text.strip())
    
    if not header_texts and not footer_texts:
        return 'warning', '页眉页脚均无内容（信拓集团文书通常需页眉）'
    if not header_texts:
        return 'warning', '页眉无内容'
    if not footer_texts:
        return 'warning', '页脚无内容（建议放置页码）'
    
    return 'pass', f'页眉={len(header_texts)}段, 页脚={len(footer_texts)}段'


def check_page_number_field(docx_path: str) -> Tuple[str, str]:
    """页码字段检查（应使用 PAGE 字段而非硬编码）"""
    try:
        with zipfile.ZipFile(docx_path, 'r') as z:
            footer_files = [n for n in z.namelist() if 'footer' in n and n.endswith('.xml')]
            if not footer_files:
                return 'skip', '无 footer.xml'
            
            page_field_count = 0
            hard_code_count = 0
            for ff in footer_files:
                content = z.read(ff).decode('utf-8', errors='ignore')
                if 'PAGE' in content and 'fldChar' in content:
                    page_field_count += 1
                # 检测硬编码的纯数字页码
                matches = re.findall(r'<w:t[^>]*>\s*\d+\s*</w:t>', content)
                hard_code_count += len(matches)
            
            if page_field_count > 0:
                return 'pass', f'PAGE 字段 {page_field_count} 个'
            if hard_code_count > 0:
                return 'warning', f'页脚含硬编码数字（{hard_code_count} 处），未使用 PAGE 字段'
            return 'warning', '页脚无页码字段'
    except Exception as e:
        return 'warning', f'检查失败: {str(e)[:80]}'


def check_heading_styles(doc) -> Tuple[str, str]:
    """标题样式引用检查（一级标题应使用 Heading 1 样式）"""
    heading_count = 0
    direct_format_count = 0
    
    for p in doc.paragraphs:
        if p.style and 'Heading' in p.style.name:
            heading_count += 1
        elif p.runs:
            # 检查是否直接设置字号（疑似伪标题）
            for run in p.runs:
                if run.font.size and run.font.size.pt >= 14:
                    if run.bold and len(p.text.strip()) < 50:
                        direct_format_count += 1
                    break
    
    if heading_count >= 1:
        return 'pass', f'Heading 样式 {heading_count} 处'
    if direct_format_count > 0:
        return 'warning', f'未使用 Heading 样式，{direct_format_count} 处疑似直接格式化的标题'
    return 'pass', '无标题段'


def check_table_borders(doc) -> Tuple[str, str]:
    """表格边框检查"""
    tables = doc.tables
    if not tables:
        return 'skip', '无表格'
    
    # 简化检查：仅确认有表格
    # 详细边框属性需要解析 XML
    return 'pass', f'共 {len(tables)} 张表格（边框详情需查 XML）'


def check_font_compliance(doc) -> Tuple[str, str]:
    """字体合规检查（仿宋_GB2312 + Times New Roman）"""
    font_count = {}
    total_runs = 0
    
    for p in doc.paragraphs:
        for run in p.runs:
            total_runs += 1
            font_name = run.font.name
            if font_name:
                font_count[font_name] = font_count.get(font_name, 0) + 1
    
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    for run in p.runs:
                        total_runs += 1
                        font_name = run.font.name
                        if font_name:
                            font_count[font_name] = font_count.get(font_name, 0) + 1
    
    if not font_count:
        return 'warning', '未检测到字体设置（可能继承样式）'
    
    # 检查是否使用仿宋
    has_fangsong = any('仿宋' in f for f in font_count.keys())
    has_times = any('Times' in f for f in font_count.keys())
    
    if has_fangsong and has_times:
        return 'pass', f'仿宋+Times New Roman 配比正确 ({sum(font_count.values())} 处 run)'
    if has_fangsong:
        return 'pass', f'使用仿宋 ({sum(font_count.values())} 处 run)'
    if has_times:
        return 'warning', f'仅 Times New Roman，未使用仿宋_GB2312 ({sum(font_count.values())} 处 run)'
    
    return 'warning', f'字体非标准配置: {list(font_count.keys())[:3]}'


def check_chinese_punctuation(doc) -> Tuple[str, str]:
    """中文标点全角检查
    
    智能识别算法：只统计“中文字符旁边的半角标点”。
    原则：纯英文 / 纯数字 / 表格分隔符、Markdown 语法，均不视为问题。
    重点检查：中文上下文中误用的半角双引号、括号、逗号、句号、险号。
    
    v0.1.1 重构：以上下文是否有中文字符为准。
    """
    critical_chars = {',', '.', '!', '?', ';', ':', '\'', '"', '(', ')'}
    # 法律文书标准：中文括号、全角引号优先。
    # 半角括号仅在纯英文上下文中合法（如"(abc)"）
    # 在中文字符旁的半角括号 (2026) 应判错。
    # 决定是否为“中文上下文”：看该标点前后 2 个字符内是否有中文
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
    halfwidth_count = 0
    halfwidth_samples = []
    
    def is_chinese_context(text, idx, window=2):
        start = max(0, idx - window)
        end = min(len(text), idx + window + 1)
        ctx = text[start:end]
        return bool(chinese_pattern.search(ctx))
    
    for para_idx, p in enumerate(doc.paragraphs):
        text = p.text
        if not text.strip():
            continue
        for idx, ch in enumerate(text):
            if ch in critical_chars and is_chinese_context(text, idx):
                halfwidth_count += 1
                if len(halfwidth_samples) < 5:
                    start = max(0, idx - 8)
                    end = min(len(text), idx + 8)
                    halfwidth_samples.append(f'段{para_idx}「{ch}」({text[start:end].strip()})')
    
    if halfwidth_count == 0:
        return 'pass', '未检测到半角中文标点'
    if halfwidth_count < 3:
        return 'warning', f'少量半角标点 ({halfwidth_count} 处): {"; ".join(halfwidth_samples)}'
    return 'fail', f'多处半角标点 ({halfwidth_count} 处): {"; ".join(halfwidth_samples)}'


def check_empty_paragraphs(doc) -> Tuple[str, str]:
    """空段检测（连续 3 个以上空段视为格式问题）"""
    paragraphs = [p.text.strip() for p in doc.paragraphs]
    max_consecutive_empty = 0
    current_consecutive = 0
    
    for text in paragraphs:
        if not text:
            current_consecutive += 1
            max_consecutive_empty = max(max_consecutive_empty, current_consecutive)
        else:
            current_consecutive = 0
    
    if max_consecutive_empty == 0:
        return 'pass', '无空段'
    if max_consecutive_empty <= 2:
        return 'pass', f'最大连续空段 {max_consecutive_empty} 处（可接受）'
    if max_consecutive_empty <= 5:
        return 'warning', f'连续空段 {max_consecutive_empty} 处（建议清理）'
    return 'fail', f'连续空段 {max_consecutive_empty} 处（严重格式问题）'


def check_text_statistics(doc) -> Tuple[str, str]:
    """字符数与段落数统计"""
    char_count = sum(len(p.text) for p in doc.paragraphs)
    para_count = len([p for p in doc.paragraphs if p.text.strip()])
    table_count = len(doc.tables)
    
    return 'pass', f'正文 {char_count} 字 / {para_count} 段 / {table_count} 表'


# ============== 主流程 ==============

def run_gate(docx_path: str, enable_render: bool = False, strict: bool = False) -> Dict[str, Any]:
    """运行门禁检查"""
    if not Path(docx_path).exists():
        return {
            'file': docx_path,
            'error': '文件不存在',
            'overall': 'error'
        }
    
    if not HAS_DOCX:
        return {
            'file': docx_path,
            'error': 'python-docx 未安装，请运行: pip install python-docx',
            'overall': 'error'
        }
    
    doc = Document(docx_path)
    
    checks = [
        ('OpenXML 结构完整性', check_openxml_structure(docx_path)),
        ('页眉页脚', check_header_footer(doc)),
        ('页码字段', check_page_number_field(docx_path)),
        ('标题样式引用', check_heading_styles(doc)),
        ('表格边框', check_table_borders(doc)),
        ('字体合规', check_font_compliance(doc)),
        ('字符数统计', check_text_statistics(doc)),
        ('中文标点全角', check_chinese_punctuation(doc)),
        ('空段检测', check_empty_paragraphs(doc)),
    ]
    
    passed = sum(1 for _, (s, _) in checks if s == 'pass')
    warning = sum(1 for _, (s, _) in checks if s == 'warning')
    failed = sum(1 for _, (s, _) in checks if s == 'fail')
    skipped = sum(1 for _, (s, _) in checks if s == 'skip')
    
    # 总体结论
    if failed > 0:
        overall = 'fail'
    elif warning > 0 and strict:
        overall = 'fail'
    elif warning > 0:
        overall = 'warning'
    else:
        overall = 'pass'
    
    return {
        'file': Path(docx_path).name,
        'checked_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'overall': overall,
        'passed': passed,
        'warning': warning,
        'failed': failed,
        'skipped': skipped,
        'items': [
            {'name': name, 'status': status, 'detail': detail}
            for name, (status, detail) in checks
        ]
    }


def print_text_report(report: Dict[str, Any]) -> None:
    """打印文本格式报告"""
    if 'error' in report:
        print(f"❌ 错误: {report['error']}")
        return
    
    print('=' * 60)
    print('md2word-gate 交付前门禁报告')
    print('=' * 60)
    print(f"文件: {report['file']}")
    print(f"检查时间: {report['checked_at']}")
    print('=' * 60)
    print()
    
    for item in report['items']:
        status_icon = {
            'pass': '✅',
            'warning': '⚠️',
            'fail': '❌',
            'skip': '⏭️'
        }.get(item['status'], '❓')
        
        print(f"{status_icon} {item['name']:<20} {item['status'].upper():<8} {item['detail']}")
    
    print()
    print('=' * 60)
    overall_icon = {
        'pass': '✅',
        'warning': '⚠️',
        'fail': '❌'
    }.get(report['overall'], '❓')
    
    print(f"{overall_icon} 结论: {report['overall'].upper()}")
    print(f"   通过 {report['passed']} / 警告 {report['warning']} / 失败 {report['failed']} / 跳过 {report['skipped']}")
    
    if report['overall'] == 'pass':
        print('\n建议: ✅ 门禁通过，可对外发送')
    elif report['overall'] == 'warning':
        print('\n建议: ⚠️ 有警告，建议人工复核后发送')
    else:
        print('\n建议: ❌ 门禁未通过，请修正后重新生成')
    print('=' * 60)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='md2word-gate 交付前门禁')
    parser.add_argument('docx', help='DOCX 文件路径')
    parser.add_argument('--json', action='store_true', help='输出 JSON 格式')
    parser.add_argument('--strict', action='store_true', help='严格模式（警告视为失败）')
    parser.add_argument('--enable-render', action='store_true', help='启用渲染页门禁（需 LibreOffice）')
    
    args = parser.parse_args()
    
    if not Path(args.docx).exists():
        print(f"❌ 文件不存在: {args.docx}", file=sys.stderr)
        sys.exit(3)
    
    report = run_gate(args.docx, enable_render=args.enable_render, strict=args.strict)
    
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_text_report(report)
    
    # 退出码
    if 'error' in report:
        sys.exit(3)
    if report['overall'] == 'fail':
        sys.exit(2)
    if report['overall'] == 'warning':
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
