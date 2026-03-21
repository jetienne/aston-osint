import os

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=True)


def generate_pdf(brief: dict) -> bytes:
    template = _env.get_template('report.html')
    html_string = template.render(brief=brief)
    return HTML(string=html_string).write_pdf()
