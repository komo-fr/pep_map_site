import codecs
from datetime import datetime
import glob
import os
from pathlib import Path
import time
import urllib.request
from urllib.parse import urlparse

import pandas as pd


class Acquirer:

    def __init__(self, should_save_raw_data: bool = False, raw_data_out_dir_path: str='html') -> None:
        self._fetch_start_datetime = None
        self._data = None
        self._csv_out_file_name_base = ''
        self._sorted_csv_column_names = ''
        self._DATETIME_FORMAT = '%Y%m%d-%H%M%S'

        self._should_save_raw_data = should_save_raw_data
        self._raw_data_out_dir_path = raw_data_out_dir_path

    @property
    def fetch_start_datetime(self):
        return self._fetch_start_datetime

    @property
    def data(self):
        return self._data

    @property  # TODO: この使い方はOK?
    def fetch_start_datetime_str(self) -> str:
        fetch_start_datetime_str = self.fetch_start_datetime.strftime(
            self._DATETIME_FORMAT)
        return fetch_start_datetime_str

    def acquire(self, input_local_root_path: str = None) -> dict:
        if input_local_root_path:
            self._fetch_start_datetime = self._get_fetch_date_from_local_path(
                input_local_root_path)
        else:
            self._fetch_start_datetime = datetime.now()

        data = self._acquire(input_local_root_path=input_local_root_path)
        self._data = data

        return data

    def _fetch_html(self, url: str, sleep_time: int=1) -> bytes:
        """
        指定したURLのHTMLデータを取得する
        :param url: 取得先のURL
        :return: 取得したHTMLデータ
        """
        # logging.info('Started to fetch: {}'.format(url))
        sleep_time = 1 if sleep_time < 1 else sleep_time  # sleep_timeが1s以下だと迷惑をかけるので強制的に1に設定する
        time.sleep(sleep_time)
        req = urllib.request.Request(str(url))
        response = urllib.request.urlopen(req)
        html = response.read()

        print('Compeleted to fetch.: {}'.format(url))

        return html

    def _save_html(self, html: bytes, path: Path) -> None:
        os.makedirs(path.parent, exist_ok=True)
        with path.open(mode='w', encoding='utf-8') as f:
            f.write(html.decode('utf-8'))

    def _load_html(self, path: Path) -> bytes:
        with codecs.open(path, mode='r', encoding='utf-8') as f:
            html = f.read()
        html = html.encode('utf-8')
        return html

    def _extract_fetch_date_time_from_path(self, path) -> datetime:
        file_base = Path(path).stem
        fetch_start_datetime_str = file_base[-len(
            datetime.now().strftime(self._DATETIME_FORMAT)):]
        fetch_start_datetime = datetime.strptime(fetch_start_datetime_str,
                                                 self._DATETIME_FORMAT)
        return fetch_start_datetime

    def _acquire_html(self, path: str) -> bytes:
        o = urlparse(path)
        if len(o.scheme) > 0:  # URLだった場合
            html = self._fetch_html(url=path)
        else:  # ローカルのパスだった場合
            html = self._load_html(path)

        return html

    def _save_csv(self, source_dict: dict, out_dir_path: str) -> None:
        # Create file path
        fetch_datetime_str = self.fetch_start_datetime.strftime(self._DATETIME_FORMAT)
        file_name = '{}_{}.csv'.format(self._csv_out_file_name_base,
                                       fetch_datetime_str)
        path = Path(out_dir_path) / file_name
        os.makedirs(path.parent, exist_ok=True)

        # Save
        df = self._to_dataframe(source_dict)
        df.to_csv(path, encoding='utf-8')
        print('Compeleted to save csv file: {}'.format(path))  # TODO: loggingで置き換える

    def _to_dataframe(self, source_dict: dict) -> pd.DataFrame:
        df = pd.DataFrame(source_dict).T
        if self._sorted_csv_column_names:
            df = df[self._sorted_csv_column_names]  # 列の並び替え
        return df

    def to_dataframe(self) -> pd.DataFrame():
        # TODO: self.dataがNoneのときは、先にacquireを使用するよう例外を投げる
        df = self._to_dataframe(self.data)
        return df

    def _get_fetch_date_from_local_path(self,
                                        input_local_dir_path: str) -> datetime:
        # 指定されたディレクトリが日付形式の場合は、その日をfetch_dateだと解釈する
        # 指定されたディレクトリが日付形式ではない場合は、そのフォルダ内の最新日付のファイルの作成日で解釈する

        dir_name = Path(input_local_dir_path).name
        try:
            fetch_start_datetime = datetime.strptime(dir_name,
                                                     self._DATETIME_FORMAT)
        except ValueError:
            path_list = glob.glob(os.path.join(input_local_dir_path, '*.html'))
            mtime_list = [os.stat(x).st_mtime for x in path_list]
            fetch_start_datetime = datetime.fromtimestamp(min(mtime_list))

        return fetch_start_datetime

    def to_csv(self, out_root_path: str = '.') -> None:
        self._save_csv(source_dict=self.data, out_dir_path=out_root_path)
