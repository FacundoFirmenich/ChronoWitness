# De la identidad del modelo al ensayo

[English](ASSAY_GUIDE.md)

| Decisión | Información necesaria | Consecuencia |
|---|---|---|
| Definir la comparación | Símbolos FD7, duración de pulso, estimando y regla de observación por brazo | Fija a qué cantidad aplica la identidad |
| Elegir el bloque experimental | Unidad de asignación, emparejamiento, dependencia y ponderación | Define la puntuación y la información disponible antes de cada bloque |
| Controlar la adquisición finita | Cotas del estado inicial, estabilización y ventana | Determina la tolerancia por transitorios |
| Elegir la lectura | Funcional de extremos y canales medidos | Permite corregir extremos o usar una cota para la ventana cruda |
| Calificar la entrega | Envolventes por brazo de amplitud y tiempos en la historia pertinente | Acota el desvío de la dinámica de referencia |
| Calificar la detección | Respuesta, topes, ganancias y envolventes condicionales de conteos | Acota saturación y otras distorsiones declaradas |
| Declarar los insumos de la prueba | Tolerancia de media predecible y soporte casi seguro | Habilita la prueba por bloques acotados |
| Interpretar un rechazo | Hipótesis conjunta de modelo y observación, y controles de atribución | Delimita la exclusión del modelo y la evidencia necesaria para identificar un mecanismo |

Calificá la referencia periódica o la cota transitoria. Si el funcional de extremos es observable, usá la lectura corregida. Si sólo disponés de la lectura cruda, verificá la cota correspondiente. Incorporá después los presupuestos de entrega y detección. La actualización secuencial exige tolerancia predecible y rango conocido. Si falta alguno, queda pendiente la calificación.

La tolerancia acota la media condicional. El radio de soporte acota la magnitud posible de la puntuación. Si la tolerancia alcanza o supera el radio, el bloque no puede incrementar el capital de apuestas especificado. Subir el tope del detector puede reducir el sesgo de recorte y ampliar el radio. Extender la estabilización o la ventana puede reducir el transitorio y aumentar el tiempo de adquisición.

En un modelo de traducción con tasas conocidas `(gamma, kappa, delta)`, una envolvente de comparación puede usar `g <= gamma`, `k >= kappa` y `d <= delta`. La corrección por extremos usa la matriz media conocida. Una traza de entrega revelada en el bloque actual requiere un argumento condicional adecuado para incorporarse como tolerancia predecible. El software comprueba los contratos numéricos. La evidencia de adquisición justifica sus premisas físicas.
