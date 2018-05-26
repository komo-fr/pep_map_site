import os
from pathlib import Path

from bs4 import BeautifulSoup
from bs4.element import Tag
import pandas as pd

from .acquirer import Acquirer


class PythonReleaseAcquirer(Acquirer):
    def __init__(self, should_save_raw_data: bool = False,
                 raw_data_out_dir_path: str = 'html') -> None:
        super().__init__(should_save_raw_data, raw_data_out_dir_path)
        self._sorted_csv_column_names = ['release_number', 'release_date',
                                         'major', 'minor', 'micro',
                                         'release_download_url',
                                         'full_change_log_url']
        self._csv_out_file_name_base = 'python_release_info'
        self._raw_out_file_name_base = 'downloads'

    def _save_raw_data(self, html,
                       out_dir_path: str) -> None:  # TODO: これをもっと抽象化できないか？
        fetch_datetime_str = self.fetch_start_datetime.strftime(
            self._DATETIME_FORMAT)
        file_name = '{}.html'.format(self._raw_out_file_name_base)
        path = Path(out_dir_path) / fetch_datetime_str / file_name
        self._save_html(html, path)

    def _to_dataframe(self, source_dict: dict) -> pd.DataFrame:
        df = super()._to_dataframe(source_dict)
        df = df.set_index('release_number')
        return df

    def _acquire(self, input_local_root_path: str = None) -> dict:
        html = self._acquire_python_release_top_html(input_local_root_path)
        data = self._scrape(html)
        return data

    def _acquire_python_release_top_html(self,
                                         input_local_root_path: str = None) -> bytes:
        if input_local_root_path:
            file_name = '{}.html'.format(self._raw_out_file_name_base)
            path = os.path.join(input_local_root_path, file_name)
        else:
            path = 'https://www.python.org/downloads/'

        html = self._acquire_html(path)

        if self._should_save_raw_data:
            self._save_raw_data(html, self._raw_data_out_dir_path)
        return html

    def _scrape(self, html) -> dict:
        soup = BeautifulSoup(html, "lxml")
        python_release_container_tag = soup.select('.list-row-container.menu')
        python_release_tags = python_release_container_tag[0].find_all('li')

        release_table_dict = {}
        for i, tag in enumerate(python_release_tags):
            release_info_dict = self.__scrape_release_info(tag)
            release_table_dict[
                release_info_dict['release_number']] = release_info_dict
        return release_table_dict

    def __scrape_release_info(self, tag: Tag) -> dict:
        release_number = tag.select('.release-number')[0].text
        major, minor, micro = release_number.replace('Python ', '').split('.')
        release_date = tag.select('.release-date')[0].text
        full_change_log_url = tag.select('.release-enhancements')[0].find(
            'a').get('href')
        release_download_url = 'https://www.python.org' + \
                               tag.select('.release-download')[0].find('a').get(
                                   'href')

        release_info_dict = dict(release_number=release_number,
                                 major=major,
                                 minor=minor,
                                 micro=micro,
                                 release_date=release_date,
                                 full_change_log_url=full_change_log_url,
                                 release_download_url=release_download_url)
        return release_info_dict