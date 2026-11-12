# ChronoWitness SuperGraph / SuperGraph de ChronoWitness

**English.** Open the [SuperGraph](https://facundofirmenich.github.io/ChronoWitness/supergraph.html?lang=en), then choose **Complete map** or a scientific lens. Source files, AND gates, acquisitions and declared revision conditions are inspectable. The E11 date selector displays the frozen policy's 84 context rows across 14 acquisitions. Observations, simulations and declared tests have distinct status labels. The public [FD7 render](https://facundofirmenich.github.io/ChronoWitness/render-fd7.html?lang=en) opens directly on the exact witness. Drag to rotate or use the arrow keys, and select a phase to compare the two state transitions.

**Castellano.** Abrí el [SuperGraph](https://facundofirmenich.github.io/ChronoWitness/supergraph.html?lang=es) y elegí **Mapa completo** o una vista temática. Se pueden inspeccionar los archivos fuente, las compuertas Y, las adquisiciones y las condiciones de revisión declaradas. El selector de fechas de E11 muestra las 84 filas de contexto de la política congelada en 14 adquisiciones. Las observaciones, las simulaciones y las pruebas declaradas tienen estados distintos. El [render FD7](https://facundofirmenich.github.io/ChronoWitness/render-fd7.html?lang=es) abre directamente en el testigo exacto. Arrastrá o usá las flechas para rotar y seleccioná una fase para comparar las dos transiciones de estado.

## Reproduction / Reproducción

```sh
python tools/build_evidence.py
python tools/build_evidence.py --check
python tools/check_atlas_browser.py
```

The HTML files embed the graph, the figure previews and the runtime. The [ledger](ATLAS_LEDGER.json) records exact source hashes. The layout and reading order organize evidence. They carry no statistical or causal interpretation. The software archive v0.15.0 predates this website revision.

Los HTML incorporan el grafo, las vistas previas de la figura y el código de interacción. El [registro](ATLAS_LEDGER.json) contiene los hashes exactos de las fuentes. La disposición y el orden de lectura organizan la evidencia. Carecen de interpretación estadística o causal. El archivo de software v0.15.0 precede a esta revisión del sitio.
