from bokeh.models import Div
from bokeh.models.sources import ColumnDataSource
from bokeh.layouts import column, row
from networkx import DiGraph

from .util import convert_node_attribute2df
from .style_setting import STATUS_COLOR_MAP_DICT, STATUS_FONT_COLOR_MAP_DICT


def generate_node_data_source(source_graph: DiGraph) -> ColumnDataSource:
    """
    ノード情報のColumnDataSourceを生成する
    :param source_graph: ソースとなるグラフ構造
    :return:
    """
    df = convert_node_attribute2df(source_graph)

    df = df.reset_index()
    df['pep_id'] = df['index']
    df = df.set_index('index')
    df['in_edge_nodes'] = df.pep_id.apply(lambda x:
                                          [edge[0] for edge
                                          in source_graph.in_edges(x)])
    df['out_edge_nodes'] = df.pep_id.apply(lambda x:
                                           [edge[1]
                                           for edge in source_graph.out_edges(x)])
    df['in_degree'] = df.pep_id.apply(lambda x: source_graph.in_degree()[x])
    df['out_degree'] = df.pep_id.apply(lambda x: source_graph.out_degree()[x])
    del df['pep_id']

    df['Created_str'] = df.Created_dt.apply(lambda x: x.strftime('%Y-%m-%d')
                                            if x == x else 'No Data')
    df['PythonVersion'] = df['Python-Version'].apply(lambda x:
                                                     x if x == x
                                                     else 'No Data')
    df['status_node_color'] = df['Status'].apply(lambda x:
                                                 STATUS_COLOR_MAP_DICT[x])
    df['status_font_color'] = df['Status'].apply(lambda x:
                                                 STATUS_FONT_COLOR_MAP_DICT[x])

    return ColumnDataSource(df)


def generate_color_description_component() -> column:
    """
    色の説明書きのコンポーネントを作成する
    :return:
    """
    div = Div(width=200, height=8, style={'color': '#545454'})
    left_div = Div(width=120, height=55, style={'color': '#545454'})
    right_div = Div(width=120, height=55, style={'color': '#545454'})

    div.text = 'Color means the status of PEPs.'
    left_div.text = """<img src="image/draft_icon.png"> Draft<br>
<img src="image/provisional_icon.png"> Provisional<br>
<img src="image/accepted_icon.png"> Accepted<br>
<img src="image/final_icon.png"> Final<br>
<img src="image/active_icon.png"> Active<br><br>
"""
    right_div.text = """<img src="image/deffered_icon.png"> Deferred<br>
<img src="image/withdrawned_icon.png"> Withdrawn<br>
<img src="image/rejected_icon.png"> Rejected<br>
<img src="image/superseded_icon.png"> Superseded<br><br>
"""

    component = column(div, row(left_div, right_div))
    return component
