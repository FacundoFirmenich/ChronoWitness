# Ensayo de trayectorias y planificación

[English](TRAJECTORY_ASSAY.md)

El estudio distingue qué modelo predice igualdad, qué observable conserva esa igualdad y cuántos datos resuelven un contraste bajo las condiciones declaradas.

## Resultados

La ocupación periódica del modelo de dos estados tiene contraste cero. Un reportero lento inicializado en cero da un contraste crudo de 0,0174473 en un período. El lector certificado de tres estados tiene contraste de ocupación positivo, cercano a 0,01007947, y contraste crudo negativo con el reportero lento. La corrección de extremos recupera la ocupación integrada en cada trayectoria simulada.

Con 8 192 bloques pareados independientes, tolerancia cero y cuatro apuestas, las potencias estimadas son 0,5605 en ventanas de un período y 0,9980 en ventanas de cuatro períodos. Cada estimación usa 512 ensayos simulados. Datos S13 registra los intervalos binomiales y los conteos por semilla. A igual tiempo acumulado, 1 024 bloques de cuatro períodos dan 0,2090 y 4 096 bloques de un período dan 0,2715, con intervalos puntuales solapados.

Si cada puntuación pareada se desvía de su ideal a lo sumo en b, la tolerancia nula es b, el radio es 1+b y el margen ideal D conserva una separación garantizada cuando D−2b>0. La cuadrícula racional de 48 casos conserva 28 márgenes de peor caso positivos y 20 casos que requieren ajustar cotas o adquisición para obtener esa garantía.

## Plan abstracto y análisis

    python research/application/plan.py --blocks 24 --pulse-duration 1 --unit dimensionless --periods 4 --burn-in-periods 1 --seed 20261110 --out fd7-plan.csv

El CSV registra los pulsos, la asignación aleatoria dentro de cada par y una fase cíclica uniforme compartida. Los metadatos registran semilla y hash. Los valores del ejemplo son adimensionales. La calificación de un sistema físico debe fijar unidades, niveles y estabilización.

El CSV de observaciones necesita columnas `block_id,score,mean_tolerance,support_radius`. Cada fila representa la unidad de asignación declarada. Las tolerancias y el soporte se fijan o se vuelven predecibles antes del resultado del bloque.

    python research/application/analyze.py observed-blocks.csv --mixture four --alpha 0.05 --out sequential-analysis.json

El analizador rechaza duplicados, entradas no finitas y puntuaciones fuera de soporte. Registra la trayectoria de evidencia y el primer cruce. La calibración física justifica rango, media condicional, emparejamiento y muestreo.

## Reproducción

Elegí el bloque 4 del paquete nativo o ejecutá desde fuentes:

    python -m pip install -r requirements-assay.txt
    python research/assay_frontier/run.py
    python research/application/verify.py

La ruta canónica desde fuentes usa Linux, Python 3.12 y C++17. El protocolo congelado fija modelos, semillas, ventanas, tolerancias, horizontes y comprobaciones. Usa trayectorias en tiempo continuo generadas por eventos, momentos calculados independientemente, cuatro referencias exactas de primer cruce y trayectorias nuevas para cada bloque de potencia. Registra los 72 escenarios, intervalos puntuales y simultáneos, casos nulos y ambas mezclas.

El reportero acotado aísla adquisición y corrección. Ruido químico de conteos, división celular, fotoblanqueo y variabilidad del dispositivo requieren modelos o cotas adecuados al ensayo. Las envolventes de conteos permiten tratar saturación y conteos moleculares no acotados. Una aplicación documenta lector, actuador, trazas, canales y tasas, precisión, saturación, lotes, unidades experimentales y regla inferencial. La evidencia piloto independiente califica viabilidad, deriva, estabilización y detector. Véase el [contexto bibliográfico](CONTEXTO_BIBLIOGRAFICO.md).
