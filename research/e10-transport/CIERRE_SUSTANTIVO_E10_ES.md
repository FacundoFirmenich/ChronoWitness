# E10: frontera de transporte temporal y jurisdicción de la calibración

El proyecto queda mejor situado para delimitar la aplicación del método: E10 añade una evaluación sin reajuste en otros dos días de adquisición y cuatro relojes de estímulo. El resultado fortalece la utilidad predictiva de la historia de entrada en estas condiciones y restringe la autoridad de la corrección aditiva temprana. La protección reduce el daño frente a la corrección sin protección, pero no acredita beneficio uniforme frente al modelo base.

## Qué se ejecutó

Se evaluaron íntegramente 36 registros de MCF-10A/optoFGFR/ERK con relojes de 5, 7, 20 y 30 minutos, ajenos a las fechas de TRAIN, calibración y TEST de E9. Los doce conjuntos de coeficientes y sus estandarizadores permanecieron congelados; no hubo reajuste, selección de penalización ni elección del alineamiento por rendimiento. Se mantuvieron horizontes de 5, 10 y 20 minutos, ambos alineamientos y las ventanas temprana, de validación y tardía de E9.

Los 216 contextos contienen 1.367.692 ventanas tardías con soporte emparejado entre métodos. Las ventanas se solapan; horizontes, alineamientos y segmentos pueden reutilizar células. Hay dos unidades de transporte por fecha, no 216 réplicas independientes ni 1.367.692 observaciones independientes. Los registros de 2019 son anteriores al entrenamiento de E9: esta evaluación es transporte retrospectivo entre adquisiciones, no una prueba de despliegue cronológico hacia el futuro.

## Resultado sustantivo

| Criterio | Corrección sin protección | Corrección con protección |
|---|---:|---:|
| Contextos con RMSE >1% peor que el modelo base | 149/216 | 76/216 |
| Contextos con q95 del error absoluto >1% peor que el base | 145/216 | 79/216 |

La protección mejora estrictamente el RMSE base en 51/216 contextos. La historia de estímulo supera al predictor que usa únicamente historia de señal en 187/216. En E9 estas cifras eran 4/72 y 21/72: corresponden a diferentes condiciones y denominadores; no son una comparación aleatorizada ni una mejora del algoritmo. E10 conserva el mismo algoritmo.

| Fecha | Reloj (min) | Contextos | Entrada mejora RMSE | Protección mejora RMSE | Daño RMSE >1% | Daño q95 >1% |
|---|---:|---:|---:|---:|---:|---:|
| 2019-09-03 | 20 | 60 | 60 | 20 | 0 | 3 |
| 2019-09-03 | 30 | 60 | 40 | 18 | 0 | 3 |
| 2021-04-07 | 5 | 48 | 42 | 0 | 48 | 48 |
| 2021-04-07 | 7 | 48 | 45 | 13 | 28 | 25 |

El fallo queda localizado con especial claridad en el reloj de 5 minutos: todos sus contextos empeoran RMSE y q95 más del 1%. En el reloj de 7 minutos, el daño de q95 aparece en 0/16 contextos a horizonte 5, 11/16 a horizonte 10 y 14/16 a horizonte 20. Los relojes 20 y 30 muestran 3/60 daños de q95 cada uno y ningún daño de RMSE superior al 1%; eso no equivale a ausencia de daños locales. El día, la historia de estimulación y el orden de los segmentos confunden una interpretación causal de la frecuencia.

## Localidad y anidaciones

Se conservaron 1.656 intersecciones pulso/señal con al menos 20 ventanas. Hay 483 daños de q95 superiores al 1%; 196 se encuentran dentro de 94 contextos cuyo q95 agregado no supera ese umbral de daño. Al añadir el segmento temporal tardío hay 3.750 intersecciones con soporte; 1.125 resultan adversas, de las cuales 448 pertenecen a 120 contextos que el criterio agregado no señala.

Estos recuentos describen resoluciones diferentes de las mismas observaciones. No se suman entre sí ni representan nuevas réplicas. Cada partición disjunta reconstruye exactamente el soporte y el cambio de MSE del padre. Los percentiles del padre se calculan desde los residuos atómicos, no promediando percentiles de hijos.

La peor intersección pulso/señal tiene q95 protegido/base=1,3567587252, un empeoramiento del 35,68%. Corresponde a binary_rep3_pos01_period5.csv, horizonte 20, alineamiento 1, al menos 15 minutos desde el último pulso y banda baja de señal, con 1.282 ventanas. La proximidad del resultado con alineamiento 0 queda registrada; no se eligió una convención favorable.

La sensibilidad al umbral conserva 705/1.656 daños locales de q95 con tolerancia cero, 483/1.656 con 1% y 276/1.656 con 5%. La conclusión no depende exclusivamente de utilizar 1%. Ninguno de estos umbrales es una prueba de significación.

## Qué explica el diagnóstico

Para una corrección constante c en una célula/jurisdicción, el cambio exacto es ΔMSE=c²−2cμ, donde μ es el error medio posterior del modelo base. De 88.564 casos célula/contexto, la protección aplica una corrección no nula a 25.193. En 15.308 de ellos empeora el MSE tardío: 10.361 tienen dirección incompatible con el error posterior y 4.947 exceden la magnitud que podría mejorar ese error. Los restantes 9.885 casos activos no empeoran el MSE según esta clasificación exacta.

La clasificación identifica por qué falla algebraicamente una corrección, sin atribuir ese fallo a un mecanismo celular concreto. Entre todos los casos célula/contexto, 58.764 tienen menos de 20 ventanas y se conservan como LOW_SUPPORT; 29.800 alcanzan ese soporte descriptivo. La identidad sigue siendo exacta con poco soporte, pero la precisión de una inferencia biológica no queda certificada por ella. No se calcularon p-valores con ventanas tratadas como independientes.

El resultado orienta la siguiente política hacia límites explícitos de transporte o actualización causal, y no hacia aplicar automáticamente un sesgo aprendido temprano. La nota matemática demuestra qué condición adicional bastaría: un intervalo válido para la media condicional futura. Con intervalo [L,U], la corrección minimax es la proyección de cero sobre ese intervalo. E10 no inventa ese intervalo, no lo extrae retrospectivamente del resultado tardío para desplegar una política y no presenta la identidad elemental como novedad matemática.

## Gates y subgates

| Gate | Subgates y evidencia | Resultado |
|---|---|---|
| G0 · Integridad y congelación | SHA-256 de fuente completa, protocolo, modelos y normalizadores; protocolo anterior a resultados E10 | Superado |
| G1 · Procedencia e independencia | 36 registros, dos fechas disjuntas de E9; agrupación explícita de archivos y segmentos dependientes | Superado para transporte entre adquisiciones; independencia celular entre segmentos no asumida |
| G2 · Admisión | Los 36 CSV: consenso de estímulo, tiempos enteros e identidad célula/tiempo sin duplicados | Superado; orden subminuto no resuelto, ambos alineamientos conservados |
| G3 · Temporalidad | Cortes y purgas heredados, predictores causales, correcciones elegidas antes del tramo tardío, ningún reajuste | Superado según implementación y protocolo; evaluación retrospectiva |
| G4 · Cobertura | 216 contextos completos, soporte común, todas las abstenciones y LOW_SUPPORT conservadas | Superado |
| G5 · Jurisdicciones | Padre, célula, pulso/señal, segmento e intersecciones; identidades de riesgo y conservación de cada partición | Superado |
| G6 · Verificación | Reconstrucción separada de residuos, métricas y decisiones desde artefactos; sensibilidad 0/1/5%; inspección visual | Superado; no equivale a reimplementar todo el generador de predicciones |
| G7 · Custodia y reproducción | Paquete completo en Drive con lectura íntegra; código, coeficientes, protocolos y reporte público separados de manuscritos | Se documenta en CUSTODY_FINAL.json y PUBLICATION_RECEIPT.json |
| G8 · Autoridad científica | Beneficio uniforme de protección, garantía prospectiva y validación celular directa FD7/FD8 | Beneficio uniforme no superado; garantía prospectiva y FD directo no establecidos |
| G9 · Reserva siguiente | 15 registros por intervalos: 14 fechas concordantes disjuntas; un conflicto de fecha; respuestas sin evaluación predictiva | Reserva identificada; requiere protocolo nuevo y resolver/adjudicar la discrepancia |

## Recursos y decisión para el preprint

La evaluación tardó 650,00 segundos, incluida descarga y auditoría, con pico RSS de 266.224 KiB (260 MiB). El análisis y verificación posterior tardó 61,11 segundos y alcanzó 248.236 KiB (242 MiB). La campaña utilizó Colab CPU. Estos tiempos no incluyen todo el desarrollo, transferencias de custodia ni redacción.

E10 merece incorporarse como prueba empírica de transporte dependiente de jurisdicción y como diagnóstico reproducible de la corrección temprana. La utilidad de la historia de estímulo y el fallo de una corrección específica son resultados compatibles. La prioridad siguiente es fijar una política causal revisada usando E9/E10 como desarrollo y evaluarla sobre la reserva de intervalos, con separación por adquisición, antes de otorgarle nueva autoridad. Los resultados E10 no pueden reutilizarse como test intacto de esa política.

Para la reserva se detectó una discrepancia entre 2020-02-08 en el nombre de carpeta y 2020-02-09 en el identificador de adquisición de min15_optmean_rep1.csv. Se conservan ambas; no se inventa su resolución. Las otras 14 fechas están mapeadas desde el código fuente del estudio. Ese mapeo no sustituye la auditoría completa de los CSV ni la congelación del siguiente protocolo.

La intervención celular directa de FD7/FD8 sigue requiriendo registros compatibles con ambos brazos físicos y sus condiciones de adquisición. E10 usa otros estímulos y no altera los certificados matemáticos ni los resultados adversos históricos.

Fuentes: [Nałęcz-Jawecki et al., PLOS Computational Biology](https://doi.org/10.1371/journal.pcbi.1011155); [datos originales, Zenodo 7808385 v1.1](https://doi.org/10.5281/zenodo.7808385), CC-BY-4.0. Código original de ChronoWitness: MIT.
