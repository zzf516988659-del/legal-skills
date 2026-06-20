#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
contract-templates 模板渲染脚本
致敬文格（lilialla/legal-document-format-skill）的"确定性模式"思路。

功能:
  1. 单份渲染：--data JSON 字符串
  2. 批量渲染：--data-file JSON 文件（每行一条数据）
  3. 支持字段校验：必填字段缺失时报警
  4. 支持可选字段默认值：{{XXX:default}}
  5. 输出 Markdown，可选触发 md2word + md2word-gate

用法:
  # 单份
  python3 render_template.py templates/律师函.md --data '{"LETTER_NO":"信拓律函字[2026]第 001 号"}' --output /tmp/律师函_001.md

  # 批量
  python3 render_template.py templates/律师函.md --data-file data.json --output-dir ./output/
"""

import sys
import os
import re
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple


def parse_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
    """解析 YAML frontmatter（仅支持简单 key: value 和 key: [list]）"""
    if not content.startswith('---'):
        return {}, content
    
    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}, content
    
    frontmatter_text = parts[1].strip()
    body = parts[2].lstrip('\n')
    
    fm = {}
    current_list_key = None
    
    for line in frontmatter_text.split('\n'):
        line_stripped = line.strip()
        if not line_stripped or line_stripped.startswith('#'):
            continue
        # 列表项
        if line.startswith('  - ') or line.startswith('- '):
            value = line.lstrip(' -').strip()
            if current_list_key and isinstance(fm.get(current_list_key), list):
                # 去除行内注释
                value = re.sub(r'\s+#.*$', '', value).strip()
                fm[current_list_key].append(value)
            continue
        # 键值对
        m = re.match(r'^(\w+):\s*(.*)$', line)
        if m:
            key = m.group(1)
            value = m.group(2).strip()
            # 去除行内注释
            value = re.sub(r'\s+#.*$', '', value).strip()
            if not value:
                # 多行列表的起始
                current_list_key = key
                fm[key] = []
            elif value.startswith('[') and value.endswith(']'):
                # 去除括号后分割，同时去除项内的注释
                items = []
                for v in value[1:-1].split(','):
                    v_clean = re.sub(r'\s+#.*$', '', v).strip()
                    if v_clean:
                        items.append(v_clean)
                fm[key] = items
                current_list_key = None
            else:
                fm[key] = value
                current_list_key = None
    
    return fm, body


def render_template(template_path: str, data: Dict[str, str], output_path: str) -> Tuple[bool, str]:
    """渲染单份模板"""
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    fm, body = parse_frontmatter(content)
    
    # 字段校验
    required = fm.get('required_fields', [])
    missing = [f for f in required if f not in data or not data[f]]
    if missing:
        return False, f'必填字段缺失: {", ".join(missing)}'
    
    # 替换字段
    # 支持三种语法：{{XXX}} {{XXX?}} {{XXX:default}}
    def replace_field(match):
        field = match.group(1)
        has_default = '?' in field
        if ':' in field:
            field_name, default_value = field.split(':', 1)
            return data.get(field_name, default_value)
        elif has_default:
            field_name = field.rstrip('?')
            return data.get(field_name, '（待补）')
        else:
            if field not in data:
                return '（待补）'
            return str(data[field])
    
    rendered = re.sub(r'\{\{([^\}]+)\}\}', replace_field, body)
    
    # 写入输出
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(rendered)
    
    return True, output_path


def render_batch(template_path: str, data_file: str, output_dir: str) -> List[Tuple[bool, str]]:
    """批量渲染"""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    results = []
    with open(data_file, 'r', encoding='utf-8') as f:
        # 支持 JSON Lines（每行一条 JSON）或普通 JSON 数组
        content = f.read().strip()
        if content.startswith('['):
            data_list = json.loads(content)
        else:
            data_list = [json.loads(line) for line in content.split('\n') if line.strip()]
    
    for i, data in enumerate(data_list, 1):
        # 文件名用 INDEX 或 CASE_NO 字段
        filename = data.get('LETTER_NO', f'output_{i:03d}').replace('/', '_').replace(' ', '_')
        output_path = os.path.join(output_dir, f'{filename}.md')
        
        ok, result = render_template(template_path, data, output_path)
        results.append((ok, result))
    
    return results


def convert_to_docx(md_path: str, docx_path: str = None) -> str:
    """走 md2word 转 Word"""
    if docx_path is None:
        docx_path = md_path.replace('.md', '.docx')
    
    md2word = os.path.expanduser('~/.openclaw/workspace/skills/legal-skills-github/skills/md2word/scripts/md2word.py')
    if not os.path.exists(md2word):
        return f'md2word 脚本不存在: {md2word}'
    
    try:
        result = subprocess.run(
            ['python3', md2word, md_path, '--preset=legal', docx_path],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            return docx_path
        return f'md2word 失败: {result.stderr[:200]}'
    except Exception as e:
        return f'md2word 异常: {str(e)[:200]}'


def main():
    parser = argparse.ArgumentParser(description='contract-templates 模板渲染')
    parser.add_argument('template', help='模板文件路径')
    parser.add_argument('--data', help='单份数据 JSON 字符串')
    parser.add_argument('--data-file', help='批量数据 JSON 文件')
    parser.add_argument('--output', help='单份输出文件路径')
    parser.add_argument('--output-dir', help='批量输出目录')
    parser.add_argument('--convert', action='store_true', help='同时转 Word')
    
    args = parser.parse_args()
    
    if not Path(args.template).exists():
        print(f'❌ 模板不存在: {args.template}')
        sys.exit(1)
    
    if args.data:
        # 单份
        try:
            data = json.loads(args.data)
        except json.JSONDecodeError as e:
            print(f'❌ JSON 解析失败: {e}')
            sys.exit(1)
        
        if not args.output:
            print('❌ 单份模式必须指定 --output')
            sys.exit(1)
        
        ok, result = render_template(args.template, data, args.output)
        if ok:
            print(f'✅ 已生成: {result}')
            if args.convert:
                docx = convert_to_docx(result)
                if docx.endswith('.docx'):
                    print(f'✅ 已转 Word: {docx}')
                else:
                    print(f'⚠️ 转 Word 失败: {docx}')
        else:
            print(f'❌ 渲染失败: {result}')
            sys.exit(1)
    
    elif args.data_file:
        # 批量
        if not args.output_dir:
            print('❌ 批量模式必须指定 --output-dir')
            sys.exit(1)
        
        results = render_batch(args.template, args.data_file, args.output_dir)
        success = sum(1 for ok, _ in results if ok)
        failed = len(results) - success
        
        print(f'✅ 批量完成: 成功 {success} / 失败 {failed} / 共 {len(results)}')
        for ok, result in results:
            icon = '✅' if ok else '❌'
            print(f'  {icon} {result}')
        
        if args.convert and success > 0:
            print('\n📄 批量转 Word 中...')
            for ok, result in results:
                if ok:
                    docx = convert_to_docx(result)
                    if not docx.endswith('.docx'):
                        print(f'  ⚠️ {result} -> {docx}')
    
    else:
        print('❌ 必须指定 --data 或 --data-file')
        sys.exit(1)


if __name__ == '__main__':
    main()
