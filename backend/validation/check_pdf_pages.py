import pypdf

def check_pages():
    reader = pypdf.PdfReader(r"c:\project\drdo\code\ADA526744.pdf")
    print(f"Total pages: {len(reader.pages)}")
    for idx in range(len(reader.pages)):
        text = reader.pages[idx].extract_text()
        print(f"Page {idx + 1}: extracted length = {len(text)} characters")

if __name__ == "__main__":
    check_pages()
