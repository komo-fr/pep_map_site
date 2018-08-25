import datetime
from datetime import datetime as dt

from bokeh.plotting import figure
from bokeh.models.sources import ColumnDataSource
from bokeh.models import HoverTool, TapTool, ResetTool, BoxZoomTool, SaveTool
from bokeh.models import Arrow, VeeHead, FuncTickFormatter, OpenURL
from bokeh.models.glyphs import MultiLine
from bokeh.models.tickers import FixedTicker
from networkx.classes.graph import Graph
import pandas as pd

from .util import convert_node_attribute2df
from .style_setting import STATUS_COLOR_MAP_DICT, PYTHON_YELLOW_COLOR_CODE


def get_timeline_plot_range(source_graph: Graph) -> (dt, dt):
    """

    :param source_graph:
    :return:
    """
    node_dict = dict(source_graph.nodes(data=True))
    date_list = [value['Created_dt'] for key, value in node_dict.items()]
    min_date = dt(min(date_list).year, 1, 1)
    max_date = dt(max(date_list).year, 12, 31)
    return min_date, max_date


def generate_timeline_data_source(source_graph: Graph) -> ColumnDataSource:
    """

    :param source_graph:
    :return:
    """
    df = convert_node_attribute2df(source_graph)
    df['y'] = 1

    df['status_node_color'] = df['Status'].apply(lambda x:
                                                 STATUS_COLOR_MAP_DICT[x])
    df['PythonVersion'] = df['Python-Version'].apply(lambda x:
                                                     x if x == x
                                                     else 'No Data')

    df = df[['PEP', 'Title', 'Type', 'Status',
             'Created', 'Created_dt', 'status_node_color',
             'y', 'PythonVersion']]
    return ColumnDataSource(df)


def generate_timeline_label_data_source(source_graph: Graph) -> ColumnDataSource:
    """

    :param source_graph:
    :return:
    """
    df = convert_node_attribute2df(source_graph)

    df = df.reset_index()
    df['pep_id'] = df['index']
    df = df.set_index('index')
    df = df[['pep_id', 'Created_dt']]
    df['displayed_text'] = [""] * len(df.index)  # 初期状態では表示しないので空文字を格納しておく
    df['y'] = 1.01
    return ColumnDataSource(df)


def generate_timeline_desc_data_source(xs: list,
                                       ys: list,
                                       font_size: int=18) -> ColumnDataSource:
    """

    :param xs:
    :param ys:
    :param font_size:
    :return:
    """
    texts = ['', '']
    font_size = 14  # debug++
    sizes = ['{}pt'.format(font_size)] * len(xs)
    return ColumnDataSource(dict(x=xs, y=ys, text=texts, size=sizes))


def setup_timeline_axis(plot: figure) -> None:
    """

    :param plot:
    :return:
    """
    start_date, end_date = plot.x_range.start, plot.x_range.end

    # 主目盛り幅の作成
    dt_dick = list(pd.date_range(start=start_date,
                                 end=end_date,
                                 freq='6M'))
    dt_dick_values = pd.to_datetime(dt_dick).astype(int)
    dt_dick_values = list(dt_dick_values / 10 ** 6)

    # 補助目盛り幅の作成
    minor_dt_dick = list(pd.date_range(start=start_date,
                                       end=end_date,
                                       freq='6M'))
    minor_dt_dick_values = pd.to_datetime(minor_dt_dick).astype(int)
    minor_dt_dick_values = list(minor_dt_dick_values / 10 ** 6)

    # 軸の設定
    plot.xaxis.axis_label = "Creation date of the PEPs " \
                            + "(Some PEPs don't have 'Created' field)"
    plot.xaxis.ticker = FixedTicker(ticks=dt_dick_values)
    plot.yaxis.visible = False

    # 目盛線の設定
    plot.xgrid.ticker = FixedTicker(ticks=minor_dt_dick_values,
                                    num_minor_ticks=1)

    format_datetime_code = """
    var date = new Date(tick)
    var month = date.getUTCMonth(date)
    if ( month == 0) { // January
    return date.getUTCFullYear(date)
    } else {
    return ""
    }
    """

    plot.xaxis.formatter = FuncTickFormatter(code=format_datetime_code)


def setup_timeline_tools(plot: figure) -> None:
    """

    :param plot:
    :return:
    """
    timeline_hover = HoverTool(tooltips=[('PEP', '@PEP'),
                                         ('Title', '@Title'),
                                         ('Type', '@Type'),
                                         ('Status', '@Status'),
                                         ('Created', '@Created'),
                                         ('Python-Version', '@PythonVersion')],
                               names=["circle"])

    release_hover = HoverTool(tooltips=[('Version', '@release_number'),
                                        ('Release Date', '@release_date_str')],
                              names=["release_label"])
    plot.add_tools(timeline_hover, release_hover,
                   BoxZoomTool(), ResetTool(), SaveTool())
    url = 'https://www.python.org/dev/peps/pep-@index/'
    taptool = plot.select(type=TapTool)
    taptool.callback = OpenURL(url=url)
    taptool.names = ['circle']


def setup_timeline_backend_parts(plot: figure,
                                 desc_label_source: ColumnDataSource) -> None:
    """

    :param plot:
    :param desc_label_source:
    :return:
    """
    start_date, end_date = plot.x_range.start, plot.x_range.end
    arrow_x = start_date + datetime.timedelta(days=180)

    # 補助線を引く
    plot.line([start_date, end_date], [1, 1],
              line_width=3, line_color='pink')
    plot.line([start_date, end_date], [0.5, 0.5],
              line_width=3, line_dash='dotted', line_color='pink')
    plot.line([start_date, end_date], [1.5, 1.5],
              line_width=3, line_dash='dotted', line_color='pink')

    # 矢印を表示する
    plot.add_layout(Arrow(end=VeeHead(size=15), line_color='black',
                          x_start=arrow_x, y_start=1.4,
                          x_end=arrow_x, y_end=1.1))
    plot.add_layout(Arrow(end=VeeHead(size=15), line_color='black',
                          x_start=arrow_x, y_start=0.9,
                          x_end=arrow_x, y_end=0.6))

    plot.text(source=desc_label_source, x='x', y='y',
              text='text', text_font_size='size', text_alpha=0.8)


def generate_timeline_plot(source_graph: Graph,
                           circle_source: ColumnDataSource,
                           label_source: ColumnDataSource,
                           desc_label_source: ColumnDataSource,
                           release_source_dict: dict) -> figure:
    """

    :param source_graph:
    :param circle_source:
    :param label_source:
    :param desc_label_source:
    :param release_source_dict:
    :return:
    """
    start_date, end_date = get_timeline_plot_range(source_graph)
    x_range = (start_date, end_date)

    plot = figure(plot_width=1200, plot_height=300,
                  x_axis_type='datetime',
                  tools='tap',
                  x_range=x_range, y_range=(0, 2.3))

    setup_timeline_tools(plot)
    setup_timeline_axis(plot)
    setup_timeline_backend_parts(plot, desc_label_source)

    # 点を表示する
    plot.circle(x='Created_dt', y='y',
                fill_color='status_node_color', fill_alpha=0.9,
                line_color='status_node_color', line_alpha=1,
                source=circle_source, size=10, name='circle')

    # PEPの番号を表示する
    plot.text(source=label_source, x='Created_dt', y='y',
              text='displayed_text', text_font_size='10pt')

    plot.text(source=release_source_dict['py2_release_label_source'],
              x='x', y='y',
              text='text', text_font_size='10pt',
              text_alpha='alpha', name='release_label',
              text_color='color')
    plot.text(source=release_source_dict['py3_release_label_source'],
              x='x', y='y',
              text='text', text_font_size='10pt',
              text_alpha='alpha', name='release_label',
              text_color='color')

    glyph = MultiLine(xs="x", ys="y", line_color='color', line_width=1,
                      line_alpha='alpha')
    plot.add_glyph(release_source_dict['py2_release_line_source'], glyph)
    plot.add_glyph(release_source_dict['py3_release_line_source'], glyph)

    return plot


def release_number2label(release_number: str) -> str:
    label = release_number.replace('Python ', '')
    label = label[:-2]
    label = label.replace('Python2', 'Python 2')
    label = label.replace('Python3', 'Python 2')
    return label


def version2color(major_version: int) -> str:
    color_map = {2: '#DDAD3E',  # Yellow
                 3: '#2E6495'}  # Blue
    return color_map[major_version]


def generate_release_label_source(source_df: pd.DataFrame,
                                  major_version: int,
                                  pos_x: datetime) -> ColumnDataSource:
    df = source_df.copy()

    df = df[df.micro == 0]
    df = df[['release_number', 'release_date', 'major']]
    df['color'] = df.major.apply(lambda x: version2color(major_version))

    df = df[df['major'] == major_version]

    series = pd.Series(['Python{} release ->'.format(major_version), pos_x,
                        PYTHON_YELLOW_COLOR_CODE, 2],
                       index=df.columns)
    df = df.append(series, ignore_index=True)
    df['x'] = df['release_date'].apply(
        lambda x: x + datetime.timedelta(days=10))
    df['y'] = df['major'].apply(lambda x: 2.15 if x == 2 else 2.0)
    df['alpha'] = 1

    df['text'] = df.release_number.apply(lambda x: release_number2label(x))
    df['release_date_str'] = df['release_date'].apply(
        lambda x: x.strftime('%Y-%m-%d'))

    return ColumnDataSource(df)


def generate_release_line_data_source(source_df: pd.DataFrame,
                                      major_version: int) -> ColumnDataSource:
    df = source_df.copy()

    df = df[['release_number', 'release_date', 'major', 'micro']]
    df['color'] = df.major.apply(lambda x: version2color(major_version))
    df['x'] = df['release_date'].apply(lambda x: [x, x])
    df['y'] = df['release_date'].apply(lambda x: [2.3, 0])
    df['alpha'] = 1

    df = df[df['major'] == major_version]
    df = df[df.micro == 0]

    return ColumnDataSource(df)
