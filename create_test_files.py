"""
ファイル差分比較アプリ用のテストファイル作成スクリプト
.doc, .docx, .ppt, .pptx, .xlsx, .pdf ファイルの各種差分パターンを生成します
"""

import os
import shutil
from docx import Document
from pptx import Presentation
from openpyxl import Workbook
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


def create_word_doc(file_path: str, content: str):
    """Word文書を作成（.doc/.docx 対応）"""
    try:
        doc = Document()
        doc.add_paragraph(content)
        doc.save(file_path)
        print(f"✅ Word文書作成: {file_path}")
    except Exception as e:
        print(f"❌ Word文書作成エラー {file_path}: {e}")


def create_excel_file(file_path: str, content: str):
    """Excel ファイルを作成"""
    try:
        wb = Workbook()
        ws = wb.active
        ws.title = "テストシート"

        # コンテンツを複数行に分割してセルに入力
        lines = content.split("\n") if "\n" in content else [content]
        for i, line in enumerate(lines, 1):
            ws[f"A{i}"] = line

        # サンプルデータも追加
        ws["B1"] = "項目"
        ws["B2"] = "値"
        ws["C1"] = "テスト"
        ws["C2"] = content[:20] + "..." if len(content) > 20 else content

        wb.save(file_path)
        print(f"✅ Excel作成: {file_path}")
    except Exception as e:
        print(f"❌ Excel作成エラー {file_path}: {e}")


def create_powerpoint(file_path: str, title: str, content: str):
    """PowerPoint プレゼンテーションを作成"""
    try:
        prs = Presentation()
        slide_layout = prs.slide_layouts[1]  # タイトルとコンテンツのレイアウト
        slide = prs.slides.add_slide(slide_layout)

        # タイトルを設定
        title_shape = slide.shapes.title
        title_shape.text = title

        # コンテンツを設定
        content_shape = slide.placeholders[1]
        content_shape.text = content

        prs.save(file_path)
        print(f"✅ PowerPoint作成: {file_path}")
    except Exception as e:
        print(f"❌ PowerPoint作成エラー {file_path}: {e}")


def create_pdf_file(file_path: str, content: str):
    """PDF ファイルを作成"""
    try:
        # ファイル名の差分テスト用に、内容は同じにする必要があるパターンを判定
        is_name_diff_test = "ファイル名差分" in file_path
        is_no_diff_test = "差分なし" in file_path

        # 差分なしとファイル名差分の場合、同一のPDFファイルを作成する
        if is_name_diff_test or is_no_diff_test:
            create_identical_pdf(file_path)
            return

        c = canvas.Canvas(file_path, pagesize=letter)

        # 日本語対応のため、内容を英語に変換
        content_map = {
            "元の内容": "Original Content",
            "変更された内容": "Modified Content",
            "削除されるファイル": "File to be Deleted",
            "追加されるファイル": "Added File",
            "旧内容": "Old Content",
            "新内容": "New Content",
        }

        # 日本語を英語に変換
        english_content = content_map.get(content, f"Content: {content}")

        # 標準フォントを使用
        c.setFont("Helvetica-Bold", 14)
        y_position = 750

        # タイトル
        c.drawString(100, y_position, "PDF Test File")
        y_position -= 30

        # ファイル名情報
        file_name = file_path.split("/")[-1].replace("\\", "/")
        file_name_map = {
            "差分なし": "no_diff",
            "内容差分": "content_diff",
            "ファイル名差分_変更前": "name_diff_before",
            "ファイル名差分_変更後": "name_diff_after",
            "削除": "deleted",
            "追加": "added",
            "内容・ファイル名差分_変更前": "both_diff_before",
            "内容・ファイル名差分_変更後": "both_diff_after",
        }

        english_file_name = file_name
        for japanese, english in file_name_map.items():
            english_file_name = english_file_name.replace(japanese, english)

        c.setFont("Helvetica", 12)
        c.drawString(100, y_position, f"File: {english_file_name}")
        y_position -= 25

        # コンテンツ
        c.setFont("Helvetica-Bold", 12)
        c.drawString(100, y_position, "Content:")
        y_position -= 20

        c.setFont("Helvetica", 12)
        lines = (
            english_content.split("\n")
            if "\n" in english_content
            else [english_content]
        )
        for line in lines:
            c.drawString(120, y_position, line)
            y_position -= 20

        # 作成日時
        y_position -= 10
        c.setFont("Helvetica", 10)
        from datetime import datetime

        c.drawString(
            100, y_position, f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        # フッター
        c.drawString(100, 50, "Test file for file comparison application")

        c.save()
        print(f"✅ PDF作成: {file_path}")
    except Exception as e:
        print(f"❌ PDF作成エラー {file_path}: {e}")


def create_identical_pdf(file_path: str):
    """差分なし・ファイル名差分テスト用の同一PDFファイルを作成"""
    c = canvas.Canvas(file_path, pagesize=letter)

    # 完全に同一の内容でPDFを作成
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 750, "PDF Test File")

    c.setFont("Helvetica", 12)
    c.drawString(100, 720, "File: identical_test.pdf")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, 695, "Content:")

    c.setFont("Helvetica", 12)
    c.drawString(120, 675, "Same Content")

    c.setFont("Helvetica", 10)
    c.drawString(100, 640, "Created: 2025-01-01 00:00:00")

    c.drawString(100, 50, "Test file for file comparison application")

    c.save()
    print(f"✅ PDF作成: {file_path}")


def create_file_by_type(file_path: str, file_type: str, content: str):
    """ファイル形式に応じてファイルを作成"""
    try:
        if file_type == "word":
            create_word_doc(file_path, content)
        elif file_type == "excel":
            create_excel_file(file_path, content)
        elif file_type == "powerpoint":
            create_powerpoint(file_path, "テストファイル", content)
        elif file_type == "pdf":
            create_pdf_file(file_path, content)
        else:
            print(f"⚠️  未対応のファイル形式: {file_type}")
    except Exception as e:
        print(f"❌ ファイル作成エラー {file_path}: {e}")


def create_test_files():
    """テスト用のファイルを作成"""
    print("🗂️  テストファイルを作成中...")

    # ディレクトリを作成（既存ファイルは削除せずにスキップ）
    for dir_name in ["変更前ディレクトリ", "変更後ディレクトリ", "保存先ディレクトリ"]:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

    # サポートするファイル形式
    file_patterns = {
        "doc": {"ext": "doc", "type": "word"},
        "docx": {"ext": "docx", "type": "word"},
        "pptx": {"ext": "pptx", "type": "powerpoint"},
        "xlsx": {"ext": "xlsx", "type": "excel"},
        "pdf": {"ext": "pdf", "type": "pdf"},
    }

    # 各差分パターンを作成
    test_cases = [
        {
            "pattern": "差分なし",
            "content_before": "同じ内容",
            "content_after": "同じ内容",
        },
        {
            "pattern": "内容差分",
            "content_before": "元の内容",
            "content_after": "変更された内容",
        },
        {
            "pattern": "ファイル名差分_変更前",
            "content_before": "名前変更テスト",
            "content_after": None,
        },
        {
            "pattern": "ファイル名差分_変更後",
            "content_before": None,
            "content_after": "名前変更テスト",
        },
        {
            "pattern": "削除",
            "content_before": "削除されるファイル",
            "content_after": None,
        },
        {
            "pattern": "追加",
            "content_before": None,
            "content_after": "追加されるファイル",
        },
        {
            "pattern": "内容・ファイル名差分_変更前",
            "content_before": "旧内容",
            "content_after": None,
        },
        {
            "pattern": "内容・ファイル名差分_変更後",
            "content_before": None,
            "content_after": "新内容",
        },
    ]

    # 各ファイル形式とテストケースの組み合わせでファイルを作成
    # PDFの同一ファイル用テンプレートを最初に作成
    master_pdf_path = "temp_master.pdf"
    create_master_pdf_template(master_pdf_path)

    for file_key, file_config in file_patterns.items():
        ext = file_config["ext"]
        file_type = file_config["type"]

        print(f"\n📄 {file_key.upper()} ファイルを作成中...")

        for case in test_cases:
            pattern = case["pattern"]

            # 変更前ディレクトリのファイル
            if case["content_before"] is not None:
                file_path = f"変更前ディレクトリ/{file_key}_{pattern}.{ext}"

                # PDF特別処理：差分なしとファイル名差分では同一ファイルをコピー
                if ext == "pdf" and pattern in ["差分なし", "ファイル名差分_変更前"]:
                    shutil.copy2(master_pdf_path, file_path)
                    print(f"✅ PDF作成: {file_path}")
                else:
                    create_file_by_type(file_path, file_type, case["content_before"])

            # 変更後ディレクトリのファイル
            if case["content_after"] is not None:
                file_path = f"変更後ディレクトリ/{file_key}_{pattern}.{ext}"

                # PDF特別処理：差分なしとファイル名差分では同一ファイルをコピー
                if ext == "pdf" and pattern in ["差分なし", "ファイル名差分_変更後"]:
                    shutil.copy2(master_pdf_path, file_path)
                    print(f"✅ PDF作成: {file_path}")
                else:
                    create_file_by_type(file_path, file_type, case["content_after"])

    # 一時ファイルを削除
    if os.path.exists(master_pdf_path):
        os.remove(master_pdf_path)

    print("\n✅ テストファイルの作成が完了しました！")
    print_test_summary()


def create_master_pdf_template(file_path: str):
    """PDF用のマスターテンプレートを作成（差分なし・ファイル名差分テスト用）"""
    c = canvas.Canvas(file_path, pagesize=letter)

    # 完全に同一の内容でPDFを作成
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 750, "PDF Test File")

    c.setFont("Helvetica", 12)
    c.drawString(100, 720, "File: identical_test.pdf")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, 695, "Content:")

    c.setFont("Helvetica", 12)
    c.drawString(120, 675, "Same Content")

    c.setFont("Helvetica", 10)
    c.drawString(100, 640, "Created: 2025-01-01 00:00:00")

    c.drawString(100, 50, "Test file for file comparison application")

    c.save()


def print_test_summary():
    """作成されたテストファイルのサマリーを表示"""
    print("\n📋 作成されたテストファイル:")
    print("=" * 60)

    for dir_name in ["変更前ディレクトリ", "変更後ディレクトリ"]:
        if os.path.exists(dir_name):
            files = os.listdir(dir_name)
            print(f"\n📂 {dir_name} ({len(files)}ファイル):")
            for file in sorted(files):
                print(f"  📄 {file}")

    print("\n🎯 期待される差分検出結果:")
    print("  ✅ 差分なし: 5ファイル (.doc, .docx, .pptx, .xlsx, .pdf)")
    print("  📝 内容変更: 5ファイル")
    print("  🔄 ファイル名変更: 5ファイル")
    print("  ➕ 追加: 5ファイル")
    print("  ➖ 削除: 5ファイル")
    print("  ⚠️  内容・ファイル名変更: 10ファイル（5削除+5追加として検出）")


if __name__ == "__main__":
    try:
        create_test_files()
        print("\n🚀 テストファイル作成完了！アプリを起動してテストしてください。")
    except Exception as e:
        print(f"❌ テストファイル作成中にエラーが発生しました: {e}")
        import traceback

        traceback.print_exc()
