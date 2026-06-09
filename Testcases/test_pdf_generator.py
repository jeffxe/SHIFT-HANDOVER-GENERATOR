from utils import pdf_generator

def test_clean_text_for_pdf_emoji_replacement():
    input_text = "🔄 SRE 🔴 CRITICAL ⚠️ WARNING ✅ RESOLVED"
    expected = "Shift SRE CRITICAL - CRITICAL WARNING - WARNING RESOLVED - RESOLVED"
    # Wait, let's check replacements mapping in clean_text_for_pdf:
    # "🔄": "Shift",
    # "🔴": "CRITICAL -",
    # "⚠️": "WARNING -",
    # "✅": "RESOLVED -",
    # So "🔄 SRE 🔴 CRITICAL" -> "Shift SRE CRITICAL - CRITICAL"
    result = pdf_generator.clean_text_for_pdf(input_text)
    assert "Shift" in result
    assert "CRITICAL -" in result
    assert "WARNING -" in result
    assert "RESOLVED -" in result

def test_clean_text_for_pdf_non_latin1_filtering():
    # Non-latin-1 characters like Chinese characters or specific unicode symbols
    # should be replaced with '?'
    input_text = "Hello 世界! Latin-1 is fine: áéíóú."
    result = pdf_generator.clean_text_for_pdf(input_text)
    assert "Hello ??! Latin-1 is fine: áéíóú." in result

def test_markdown_to_pdf_conversion():
    markdown = """
# Shift Handover Report
**Shift Health Score:** 80/100 (Grade: B)

## High Priority Issues
| Severity | Incident | Owner | Status | Context |
|---|---|---|---|---|
| Critical | TKT-1 | alice | Open | Outage |

## Completed Tasks
| Incident | Owner | Resolution Summary |
|---|---|---|
| TKT-2 | bob | Restored backup |

## Watchlist
- TKT-3 - Medium issue (charlie)

## Recommended Actions
- Monitor CPU utilization on gateway nodes
- Follow up on database backup verification

## Shift Summary
This was a stable shift. No major incidents remains unresolved.
"""
    pdf_bytes = pdf_generator.markdown_to_pdf(markdown)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0
    # A standard PDF file starts with %PDF
    assert pdf_bytes.startswith(b"%PDF")
