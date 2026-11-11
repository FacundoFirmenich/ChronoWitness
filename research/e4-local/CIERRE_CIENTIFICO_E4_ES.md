# Cierre científico E4: jurisdicciones locales y transporte de calibración

La posición científica mejora: el análisis identifica contextos donde una decisión temprana de calibración conserva o reduce el error absoluto en segmentos posteriores. El avance pertenece a la capa de observación y calibración sobre datos celulares publicados. La identidad matemática FD7 y sus certificados mantienen su alcance; este conjunto experimental no contiene la intervención pareada FD7.

## Resultado y soporte

Se ejecutaron las 648 jurisdicciones previstas, definidas por experimento, alineamiento, horizonte, segmento temporal, transición de entrada y banda de fluorescencia. Las bandas se fijaron con los cuatro experimentos de entrenamiento, con igual peso por experimento. La elección de corrección utiliza solamente segmentos tempranos; las ventanas posteriores permanecen fuera de esa elección.

De 648 jurisdicciones, 497 tienen soporte de evaluación y 270 tienen además soporte temprano para calibración local. En estas 270, la regla registra 129 mejoras de MAE superiores al 1%, 141 empates prácticos y ninguna pérdida superior al 1%. Las 227 con evaluación suficiente pero calibración insuficiente se conservan como OUT_OF_SUPPORT; las 151 con evaluación insuficiente, como NOT_ESTIMABLE. El fallback conserva el predictor original y no convierte ausencia de soporte en evidencia favorable.

Los recuentos son descriptivos: combinaciones de horizontes, segmentos y alineamientos comparten observaciones. No equivalen a 270 experimentos independientes. El umbral de 1% es una tolerancia descriptiva fijada antes de esta ejecución, con sensibilidad completa a 0,1% y 5%; no es significación estadística ni un umbral biológico universal.

## Contexto agregado principal: 60 minutos, alineamiento primario

| Experimento | Reducción MAE | Reducción RMSE | Cambio del error medio en la cola superior del 5% |
|---|---:|---:|---:|
| 2022-04-15 | 5.857% | 2.225% | +1.089% |
| 2022-04-21 | 1.631% | 0.781% | +0.490% |
| 2022-04-23 | 0.512% | 0.277% | -0.012% |

Los agregados son contexto y se reconstruyen exactamente a partir de las jurisdicciones. La cola muestra por qué no basta el promedio: en los dos primeros experimentos, la regla mejora MAE y RMSE globales, pero aumenta el promedio de los mayores errores. La selección optimiza MAE temprano; no se diseñó para garantizar mejora simultánea de todos los funcionales de error.

## Comparadores y evidencia adversa

En las 270 jurisdicciones comunes, la mezcla local fija (un tercio predictor original, un tercio offset y un tercio afín) registra 170 mejoras, 41 pérdidas y 59 empates. La corrección afín local registra 160 mejoras, 75 pérdidas y 35 empates. La regla selectiva reduce las pérdidas relevantes observadas a costa de actuar en menos contextos; no se declara un ganador universal. El soporte común permite comparar decisiones sin atribuir diferencias a composiciones distintas de datos.

Se conservan las métricas continuas, sesgo firmado, mediana, cuantiles 90/95 y promedio de la cola superior; ninguna presupone gaussianidad. La selección por fluorescencia actual usa información disponible en el origen, no estados regulatorios latentes. Las aristas representan transiciones programadas de entrada, no conexiones moleculares inferidas.

## Verificación y consecuencia para el preprint

La ejecución CPU de Colab terminó sin error: 63,43 segundos totales y 10,54 segundos en la etapa científica, en una máquina de dos CPU lógicas. Se verificaron CRC, hashes, igualdad de las fuentes con el paquete congelado, reconstrucción de decisiones tempranas y de MAE, sesgo y MSE agregados. El propio ejecutable reprodujo las métricas globales E3 para los comparadores heredados.

El resultado fortalece el preprint como contribución teórica y computacional con un estudio retrospectivo de observación celular. Permite describir dónde es útil una corrección y dónde se debe abstener. La generalización a experimentos nuevos, una garantía condicional de sesgo para el test FD7 y la validación celular directa de sus estímulos siguen siendo cuestiones distintas. El próximo paso de esta edición es integrar estos resultados y su evidencia adversa en manuscrito, suplemento, figuras y repositorio, conservando el contenido matemático y la separación respecto del anexo comercial confidencial.
