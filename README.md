# ファイル差分比較アプリ

## 概要

このアプリケーションは、２つのディレクトリ間でファイルの差分を比較し、結果を Streamlit ベースの GUI で表示・操作するためのツールです。

## 機能

-   **ファイル名の違い検出**: ファイル名が変更されたファイルを識別
-   **ファイル内容の違い検出**: doc, docx, ppt, pptx, xlsx, pdf ファイルの内容比較
-   **追加・削除ファイルの検出**: 新規追加または削除されたファイルを識別
-   **差分フィルタリング**: 表示する差分の種類を選択可能
-   **ファイルコピー機能**: 選択したファイルを指定ディレクトリにコピー
-   **進捗表示**: 処理の進行状況をリアルタイムで表示

## 対応ファイル形式

-   Microsoft Word (.doc, .docx)
-   Microsoft PowerPoint (.ppt, .pptx)
-   Microsoft Excel (.xlsx)
-   PDF (.pdf)

## セットアップ手順

### 1. 仮想環境の作成

```powershell
python -m venv .venv
```

### 2. PowerShell 実行ポリシーの設定（初回のみ）

```powershell
Set-ExecutionPolicy RemoteSigned -Scope Process
```

### 3. 仮想環境のアクティベート

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. 依存関係のインストール

```powershell
pip install -r requirements.txt
```

## 使用方法

### 1. アプリケーションの起動

**PowerShell 実行ポリシーの設定（初回のみ）:**

```powershell
Set-ExecutionPolicy RemoteSigned -Scope Process
```

**仮想環境をアクティベートしてアプリ起動:**

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run app.py
```

**注意**: エラーメッセージが表示されても、ブラウザでアプリは正常に動作します。

### 2. テストファイルの生成（任意）

アプリをテストする場合は、以下のコマンドでテストファイルを生成できます：

```powershell
python create_test_files.py
```

これにより、以下のテストパターンを含むファイルが生成されます：

-   差分なしファイル
-   内容変更ファイル
-   ファイル名変更ファイル
-   追加ファイル
-   削除ファイル
-   内容とファイル名の両方が変更されたファイル

### 3. ディレクトリの設定

-   **変更前ディレクトリ**: 比較元のディレクトリパス
-   **変更後ディレクトリ**: 比較先のディレクトリパス
-   **保存先ディレクトリ**: 選択したファイルのコピー先（任意のパスを指定可能）

#### 保存先ディレクトリについて

-   **相対パス例**: `./出力フォルダ`, `../バックアップ`
-   **絶対パス例**: `C:\Users\username\Documents\output`
-   **ネットワークパス例**: `\\server\share\backup`
-   存在しないディレクトリは自動的に作成されます

### 4. 比較の実行

1. 「ファイル差分比較を実行」ボタンをクリック
2. 比較結果が表示されます

### 5. 結果の確認

比較結果は以下のカテゴリに分類されます：

-   **追加**: 変更後ディレクトリにのみ存在するファイル
-   **削除**: 変更前ディレクトリにのみ存在するファイル
-   **内容変更**: 内容が変更されたファイル
-   **名前変更**: ファイル名が変更されたファイル（内容は同じ）
-   **変更なし**: 内容に変更がないファイル

### 6. ファイルのコピー

1. コピーしたいファイルにチェックを入れる
2. 「選択したファイルを保存先にコピー」ボタンをクリック

## ディレクトリ構造例

```
プロジェクトディレクトリ/
├── app.py                    # メインアプリケーション
├── create_test_files.py      # テストファイル生成スクリプト
├── requirements.txt          # 依存関係
├── README.md                # このファイル
├── .venv/                   # 仮想環境
├── 変更前ディレクトリ/         # 比較元ディレクトリ
├── 変更後ディレクトリ/         # 比較先ディレクトリ
└── 保存先ディレクトリ/         # コピー先ディレクトリ
```

## 技術詳細

### 使用ライブラリ

-   **Streamlit**: Web アプリケーション UI
-   **python-docx**: Word 文書の読み込み
-   **python-pptx**: PowerPoint 文書の読み込み
-   **openpyxl**: Excel 文書の読み込み
-   **pandas**: データ処理
-   **PyMuPDF**: PDF ファイルの読み込み
-   **pdfminer.six**: PDF テキスト抽出（フォールバック）

### ファイル比較アルゴリズム

1. **ハッシュベース比較**: 高速な差分検出のため MD5 ハッシュを使用
2. **内容ベース比較**: ファイル形式に応じた専用ライブラリでテキスト抽出
3. **名前変更検出**: 内容が同じで名前が異なるファイルを識別

## トラブルシューティング

### よくある問題

1. **PowerShell 実行ポリシーエラー**

    - エラー: `このシステムではスクリプトの実行が無効になっているため、ファイル xxx を読み込むことができません。`
    - 解決方法: `Set-ExecutionPolicy RemoteSigned -Scope Process` を実行してください

2. **仮想環境がアクティベートされていない**

    - 解決方法: `.\.venv\Scripts\Activate.ps1` を実行してください

3. **パッケージのインストールエラー**

    - 解決方法: `pip install --upgrade pip` で pip を最新版にアップグレードしてから `pip install -r requirements.txt` を実行

4. **Unicode/ビルドエラー（日本語パス問題）**

    - エラー: `UnicodeDecodeError: 'utf-8' codec can't decode byte 0x8b`
    - 解決方法: `pip install --only-binary=all pandas numpy` でプリビルド版を使用

5. **Python 3.13 互換性エラー（ThreadHandle/イベントループ）**

    - エラー: `TypeError: 'handle' must be a _ThreadHandle`
    - 解決方法: 以下のいずれかを試してください：
        - エラーメッセージは無視してブラウザでアプリを使用（機能に問題はありません）
        - 環境変数を設定: `$env:STREAMLIT_SERVER_ENABLE_WEBSOCKET_COMPRESSION = "false"`
        - 代替ポートで起動: `streamlit run app.py --server.port 8502`

6. **ファイル読み込みエラー**
    - ファイルが他のアプリケーションで開かれていないことを確認
    - ファイルの読み取り権限があることを確認

## ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。
