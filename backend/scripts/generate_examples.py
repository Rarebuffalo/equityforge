#!/usr/bin/env python3
"""Generate example PDF reports from sample documents."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.report_pipeline import generate_report  # noqa: E402

SAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "samples"
OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "examples"

SAMPLE_JOBS = [
    ("ICICI Bank", "ICICI Q2FY26.pdf"),
    ("JSW Energy", "JSW Energy Q2FY26.pdf"),
    ("LTTS", "LTTS Q2FY26.pdf"),
    ("POCL", "POCL_Q2FY26.txt"),
    ("Apex Auto Tech", "Sample_Company_Q2FY26.csv"),
]



def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    for company_name, filename in SAMPLE_JOBS:
        path = SAMPLES_DIR / filename
        if not path.exists():
            print(f"Skipping missing sample: {path}")
            continue
        content = path.read_bytes()
        pdf_bytes, report = generate_report(company_name, content, filename)
        out = OUTPUT_DIR / f"{company_name.replace(' ', '_')}_report.pdf"
        out.write_bytes(pdf_bytes)
        print(f"Generated: {out} ({len(pdf_bytes):,} bytes) — rating={report.rating}")

    # Copy working screenshot to docs/equityforge_demo.png
    import shutil
    brain_dir = Path("/home/Krishna-Singh/.gemini/antigravity-ide/brain/48a9146d-a4d3-4792-9be8-affbe0aae4b4")
    matches = sorted(brain_dir.glob("media__*.png"))
    if matches:
        docs_dir = Path(__file__).resolve().parent.parent.parent / "docs"
        docs_dir.mkdir(exist_ok=True)
        shutil.copyfile(matches[-1], docs_dir / "equityforge_demo.png")
        print(f"Updated docs/equityforge_demo.png from {matches[-1].name}")


if __name__ == "__main__":
    main()

