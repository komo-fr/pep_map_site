from bokeh.models.sources import ColumnDataSource
from bokeh.models.widgets import DataTable, TableColumn
from bokeh.models.widgets.tables import HTMLTemplateFormatter
from networkx.classes.graph import Graph

from .util import convert_node_attribute2df


def generate_data_table_data_source(source_graph: Graph) -> ColumnDataSource:
    """

    :param source_graph:
    :return:
    """
    df = convert_node_attribute2df(source_graph)
    df['Created_str'] = df.Created_dt.apply(lambda x: x.strftime('%Y-%m-%d')
                                            if x == x else 'No Data')
    df = df[['PEP', 'Title', 'Status', 'Created_str', 'status_node_color']]
    return ColumnDataSource(df)


def generate_data_table(data_source: ColumnDataSource) -> DataTable:
    """

    :param data_source:
    :return:
    """
    index_template = "<a href='https://www.python.org/dev/peps/pep-<%= index %>' target='_blank'>" \
                     "PEP <%= PEP %>" \
                     "</a>"
    status_template = "<div style='background:<%= status_node_color %>; color:#FAFAFA; text-align:center'>" \
                      "<%= Status %>" \
                      "</div>"

    columns = [
        TableColumn(field='index', title='PEP', width=60,
                    formatter=HTMLTemplateFormatter(template=index_template)),
        TableColumn(field='Title', title='Title', width=280),
        TableColumn(field='Status', title='Status', width=80,
                    formatter=HTMLTemplateFormatter(template=status_template)),
        TableColumn(field='Created_str', title='Created', width=100),
    ]

    data_table = DataTable(source=data_source, columns=columns,
                           width=540, height=400,
                           row_headers=False)

    return data_table
