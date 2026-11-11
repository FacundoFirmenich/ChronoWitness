# E11 · Calibración causal con jurisdicciones anidadas

E11 desarrolla una corrección temporal sobre E9/E10 y reserva 14 adquisiciones con estímulos por intervalos para evaluar una sola política seleccionada. La historia de estímulo y el predictor base permanecen congelados; la modificación afecta exclusivamente a la corrección de sus errores.

## Regla causal

En el instante de predicción t se admiten únicamente errores del mismo identificador celular cuyo objetivo ya fue observado: s+h<t. Se conserva una memoria de 180 o 360 minutos y se toman como máximo los 12 intervalos de predicción más recientes que no se solapan en su interior. Esto evita reutilizar indefinidamente un sesgo inicial, pero no hace independientes las observaciones ni sus historias.

La variante anidada busca soporte en célula × fase de pulso × banda de señal, después en célula × fase de pulso y finalmente en célula. Las bandas de señal proceden exclusivamente del TRAIN de E9. La variante de control utiliza solamente el nivel celular. Se exige un mínimo de seis errores maduros; los dos bloques cronológicos contienen al menos tres cada uno.

Si las medias de error de ambos bloques tienen el mismo signo no nulo, se propone

`c = shrink * sign(mu_recent) * min(abs(mu_older), abs(mu_recent))`,

con shrink igual a 0,25 o 0,5. La corrección se acepta únicamente si en cada bloque el percentil 95 del error absoluto corregido no supera 1,01 veces el original. En caso contrario se conserva la predicción base. Si una jurisdicción tiene soporte suficiente pero falla ese criterio, no se retrocede a una jurisdicción más amplia para forzar una corrección.

El acuerdo y el control de colas son criterios históricos de admisión. No constituyen una banda de confianza para la media futura ni una garantía prospectiva de ausencia de daño. Los residuos utilizados como realimentación son siempre los del predictor base, no los del predictor ya corregido.

## Desarrollo y evaluación

Las ocho combinaciones se comparan sobre cuatro días ya examinados de E9/E10. Se descartan las que no actúan en al menos el 1% de las ventanas de cada día o cuyo RMSE medio relativo por día supera 1,05. Entre las admisibles, la selección prioriza la peor fracción diaria media de jurisdicciones pulso/señal con daño de q95 superior al 1%; después, su media entre días; después, la media entre días del logaritmo de la razón de RMSE. Los empates se resuelven por identificador. Estos son criterios de diseño, no pruebas de significación.

`SELECTED_POLICY.json` se genera antes de ejecutar la reserva. Si ninguna candidata cumple la admisión, la reserva permanece sin puntuar. Una vez seleccionada, la candidata se compara sobre idénticas ventanas tardías con el predictor base, el predictor sin historia de entrada, la persistencia y la protección fija de E9. Durante el tramo tardío puede utilizar resultados anteriores que ya han madurado; se trata de una evaluación secuencial con realimentación.

Los horizontes siguen siendo 5, 10 y 20 minutos, ambos alineamientos se conservan y no se modifica el predictor con los resultados de la reserva. El predictor base utiliza las futuras entradas programadas, como E9: se evalúa predicción condicionada al estímulo conocido, no predicción de intervenciones futuras desconocidas.

La política revisada utiliza realimentación de errores tardíos anteriores ya maduros, mientras la protección fija mantiene su sesgo temprano. La comparación evalúa el régimen completo de actualización, memoria, contracción y localidad. No identifica aisladamente el efecto causal de la anidación. Las variantes celulares y las otras memorias se comparan para desarrollo y selección; no se puntúan como nuevas alternativas en la reserva.

Se mantienen padres, células, intersecciones pulso/señal, segmentos temporales e intersecciones de esos segmentos. Los nodos con menos de 20 ventanas se conservan como LOW_SUPPORT. Se reconstruye el MSE del padre desde cada partición disjunta. Los percentiles se calculan desde observaciones atómicas, sin promediar percentiles de hijos.

## Procedencia y límites

Las 14 fechas reservadas son disjuntas de E9/E10 y pertenecen al mismo estudio y laboratorio. Algunas son anteriores al entrenamiento de E9; esta es una evaluación retrospectiva de transporte entre adquisiciones. El archivo min15_optmean_rep1.csv queda en cuarentena por la discrepancia 2020-02-08 / 2020-02-09 de su configuración original. No se inventa una fecha y no se calculan sus resultados predictivos.

Los recuentos de archivos, células y ventanas no son recuentos de réplicas independientes. El análisis de estabilidad por remuestreo utiliza pares de resúmenes de adquisición observados; no genera trayectorias celulares ni considera independientes las ventanas. Su intervalo percentil describe estabilidad frente al remuestreo del banco observado y no garantiza representatividad poblacional.

Los registros no implementan los dos brazos físicos FD7/FD8. La evidencia corresponde al transporte de predicción y calibración, separado de los certificados de identidad temporal.

## Reproducción

Crear `E11_INPUTS.zip` con `e9_core.py`, `MODEL_SELECTION.json`, `E9_NUMERICAL_PROTOCOL.json`, `policy.py`, `COHORTS.json` y `E11_PROTOCOL.json`. Copiar ese ZIP, `preflight.py`, `run_e11.py` y `analyze_reserve.py` a `/content` en Colab CPU.

1. Ejecutar `python /content/preflight.py`. Instala NumPy 2.2.6, pandas 2.2.3 y Numba 0.61.2; descarga y verifica el archivo fuente; audita los 62 CSV admitidos.
2. Ejecutar `python /content/run_e11.py development`. Conserva todas las comparaciones y congela una candidata si existe alguna admisible.
3. Solamente con `SELECTED_POLICY.json` en estado `FROZEN_BEFORE_RESERVE`, ejecutar `python /content/run_e11.py reserve`.
4. Ejecutar `python /content/analyze_reserve.py` después de completar los 84 contextos reservados. Requiere también matplotlib.

Los resultados se escriben en `/content/chronowitness-e11-20261111`. Utilizar un runtime nuevo para una reproducción independiente. La auditoría separada comprueba métricas, identidades y maduración; durante ejecución se contrasta la fórmula del predictor por dos expresiones algebraicas y la política con otra implementación y con enmascaramiento de errores futuros. Esto no constituye un nuevo ajuste independiente de los modelos.

La custodia de esta campaña se realiza mediante el conector autenticado de Drive con lectura íntegra de los bytes. Los scripts no montan Drive automáticamente.

## Licencias

Código original de ChronoWitness: MIT. Datos de Nałęcz-Jawecki et al.: [Zenodo 7808385 v1.1](https://doi.org/10.5281/zenodo.7808385), CC-BY-4.0. Artículo: [The MAPK/ERK channel capacity exceeds 6 bit/hour](https://doi.org/10.1371/journal.pcbi.1011155). La procedencia de fechas se conserva respecto del commit `03f9a059d91caa2b72873e2317134ea7f7500203` de `pawelnalecz/pulsatile-information`. Las licencias de datos originales se conservan; los manuscritos privados y el anexo comercial no forman parte de esta publicación de código.
