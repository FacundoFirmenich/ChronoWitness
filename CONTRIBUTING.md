# Contributing / Contribuir

## English

Questions about research use and interpretation belong in [Discussions](https://github.com/FacundoFirmenich/ChronoWitness/discussions). Use [Issues](https://github.com/FacundoFirmenich/ChronoWitness/issues) for a reproducible defect or a change you can describe concretely. English and Spanish reports are welcome.

Start with the [FD7 case](docs/FD7_DEMO.md). When reporting a result, include the software version or commit, platform, entry point, expected and observed values, and the input or public source. For cellular comparisons, include the acquisition, horizon, alignment and support. Share traces or exported results you have permission to distribute.

Keep a pull request focused on one scientific or usability change. Preserve existing evidence and source identifiers. Update the corresponding English and Spanish documentation and run the checks for the affected route. The FD7 editor uses `python -m unittest discover -s tests -p test_fd7_demo.py`. For atlas changes, run `python tools/build_evidence.py --check` and `python tools/check_atlas_browser.py`.

## Castellano

Usá [Discussions](https://github.com/FacundoFirmenich/ChronoWitness/discussions) para consultas de aplicación o interpretación. Abrí un [issue](https://github.com/FacundoFirmenich/ChronoWitness/issues) para un fallo reproducible o un cambio que puedas describir con precisión. Podés escribir en castellano o en inglés.

Empezá por el [caso FD7](docs/DEMO_FD7_ES.md). Al informar un resultado, incluí versión o commit, plataforma, punto de entrada, valores esperados y observados, y la entrada o fuente pública. En contrastes celulares, incluí adquisición, horizonte, alineación y soporte. Compartí trazas y exportaciones cuya distribución esté autorizada.

Dedicá cada pull request a un cambio científico o de uso. Conservá la evidencia previa y los identificadores de fuente. Actualizá la documentación correspondiente en ambos idiomas y ejecutá las comprobaciones de la ruta afectada. Para el editor FD7 usá `python -m unittest discover -s tests -p test_fd7_demo.py`. Para el atlas, ejecutá `python tools/build_evidence.py --check` y `python tools/check_atlas_browser.py`.
