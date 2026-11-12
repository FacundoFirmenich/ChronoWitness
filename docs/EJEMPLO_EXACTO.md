# Ejemplo exacto paso a paso

[English](WORKED_EXAMPLE.md)

Elegí `example` en el menú o ejecutá `python research/design_frontier/tutorial.py` desde la raíz. El programa usa aritmética racional y el certificado cinético distribuido.

1. **Verificar FD7.** La construcción polinómica hacia adelante comprueba la igualdad de los numeradores de ocupación de dos estados para ambos símbolos.
2. **Fijar un promotor.** Las fracciones de equilibrio son 1/4 y 3/4, las tasas de relajación son uno y dos y la duración de pulso es log(2). Las contracciones son exactamente 1/2 y 1/4.
3. **Integrar un período.** Ambas secuencias dan `1346711/1474746 + 12 log(2)`. Es una instancia de la identidad paramétricamente uniforme.
4. **Transportar la media.** Un reportero lineal común con cociente síntesis/degradación 3/2 conserva el contraste periódico cero.
5. **Leer el certificado alternativo.** El candidato positivo de tres estados tiene contraste integrado certificado del estado cero superior a 0,01007947.
6. **Definir la observación.** Cada bloque pareado independiente muestrea los indicadores de ambos brazos a tiempos uniformes independientes en sus ciclos periódicos. La diferencia tiene soporte [-1,1] y esperanza igual al contraste de ocupación.
7. **Calcular un horizonte suficiente.** Para nivel 0,05 y potencia objetivo 0,8, la cota de Hoeffding y las cotas racionales de logaritmos y raíces certifican 200 326 bloques suficientes en el modelo ideal. Es una cota conservadora para esa ley de observación.

`Data_S12_design_power.csv` compara probabilidades exactas de primer cruce para dos mezclas válidas bajo leyes iid de puntuaciones en {-1,+1}, con probabilidades y tolerancias declaradas. El control `python research/design_frontier/controls.py` verifica que otro par con la misma dosis, las mismas rachas y el mismo número de conmutaciones pierde la identidad polinómica.

Un ensayo real necesita sustituir el indicador ideal por un reportero medido y justificar las condiciones de entrega, transitorio, detector y bloques. Véase la [guía del ensayo](ASSAY_GUIDE.md).

## Por qué contar prefijos

Para las leyes de dos puntos declaradas, el capital queda determinado por el número de bloques y de resultados positivos. Agrupar prefijos equivalentes vuelve factible el cálculo exacto de primer cruce. Cuando el modelo de observación o dependencia rompe esa agrupación, Monte Carlo permite estimar la probabilidad con incertidumbre de simulación cuantificada. Los casos exactos sirven de referencia para verificar ese simulador.
