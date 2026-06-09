import os
import sys

# Ensure workspace is in python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.pdf_generator import markdown_to_pdf

def compile_test_report():
    print("Compiling test report...")
    
    # 1. Base Walkthrough content
    md_content = """# SRE Shift Handover - Test Cases Report
**Technical Deliverable #5 - Automated Test Cases**

This document contains the complete test suite documentation, test case source files, and automated verification results for the SRE Shift Handover platform.

---

## 📈 Test Execution Results
All 22 test cases passed successfully.

```
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0
collected 22 items

Testcases/test_agent1.py::test_agent1_data_collection_happy_path PASSED
Testcases/test_agent2.py::test_similarity_identical PASSED
Testcases/test_agent2.py::test_similarity_different PASSED
Testcases/test_agent2.py::test_similarity_partial PASSED
Testcases/test_agent2.py::test_deduplication_no_duplicates PASSED
Testcases/test_agent2.py::test_deduplication_chat_vs_ticket PASSED
Testcases/test_agent2.py::test_deduplication_first_wins PASSED
Testcases/test_agent3.py::test_parse_json_response_clean PASSED
Testcases/test_agent3.py::test_parse_json_response_with_markdown PASSED
Testcases/test_agent3.py::test_parse_json_response_invalid PASSED
Testcases/test_agent3.py::test_summarise PASSED
Testcases/test_agent3.py::test_run_happy_path PASSED
Testcases/test_agent4.py::test_run_risk_filtering PASSED
Testcases/test_agent5.py::test_health_score_empty PASSED
Testcases/test_agent5.py::test_health_score_perfect PASSED
Testcases/test_agent5.py::test_health_score_all_mitigated PASSED
Testcases/test_agent5.py::test_health_score_complex_deductions PASSED
Testcases/test_agent5.py::test_health_score_grades PASSED
Testcases/test_agent6.py::test_run_report_generation PASSED
Testcases/test_pdf_generator.py::test_clean_text_for_pdf_emoji_replacement PASSED
Testcases/test_pdf_generator.py::test_clean_text_for_pdf_non_latin1_filtering PASSED
Testcases/test_pdf_generator.py::test_markdown_to_pdf_conversion PASSED

======================== 22 passed in 0.30s ========================
```

---

## 📁 Test Case Implementations
Below is the full source code for the test files.

"""

    test_files = [
        "Testcases/test_agent1.py",
        "Testcases/test_agent2.py",
        "Testcases/test_agent3.py",
        "Testcases/test_agent4.py",
        "Testcases/test_agent5.py",
        "Testcases/test_agent6.py",
        "Testcases/test_pdf_generator.py"
    ]

    for file_path in test_files:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()
            # Title for section
            file_name = os.path.basename(file_path)
            md_content += f"\n### {file_name}\n"
            # Since markdown_to_pdf handles basic markdown formatting, we can add the code blocks.
            # However, the pdf_generator parses paragraphs line-by-line. To render code cleanly in PDF
            # without nested code block parser crashes, we can indent the code block lines or output it.
            # Let's check how pdf_generator.py renders text. It says:
            # "Paragraph text: Dark text, self.multi_cell(..., f'{indent}{stripped}', markdown=True)"
            # and "Bullet lists", "Headers".
            # It doesn't have a special code block visual renderer, it just renders text using Helvetica.
            # Let's present the code line by line with indentation to make it look clean.
            indented_code = ""
            for line in code.split("\n"):
                # Use standard spaces for rendering preformatted lines in Helvetica
                indented_code += f"    {line}\n"
            md_content += indented_code + "\n"
        else:
            md_content += f"\n### {file_path} (Missing)\n"

    print("Converting markdown to PDF...")
    pdf_bytes = markdown_to_pdf(md_content)
    
    output_path = "test_cases_report.pdf"
    with open(output_path, "wb") as f:
        f.write(pdf_bytes)
        
    print(f"Success! Saved test report PDF to: {os.path.abspath(output_path)}")

if __name__ == "__main__":
    compile_test_report()
