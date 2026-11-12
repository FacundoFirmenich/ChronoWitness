# Observaciones celulares, predicción y transporte local

[English](CELLULAR_OBSERVATIONS.md)

Estos estudios complementan la identidad exacta al evaluar la capa de observación. Las mediciones publicadas proceden de [Lugagne, Blassick y Dunlop, Nature Communications 15:2148 (2024)](https://doi.org/10.1038/s41467-024-46361-1). Los [datos procesados](https://doi.org/10.5281/zenodo.8114649) se distribuyen con CC BY 4.0.

E1 conserva cuatro experimentos originales de entrenamiento y tres de evaluación. Añadir la entrada al historial de fluorescencia reduce el RMSE principal a 60 minutos en 4,9729%, 17,0950% y 17,0921%. El primer valor queda 0,0271 puntos porcentuales por debajo del criterio descriptivo original del 5%. E2 transporta a ventanas tardías la calibración temprana por desplazamiento y afín, con resultados mixtos. E3 selecciona la corrección en una validación temprana temporalmente separada. Entre 54 combinaciones correlacionadas obtiene 13 mejoras de RMSE, 3 deterioros y 38 predicciones iguales. E4 desagrega el transporte por contexto local, soporte y distribución de errores.

| Política sobre las mismas 270 jurisdicciones con soporte | Mejoras de MAE >1% | Deterioros >1% | Empates prácticos |
|---|---:|---:|---:|
| Desplazamiento | 127 | 80 | 63 |
| Afín | 160 | 75 | 35 |
| Mezcla fija equiponderada | 170 | 41 | 59 |
| Selección temprana | 129 | 0 | 141 |

La selección eleva la media de error de la cola superior en 31 jurisdicciones con soporte. Las ventanas solapadas, los horizontes y los alineamientos comparten datos. Cada arista representa una transición de entrada observada. La inferencia se circunscribe a la predicción y al transporte de calibración. Sigue abierta la intervención emparejada FD7 en células y la inferencia del número de estados del promotor a partir de estos registros.

## Reproducción

- E1/E2: [protocolo, benchmark, calibración y evidencia](../research/e2-memory-check/).
- E3: [selección agrupada anidada y decisiones tempranas](../research/e3-calibration-transport/).
- E4: [registro de soporte, métricas y verificación independiente](../research/e4-local/).

`python reproduce_release.py` reproduce el núcleo matemático y el Monte Carlo de trayectorias. Los estudios con datos externos tienen instrucciones propias de adquisición y ejecución. Comparten NumPy 2.2.6 y SciPy 1.15.3.
