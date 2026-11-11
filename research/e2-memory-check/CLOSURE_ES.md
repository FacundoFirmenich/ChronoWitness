# E2: encaje de memoria verificado y preparación Colab + Drive

11 noviembre 2026. La posición operativa mejora: E1 completo y E2-A retrospectivo se ejecutaron con datos reales bajo un límite de memoria menor que 3 GB, sin swap. Ya no hay una incertidumbre importante sobre el encaje del cálculo en 4 GB. La prueba fue en GitHub Actions; no mide los servicios base ni la CPU concreta de qBraid o Colab.

## Resultado medido

| Medida | Resultado |
|---|---:|
| CPU asignada al contenedor | 2 equivalentes CPU |
| Límite solicitado | 3.000.000.000 bytes |
| Límite efectivo del kernel, redondeado por páginas | 2.999.996.416 bytes |
| Swap permitido | 0 |
| Pico de memoria cgroup, con procesos y caché | 1.137.885.184 bytes = 1,138 GB decimales |
| Mayor RSS de un proceso hijo | 538.456 KiB = 551.378.944 bytes |
| Eventos de agotamiento / procesos eliminados por memoria | 0 / 0 |
| Job completo, incluidas preparación y entrega | 7 min 46 s |
| Pipeline medido E1 + E2 | 444,69 s |
| Etapa E1, incluida descarga y reajuste | 441,37 s |
| Etapa E2, con los datos y modelos ya disponibles | 3,31 s |
| Reproducción E1 | 210 registros contrastados con el archivo previo; las métricas JSON coinciden byte por byte |
| E2-A | 810 registros de métricas; 270 registros de calibración; 54 comprobaciones de ventanas |

El presupuesto previo de 1–4 horas era una reserva de planificación, no una medida. Este alcance ya implementado se completó mucho más rápido. Los 441,37 s de E1 incluyen red y lectura: no se atribuyen íntegramente al cálculo CPU. Los 3,31 s no incluyen descargar datos, instalar dependencias ni reentrenar E1. La lectura de memoria es del contenedor completo; el RSS es del mayor proceso hijo, magnitudes distintas.

El primer intento, run 42930922679, terminó antes de cargar datos por una comprobación demasiado estricta de igualdad del límite: el kernel redondea a páginas de 4096 bytes. Se corrigió la comprobación para admitir exclusivamente ese redondeo hacia abajo, conservando el mismo límite. Su evidencia se preserva. No fue un fallo de memoria de E2.

## Alcance científico realmente ejecutado

El código E1 y su protocolo se verificaron contra el commit congelado original. E2 utiliza cinco predictores, dos alineamientos temporales, tres horizontes y tres ventanas tempranas de calibración. Compara predicción original, corrección de desplazamiento y corrección afín con pendiente no negativa. Los targets de calibración terminan en los frames 72, 96 o 120; la evaluación común comienza en origen 132, cuya historia empieza en 121. No hay solapamiento temporal entre los targets de calibración y las características de evaluación. Las células pueden repetirse: no es validación en células nuevas.

E2 es desarrollo retrospectivo: los experimentos de evaluación E1 ya se habían examinado. La prueba computacional no demuestra que una calibración predictiva sea una cota física de sesgo FD7 ni sustituye un experimento FD7 celular.

El resultado científico inicial es matizado: corregir desplazamiento puede reducir sesgo, pero añadir escala no mejora uniformemente. Por ejemplo, para historia con entrada, horizonte 60 min, alineamiento principal y cutoff 120, la corrección afín mejora RMSE en dos experimentos y lo empeora en el tercero (406,829 a 408,765). Conservamos todos los cortes y métodos; no seleccionamos después el más favorable. La siguiente tabla muestra toda la sensibilidad a los tres cortes en esa combinación de modelo, horizonte y alineamiento; el paquete incluye las restantes combinaciones.

| Experimento | Último target de calibración | RMSE original | RMSE desplazamiento | RMSE afín | Sesgo original / desplazamiento / afín |
|---|---:|---:|---:|---:|---|
| 2022-04-15 | 72 | 447.430 | 440.833 | 438.216 | 76.560 / 1.548 / -32.787 |
| 2022-04-21 | 72 | 413.252 | 420.953 | 421.895 | -48.522 / 93.694 / 98.136 |
| 2022-04-23 | 72 | 406.829 | 409.109 | 409.912 | -1.592 / 43.159 / 50.667 |
| 2022-04-15 | 96 | 447.430 | 440.848 | 438.216 | 76.560 / -3.881 / -33.558 |
| 2022-04-21 | 96 | 413.252 | 413.325 | 412.842 | -48.522 / 49.138 / 29.253 |
| 2022-04-23 | 96 | 406.829 | 406.892 | 410.224 | -1.592 / 7.332 / -20.534 |
| 2022-04-15 | 120 | 447.430 | 440.982 | 438.749 | 76.560 / -11.558 / -39.278 |
| 2022-04-21 | 120 | 413.252 | 411.439 | 412.307 | -48.522 / 29.316 / 10.714 |
| 2022-04-23 | 120 | 406.829 | 406.826 | 408.765 | -1.592 / -0.762 / -17.131 |

No se han generado intervalos o p-valores tratando ventanas o células como réplicas independientes. El resultado requiere evaluación científica completa antes de integrarse en el manuscrito; el encaje de recursos sí queda verificado para este código y estos datos.


## Reproduction

The repository includes a CPU Colab notebook with explicit Drive checkpoints. Its Colab execution remains pending.

Measured run: https://github.com/FacundoFirmenich/ChronoWitness/actions/runs/42931139856
