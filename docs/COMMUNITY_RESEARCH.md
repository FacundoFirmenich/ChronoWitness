# ChronoWitness for researchers and contributors

[Castellano](COMUNIDAD_INVESTIGACION_ES.md) · [FD7 leading case](FD7_DEMO.md) · [Reproduction](GETTING_STARTED.md)

ChronoWitness provides exact test inputs, reader and instrument models, observation bounds, and a way to inspect how each result was established. Start with the [FD7 case](FD7_DEMO.md), then select the part that matches your research question.

| Research use | Entry point | Evidence to retain |
|---|---|---|
| Temporal design and model discrimination | [Exact witnesses and thresholds](SCIENTIFIC_RESULTS.md) | The input pair, reader class, observable and certificate |
| Finite acquisition and statistical inference | [Observation and assay guide](ASSAY_GUIDE.md) | Delivery assumptions, acquisition window, score law and threshold |
| Local calibration in cellular recordings | [Cellular observations](CELLULAR_OBSERVATIONS.md) | Acquisition, horizon, alignment, local support and tail metric |

These three lines have separate implementations and results within the ChronoWitness research programme. The [SuperGraph](https://facundofirmenich.github.io/ChronoWitness/supergraph.html?lang=en) connects them through their assumptions and source records. The CRISPR Observability project develops the shared lab engine. ChronoWitness has replayed temporal cases in its own adapter and provides a browser-based FD7 editor here.

The wider programme also coordinates three named projects. **ChronoWitness** supplies temporal model discrimination, **ExposureBounds** supplies bounds for delivered inputs, and **Living Order** maintains their scientific interface and source history. Their coordination concerns shared assumptions and evidence. The molecular laboratory and the FD7 temporal editor expose different input contracts.

For a new study, define the temporal input and the quantity you will compare before reading outcomes. Record what is directly observed, which model class supplies the null, and which acquisition or context defines a comparison. Export the parameters and attach the source or certificate when you report a result. With public cellular data, keep shared acquisitions and overlapping windows visible in the analysis.

Run the web demo or open the native package for Windows x64, Linux x64 or macOS on Apple Silicon or Intel. The source checkout also includes the Streamlit editor, a Docker recipe for the editor, and the existing reproduction container. Local development used a mid-range **2016 laptop** with an Intel i5-6200U and 8–16 GB DDR3 RAM. The larger campaigns also used hosted CPU resources. See the [native releases and verification receipts](https://github.com/FacundoFirmenich/ChronoWitness/releases).

The original code is MIT licensed. Cite the [software version](../CITATION.cff) and the relevant study or dataset. Contributions can be scientific, editorial or technical. A useful first contribution is a platform-specific reproduction report or a comparison that documents the exact conditions under which a result changes. [Contribution guide](../CONTRIBUTING.md) · [Issues](https://github.com/FacundoFirmenich/ChronoWitness/issues) · [Discussions](https://github.com/FacundoFirmenich/ChronoWitness/discussions)
