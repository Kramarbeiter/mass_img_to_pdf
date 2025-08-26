import os
import zipfile
import shutil
from PIL import Image
from fpdf import FPDF

class PDFConverter:
    """
    Converts images from all subfolders (recursively) into individual PDF files,
    stored in the main folder. Also extracts and deletes any ZIP files before conversion,
    and cleans up all non-PDF content afterward.
    """

    def __init__(self, folder_path: str):
        if not os.path.exists(folder_path):
            raise ValueError(f"The specified folder path does not exist: {folder_path}")
        self.folder_path = folder_path

    def _extract_and_delete_zip_files(self):
        print("\n🔍 Suche nach ZIP-Dateien...")
        zip_count = 0
        for root, _, files in os.walk(self.folder_path):
            for file in files:
                if file.lower().endswith('.zip'):
                    zip_path = os.path.join(root, file)
                    try:
                        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                            zip_ref.extractall(root)
                        os.remove(zip_path)
                        zip_count += 1
                        print(f"📦 Entpackt und gelöscht: {os.path.relpath(zip_path, self.folder_path)}")
                    except Exception as e:
                        print(f"⚠️ Fehler beim Entpacken von {zip_path}: {e}")
        print(f"✅ {zip_count} ZIP-Datei(en) verarbeitet.\n")

    def _cleanup_non_pdf_files(self):
        print("\n🧹 Bereinige Verzeichnis (lösche alles außer PDFs)...")
        for root, dirs, files in os.walk(self.folder_path, topdown=False):
            for file in files:
                if not file.lower().endswith('.pdf'):
                    try:
                        os.remove(os.path.join(root, file))
                    except Exception as e:
                        print(f"⚠️ Datei konnte nicht gelöscht werden: {file} ({e})")

            for dir in dirs:
                dir_path = os.path.join(root, dir)
                try:
                    shutil.rmtree(dir_path)
                except Exception as e:
                    print(f"⚠️ Ordner konnte nicht gelöscht werden: {dir_path} ({e})")

        print("✅ Aufräumen abgeschlossen.")

    def convert_images_to_pdf(self):
        self._extract_and_delete_zip_files()

        folders_with_images = []

        for root, _, files in os.walk(self.folder_path):
            if any(f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')) for f in files):
                folders_with_images.append(root)

        total_folders = len(folders_with_images)
        print(f"📁 {total_folders} Ordner mit Bildern gefunden.\n")

        for idx, folder in enumerate(folders_with_images, start=1):
            relative_path = os.path.relpath(folder, self.folder_path)
            safe_pdf_name = relative_path.replace(os.sep, "_")
            print(f"[{idx}/{total_folders}] ➜ Erstelle PDF: '{safe_pdf_name}.pdf'")
            self._create_pdf_from_images(folder, safe_pdf_name)

        self._cleanup_non_pdf_files()
        print("\n✅ PDF-Konvertierung und Aufräumen abgeschlossen.")

    def _create_pdf_from_images(self, subfolder_path: str, pdf_name: str):
        pdf = FPDF()
        image_files = sorted([
            f for f in os.listdir(subfolder_path)
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))
        ])

        for image_file in image_files:
            image_path = os.path.join(subfolder_path, image_file)

            try:
                image = Image.open(image_path)
                if image.mode != 'RGB':
                    image = image.convert('RGB')

                temp_image_path = f"{image_path}.jpg"
                image.save(temp_image_path, 'JPEG')

                pdf.add_page()
                pdf.image(temp_image_path, x=10, y=10, w=pdf.w - 20)

                os.remove(temp_image_path)
            except Exception as e:
                print(f"⚠️ Fehler bei {image_file}: {e}")

        pdf_output_path = os.path.join(self.folder_path, f"{pdf_name}.pdf")
        pdf.output(pdf_output_path)

# Beispielhafte Nutzung
if __name__ == "__main__":
    folder_path = "C:\\Users\\luisk\\Downloads\\img_to_pdf"  # Passe den Pfad an
    converter = PDFConverter(folder_path)
    converter.convert_images_to_pdf()
