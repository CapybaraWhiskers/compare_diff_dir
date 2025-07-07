import streamlit as st
import os
import shutil
from pathlib import Path
import hashlib
from typing import Dict, List, Tuple, Optional
import pandas as pd
from docx import Document
from pptx import Presentation
import fitz  # PyMuPDF
from pdfminer.high_level import extract_text
import tempfile

# ページ設定
st.set_page_config(page_title="ファイル差分比較アプリ", page_icon="📄", layout="wide")


class FileComparator:
    """ファイル比較クラス"""

    def __init__(self):
        self.supported_extensions = {".doc", ".docx", ".ppt", ".pptx", ".xlsx", ".pdf"}

    def get_files_in_directory(self, directory: str) -> Dict[str, str]:
        """ディレクトリ内のサポートされているファイル一覧を取得"""
        files = {}
        if not os.path.exists(directory):
            return files

        for file_path in Path(directory).rglob("*"):
            if (
                file_path.is_file()
                and file_path.suffix.lower() in self.supported_extensions
            ):
                relative_path = str(file_path.relative_to(directory))
                files[relative_path] = str(file_path)
        return files

    def extract_text_from_file(self, file_path: str) -> str:
        """ファイルからテキストを抽出"""
        try:
            file_ext = Path(file_path).suffix.lower()

            if file_ext in [".doc", ".docx"]:
                return self._extract_from_docx(file_path)
            elif file_ext in [".ppt", ".pptx"]:
                return self._extract_from_pptx(file_path)
            elif file_ext == ".xlsx":
                return self._extract_from_xlsx(file_path)
            elif file_ext == ".pdf":
                return self._extract_from_pdf(file_path)
            else:
                return ""
        except Exception as e:
            st.warning(
                f"ファイル {file_path} の読み込みでエラーが発生しました: {str(e)}"
            )
            return ""

    def _extract_from_docx(self, file_path: str) -> str:
        """DOCXファイルからテキストを抽出"""
        doc = Document(file_path)
        text = []
        for paragraph in doc.paragraphs:
            text.append(paragraph.text)
        return "\n".join(text)

    def _extract_from_pptx(self, file_path: str) -> str:
        """PPTXファイルからテキストを抽出"""
        prs = Presentation(file_path)
        text = []
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text.append(shape.text)
        return "\n".join(text)

    def _extract_from_xlsx(self, file_path: str) -> str:
        """XLSXファイルからテキストを抽出"""
        df = pd.read_excel(file_path, sheet_name=None)
        text = []
        for sheet_name, sheet_df in df.items():
            text.append(f"Sheet: {sheet_name}")
            text.append(sheet_df.to_string())
        return "\n".join(text)

    def _extract_from_pdf(self, file_path: str) -> str:
        """PDFファイルからテキストを抽出"""
        try:
            # PyMuPDFを使用
            doc = fitz.open(file_path)
            text = []
            for page in doc:
                text.append(page.get_text())
            doc.close()
            return "\n".join(text)
        except:
            # フォールバックとしてpdfminer.sixを使用
            return extract_text(file_path)

    def calculate_file_hash(self, file_path: str) -> str:
        """ファイルのハッシュ値を計算"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
        except Exception:
            return ""
        return hash_md5.hexdigest()

    def compare_directories(self, dir1: str, dir2: str) -> Dict:
        """ディレクトリ間のファイル差分を比較"""
        files1 = self.get_files_in_directory(dir1)
        files2 = self.get_files_in_directory(dir2)

        result = {
            "added": [],  # 追加されたファイル
            "deleted": [],  # 削除されたファイル
            "modified": [],  # 内容が変更されたファイル
            "renamed": [],  # ファイル名が変更されたファイル
            "unchanged": [],  # 変更なし
        }

        # 進捗バーの表示
        progress_bar = st.progress(0)
        status_text = st.empty()

        total_files = len(set(files1.keys()) | set(files2.keys()))
        current_file = 0

        # 追加されたファイル
        for file_name in files2.keys() - files1.keys():
            result["added"].append(
                {"name": file_name, "path": files2[file_name], "type": "added"}
            )
            current_file += 1
            progress_bar.progress(current_file / total_files)
            status_text.text(f"処理中... {current_file}/{total_files}")

        # 削除されたファイル
        for file_name in files1.keys() - files2.keys():
            result["deleted"].append(
                {"name": file_name, "path": files1[file_name], "type": "deleted"}
            )
            current_file += 1
            progress_bar.progress(current_file / total_files)
            status_text.text(f"処理中... {current_file}/{total_files}")

        # 共通ファイルの内容比較
        common_files = files1.keys() & files2.keys()
        for file_name in common_files:
            file1_path = files1[file_name]
            file2_path = files2[file_name]

            # ハッシュ値で高速比較
            hash1 = self.calculate_file_hash(file1_path)
            hash2 = self.calculate_file_hash(file2_path)

            if hash1 != hash2:
                result["modified"].append(
                    {
                        "name": file_name,
                        "path1": file1_path,
                        "path2": file2_path,
                        "type": "modified",
                    }
                )
            else:
                result["unchanged"].append(
                    {
                        "name": file_name,
                        "path1": file1_path,
                        "path2": file2_path,
                        "type": "unchanged",
                    }
                )

            current_file += 1
            progress_bar.progress(current_file / total_files)
            status_text.text(f"処理中... {current_file}/{total_files}")

        # ファイル名変更の検出（内容ベース）
        try:
            self._detect_renamed_files(result, files1, files2)
        except Exception as e:
            st.warning(f"ファイル名変更検出でエラーが発生しました: {str(e)}")

        progress_bar.progress(1.0)
        status_text.text("比較完了!")

        return result

    def _detect_renamed_files(self, result: Dict, files1: Dict, files2: Dict):
        """ファイル名変更の検出（改善版）"""
        # 追加・削除されたファイルの中で内容が同じものを探す
        added_files = result["added"][:]  # コピーを作成
        deleted_files = result["deleted"][:]  # コピーを作成

        files_to_remove_from_added = []
        files_to_remove_from_deleted = []

        # ファイルサイズも考慮した高速マッチング
        added_file_info = []
        deleted_file_info = []

        # 追加ファイルの情報を収集
        for added_file in added_files:
            if added_file in files_to_remove_from_added:
                continue
            try:
                file_path = added_file["path"]
                file_size = os.path.getsize(file_path)
                file_hash = self.calculate_file_hash(file_path)
                if file_hash:
                    added_file_info.append(
                        {
                            "file": added_file,
                            "size": file_size,
                            "hash": file_hash,
                            "ext": Path(file_path).suffix.lower(),
                        }
                    )
            except Exception:
                continue

        # 削除ファイルの情報を収集
        for deleted_file in deleted_files:
            if deleted_file in files_to_remove_from_deleted:
                continue
            try:
                file_path = deleted_file["path"]
                file_size = os.path.getsize(file_path)
                file_hash = self.calculate_file_hash(file_path)
                if file_hash:
                    deleted_file_info.append(
                        {
                            "file": deleted_file,
                            "size": file_size,
                            "hash": file_hash,
                            "ext": Path(file_path).suffix.lower(),
                        }
                    )
            except Exception:
                continue

        # マッチング処理（ハッシュ + サイズ + 拡張子で判定）
        for deleted_info in deleted_file_info:
            if deleted_info["file"] in files_to_remove_from_deleted:
                continue

            for added_info in added_file_info:
                if added_info["file"] in files_to_remove_from_added:
                    continue

                # ハッシュ、サイズ、拡張子が全て一致する場合
                if (
                    deleted_info["hash"] == added_info["hash"]
                    and deleted_info["size"] == added_info["size"]
                    and deleted_info["ext"] == added_info["ext"]
                ):

                    # ファイル名変更として認識
                    result["renamed"].append(
                        {
                            "old_name": deleted_info["file"]["name"],
                            "new_name": added_info["file"]["name"],
                            "old_path": deleted_info["file"]["path"],
                            "new_path": added_info["file"]["path"],
                            "type": "renamed",
                        }
                    )

                    # 削除対象リストに追加
                    files_to_remove_from_added.append(added_info["file"])
                    files_to_remove_from_deleted.append(deleted_info["file"])
                    break

        # リストから削除（安全に削除）
        for file_item in files_to_remove_from_added:
            if file_item in result["added"]:
                result["added"].remove(file_item)

        for file_item in files_to_remove_from_deleted:
            if file_item in result["deleted"]:
                result["deleted"].remove(file_item)


def main():
    st.title("📄 ファイル差分比較アプリ")
    st.markdown("---")

    # ディレクトリパスの設定
    col1, col2 = st.columns(2)

    with col1:
        dir1 = st.text_input("変更前ディレクトリ", value="./変更前ディレクトリ")

    with col2:
        dir2 = st.text_input("変更後ディレクトリ", value="./変更後ディレクトリ")

    save_dir = st.text_input(
        "保存先ディレクトリ",
        value="./保存先ディレクトリ",
        help="ファイルをコピーする保存先ディレクトリのパスを入力してください。\n例:\n- ./出力フォルダ (相対パス)\n- C:\\Users\\username\\Documents\\output (絶対パス)\n- Z:\\共有フォルダ\\バックアップ (ネットワークパス)",
    )

    # 保存先ディレクトリの存在確認と作成確認
    if save_dir:
        try:
            abs_path = os.path.abspath(save_dir)
            if os.path.exists(save_dir):
                st.info(f"📁 保存先: `{abs_path}` （既存ディレクトリ）")
            else:
                st.warning(f"📁 保存先: `{abs_path}` （新規作成されます）")
        except Exception as e:
            st.error(f"⚠️ 無効なパス: {str(e)}")

    # ディレクトリの存在確認
    dir1_exists = os.path.exists(dir1)
    dir2_exists = os.path.exists(dir2)

    col1, col2 = st.columns(2)
    with col1:
        if dir1_exists:
            st.success(f"✅ {dir1} が見つかりました")
        else:
            st.error(f"❌ {dir1} が見つかりません")

    with col2:
        if dir2_exists:
            st.success(f"✅ {dir2} が見つかりました")
        else:
            st.error(f"❌ {dir2} が見つかりません")

    if not (dir1_exists and dir2_exists):
        st.warning("比較を開始するには、両方のディレクトリが存在する必要があります。")
        return

    # 比較実行ボタン
    if st.button("🔍 ファイル差分比較を実行", type="primary"):
        with st.spinner("ファイルを比較中..."):
            comparator = FileComparator()
            result = comparator.compare_directories(dir1, dir2)

            # セッション状態に結果を保存
            st.session_state.comparison_result = result
            st.session_state.comparator = comparator

    # 結果の表示
    if "comparison_result" in st.session_state:
        result = st.session_state.comparison_result
        comparator = st.session_state.comparator

        st.markdown("---")
        st.header("📊 比較結果")

        # サマリー表示
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric(
                "追加",
                len(result["added"]),
                delta=len(result["added"]) if result["added"] else None,
            )
        with col2:
            st.metric(
                "削除",
                len(result["deleted"]),
                delta=-len(result["deleted"]) if result["deleted"] else None,
            )
        with col3:
            st.metric("内容変更", len(result["modified"]))
        with col4:
            st.metric("名前変更", len(result["renamed"]))
        with col5:
            st.metric("変更なし", len(result["unchanged"]))

        # フィルタリングオプション
        st.markdown("---")
        st.subheader("🔧 フィルタリング")

        filter_options = st.multiselect(
            "表示する差分の種類を選択:",
            ["追加", "削除", "内容変更", "名前変更", "変更なし"],
            default=["追加", "削除", "内容変更", "名前変更"],
        )

        # 結果の詳細表示とファイル選択
        selected_files = []

        if "追加" in filter_options and result["added"]:
            st.markdown("### ➕ 追加されたファイル")
            for item in result["added"]:
                if st.checkbox(f"📄 {item['name']}", key=f"added_{item['name']}"):
                    selected_files.append(("added", item))

        if "削除" in filter_options and result["deleted"]:
            st.markdown("### ➖ 削除されたファイル")
            for item in result["deleted"]:
                st.write(f"🗑️ {item['name']}")

        if "内容変更" in filter_options and result["modified"]:
            st.markdown("### 📝 内容変更されたファイル")
            for item in result["modified"]:
                if st.checkbox(f"📄 {item['name']}", key=f"modified_{item['name']}"):
                    selected_files.append(("modified", item))

        if "名前変更" in filter_options and result["renamed"]:
            st.markdown("### 🔄 名前変更されたファイル")
            for item in result["renamed"]:
                if st.checkbox(
                    f"📄 {item['old_name']} → {item['new_name']}",
                    key=f"renamed_{item['new_name']}",
                ):
                    selected_files.append(("renamed", item))

        if "変更なし" in filter_options and result["unchanged"]:
            st.markdown("### ✅ 変更なしのファイル")
            for item in result["unchanged"]:
                if st.checkbox(f"📄 {item['name']}", key=f"unchanged_{item['name']}"):
                    selected_files.append(("unchanged", item))

        # ファイルコピー機能
        if selected_files:
            st.markdown("---")
            st.subheader("💾 選択したファイルをコピー")

            # 保存先ディレクトリの確認
            if save_dir.strip():
                save_path_display = os.path.abspath(save_dir) if save_dir else ""
                st.info(f"📁 コピー先: `{save_path_display}`")

                if st.button("📁 選択したファイルを保存先にコピー", type="secondary"):
                    copy_files(selected_files, save_dir, dir2)
            else:
                st.warning("⚠️ 保存先ディレクトリを指定してください。")


def copy_files(selected_files: List[Tuple], save_dir: str, source_dir: str):
    """選択されたファイルを保存先にコピー"""
    try:
        # 保存先ディレクトリの絶対パスを取得
        abs_save_dir = os.path.abspath(save_dir)

        # 保存先ディレクトリを作成
        if not os.path.exists(abs_save_dir):
            os.makedirs(abs_save_dir)
            st.info(f"📁 保存先ディレクトリを作成しました: {abs_save_dir}")

        success_count = 0
        error_count = 0

        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, (file_type, item) in enumerate(selected_files):
            try:
                if file_type == "added":
                    source_path = item["path"]
                    dest_path = os.path.join(abs_save_dir, item["name"])
                elif file_type == "modified":
                    source_path = item["path2"]  # 内容変更後のファイル
                    dest_path = os.path.join(abs_save_dir, item["name"])
                elif file_type == "renamed":
                    source_path = item["new_path"]
                    dest_path = os.path.join(abs_save_dir, item["new_name"])
                elif file_type == "unchanged":
                    source_path = item["path2"]
                    dest_path = os.path.join(abs_save_dir, item["name"])

                # ディレクトリ構造を作成
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)

                # ファイルをコピー
                shutil.copy2(source_path, dest_path)
                success_count += 1

            except Exception as e:
                st.error(
                    f"ファイルのコピーに失敗しました: {item.get('name', 'Unknown')} - {str(e)}"
                )
                error_count += 1

            progress_bar.progress((i + 1) / len(selected_files))
            status_text.text(f"コピー中... {i + 1}/{len(selected_files)}")

        progress_bar.progress(1.0)
        status_text.text("コピー完了!")

        if success_count > 0:
            st.success(f"✅ {success_count} 個のファイルが正常にコピーされました!")
            st.info(f"📁 保存先: {abs_save_dir}")

        if error_count > 0:
            st.error(f"❌ {error_count} 個のファイルでエラーが発生しました。")

    except Exception as e:
        st.error(f"保存先ディレクトリの作成に失敗しました: {str(e)}")
        st.info("💡 ヒント: 書き込み権限があるディレクトリを指定してください。")


if __name__ == "__main__":
    main()
