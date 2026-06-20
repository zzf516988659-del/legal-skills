#!/usr/bin/env python3
"""
创建信拓集团律师函 DOCX 模板（含页眉/页脚/标准格式）
用法: python3 make_letter_template.py
输出: docx_templates/律师函_template.docx
"""

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy

def set_font(run, font_name_cn, font_name_en, size_pt, bold=False):
    """设置 run 的字体"""
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.name = font_name_en
    run._element.rPr.rFonts.set(qn('w:eastAsia'), font_name_cn)

def add_header_footer(doc):
    """添加页眉页脚"""
    section = doc.sections[0]
    
    # 页眉
    header = section.header
    header.is_linked_to_previous = False
    header_para = header.paragraphs[0]
    header_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = header_para.add_run('江苏信拓建设（集团）股份有限公司')
    set_font(run, '仿宋_GB2312', 'Times New Roman', 10.5)
    
    # 添加水平线
    p = header_para._p
    pPr = p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '6')
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), 'auto')
    pBdr.append(bottom)
    pPr.append(pBdr)
    
    # 页脚
    footer = section.footer
    footer.is_linked_to_previous = False
    footer_para = footer.paragraphs[0]
    footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # 使用 PAGE 和 NUMPAGES 字段
    run_pre = footer_para.add_run('第 ')
    set_font(run_pre, '仿宋_GB2312', 'Times New Roman', 10.5)
    
    # PAGE 字段
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')
    instrText = OxmlElement('w:instrText')
    instrText.text = ' PAGE '
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'end')
    
    run_page = footer_para.add_run()
    run_page._r.append(fldChar1)
    run_page._r.append(instrText)
    run_page._r.append(fldChar2)
    set_font(run_page, '仿宋_GB2312', 'Times New Roman', 10.5)
    
    run_post = footer_para.add_run(' 页 共 ')
    set_font(run_post, '仿宋_GB2312', 'Times New Roman', 10.5)
    
    # NUMPAGES 字段
    fldChar3 = OxmlElement('w:fldChar')
    fldChar3.set(qn('w:fldCharType'), 'begin')
    instrText2 = OxmlElement('w:instrText')
    instrText2.text = ' NUMPAGES '
    fldChar4 = OxmlElement('w:fldChar')
    fldChar4.set(qn('w:fldCharType'), 'end')
    
    run_total = footer_para.add_run()
    run_total._r.append(fldChar3)
    run_total._r.append(instrText2)
    run_total._r.append(fldChar4)
    set_font(run_total, '仿宋_GB2312', 'Times New Roman', 10.5)
    
    run_end = footer_para.add_run(' 页')
    set_font(run_end, '仿宋_GB2312', 'Times New Roman', 10.5)

def set_page_margins(section):
    """设置页边距"""
    section.top_margin = Cm(2.54)
    section.bottom_margin = Cm(2.54)
    section.left_margin = Cm(2.54)
    section.right_margin = Cm(2.54)

def add_meta_block(doc, fields):
    """添加文件信息块"""
    for label, key in fields:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        run_label = p.add_run(f'{label}：')
        set_font(run_label, '仿宋_GB2312', 'Times New Roman', 14)
        run_value = p.add_run(f'{{{{{key}}}}}')
        set_font(run_value, '仿宋_GB2312', 'Times New Roman', 14)

def add_body_paragraph(doc, text, indent=False, bold=False, size=14):
    """添加正文段落"""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    if indent:
        p.paragraph_format.first_line_indent = Cm(0.74)  # 2字符
    run = p.add_run(text)
    set_font(run, '仿宋_GB2312', 'Times New Roman', size, bold)
    return p

def create_letter_template():
    doc = Document()
    section = doc.sections[0]
    set_page_margins(section)
    add_header_footer(doc)
    
    # 默认样式：仿宋 14pt
    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(14)
    style._element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋_GB2312')
    
    # 元信息块
    add_meta_block(doc, [
        ('文件编号', 'LETTER_NO'),
        ('发函日期', 'ISSUE_DATE'),
        ('发函单位', 'ISSUER'),
    ])
    
    # 收函人
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run('致：{{RECIPIENT}}')
    set_font(run, '仿宋_GB2312', 'Times New Roman', 14, bold=True)
    
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run('地址：{{RECIPIENT_ADDR}}')
    set_font(run, '仿宋_GB2312', 'Times New Roman', 14)
    
    # 分隔线
    doc.add_paragraph()
    
    # 标题
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run('律 师 函')
    run.font.size = Pt(22)
    run.font.bold = True
    run.font.name = '黑体'
    run._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
    
    # 引言段
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.first_line_indent = Cm(0.74)
    run = p.add_run('{{ISSUER}}（以下简称"本公司"）就 {{SUBJECT}} 一事，委托本公司常年法律顾问，致函贵方如下：')
    set_font(run, '仿宋_GB2312', 'Times New Roman', 14)
    
    # 一、事实
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run('一、事实')
    set_font(run, '仿宋_GB2312', 'Times New Roman', 14, bold=True)
    
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.first_line_indent = Cm(0.74)
    run = p.add_run('{{FACT}}')
    set_font(run, '仿宋_GB2312', 'Times New Roman', 14)
    
    # 二、主张
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run('二、本公司主张')
    set_font(run, '仿宋_GB2312', 'Times New Roman', 14, bold=True)
    
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.first_line_indent = Cm(0.74)
    run = p.add_run('依据《中华人民共和国民法典》及相关法律法规，结合上述事实，本公司主张如下：')
    set_font(run, '仿宋_GB2312', 'Times New Roman', 14)
    
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.first_line_indent = Cm(0.74)
    run = p.add_run('{{DEMAND}}')
    set_font(run, '仿宋_GB2312', 'Times New Roman', 14)
    
    # 三、履行期限
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run('三、履行期限')
    set_font(run, '仿宋_GB2312', 'Times New Roman', 14, bold=True)
    
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.first_line_indent = Cm(0.74)
    run = p.add_run('请贵方于 {{DEADLINE}} 之前履行上述义务。')
    set_font(run, '仿宋_GB2312', 'Times New Roman', 14)
    
    # 四、法律后果
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run('四、法律后果')
    set_font(run, '仿宋_GB2312', 'Times New Roman', 14, bold=True)
    
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.first_line_indent = Cm(0.74)
    run = p.add_run('如贵方未在上述期限内履行，{{CONSEQUENCE}}。本公司将依法采取下列措施维护自身合法权益，一切法律后果由贵方自行承担：')
    set_font(run, '仿宋_GB2312', 'Times New Roman', 14)
    
    # 列表项
    for item in ['向有管辖权的人民法院提起诉讼', '向有管辖权的人民法院申请财产保全', '依法主张违约金、赔偿金及实现债权的全部费用', '其他依法可采取的救济措施']:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.left_indent = Cm(0.74)
        p.paragraph_format.first_line_indent = Cm(-0.37)
        run = p.add_run(f'— {item}')
        set_font(run, '仿宋_GB2312', 'Times New Roman', 14)
    
    # 五、声明
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run('五、声明')
    set_font(run, '仿宋_GB2312', 'Times New Roman', 14, bold=True)
    
    for text in [
        '本律师函不影响本公司依据法律法规及合同约定所享有的其他权利，亦不构成本公司放弃任何权利的意思表示。',
        '本律师函以特快专递（EMS）方式送达贵方，同时以电子邮件方式发送至贵方预留的电子邮箱。送达即视为贵方收悉。',
    ]:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.first_line_indent = Cm(0.74)
        run = p.add_run(text)
        set_font(run, '仿宋_GB2312', 'Times New Roman', 14)
    
    # 落款
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run('特此函告。')
    set_font(run, '仿宋_GB2312', 'Times New Roman', 14)
    
    doc.add_paragraph()
    
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(0)
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = p.add_run('{{ISSUER}}')
    set_font(run, '仿宋_GB2312', 'Times New Roman', 14)
    
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = p.add_run('{{ISSUE_DATE}}')
    set_font(run, '仿宋_GB2312', 'Times New Roman', 14)
    
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(6)
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = p.add_run('（盖章）')
    set_font(run, '仿宋_GB2312', 'Times New Roman', 14)
    
    return doc

if __name__ == '__main__':
    output_path = '/home/administrator/.openclaw/workspace/skills/legal-skills-github/skills/contract-templates/docx_templates/律师函_template.docx'
    doc = create_letter_template()
    doc.save(output_path)
    print(f'律师函模板已保存: {output_path}')