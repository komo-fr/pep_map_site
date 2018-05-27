import argparse
from datetime import datetime as dt
import os

import pandas as pd
import networkx as nx

from acquirer.pep_acquirer import PepAcquirer, PepHeaderAcquirer, PepLinkDestinationAcquirer
from acquirer.python_release_acquirer import PythonReleaseAcquirer


def to_adjacency_matrix(source_df: pd.DataFrame) -> pd.DataFrame:
    df = source_df.copy()
    # 不足列を追加する
    missing_columns = list(set(source_df.index) - set(df.columns))  # 行にあって、列にない
    for column in missing_columns:
        df[column] = 0

    # 不足行を追加する
    missing_lines = list(set(df.columns) - set(df.index))  # 列にあって、行にない
    for line in missing_lines:
        df.loc[line] = 0

    # 列と行の並び順を揃える
    df = df[sorted(df.columns)]
    df = df.sort_index()

    # PEP 0 は目次なので除外する
    df = df.loc[df.index != '0000', df.columns != '0000']

    return df


def make_pep_graph(source_link_df: pd.DataFrame,
                   source_header_df: pd.DataFrame,
                   fetch_start_datetime=None) -> pd.DataFrame:
    # 隣接行列に変換する
    df = source_link_df.copy()
    adj_df = to_adjacency_matrix(df)

    pep_graph = nx.from_pandas_adjacency(adj_df, create_using=nx.DiGraph())

    header_df = source_header_df.copy()

    # ヘッダ情報を属性情報として付加する
    for column_name, series in header_df.iteritems():
        nx.set_node_attributes(pep_graph, dict(series), column_name)

    print(nx.info(pep_graph))

    pep_graph.graph['fetch_start_datetime'] = fetch_start_datetime

    return pep_graph


def main(output_root_path: str=None) -> None:
    if not output_root_path:
        output_root_path = dt.now().strftime('%Y%m%d')

    # Pythonのリリース情報の取得
    python_release_acquirer = PythonReleaseAcquirer()
    python_release_acquirer.acquire()

    python_release_acquirer.to_csv(output_root_path)

    # PEP Headerの取得
    raw_root_path = os.path.join(output_root_path, 'raw')
    pep_header_acquirer = PepHeaderAcquirer(raw_data_out_root_path=raw_root_path,
                                            should_save_raw_data=True)
    pep_header_acquirer.acquire()
    pep_header_df = pep_header_acquirer.to_dataframe()

    pep_header_acquirer.to_csv(out_root_path=output_root_path)

    # 取得済みのPEPリスト
    acquired_pep_ids = list(pep_header_acquirer.data.keys())

    # 各PEPのリンク先PEPの取得
    # ローカルファイルから取得する
    raw_data_dir_path = pep_header_acquirer.raw_data_out_dir_path

    pep_link_acquirer = PepLinkDestinationAcquirer()
    pep_link_acquirer.acquire(pep_ids=acquired_pep_ids,
                              input_local_dir_path=raw_data_dir_path)
    pep_link_df = pep_link_acquirer.to_dataframe()

    pep_link_acquirer.to_csv(output_root_path)

    # make pep graph
    pep_graph = make_pep_graph(pep_link_df,
                               pep_header_df,
                               pep_link_acquirer.fetch_start_datetime)

    # Save
    fetch_datetime = pep_graph.graph['fetch_start_datetime'].strftime('%Y%m%d-%H%M%S')
    file_name = 'pep_graph_{fetch_datetime}.gpickle'.format(fetch_datetime=fetch_datetime)
    file_path = os.path.join(output_root_path, file_name)

    nx.write_gpickle(pep_graph, file_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='PEPのリンク関係のグラフ構造ファイルを作成します。')
    # parser.add_argument('-s',
    #                    '--source',
    #                    type=str,
    #                    help='入力となるCSVファイル')
    parser.add_argument('-d',
                        '--destination',
                        type=str,
                        help='出力となるフォルダのパス。デフォルトでは実行時の日付')
    args = parser.parse_args()
    # TODO: パスのチェック
    # TODO: ログ出力
    main(output_root_path=args.destination)
