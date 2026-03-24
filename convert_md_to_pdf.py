import os
import sys
import textwrap

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Preformatted, SimpleDocTemplate, Spacer


def wrap_code_line(line, width=74):
    if not line:
        return [""]
    return textwrap.wrap(
        line,
        width=width,
        expand_tabs=False,
        replace_whitespace=False,
        drop_whitespace=False,
        break_long_words=True,
        break_on_hyphens=False,
    ) or [line]


input_path = sys.argv[1] if len(sys.argv) > 1 else "WDD_Assignment_3.md"
output_path = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(input_path)[0] + ".pdf"

with open(input_path, "r", encoding="utf-8") as f:
    content = f.read()

lines = content.split("\n")
story = []
styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "Title",
    parent=styles["Heading1"],
    fontSize=18,
    spaceAfter=28,
)

heading_style = ParagraphStyle(
    "Heading",
    parent=styles["Heading2"],
    fontSize=14,
    spaceAfter=18,
)

normal_style = ParagraphStyle(
    "NormalText",
    parent=styles["Normal"],
    spaceAfter=10,
)

code_style = ParagraphStyle(
    "Code",
    parent=styles["Normal"],
    fontName="Courier",
    fontSize=8,
    leading=10,
    leftIndent=12,
    rightIndent=12,
    spaceAfter=10,
)

i = 0
while i < len(lines):
    raw_line = lines[i]
    line = raw_line.strip()

    if line.startswith("# "):
        story.append(Paragraph(line[2:], title_style))
    elif line.startswith("## "):
        story.append(Paragraph(line[3:], heading_style))
    elif line.startswith("```"):
        code_lines = []
        i += 1
        while i < len(lines) and not lines[i].strip().startswith("```"):
            code_lines.append(lines[i])
            i += 1

        wrapped_code = []
        for code_line in code_lines:
            wrapped_code.extend(wrap_code_line(code_line))
        story.append(Preformatted("\n".join(wrapped_code), code_style))
    elif line.startswith("**") and line.endswith("**"):
        story.append(Paragraph(line[2:-2], styles["Italic"]))
    elif line.startswith("- "):
        story.append(Paragraph("&bull; " + line[2:], normal_style))
    elif line:
        story.append(Paragraph(raw_line, normal_style))
    else:
        story.append(Spacer(1, 10))
    i += 1

doc = SimpleDocTemplate(
    output_path,
    pagesize=letter,
    leftMargin=0.75 * inch,
    rightMargin=0.75 * inch,
    topMargin=1 * inch,
    bottomMargin=1 * inch,
)
doc.build(story)
