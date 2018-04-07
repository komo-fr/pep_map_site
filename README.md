# PEP Map Site

## What is this?
PEP (Python Enhancement Proposals) 同士の参照関係を可視化するページです。
左上のテキストボックスにPEPの番号を入力すると、以下の情報を年表形式・表形式で表示します。
1. その PEPが、他のどのPEPから参照されているか（リンク元）
2. そのPEPが、他のどのPEPを参照しているか（リンク先）


ゆるく作っていますが、不具合や気づいた点などあれば、[issue](https://github.com/komo-fr/pep_map_site/issues)やtwitterの[@komo_fr](https://twitter.com/komo_fr)宛に教えて頂けると助かります。
※ 元々自分用に作ったものなので、対応できるかどうかは気力次第です。

## Detail
- PEP同士の参照関係について：
	+ 参照関係の有無は`<a>`タグを元に判断しています。そのため、実際には他のPEPに言及していてもリンクが貼られていないケースには対応できていません。
	+ 現在手動でスクレイピングしているので、可視化されているのは最新のデータではありません。データ取得日は画面中央の赤字の「Data as of  …」で確認してください。
- 時系列プロットについて：
	+  色: PEPのStatus別。([PEP 1](https://www.python.org/dev/peps/pep-0001/ "PEP 1")参照)
	+ 日付(x軸): 各PEPのCreatedフィールドの値。
		* PEP 1のPEP Header Preamble
によるとCreatedフィールドは必須項目のようですが、実際にはCreatedが空のPEPが存在します。Createdが空の場合は、時系列上には表示していません。