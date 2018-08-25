import argparse
import datetime

import pandas as pd
from bokeh.io import show, output_file
from bokeh.models import Div
from bokeh.models.callbacks import CustomJS
from bokeh.models.widgets import TextInput, CheckboxGroup
from bokeh.layouts import column, row
import networkx as nx

import component.component as compo
import component.table_component as table_compo
import component.timeline_component as tl_compo
from component.style_setting import BASE_FONT_COLOR, PYTHON_YELLOW_COLOR_CODE, PYTHON_BLUE_COLOR_CODE


def make_timeline_html(input_path: str, output_path: str) -> None:
    # Load Data
    pep_graph = nx.read_gpickle(input_path)

    # debug++ ここから
    path = 'data/python_release_info.csv'  # TODO inputで入力する
    release_df = pd.read_csv(path,
                             encoding='utf-8',
                             parse_dates=['release_date'])

    release_df = release_df[release_df.micro == 0]
    release_df['color'] = release_df.major.apply(lambda x: PYTHON_YELLOW_COLOR_CODE if x == 2 else PYTHON_BLUE_COLOR_CODE)  # 2, 3以外が出てきたら再考すること

    node_dict = dict(pep_graph.nodes(data=True))
    date_list = [value['Created_dt'] for key, value in node_dict.items()]

    min_date = datetime.datetime(min(date_list).year, 1, 1)
    py2_release_label_data_source = tl_compo.generate_release_label_source(release_df,
                                                                           major_version=2,
                                                                           pos_x=min_date)
    py3_release_label_data_source = tl_compo.generate_release_label_source(release_df,
                                                                           major_version=3,
                                                                           pos_x=min_date)

    py2_release_line_data_source = tl_compo.generate_release_line_data_source(release_df,
                                                                              major_version=2)
    py3_release_line_data_source = tl_compo.generate_release_line_data_source(release_df,
                                                                              major_version=3)

    release_source_dict = {'py2_release_label_source': py2_release_label_data_source,
                           'py3_release_label_source': py3_release_label_data_source,
                           'py2_release_line_source': py2_release_line_data_source,
                           'py3_release_line_source': py3_release_line_data_source
                           }

    # debug++ ここまで

    all_pep_data_source = compo.generate_node_data_source(pep_graph)

    # DataTable用のデータソースを用意する
    linked_from_table_source = table_compo.generate_data_table_data_source(pep_graph)
    link_to_table_source = table_compo.generate_data_table_data_source(pep_graph)

    linked_from_data_table = table_compo.generate_data_table(linked_from_table_source)
    link_to_data_table = table_compo.generate_data_table(link_to_table_source)

    linked_from_table_title_div = Div(text='<strong>PEP N is linked from ...</strong>',
                                      style={'color': BASE_FONT_COLOR})
    link_to_table_title_div = Div(text='<strong>PEP N links to ...</strong>',
                                  style={'color': BASE_FONT_COLOR})

    # Timeline用のデータソースを用意する
    timeline_display_circle_source = tl_compo.generate_timeline_data_source(pep_graph)
    timeline_label_source = tl_compo.generate_timeline_label_data_source(pep_graph)
    desc_start_date, _ = tl_compo.get_timeline_plot_range(pep_graph)
    desc_start_date = desc_start_date + datetime.timedelta(days=30)
    timeline_desc_label_source = tl_compo.generate_timeline_desc_data_source(xs=[desc_start_date, desc_start_date],
                                                                             ys=[1.7, 0.1],
                                                                             font_size=15)

    # 入力ボックス用のデータソース生成
    error_message_div = Div(width=300, height=8, style={'color': 'red'}, text='')

    title_div = Div(width=700,
                    style={'font-size': 'large',
                           'line-height': '1.5',
                           'color': BASE_FONT_COLOR})
    title_div.text = """
    Let's enter the PEP number in the left text box.<br>
    Then you can see the following information.
    <li>Which PEPs do link that PEP?</li>
    <li>Which PEPs are linked from that PEP?</li>
    """

    checkbox_group = CheckboxGroup(labels=["Show Python 2 release dates",
                                           "Show Python 3 release dates"],
                                   active=[0, 1])

    def callback_input_pep_number(all_pep_data_source=all_pep_data_source,
                                  link_to_table_source=link_to_table_source,
                                  linked_from_table_source=linked_from_table_source,
                                  link_to_table_title_div=link_to_table_title_div,
                                  linked_from_table_title_div=linked_from_table_title_div,
                                  timeline_display_circle_source=timeline_display_circle_source,
                                  timeline_label_source=timeline_label_source,
                                  timeline_desc_source=timeline_desc_label_source,
                                  title_div=title_div,
                                  error_message_div=error_message_div) -> None:
        """
        テキストボックスに文字入力されたときに実行される関数。
        PyScriptを使ってJavaScriptに変換される。
        参考: https://bokeh.pydata.org/en/latest/docs/user_guide/interaction/callbacks.html#customjs-with-a-python-function
        * このパラメータの設定の仕方以外にもあるかもしれない

        :param all_pep_data_source:
        :param link_to_table_source:
        :param linked_from_table_source:
        :param link_to_table_title_div:
        :param linked_from_table_title_div:
        :param timeline_display_circle_source:
        :param timeline_label_source:
        :param timeline_desc_source:
        :param title_div:
        :param error_message_div:
        :param debug_div:
        :return:
        """

        inputed_text = cb_obj['value']

        # PyScriptで変換するときに自分の外側の関数の呼び方がわからないので、
        # 暫定で関数内関数で定義する。
        def create_header_text(pep_dict: dict) -> str:
            if not pep_dict:
                return 'Not Found.'

            # .formatを使うとJavaScript変換後に実行時エラーになるので、
            # +演算子で連結している
            description_text = "<span>Created: " \
                               + pep_dict['Created_str'] \
                               + "&nbsp;&nbsp;&nbsp;&nbsp;Type: " \
                               + pep_dict['Type'] \
                               + "<br>"

            link_text = "<a href='https://www.python.org/dev/peps/pep-" \
                        + pep_dict['index'] \
                        + "/' target='_blank'>PEP " \
                        + pep_dict['PEP'] \
                        + "</a>"
            title_text = "<span style='font-size : xx-large;'>" \
                         + link_text \
                         + "<br>" \
                         + pep_dict['Title'] \
                         + " (" + pep_dict['Status'] + ")" \
                         + "</span>"

            return description_text + title_text

        def search_index_by_pep_number(text: str) -> int:
            index = 0

            for pep_number in all_pep_data_source['data']['PEP']:
                if text == str(pep_number):
                    return index
                index += 1

            return -1  # Not Found

        def get_inputed_pep_dict(text: int) -> dict:
            selected_index = search_index_by_pep_number(text)
            if selected_index == -1:
                return {}
            pep_dict = {}

            for key, value in all_pep_data_source.data.items():
                pep_dict[key] = value[selected_index]

            return pep_dict

        def get_pep_info(list_index: int) -> dict:
            pep_dict = {}

            for key, value in all_pep_data_source['data'].items():
                pep_dict[key] = value[list_index]

            return pep_dict

        def get_neighbor_node_info(pep_dict: dict,
                                   neighbor_type: str) -> dict:
            neighbors = dict()
            for key, value in all_pep_data_source.data.items():
                neighbors[key] = []

            for pep_id in pep_dict[neighbor_type]:
                index = search_index_by_pep_number(int(pep_id))
                work_pep_dict = get_pep_info(index)
                for key in neighbors.keys():
                    neighbors[key].append(work_pep_dict[key])
            return neighbors

        def generate_timeline_source_dict(pep_dict: dict) -> dict:

            in_edge_nodes_dict = get_neighbor_node_info(pep_dict,
                                                        'in_edge_nodes')
            out_edge_nodes_dict = get_neighbor_node_info(pep_dict,
                                                         'out_edge_nodes')
            in_edge_nodes_dict['y'] = [1.5] * len(in_edge_nodes_dict['PEP'])
            out_edge_nodes_dict['y'] = [0.5] * len(out_edge_nodes_dict['PEP'])

            timeline_source_dict = in_edge_nodes_dict
            del timeline_source_dict['in_degree']
            del timeline_source_dict['in_edge_nodes']
            del timeline_source_dict['out_degree']
            del timeline_source_dict['out_edge_nodes']
            for key, value in timeline_source_dict.items():
                timeline_source_dict[key] += out_edge_nodes_dict[key]
                if key == 'y':
                    timeline_source_dict[key].append(1)
                else:
                    timeline_source_dict[key].append(pep_dict[key])

            return timeline_source_dict

        def update_data_table(pep_dict: dict) -> None:
            linked_from_table_title_div.text = '<strong>PEP ' \
                                               + pep_dict['PEP'] \
                                               + ' is linked from ...</strong>'
            link_to_table_title_div.text = '<strong>PEP ' \
                                           + pep_dict['PEP'] \
                                           + ' links to ...</strong>'

            in_edge_nodes_dict = get_neighbor_node_info(pep_dict,
                                                        'in_edge_nodes')
            linked_from_table_source.data = in_edge_nodes_dict
            linked_from_table_source.change.emit()

            out_edge_nodes_dict = get_neighbor_node_info(pep_dict,
                                                         'out_edge_nodes')
            link_to_table_source.data = out_edge_nodes_dict
            link_to_table_source.change.emit()

        def update_timeline(pep_dict: dict) -> None:
            timeline_circle_dict = generate_timeline_source_dict(pep_dict)
            timeline_display_circle_source.data = timeline_circle_dict
            timeline_display_circle_source.change.emit()

            timeline_label_dict = generate_timeline_source_dict(pep_dict)
            timeline_label_dict['displayed_text'] = timeline_label_dict['PEP']
            timeline_label_source.data = timeline_label_dict
            timeline_label_source.change.emit()

            texts = ['PEP ' + pep_dict['PEP'] + ' is linked from...',
                     'PEP ' + pep_dict['PEP'] + ' links to...', ]

            timeline_desc_dict = dict(x=timeline_desc_source.data['x'],
                                      y=timeline_desc_source.data['y'],
                                      text=texts,
                                      size=timeline_desc_source.data['size'],
                                      )

            timeline_desc_source.data = timeline_desc_dict
            timeline_desc_source.change.emit()

        # 正規表現でタグを除去したいけど、JS変換後にreを呼べないので、暫定で<と>を外す
        inputed_text = inputed_text.replace('<', '')
        inputed_text = inputed_text.replace('>', '')
        inputed_text = inputed_text.strip()

        # 入力文字のチェック
        if not inputed_text:
            error_message_div.text = 'Please enter the number of PEP' + inputed_text
            return

        inputed_text = inputed_text.lstrip('0')

        # 表示の更新
        selected_pep_dict = get_inputed_pep_dict(inputed_text)

        if selected_pep_dict:
            title_div.text = create_header_text(selected_pep_dict)
            update_data_table(selected_pep_dict)
            update_timeline(selected_pep_dict)
            error_message_div.text = ""
        else:
            error_message_div.text = "Not Found: PEP " + inputed_text

    def callback_change_checkbox(py2_label_source=py2_release_label_data_source,
                                 py2_line_source=py2_release_line_data_source,
                                 py3_label_source=py3_release_label_data_source,
                                 py3_line_source=py3_release_line_data_source):

        def switch_show_or_hide(label_source, line_source, major_version):

            label_data = label_source.data
            line_data = line_source.data

            check_box_index_map = {2: 0, 3: 1}

            if check_box_index_map[major_version] in cb_obj.active:
                label_data['alpha'] = [1] * len(label_data['alpha'])
                line_data['alpha'] = [1] * len(line_data['alpha'])
            else:
                label_data['alpha'] = [0] * len(label_data['alpha'])
                line_data['alpha'] = [0] * len(line_data['alpha'])

            label_source.data = label_data
            label_source.change.emit()

            line_source.data = line_data
            line_source.change.emit()

        switch_show_or_hide(py2_label_source, py2_line_source, 2)
        switch_show_or_hide(py3_label_source, py3_line_source, 3)

    # Header Component
    pep_textinput = TextInput(title='PEP:',
                              placeholder='Please enter the PEP number.',
                              callback=CustomJS.from_py_func(callback_input_pep_number),
                              width=190)
    info_div = Div(width=200, height=20,
                   style={'background-color': '#175A89',
                          'padding': '5px',
                          'color': '#FFFFFF'})
    info_div.text = "<li>" \
                    "<a href='https://github.com/komo-fr/pep_map_site'><font color='#FFFFFF'>repository</font></a>" \
                    "</li>"
    inputbox_component = column(pep_textinput, error_message_div)
    color_desc_component = compo.generate_color_description_component()
    header_component = row(column(inputbox_component, color_desc_component),
                           title_div,
                           info_div)

    # Timeline Component
    checkbox_group.callback = CustomJS.from_py_func(callback_change_checkbox)
    timeline_plot = tl_compo.generate_timeline_plot(pep_graph,
                                                    timeline_display_circle_source,
                                                    timeline_label_source,
                                                    timeline_desc_label_source,
                                                    release_source_dict)
    as_of_date_div = Div(width=200, height=8, style={'color': 'red'})
    # TODO: fetch_start_datetimeを持っていないときの対応について決める
    fetch_datetime = pep_graph.graph['fetch_start_datetime'].strftime('%Y/%m/%d') \
        if 'fetch_start_datetime' in pep_graph.graph else 'Unknown'

    as_of_date_div.text = '* Data as of {}'.format(fetch_datetime)  # データ取得日
    timeline_component = column(timeline_plot, as_of_date_div)

    # Table Component
    margin_div = Div(width=50)
    link_to_table_component = column(link_to_table_title_div, link_to_data_table)
    linked_from_table_component = column(linked_from_table_title_div, linked_from_data_table)
    table_component = row(linked_from_table_component, margin_div, link_to_table_component)

    # TODO: ここでshowしなくても出力できる方法はないか？
    output_file(output_path, 'PEP Map | Timeline')

    show(column(header_component, checkbox_group, timeline_component, table_component))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='PEPの参照関係を年表形式で可視化するHTMLファイルを生成します。')
    parser.add_argument('-s',
                        '--source',
                        type=str,
                        help='入力となるPEPの参照関係を表現したグラフ構造のファイルパス(gpickle形式)')
    parser.add_argument('-d',
                        '--destination',
                        type=str,
                        help='出力となるHTMLのファイルパス')
    args = parser.parse_args()
    # TODO: パスのチェック
    # TODO: ログ出力
    make_timeline_html(input_path=args.source, output_path=args.destination)
