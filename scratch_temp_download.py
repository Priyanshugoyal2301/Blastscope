import pypdf
import os

def check_text_layout():
    # If the text was scanned but OCR was run, or if it is layout-based, sometimes pypdf layout mode can extract it.
    reader = pypdf.PdfReader("ADA526744.pdf")
    os.makedirs("./extracted_pages", exist_ok=True)
    for i in range(7, len(reader.pages)):
        page = reader.pages[i]
        # Try extraction with layout mode
        text_layout = page.extract_text(extraction_mode="layout")
        text_plain = page.extract_text()
        print(f"Page {i+1}: layout len={len(text_layout)}, plain len={len(text_plain)}")
        with open(f"./extracted_pages/page_{i+1}_layout.txt", "w", encoding="utf-8") as f:
            f.write(text_layout)
        with open(f"./extracted_pages/page_{i+1}_plain.txt", "w", encoding="utf-8") as f:
            f.write(text_plain)

if __name__ == "__main__":
    check_text_layout()
