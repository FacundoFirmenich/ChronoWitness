# Reproducing the figures

## Current public overview

Install `requirements-figures.txt`, then run `python tools/render_figures.py`. The script reads the exact FD7 certificate and the distributed E11 acquisition summaries. It generates input structure, acquisition-resolved local-tail evidence and an English visual abstract in PDF, SVG and 400-dpi PNG. `PROVENANCE.json` records input hashes. No cellular observations are generated or imputed.

## Full manuscript figure sources

Extract `research/FIGURE_SOURCES.zip` into a separate directory. Install `requirements-figures.txt`, then run `python reproduce_figures.py` from the extracted folder. Keep its directories intact. `INPUT_MANIFEST.json` binds source code and measured/certified inputs to their bytes; `COMMANDS.json` lists the execution order. The bundle includes the inputs used for all 24 distinct figures referenced by the English manuscript and supplement, including E5, E8 and integrated evidence maps. This reproduces the figures from frozen inputs; it does not rerun all upstream scientific campaigns.

Mathematical data are exact until plotting conversion. Empirical views retain acquisition identifiers, local support and adverse outcomes. Parent quantiles are not averages of child quantiles. The E8 plotting input is an exact extracted member of the campaign archive; it is not a replacement campaign archive.

The visual palette uses blue, indigo, violet, rose and pale backgrounds. Colour is supplemented by labels, positions and line styles. Vector PDF/SVG is preferred for publication; PNG is provided for review. The manuscript files remain private. Historical bilingual labels in archived generators retain their provenance; the public interface and current scientific documentation are in English.
