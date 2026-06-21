import pypdf
import re

def search_pdf():
    reader = pypdf.PdfReader(r"c:\project\drdo\code\ADA526744.pdf")
    print(f"Total pages: {len(reader.pages)}")
    
    keywords = ["spherical", "free air", "free-air", "air burst", "air-burst", "coefficients", "fit"]
    
    for idx, page in enumerate(reader.pages):
        text = page.extract_text()
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', text, re.IGNORECASE):
                print(f"Page {idx + 1} matches keyword '{kw}'")
                
        # Print first few lines of each page to see if it is table-rich
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if lines:
            print(f"  Page {idx + 1} start: {lines[:3]}")

if __name__ == "__main__":
    search_pdf()
