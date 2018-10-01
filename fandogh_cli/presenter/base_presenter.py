from beautifultable import BeautifulTable
import os

from fandogh_cli.utils import get_window_width

FANDOGH_DEBUG = os.environ.get('FANDOGH_DEBUG', False)


def _create_table(columns):
    min_width = 80
    width = max(min_width, get_window_width() or 160)
    table = BeautifulTable(max_width=width)
    table.column_headers = columns
    table.row_separator_char = ''
    return table


def table_renderer(data, **kwargs):
    headers = kwargs.get('headers')
    column_names = kwargs.get('columns')
    table = _create_table(headers)
    for item in data:
        row = []
        for cn in column_names:
            if item.get(cn) is True:
                row.append('Yes')
            elif item.get(cn) is False:
                row.append('No')
            else:
                row.append(item.get(cn))
        table.append_row(row)
    return table


def text_renderer(data, **kwargs):
    field = kwargs.get('field', None)
    if field:
        return str(data.get(field) or '')
    else:
        return str(data or '')


renderers = {
    'table': table_renderer,
    'text': text_renderer
}


def present(data_provider, pre='', post='', renderer='text', **kwargs):
    data = data_provider()
    rendered = renderers.get(renderer)(data, **kwargs)
    return pre + str(rendered) + post
