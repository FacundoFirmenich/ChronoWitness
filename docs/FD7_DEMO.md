# Leading case · FD7, one cycle and two trajectories

[Castellano](DEMO_FD7_ES.md) · [Community and research guide](COMMUNITY_RESEARCH.md)

Two 24-symbol schedules agree on all cyclic word counts through order seven. Feed both through the same synchronizing four-state reader and ask whether they spend the same fraction of the cycle in state 3. This case connects an exact certificate, a 3D trajectory and an inspectable argument.

1. Open the [FD7 render](https://facundofirmenich.github.io/ChronoWitness/render-fd7.html?lang=en). Rotate the view and select phase 1. The axes show phase, arm and reader state. The number at the end of the trajectory closes the cycle and is excluded from the occupation count.
2. In Streamlit, leave **Certified pair** selected. Arm A visits state 3 three times and arm B visits it twice. The exact occupation difference is **1/24**. Inspect a phase to see the input symbol and the two state transitions.
3. Select **Flip one symbol**, arm **A**, phase **1**. The tool flips `0` to `1`. With the reader and starting state held fixed, the two finite-window counts become **2/24** and the contrast becomes **0**. The export records the changed symbol and the scope of this calculation.
4. Download the JSON and open the [epistemic graph](https://facundofirmenich.github.io/ChronoWitness/epistemic-graph.html?lang=en). Follow the FD7 structure and four-state witness to their certificates. Open the [SuperGraph](https://facundofirmenich.github.io/ChronoWitness/supergraph.html?lang=en) to see the wider network of assumptions, observation, inference and acquisition. The cellular observation branch shows where a physical comparison would require its own measurements.

## Run the editor

From a checkout containing `streamlit_app.py`, run these commands with Python 3.12.

```sh
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

For Docker, run the following from the same checkout and open `http://localhost:8501`.

```sh
docker build -f Dockerfile.streamlit -t chronowitness-demo .
docker run --rm -p 127.0.0.1:8501:8501 chronowitness-demo
```

For the offline viewer and computational menu, extract the matching [native release](https://github.com/FacundoFirmenich/ChronoWitness/releases) and launch the included application. Select `en atlas` for the graph and 3D witness or `en 1` for the exact reader block. The Streamlit editor is distributed as source and as a container recipe.

The JSON includes the words, state paths, transition table, exact contrast and source paths. To compare edits, use the same initial state, window and reader. The two-state identity concerns the certified schedules and the specified periodic observable. The edited scenario is a finite-window calculation. Public cellular records document a separate empirical scope.

## Run the same model in the terminal

The browser editor and this temporal laboratory entry point use the same evaluator. Save the JSON output to record a scenario for review or reuse.

```sh
python -m tools.fd7_demo
python -m tools.fd7_demo --arm A --phase 1
```

The shared Read Observability Lab v0.4 has its own molecular input contract. The ChronoWitness case uses temporal symbols and reader states. This repository exposes it through the browser editor and the command above. [Shared lab engine](https://github.com/FacundoFirmenich/crispr-observability/tree/lab-engine-multientrada-v04/engine)
