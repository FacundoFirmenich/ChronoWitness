# Resultados científicos e interpretación

[English](SCIENTIFIC_RESULTS.md)

ChronoWitness estudia qué puede distinguir una entrada temporal para una lectura fijada. El par FD7 iguala varios resúmenes habituales y permite separar clases concretas de lectores dinámicos.

## Identidad y umbrales

Cada secuencia tiene 24 símbolos, doce de cada tipo. Coinciden los conteos cíclicos de palabras hasta orden siete, el multiconjunto de rachas etiquetadas por símbolo y la autocorrelación cíclica. También coinciden exactamente los polinomios de ocupación de dos estados. En régimen periódico, todo lector de Markov estrictamente positivo de dos estados de la clase especificada tiene el mismo perfil en ambos brazos. La identidad para promotores en tiempo continuo y una cascada lineal estable común extienden la igualdad a la expresión media por período.

Cada umbral combina la exclusión de la clase inferior con un testigo explícito. Cuatro estados deterministas son necesarios y suficientes para separar la ley de perfiles balanceada por fase. Tres estados bastan para los observables respectivos de lectores de Markov positivos y lectores cinéticos positivos en tiempo continuo. El resultado afirma la existencia de un separador en cada umbral.

## Margen certificado

El primer testigo cinético emplea espectros enteros y propagadores racionales por pulso. Su contraste de ocupación del estado cero es aproximadamente 1,03 × 10⁻⁶. Una búsqueda declarada por separado sobre tasas positivas produce un candidato racional cuyo contraste integrado para un indicador de estado en [0,1] está entre 0,0100794705475041 y 0,0100794705475042.

La uniformización con redondeo dirigido y el cálculo de la distribución invariante mediante árboles de Markov certifican el candidato. Una vecindad cuantificada de perturbaciones conserva la mitad del margen. Las tres búsquedas agotaron su presupuesto fijo de generaciones. La certificación establece la mejora del candidato y deja abierta la optimización global.

## Observación e inferencia

La ventana finita puede retener transitorios del promotor y del reportero. La corrección por extremos cancela la contribución de la condición inicial del reportero si el funcional correspondiente es observable. Las cotas de contracción de la ventana cruda ofrecen otra vía. Los errores de amplitud y tiempo de entrega requieren información por brazo. La saturación requiere una cota del cambio de media condicional. La envolvente explícita de traducción conserva la correlación ARNm–proteína y las degradaciones.

La prueba usa bloques con soporte acotado y tolerancia justificada en la media condicional. Las apuestas predecibles y las mezclas fijas especificadas preservan la validez bajo parada opcional. El conteo exacto de prefijos calcula probabilidades de primer cruce bajo leyes de bloques de dos puntos declaradas y muestra el efecto de la tolerancia y de la asignación de apuestas en esos modelos.

## Procedencia y mapa de evidencia

El certificado FD7 v0.7.0 fija el par y sus propiedades. Hay programas independientes que las reproducen. El historial de descubrimiento, la minimalidad de la longitud y una familia general FDₖ quedan abiertos. El control adicional con rachas emparejadas verifica que igualar dosis, multiconjunto de rachas y número de conmutaciones admite pares que pierden la identidad de ocupación.

| Resultado | Implementación | Evidencia |
|---|---|---|
| Diseño emparejado y umbral determinista | `research/analysis/` | Datos S1–S4 |
| Criterio de ocupación de dos estados | `research/analysis/verify_markov_boundary.py` | Certificados polinómicos y salidas de referencia |
| Reportero finito y cotas de entrega | `research/finite_reporter/`, `research/input_robustness/` | Datos S6–S7 |
| Inferencia estadística y saturación | `research/statistical_inference/`, `research/count_tails/` | Datos S8–S9 |
| Traducción catalítica explícita | `research/translation_counts/` | Datos S10 |
| Testigo cinético espectral | `research/kinetic_reader/` | Datos S11 |
| Testigo de mayor margen, potencia y controles | `research/design_frontier/` | Datos S12 |
