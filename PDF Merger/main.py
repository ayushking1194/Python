import os
from PyPDF2 import PdfMerger

class PDFMergerService:
    def __init__(self, input_folder="pdfs", output_file="merged.pdf"):
        self.input_folder = input_folder
        self.output_file = output_file
        self.pdf_files = []

        self._validate_folder()
        self._collect_pdf_files()

    def _validate_folder(self):
        if not os.path.exists(self.input_folder):
            raise FileNotFoundError(f"The folder '{self.input_folder}' does not exist.")

    def _collect_pdf_files(self):
        self.pdf_files = sorted(
            f for f in os.listdir(self.input_folder)
            if f.lower().endswith(".pdf")
        )
        if not self.pdf_files:
            raise ValueError(f"No PDF files found in folder '{self.input_folder}'.")

    def merge_pdfs(self):
        merger = PdfMerger()
        for pdf in self.pdf_files:
            merger.append(os.path.join(self.input_folder, pdf))
        merger.write(self.output_file)
        merger.close()
        print(f"Merged {len(self.pdf_files)} PDFs into '{self.output_file}'")

def main():
    merger_service = PDFMergerService()
    merger_service.merge_pdfs()
    
if __name__ == "__main__":
    main()