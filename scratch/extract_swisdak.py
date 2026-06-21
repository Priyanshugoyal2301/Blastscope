import pypdf

reader = pypdf.PdfReader(r"c:\project\drdo\code\ADA526744.pdf")
print("Total pages:", len(reader.pages))

for i in range(7, len(reader.pages)):
    print(f"\n--- PAGE {i+1} ---")
    print(reader.pages[i].extract_text()[:1000]) # Print first 1000 chars of each page
