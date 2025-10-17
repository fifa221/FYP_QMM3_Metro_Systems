<!-- Copilot / AI agent instructions for the FYP_QMM3_Metro_Systems repository -->
# Quick orientation

This repository is a LaTeX thesis template and (likely) working folder for a PhD/MSc thesis. The primary source is `FYP_QMM3_Metro_Systems.tex` at the project root and a small project subfolder `FYP_QMM3_Metro_Systems/` that currently contains a Git repository and supporting files.

# What the agent should know (concise)

- Big picture: this is a single-document LaTeX project (thesis). Changes typically modify the main `.tex` source, image assets referenced by `\includegraphics{...}`, and the bibliography file `bib.bib` (referenced in the main `.tex`). There is no application code, services, or tests in this repository.
- Build flow: compile the top-level `FYP_QMM3_Metro_Systems.tex` with a standard LaTeX toolchain (pdflatex/xelatex + biber/bibtex where appropriate). The agent should not add unrelated toolchains or languages.
- File of interest: `FYP_QMM3_Metro_Systems.tex` — use this as the canonical document for structure, commands, packages, and custom macros.

# Common tasks and explicit commands

When asked to build or advise on building the PDF, prefer these conservative commands (Windows PowerShell):

```powershell
# one-pass PDF with biber (if using biblatex)
pdflatex FYP_QMM3_Metro_Systems.tex; biber FYP_QMM3_Metro_Systems; pdflatex FYP_QMM3_Metro_Systems.tex; pdflatex FYP_QMM3_Metro_Systems.tex

# or using xelatex (for fonts/Unicode):
xelatex FYP_QMM3_Metro_Systems.tex; biber FYP_QMM3_Metro_Systems; xelatex FYP_QMM3_Metro_Systems.tex
```

Only suggest installing LaTeX packages when the log shows missing packages; prefer to point the user to their TeX distribution (TeX Live / MiKTeX) for package installation.

# Style and content conventions (observed)

- Single main document: Keep structural changes in `FYP_QMM3_Metro_Systems.tex` unless creating clearly-scoped included files (use `\input{}` or `\include{}` patterns when splitting chapters).
- Bibliography uses `biblatex` with `\addbibresource{bib.bib}` — preserve that pattern when editing citations or references.
- Custom macros: review the preamble for `\newcommand` / `\DeclareMathOperator` before changing math notation.
- Images: referenced relative to the project root (example: `QM_logo_Blue_CMYK.png`) — preserve image paths when editing figures.

# Search and edit guidance

- When adding files, prefer creating them under the project root or a `figures/` or `chapters/` directory. If adding a new chapter file, show how to `\include{chapters/chapter2}` and update the TOC where applicable.
- Do not initialize new programming language projects or CI unless the user requests it. This repository's scope is document preparation.

# Examples to refer to in edits

- Preamble macros: lines defining `\newcommand{\C}{\mathbb{C}}` and `\DeclareMathOperator{\arctg}{arctg}` — use these when normalizing notation.
- Bibliography entry: `\addbibresource{bib.bib}` — if asked to add references, modify `bib.bib` and cite with `\cite{...}` in the `.tex` file.

# When to ask for clarification

- If a change affects submission requirements (margins, spacing, title page content, or `\documentclass`), ask the user which university/school guidelines to follow.
- If compilation fails with missing packages or fonts, provide the LaTeX error snippet and ask whether to install packages or modify the document to avoid them.

# Minimal checklist for PRs from an agent

- Include a short summary of the change (what file(s) modified).
- If adding images or bibliography items, confirm paths and encoding (UTF-8) in the PR description.
- If splitting the document into includes, update the main `.tex` so it compiles locally with the provided commands.

-- End of repo-specific Copilot instructions --
