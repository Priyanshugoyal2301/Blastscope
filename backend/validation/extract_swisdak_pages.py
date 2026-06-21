import pypdf

def extract_pages():
    reader = pypdf.PdfReader(r"c:\project\drdo\code\ADA526744.pdf")
    for page_num in range(3, 8):  # Pages 4 to 8 (0-indexed 3 to 7)
        text = reader.pages[page_num].extract_text()
        print(f"\n=================== PAGE {page_num + 1} ===================")
        print(text)

if __name__ == "__main__":
    extract_pages()
