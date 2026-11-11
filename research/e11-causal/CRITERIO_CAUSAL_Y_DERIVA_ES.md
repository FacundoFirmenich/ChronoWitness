# Criterio causal y presupuesto condicional de deriva

La revisión E11 conserva la identidad de riesgo de E10 y hace explícita la disponibilidad temporal de la información. Sean F_t los datos disponibles antes de emitir una predicción, e_t su error base futuro y c_t una corrección medible respecto de F_t. Con segundo momento finito,

E[(e_t−c_t)²−e_t² | F_t] = c_t²−2c_t E[e_t|F_t].

La identidad no requiere gaussianidad ni independencia temporal. Requiere que c_t no utilice el error futuro que está corrigiendo. Por eso E11 admite únicamente residuos cuyo instante objetivo es estrictamente anterior al origen de la predicción actual. Los residuos del instante actual y posteriores se ocultan en una comprobación de invariancia de las decisiones.

## Qué garantiza realmente la regla sobre el pasado

Sean m_1 y m_2 las medias de dos bloques históricos admitidos, con el mismo signo no nulo. E11 propone c=γ sign(m_2) min(|m_1|,|m_2|), con γ en {1/4,1/2}. Entonces para cada bloque b se cumple c²−2cm_b<0. La razón es que c y m_b comparten signo y 0<|c|≤γ|m_b|<2|m_b|.

Además se comprueba directamente que el q95 histórico del error absoluto no empeore más de 1% en ninguno de los bloques. Esta segunda condición no se deduce de la disminución de MSE: son controles distintos. Ambos describen los datos históricos usados para construir la decisión; no constituyen una validación independiente sobre esos mismos bloques.

## Cuánto cambio futuro toleraría la corrección

Supongamos adicionalmente que la media condicional futura μ_t pertenece al intervalo [m_2−δ,m_2+δ]. Para una corrección c del mismo signo que m_2, el peor incremento de riesgo en ese intervalo es

c²−2|c|(|m_2|−δ).

La corrección es segura en MSE bajo esa hipótesis cuando

δ ≤ |m_2|−|c|/2.

Como E11 usa |c|≤|m_2|/2, el margen algebraico del miembro derecho es al menos 3|m_2|/4. Si se usa γ=1/4, es al menos 7|m_2|/8. Son relaciones condicionales, no estimaciones de la deriva real ni garantías obtenidas automáticamente del historial.

En particular, δ tendría que cubrir conjuntamente la incertidumbre de estimar una media con pocos datos y su posible cambio temporal o contextual. Las observaciones históricas son dependientes. E11 no afirma haber construido una cobertura válida para μ_t a partir de esos bloques y no convierte estos márgenes algebraicos en intervalos de confianza.

## Anidación y abstención

El nivel de localidad se determina por variables disponibles en el origen y por el soporte histórico: célula–fase–banda, célula–fase y célula. El retroceso responde a insuficiencia de soporte. Cuando una jurisdicción ya tiene soporte pero falla la condición de signo o de cola, el método se abstiene en vez de buscar un padre más favorable.

Eso conserva el significado de un resultado local adverso. No supone que todas las jurisdicciones sean intercambiables ni utiliza otras células para inventar soporte de una célula escasa. La variante celular sin las dos particiones adicionales permite contrastar si esa resolución aporta valor en el banco observado.

## Cómo se adjudica el transporte

La selección usa únicamente E9/E10 como desarrollo. La prueba reservada conserva las adquisiciones por fecha, todos los horizontes y ambos alineamientos. Durante esa prueba se permite aprender de errores anteriores ya observados, como haría una política secuencial; no se permite volver a escoger parámetros utilizando el resultado final.

La mejora del predictor que conoce la historia de estímulo, la mejora de su calibración y la identificación de un mecanismo celular son tres afirmaciones distintas. E11 aborda la segunda bajo un predictor base congelado y registra la primera como comparación complementaria. No atribuye causalmente los cambios de error a una topología biológica ni valida una intervención FD7/FD8 ausente del experimento.
