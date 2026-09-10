#!/usr/bin/env python3
"""Build synchronized author and blinded manuscript submission artifacts."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SUBMISSION = HERE / "submission_files"
MARKDOWN_FORMAT = (
    "markdown+yaml_metadata_block+implicit_figures+tex_math_dollars+"
    "pipe_tables+link_attributes"
)
TITLE = "Auditing constrained geospatial allocation under annual land-cover product uncertainty"


def run(*args: str, cwd: Path = HERE) -> None:
    subprocess.run(args, cwd=cwd, check=True)


def markdown_to_latex(source: Path, target: Path) -> None:
    run(
        "pandoc",
        str(source),
        f"--from={MARKDOWN_FORMAT}",
        "--to=latex",
        f"--resource-path={ROOT}",
        "--output",
        str(target),
    )
    content = target.read_text(encoding="utf-8")
    if content.startswith("\\maketitle\n"):
        content = content.removeprefix("\\maketitle\n")
    target.write_text(content.rstrip() + "\n", encoding="utf-8")


def markdown_to_docx(source: Path, target: Path) -> None:
    run(
        "pandoc",
        str(source),
        f"--from={MARKDOWN_FORMAT}",
        "--standalone",
        f"--resource-path={ROOT}",
        "--output",
        str(target),
    )


def markdown_to_pdf(source: Path, target: Path) -> None:
    run(
        "pandoc",
        str(source),
        f"--from={MARKDOWN_FORMAT}",
        "--standalone",
        "--pdf-engine=xelatex",
        f"--resource-path={ROOT}",
        "--variable=mainfont:Arial Unicode MS",
        "--variable=papersize:a4",
        "--variable=fontsize:10pt",
        "--variable=geometry:top=22mm,bottom=20mm,left=20mm,right=20mm",
        "--output",
        str(target),
    )


def anonymize(main: str) -> str:
    body, references = main.split("## Data availability", maxsplit=1)
    references = "## References" + references.split("## References", maxsplit=1)[1]
    body = body.replace(
        "the accompanying source repository `FLUS_console_crossplatform` at commit `47e65b3` contains the author modifications used for this paper.",
        "an archived source repository at an anonymized revision contains the modifications used for this paper.",
    )
    body = body.replace("the author's `train`/`train-update`", "the modified `train`/`train-update`")
    return "\n".join(
        [
            "---",
            f'title: "{TITLE}"',
            'author: ""',
            'date: ""',
            "---",
            "",
            body.strip(),
            "",
            "## Data availability",
            "",
            "The public-data benchmark manifests, reports, generated delivery artefacts and source-data tables are available from an anonymized repository and archival package. Repository and archive identifiers are withheld during double-anonymized review and will be supplied in the accepted version. The package includes the Dynamic World and ArcGIS-served product-track reports, aligned public rasters, planning outputs, raster-cell transition footprints and integrity manifests. Authoritative Abu Dhabi land-use and independent reference data are not part of this study.",
            "",
            "## Code availability",
            "",
            "The analysis scripts, benchmark protocol, model runners, figure-generation code, model assets and integrity checks are maintained in the accompanying anonymized repository and archival package. Identifiers and contact details are withheld during double-anonymized review and will be supplied in the accepted version.",
            "",
            "## Declarations",
            "",
            "Funding, competing interests, author contributions, acknowledgements and ethics information are supplied in the separate title page and submission metadata.",
            "",
            references.strip(),
            "",
        ]
    )


def submission_texts(main: str) -> dict[str, str]:
    abstract = main.split("## Abstract", maxsplit=1)[1].split("## Highlights", maxsplit=1)[0].strip()
    highlights = main.split("## Highlights", maxsplit=1)[1].split("## Keywords", maxsplit=1)[0].strip()
    cover = f"""# Cover Letter

Dear Editor,

Please consider our manuscript entitled \"{TITLE}\" for publication as a Research Article in *Landscape and Urban Planning*.

The manuscript evaluates Geospatial Kernel, the algorithmic core of a Geospatial World Model, as an auditable execution layer for constrained spatial allocation. Using two public annual land-cover product tracks for Abu Dhabi, it tests whether model rankings are robust to product choice while retaining explicit proposal, constraint-projection and state-writeback traces.

The study is deliberately framed as a public-data benchmark and conditional planning stress test, rather than as an official forecast of Abu Dhabi statutory land-use change. The refreshed reproducibility package, including the ArcGIS-served product track, will be archived in a versioned record before submission.

I confirm that the manuscript is original, is not under consideration by another journal, and has been approved for submission.

The corresponding author is:

Ning Zhou\\
Beijing Freedo Technology Co., Ltd.\\
Email: zhouning@freedotech.com

Sincerely,

Ning Zhou
"""
    title_page = f"""# Title Page

## Title

{TITLE}

## Author

Ning Zhou

## Affiliation

Beijing Freedo Technology Co., Ltd.

## Corresponding author

Ning Zhou\\
Beijing Freedo Technology Co., Ltd.\\
Email: zhouning@freedotech.com

## Declarations

**Funding.** No external funding was received for this study.

**Competing interests.** Ning Zhou is employed by Beijing Freedo Technology Co., Ltd., which develops geospatial-world-model software. The author declares no other competing financial or personal interests.

**CRediT author statement.** Ning Zhou: Conceptualization, methodology, software, data curation, formal analysis, visualization, writing—original draft, writing—review and editing.

**Acknowledgements.** The author thanks the anonymous reviewers for independent technical verification and constructive methodological comments.

**Ethics statement.** Not applicable; the study used geospatial raster, vector and derived public-data products and did not involve human or animal participants.

**Data and code.** The refreshed public reproducibility package will be versioned and archived before submission. The existing v1 archive is https://doi.org/10.5281/zenodo.22663476 and does not yet contain the ArcGIS-served v2 experiment.
"""
    return {
        "abstract.md": f"# Abstract\n\n{abstract}\n",
        "highlights.md": f"# Highlights\n\n{highlights}\n",
        "cover_letter.md": cover,
        "title_page.md": title_page,
    }


def build() -> None:
    main_markdown = HERE / "manuscript.md"
    main = main_markdown.read_text(encoding="utf-8")
    SUBMISSION.mkdir(exist_ok=True)

    markdown_to_latex(main_markdown, HERE / "manuscript_pandoc.tex")
    run("xelatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex")
    run("xelatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex")
    run("xelatex", "-interaction=nonstopmode", "-halt-on-error", "lup_submission.tex")
    run("xelatex", "-interaction=nonstopmode", "-halt-on-error", "lup_submission.tex")
    shutil.copy2(HERE / "main.pdf", HERE / "manuscript.pdf")
    markdown_to_docx(main_markdown, HERE / "manuscript.docx")

    anonymous_markdown = SUBMISSION / "manuscript_anonymous.md"
    anonymous_markdown.write_text(anonymize(main), encoding="utf-8")
    markdown_to_latex(anonymous_markdown, SUBMISSION / "manuscript_anonymous_pandoc.tex")
    run("xelatex", "-interaction=nonstopmode", "-halt-on-error", "manuscript_anonymous.tex", cwd=SUBMISSION)
    run("xelatex", "-interaction=nonstopmode", "-halt-on-error", "manuscript_anonymous.tex", cwd=SUBMISSION)
    markdown_to_docx(anonymous_markdown, SUBMISSION / "manuscript_anonymous.docx")

    for markdown_name, content in submission_texts(main).items():
        source = SUBMISSION / markdown_name
        source.write_text(content, encoding="utf-8")
        markdown_to_docx(source, source.with_suffix(".docx"))
        markdown_to_pdf(source, source.with_suffix(".pdf"))


if __name__ == "__main__":
    build()
