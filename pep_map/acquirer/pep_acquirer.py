import collections
from datetime import datetime
import os
from pathlib import Path
import re

from bs4 import BeautifulSoup
import pandas as pd

from .acquirer import Acquirer


class PepAcquirer(Acquirer):
    def __init__(self, should_save_raw_data: bool= False,
                 raw_data_out_dir_path: str = 'html') -> None:
        super().__init__(should_save_raw_data, raw_data_out_dir_path)

    def _save_raw_data(self, html, pep_id: str, out_dir_path: str) -> None:
        fetch_datetime_str = self.fetch_start_datetime.strftime(
            self._DATETIME_FORMAT)
        file_name = 'pep-{}.html'.format(pep_id)
        path = Path(out_dir_path) / fetch_datetime_str / file_name
        self._save_html(html, path)

    def _extract_pep_id(self, url: str) -> str:
        """
        URL文字列から、PEPの番号を抽出する
        :param url: 抽出元のURL
        :return: PEPの番号 ()
        """
        # TODO: どういう経緯で条件分岐が必要だったのか確認する
        if re.match('.+/pep-[0-9]{4}/#.+', url):
            return [x[len('pep-'):] for x in url.split('/') if x][
                -2]  # TODO: prefixの除去方法
        elif re.match('.+/pep-[0-9]{4}/{0,1}', url):
            return [x[len('pep-'):] for x in url.split('/') if x][
                -1]  # TODO: prefixの除去方法

    def _acquire_pep_html(self, pep_id: str,
                          input_local_dir_path=None) -> bytes:
        # pep-NNNN.htmlというファイル名規則で保存されていることを前提にしている

        if input_local_dir_path:  # ローカルのHTMLファイルから取得
            path = Path(input_local_dir_path) / 'pep-{}.html'.format(pep_id)
            path = str(path)
        else:  # Webから取得
            base_url = 'https://www.python.org/dev/peps/pep-{}'
            path = base_url.format(pep_id)

        html = self._acquire_html(path)

        if self._should_save_raw_data:
            self._save_raw_data(html, pep_id, self._raw_data_out_dir_path)

        return html

    def _acquire_all_pep_ids(self, input_local_dir_path: str = None) -> list:
        # インデックスからすべてのPEPの番号を取得する
        pep_id = '0000'
        html = self._acquire_pep_html(pep_id=pep_id,
                                      input_local_dir_path=input_local_dir_path)
        all_pep_ids = self._scrape_linked_pep_list(html)
        return all_pep_ids

    def _scrape_linked_pep_list(self, html: bytes,
                                allow_duplication: bool = False) -> list:
        """
        PEP一覧のHTMLデータから、リンクされているPEPを取得する（重複がある）
        :param html: リンク抽出元のPEPのHTML
        :return: リンクされているPEPのリスト（重複あり）
        """
        soup = BeautifulSoup(html, "lxml")
        a_tags = soup.find_all("a", href=re.compile("/dev/peps/pep-[0-9]{4}"))
        link_destination_pep_ids = []
        for a_tag in a_tags:
            pep_url = a_tag.get("href")
            pep_id = self._extract_pep_id(pep_url)
            link_destination_pep_ids.append(pep_id)

        if not allow_duplication:
            # 重複の排除
            link_destination_pep_ids = set(link_destination_pep_ids)
            link_destination_pep_ids = list(link_destination_pep_ids)

        return link_destination_pep_ids

    def acquire(self, input_local_dir_path: str = None, pep_ids: list = None):

        if input_local_dir_path:
            self._fetch_start_datetime = self._get_fetch_date_from_local_path(
                input_local_dir_path)
        else:
            self._fetch_start_datetime = datetime.now()

        data = self._acquire(input_local_dir_path=input_local_dir_path,
                             pep_ids=pep_ids)
        self._data = data

        return data

    def _acquire(self, input_local_dir_path: str = None,
                 pep_ids: list=None) -> dict:

        # pep_idsはstr型のlist(0000,0001などの文字列)
        if not pep_ids:
            pep_ids = self._acquire_all_pep_ids(input_local_dir_path=input_local_dir_path)

        peps_dict = {}

        for pep_id in pep_ids:
            pep_dict = self._acquire_one_record(pep_id=pep_id,
                                                input_local_dir_path=input_local_dir_path)
            peps_dict[pep_id] = pep_dict
            print('Completed to acquire: {}'.format(pep_id))  # TODO: logging

        return peps_dict

    def _acquire_one_record(self, pep_id: str,
                            input_local_dir_path: str = None):
        html = self._acquire_pep_html(pep_id=pep_id,
                                      input_local_dir_path=input_local_dir_path)
        pep_dict = self._scrape(html)
        return pep_dict

    def _scrape(self, html: str) -> dict:
        raise NotImplementedError

    def _str2datetime(self, source_str: str) -> datetime:
        """
        文字列を日付型に変換する
        :param source_str: 変換前の文字列
        :return: 変換後の日付型。変換に失敗したら文字列'Failed to convert'を返す
        """

        if (source_str != source_str) or not source_str:  # nullチェック
            return source_str

        converted = ''
        # 想定する日付書式のリスト
        format_list = ['%d-%b-%Y', '%d-%B-%Y', '%Y-%m-%d', '%d %b %Y',
                       '%d %B %Y']
        for format_text in format_list:
            try:
                converted = datetime.strptime(source_str, format_text)
            except:  # TODO: ちゃんと指定する
                continue

        if not converted:
            # 個別対応
            # 日付情報の後にコメントが入っている形式があるので、
            # コメント部分をトリミングしてから日付型に変換する
            pattern = '^[0-9]{1,2}-[a-z,A-Z]{3}-[0-9]{4}.+$'
            if re.match(pattern, source_str):
                source_str = source_str[:len('YYYY-mm-dd') + 1]
                converted = datetime.strptime(source_str, '%d-%b-%Y')
            else:
                converted = 'Failed to convert'

        return converted


class PepHeaderAcquirer(PepAcquirer):
    def __init__(self, should_save_raw_data: bool = False,
                 raw_data_out_dir_path: str = 'html') -> None:
        super().__init__(should_save_raw_data, raw_data_out_dir_path)
        self._csv_out_file_name_base = 'pep_header'

    def _to_dataframe(self, source_dict: dict) -> pd.DataFrame:
        df = super()._to_dataframe(source_dict)
        df = df.reset_index()
        df['pep_id'] = df['index']
        del df['index']
        df = df.set_index('pep_id')
        return df

    def _scrape(self, html: str) -> dict:
        """
        PEPの個別ページのHTML文字列から、基本情報（Title, Createdなど）を抽出する
        :param html: 抽出元となるHTMLファイルの中身（文字列）
        :return: 抽出した基本情報の辞書
        """

        soup = BeautifulSoup(html, "lxml")
        table_tag = soup.select("table.rfc2822")
        if not table_tag:
            return {}
        tr_tags = table_tag[0].find_all('tr')
        header_dict = {}
        for tr_tag in tr_tags:
            field_name = tr_tag.find('th').text.replace(':', '')
            field_body = tr_tag.find('td').text.replace(':', '')
            header_dict[field_name] = field_body

        # Cratedフィールドは日付形式が揃っていないので揃える
        header_dict['Created_dt'] = self._str2datetime(header_dict['Created'])

        return header_dict


class PepLinkDestinationAcquirer(PepAcquirer):
    def __init__(self, should_save_raw_data: bool = False,
                 raw_data_out_dir_path: str = 'html') -> None:
        super().__init__(should_save_raw_data, raw_data_out_dir_path)
        self._csv_out_file_name_base = 'pep_link_destination'

    def _to_dataframe(self, source_dict: dict) -> pd.DataFrame:
        df = super()._to_dataframe(source_dict)
        df = df.reset_index()
        df['link_source_pep_id'] = df['index']
        del df['index']
        df = df.set_index('link_source_pep_id')
        df = df.fillna(0)
        for column in df.columns:
            df[column] = df[column].astype(int)
        return df

    def _scrape(self, html: bytes) -> dict:
        """
        PEP一覧のHTMLデータから、リンク数を取得する
        :param html: PEP一覧(PEP 0)のHTMLデータ
        :return: PEPごとのリンク数の辞書
        """
        link_destination_pep_ids = self._scrape_linked_pep_list(html, allow_duplication=True)
        count_dict = collections.Counter(link_destination_pep_ids)
        return dict(count_dict)
