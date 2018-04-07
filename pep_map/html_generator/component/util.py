import math
from networkx.classes.graph import Graph
import pandas as pd


def calc_radius(size: float) -> float:
    """
    面積から半径を算出する
    :param size: 面積
    :return: 半径
    """
    radius = math.sqrt(size / math.pi)
    return radius


def convert_node_attribute2df(source_graph: Graph) -> pd.DataFrame:
    """
    networkxのノードの属性をpandasのDataFrame型に変換する
    :param source_graph: 変換元のnetworkxのグラフ構造
    :return: 変換先のpandasのDataFrame
    """
    node_dict = dict(source_graph.nodes(data=True))
    node_df = pd.DataFrame.from_dict(node_dict).T
    return node_df


def calc_node_position_range(source_graph: Graph) -> dict:
    """
    引数で渡されたネットワーク構造について、ノードの座標の範囲を算出する
    事前条件：引数で渡されたネットワーク構造のノードの属性に「position」があること
    :param source_graph:
    :return:
    """
    # TODO: ノード属性にpositionがあるかどうかをチェックする
    position_dict = dict(source_graph.nodes(data="position"))
    x_list = [value[0] for key, value in position_dict.items()]
    y_list = [value[1] for key, value in position_dict.items()]
    range_dict = dict(x_range=(min(x_list), max(x_list)),
                      y_range=(min(y_list), max(y_list))
                      )
    return range_dict
