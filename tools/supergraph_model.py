"""Build the additional public evidence layers of the ChronoWitness SuperGraph."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Each record describes one result or condition and identifies its public source.
CLAIMS = [
    ("fd7-structure", "formal", "EXACT", "expected/core/DESIGN_STRUCTURE.json",
     "Matched summaries", "Resúmenes emparejados", "Cyclic counts through order seven, runs and cyclic autocorrelation coincide.", "Coinciden los conteos cíclicos hasta orden siete, las rachas y la autocorrelación cíclica."),
    ("phase-law", "formal", "EXACT", "expected/core/PHASE_ENSEMBLE_CERTIFICATE.json",
     "Deterministic phase-profile law", "Ley de perfiles deterministas por fase", "Four states are necessary and sufficient for separation under the declared phase-balanced profile law.", "Cuatro estados son necesarios y suficientes para separar bajo la ley de perfiles balanceada por fase."),
    ("markov-null", "formal", "EXACT", "expected/core/MARKOV_VERIFICATION.json",
     "Two-state occupation polynomial", "Polinomio de ocupación de dos estados", "The identity holds for all strictly positive two-state Markov readers in the periodic class.", "La identidad vale para todos los lectores de Markov estrictamente positivos de dos estados en la clase periódica."),
    ("discrete-witness", "formal", "EXACT", "expected/core/MARKOV_BOUNDARY.json",
     "Three-state discrete witness", "Testigo discreto de tres estados", "An explicit positive discrete reader separates. Its matrices do not embed as homogeneous CTMC pulse propagators.", "Un lector discreto positivo explícito separa. Sus matrices no son propagadores de pulsos de una CTMC homogénea."),
    ("kinetic-certificate", "formal", "CERTIFIED", "research/supplement-v010/data/Data_S11_kinetic_audit.json",
     "Continuous-time certificate", "Certificado de tiempo continuo", "The positive three-state kinetic witness has an exact positive integrated contrast and a certified rate neighborhood.", "El testigo cinético positivo de tres estados tiene contraste integrado positivo exacto y una vecindad de tasas certificada."),
    ("fd8-design", "formal", "CERTIFIED", "research/e6-e8-fd8/README.md",
     "FD8-32 design comparison", "Comparación de diseño FD8-32", "The 32-pulse pair matches words through order nine and increases one certified contrast by 60.33% at fixed period.", "El par de 32 pulsos iguala palabras hasta orden nueve y eleva un contraste certificado en 60,33 % a período fijo."),
    ("exposurebounds", "assay", "CERTIFIED", "docs/EXPOSURE_INTERFACE.md",
     "ExposureBounds software archive", "Archivo de software ExposureBounds",
     "Version 4.16.0 contains formal delivery certificates and an exact per-arm transfer example. DOI 10.5281/zenodo.24182710.",
     "La versión 4.16.0 contiene certificados formales de entrega y un ejemplo exacto de transferencia por brazo. DOI 10.5281/zenodo.24182710."),
    ("fd7-prospective", "limits", "DECLARED", "docs/EXPOSURE_INTERFACE.md",
     "Prospective cellular FD7 evaluation", "Evaluación celular prospectiva de FD7",
     "Instrument qualification, a cellular pilot and independent frozen evaluation define the proposed route.",
     "La calificación instrumental, un piloto celular y una evaluación independiente congelada definen la ruta propuesta."),
    ("endpoint", "assay", "CONDITIONAL", "expected/core/FINITE_REPORTER.json",
     "Finite-window endpoint correction", "Corrección de extremos en ventana finita", "Exact endpoint correction requires the needed functional to be identifiable from the measured channels.", "La corrección exacta requiere identificar el funcional de extremos a partir de los canales medidos."),
    ("delivery", "assay", "CONDITIONAL", "expected/core/INPUT_ROBUSTNESS.json",
     "Delivery bounds", "Cotas de entrega", "Per-arm amplitude and timing errors enter the conditional bias allowance.", "Los errores de amplitud y tiempo por brazo entran en la tolerancia de sesgo condicional."),
    ("counts", "assay", "CONDITIONAL", "expected/core/COUNT_TAILS.json",
     "Detector saturation and count tails", "Saturación y colas de conteos", "A conditional tail envelope bounds saturation distortion. Equal means alone do not supply that bound.", "Una envolvente condicional de colas acota la distorsión por saturación. Igualar medias no aporta por sí solo esa cota."),
    ("instrument", "assay", "EXACT", "expected/core/READER_INSTRUMENT_INDEPENDENT.json",
     "Instrument-memory counterexample", "Contraejemplo de memoria instrumental", "A stateful instrument can separate trajectories before aggregation even under a reader-level equality.", "Un instrumento con estado puede separar trayectorias antes de agregarlas pese a una igualdad al nivel del lector."),
    ("power", "assay", "CERTIFIED", "research/supplement-v011/data/Data_S12_design_power.csv",
     "Exact first-crossing probabilities", "Probabilidades exactas de primer cruce", "Exact prefix counts give power for the declared two-point laws and fixed horizons.", "El conteo exacto de prefijos da la potencia bajo las leyes de dos puntos y horizontes declarados."),
    ("assay-mc", "assay", "SIMULATED", "research/supplement-v012/data/Data_S13_assay_audit.json",
     "Event-driven assay simulation", "Simulación del ensayo por eventos", "The frozen simulation retains 72 settings, seed-specific counts and Monte Carlo uncertainty.", "La simulación congelada conserva 72 escenarios, recuentos por semilla e incertidumbre de Monte Carlo."),
    ("e1", "observed", "OBSERVED", "docs/CELLULAR_OBSERVATIONS.md",
     "E1 measured prediction", "E1 predicción medida", "Three held-out experiments give 60-minute RMSE reductions of 4.9729%, 17.0950% and 17.0921%.", "Tres experimentos reservados dan reducciones de RMSE a 60 minutos de 4,9729 %, 17,0950 % y 17,0921 %."),
    ("e2", "observed", "OBSERVED", "research/e2-memory-check/README.md",
     "E2 calibration transfer", "E2 transporte de calibración", "Early offset and affine calibration transfer with mixed later-window results.", "La calibración temprana afín y por desplazamiento da resultados mixtos en ventanas posteriores."),
    ("e3", "observed", "OBSERVED", "research/e3-calibration-transport/README.md",
     "E3 early model selection", "E3 selección temprana", "Temporally separated early selection yields 13 RMSE gains, 3 losses and 38 ties across 54 correlated combinations.", "La selección temprana temporalmente separada da 13 mejoras de RMSE, 3 deterioros y 38 empates en 54 combinaciones correlacionadas."),
    ("e5", "observed", "OBSERVED", "research/e5-nested/README.md",
     "E5 nested jurisdictions", "E5 jurisdicciones anidadas", "The inclusion lattice retains local RMSE deterioration masked by favorable containing sets.", "El retículo de inclusión conserva deterioros locales de RMSE ocultos por conjuntos mayores favorables."),
    ("e6", "observed", "OBSERVED", "research/e6-e8-fd8/E6_VERIFICATION_SUMMARY.json",
     "E6 tail-aware selection", "E6 selección sensible a la cola", "Tail losses over 1% fell from 20 to 3 on 232 common leaves, with fewer MAE improvements.", "Las pérdidas de cola superiores al 1 % bajaron de 20 a 3 en 232 hojas comunes, con menos mejoras de MAE."),
    ("e8-transfer", "observed", "OBSERVED", "research/e6-e8-fd8/E8_VERIFICATION_SUMMARY.json",
     "E8 ten additional acquisitions", "E8 diez adquisiciones adicionales", "Tail losses fell from 102 to 62 on 552 common leaves. Adverse transport persists.", "Las pérdidas de cola bajaron de 102 a 62 en 552 hojas comunes. Persiste el transporte adverso."),
    ("e9-masking", "observed", "OBSERVED", "research/e9-execution/AGGREGATION_MASKING_CHECK.json",
     "E9 aggregation masking", "E9 ocultamiento por agregación", "Local and containing contexts are compared within the executed temporal split.", "Los contextos locales y sus conjuntos mayores se comparan dentro de la partición temporal ejecutada."),
    ("reserve-freeze", "observed", "OBSERVED", "research/e11-causal/IMPLEMENTATION_FREEZE.json",
     "E11 policy and implementation freeze", "E11 congelación de política e implementación", "The frozen implementation and policy bind the reserved evaluation.", "La implementación y política congeladas fijan la evaluación reservada."),
    ("reserve-local", "limits", "OBSERVED", "research/e11-causal/LOCAL_CASE_SELECTION.json",
     "E11 local tail reversal", "E11 reversión local de cola", "Post-evaluation selection of an adverse supported jurisdiction within a favorable containing context.", "Selección posterior de una jurisdicción con deterioro y soporte dentro de un contexto padre favorable."),
    ("nesting-effect", "limits", "NOT_EVALUATED", "research/e11-causal/E11_GATE_LEDGER.json",
     "Independent effect of nesting", "Efecto independiente de la anidación", "The reserved comparison does not isolate the independent effect of nesting.", "La comparación reservada no aísla el efecto independiente de la anidación."),
    ("future-mean", "limits", "NOT_EVALUATED", "research/e11-causal/E11_GATE_LEDGER.json",
     "Future-acquisition uncertainty", "Incertidumbre en adquisiciones futuras", "A confidence interval for future acquisitions is outside the authority of the retrospective reserve.", "Un intervalo de confianza para adquisiciones futuras queda fuera del alcance de la reserva retrospectiva."),
]

RELATIONS = [
    ("fd7-structure", "fd7", "verifies matched summaries", "verifica los resúmenes emparejados"),
    ("markov-null", "fd7", "establishes the occupation identity", "establece la identidad de ocupación"),
    ("phase-law", "reader", "establishes the deterministic threshold", "establece el umbral determinista"),
    ("discrete-witness", "reader", "supplies the discrete alternative", "aporta la alternativa discreta"),
    ("kinetic-certificate", "kinetic", "certifies a continuous-time alternative", "certifica una alternativa en tiempo continuo"),
    ("kinetic", "fd8-design", "provides a comparison target", "aporta el objetivo de comparación"),
    ("endpoint", "reporter", "qualifies finite observation", "califica la observación finita"),
    ("instrument", "reporter", "exposes a trajectory-level failure mode", "muestra un modo de fallo en la trayectoria"),
    ("exposurebounds", "delivery", "supplies formal per-arm certificates", "aporta certificados formales por brazo"),
    ("exposurebounds", "fd7-prospective", "supports instrument qualification", "sustenta la calificación instrumental"),
    ("physical", "fd7-prospective", "motivates direct evaluation", "motiva la evaluación directa"),
    ("delivery", "statistics", "contributes a bias allowance", "contribuye a la tolerancia de sesgo"),
    ("counts", "statistics", "contributes a saturation allowance", "contribuye a la tolerancia por saturación"),
    ("statistics", "power", "defines first crossing", "define el primer cruce"),
    ("power", "assay-mc", "benchmarks simulated first crossing", "contrasta el primer cruce simulado"),
    ("e1", "e2", "supplies prediction inputs", "aporta las entradas de predicción"),
    ("e2", "e3", "motivates early policy selection", "motiva la selección temprana de política"),
    ("e3", "e4", "is resolved by local support", "se desagrega por soporte local"),
    ("e4", "e5", "reconstructs containing sets", "reconstruye los conjuntos contenedores"),
    ("e5", "e6", "motivates a tail-aware revision", "motiva una revisión sensible a las colas"),
    ("e6", "e8-transfer", "tests transport to additional acquisitions", "evalúa el transporte a adquisiciones adicionales"),
    ("e8-transfer", "e8", "supplies acquisition-level evidence", "aporta evidencia por adquisición"),
    ("e9", "e9-masking", "supports local comparisons", "sustenta comparaciones locales"),
    ("e11", "reserve-local", "retains a descriptive adverse case", "conserva un caso adverso descriptivo"),
    ("e11", "nesting-effect", "leaves attribution open", "deja abierta la atribución"),
    ("e11", "future-mean", "leaves prospective uncertainty open", "deja abierta la incertidumbre prospectiva"),
]

GATES = [
    ("gate-reader", "formal", "docs/SCIENTIFIC_RESULTS.md",
     "Reader-threshold argument", "Argumento del umbral de lectores", ("phase-law", "witness")),
    ("gate-assay", "assay", "docs/ASSAY_GUIDE.md",
     "Observation qualification", "Calificación de la observación", ("reporter", "delivery", "counts")),
    ("gate-reserve", "observed", "research/e11-causal/E11_GATE_LEDGER.json",
     "Retrospective reserve interpretation", "Interpretación de la reserva retrospectiva", ("reserve-freeze", "e11")),
]

ROUTES = [
    ("What does FD7 match?", "¿Qué iguala FD7?", ["fd7-structure", "markov-null", "fd7"]),
    ("Which readers separate?", "¿Qué lectores separan?", ["phase-law", "witness", "gate-reader", "discrete-witness", "kinetic-certificate"]),
    ("What changes in FD8-32?", "¿Qué cambia con FD8-32?", ["kinetic", "fd8-design"]),
    ("What qualifies an observation?", "¿Qué califica una observación?", ["instrument", "endpoint", "delivery", "counts", "gate-assay"]),
    ("What does the sequential test certify?", "¿Qué certifica la prueba secuencial?", ["statistics", "qualified", "power", "assay-mc"]),
    ("Where does aggregation hide losses?", "¿Dónde oculta pérdidas la agregación?", ["e1", "e2", "e3", "e4", "e5", "e6", "e8-transfer"]),
    ("What does the reserve establish?", "¿Qué establece la reserva?", ["e9", "e10", "reserve-freeze", "gate-reserve", "reserve-local", "harm"]),
    ("How does delivered exposure enter the FD7 test?", "¿Cómo entra la exposición entregada en la prueba FD7?", ["exposurebounds", "delivery", "gate-assay", "fd7-prospective"]),
    ("What would change the conclusions?", "¿Qué cambiaría las conclusiones?", ["date", "nesting-effect", "future-mean", "physical"]),
]


def extend(data):
    """Attach claims, conjunctions, revision conditions, sources and reserve rows."""
    nodes, edges = data["nodes"], data["edges"]

    def edge(source, target, en, es, kind="scientific"):
        edges.append({"id": f"edge-{len(edges)}", "from": source, "to": target,
                      "relation": en, "relation_es": es, "kind": kind})

    def node(id_, group, status, source, title, title_es, meaning, meaning_es, **extras):
        nodes.append(dict(id=id_, group=group, status=status, source=source, title=title,
                          title_es=title_es, meaning=meaning, meaning_es=meaning_es,
                          **extras))

    for item in nodes:
        item.update(kind="gate" if item.get("premises") else "claim", overview=True)
    for item in edges:
        item["kind"] = "premise" if item["relation"] == "required premise" else "scientific"
    for claim in CLAIMS:
        node(*claim, kind="claim")
    for relation in RELATIONS:
        edge(*relation)
    for id_, group, source, en, es, premises in GATES:
        node(id_, group, "CONDITIONAL", source, en, es, "The interpretation requires every listed premise.",
             "La interpretación requiere cada premisa indicada.", kind="gate", premises=list(premises))
        for premise in premises:
            edge(premise, id_, "required premise", "premisa necesaria", "premise")

    revisions = [
        ("physical", "Paired intervention evidence", "Evidencia de intervención pareada",
         "Requires compatible FD7/FD8 arms, delivery and qualified readout on independent blocks.",
         "Requiere brazos FD7/FD8 compatibles, entrega y lectura calificadas en bloques independientes."),
        ("date", "Acquisition chronology check", "Contraste de cronología de adquisición",
         "Requires a primary record resolving the conflicting acquisition dates.",
         "Requiere un registro primario que resuelva el conflicto de fechas."),
        ("nesting-effect", "Matched attribution check", "Contraste emparejado de atribución",
         "Requires a frozen matched comparison that isolates the effect of nesting.",
         "Requiere una comparación emparejada congelada que aísle el efecto de la anidación."),
        ("future-mean", "Prospective acquisition check", "Contraste prospectivo de adquisiciones",
         "Requires a new independently qualified acquisition set and a declared inferential design.",
         "Requiere un nuevo conjunto de adquisiciones calificadas de forma independiente y un diseño inferencial declarado."),
    ]
    by_id = {n["id"]: n for n in nodes}
    for target, en, es, description, description_es in revisions:
        id_ = "revise-" + target
        node(id_, "limits", "DECLARED", by_id[target]["source"], en, es,
             description, description_es, kind="revision")
        edge(id_, target, "condition for revision", "condición de revisión", "revision")

    source = "research/e11-causal/RESERVE_SUMMARY.json"
    reserve = [row for row in json.loads((ROOT/source).read_bytes()) if row["model"] == "causal_selected"]
    dates = sorted({row["date"] for row in reserve})
    assert len(dates) == 14 and len(reserve) == 84
    for date in dates:
        rows = [row for row in reserve if row["date"] == date]
        id_ = "acquisition-" + date
        node(id_, "observed", "OBSERVED", source, f"E11 acquisition {date}", f"E11 adquisición {date}",
             f"{len(rows)} context rows for the frozen causal policy on this acquisition.",
             f"{len(rows)} filas de contexto para la política causal congelada en esta adquisición.",
             kind="acquisition", date=date, contexts=rows)
        edge(id_, "e11", "observed reserve acquisition", "adquisición observada de reserva", "containment")
    data["acquisitions"] = dates
    data["routes"] = [dict(en=en, es=es, steps=steps) for en, es, steps in ROUTES]

    sources = {}
    for item in list(nodes):
        path = item["source"]
        if path not in sources:
            id_ = "source-" + hashlib.sha256(path.encode()).hexdigest()[:12]
            sources[path] = id_
            name = Path(path).name
            node(id_, item["group"], "ARTIFACT", path, name, name, "Public source bound by SHA-256.",
                 "Fuente pública identificada por SHA-256.", kind="source")
        edge(sources[path], item["id"], "documents", "documenta", "provenance")
