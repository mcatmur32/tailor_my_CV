from jinja2 import Environment, FileSystemLoader
from pathlib import Path

"""def generate_latex(cv_object):
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('cv_template_2.tex')

    rendered_latex = template.render(cv=cv_object)

    output_path = Path("output_cv.tex")
    output_path.write_text(rendered_latex, encoding='utf-8')
    return output_path"""


def generate_latex(cv_object):
    env = Environment(
        loader=FileSystemLoader('.'),
        block_start_string='((*',
        block_end_string='*))',
        variable_start_string='(((',
        variable_end_string=')))',
        comment_start_string='((#',
        comment_end_string='#))'
    )

    template = env.get_template('cv_template_2.tex')
    rendered_latex = template.render(cv=cv_object)

    output_path = Path("output_cv.tex")
    output_path.write_text(rendered_latex, encoding='utf-8')
    return output_path
