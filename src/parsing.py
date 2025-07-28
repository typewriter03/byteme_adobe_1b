import pymupdf4llm
import re
import fitz  # PyMuPDF

def process_all_pdfs(pdf_paths: list[str]) -> list[dict]:
    all_sections = []

    for doc_path in pdf_paths:
        doc_name = doc_path.split('/')[-1] if '/' in doc_path else doc_path.split('\\')[-1]

        try:
            with fitz.open(doc_path) as doc:
                total_pages = len(doc)
        except Exception as e:
            print(f"Could not open {doc_name} with PyMuPDF: {e}")
            continue

        try:
            md_text = pymupdf4llm.to_markdown(doc_path)
        except Exception as e:
            print(f"Could not process {doc_name} with PyMuPDF4LLM: {e}")
            continue

        lines = md_text.split('\n')
        lines_per_page = max(1, len(lines) // total_pages)  # To estimate page numbers

        current_heading_text = "Introduction"
        current_heading_level = "H1"
        current_text_content = ""
        section_start_line = 0

        for i, line in enumerate(lines):
            heading_match = re.match(r'^(#+)\s+(.*)', line)

            if heading_match:
                if current_text_content.strip():
                    est_page = (section_start_line // lines_per_page) + 1

                    all_sections.append({
                        "doc_name": doc_name,
                        "page_num": est_page,
                        "title": current_heading_text,
                        "level": current_heading_level,
                        "content_text": current_text_content.strip()
                    })

                num_hashes = len(heading_match.group(1))
                current_heading_level = f"H{num_hashes}"
                current_heading_text = heading_match.group(2).strip()
                current_text_content = ""
                section_start_line = i
            else:
                current_text_content += line + "\n"

        if current_text_content.strip():
            est_page = (section_start_line // lines_per_page) + 1
            all_sections.append({
                "doc_name": doc_name,
                "page_num": est_page,
                "title": current_heading_text,
                "level": current_heading_level,
                "content_text": current_text_content.strip()
            })

    return all_sections
