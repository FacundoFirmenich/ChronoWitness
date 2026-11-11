# Transporte local de una corrección aditiva

Esta nota deriva el criterio de riesgo que gobierna E10. La identidad es elemental y se utiliza como instrumento de diagnóstico; no se reclama prioridad matemática. Los resultados empíricos se incorporan separadamente cuando termina la ejecución.

Sea e la predicción base menos el valor observado, y c una corrección que se resta de esa predicción. En una jurisdicción j donde c es constante, con el mismo soporte de observaciones para ambos métodos,

ΔMSE_j = media_j[(e−c)²−e²] = c²−2c μ_j,

donde μ_j=media_j(e). No requiere gaussianidad, independencia ni aproximaciones asintóticas. Es una identidad descriptiva de los errores observados; no identifica por sí sola un mecanismo celular.

Para c≠0, una corrección empeora el MSE si y solo si c²>2cμ_j. Hay dos casos mutuamente excluyentes: dirección incompatible, cμ_j≤0; y exceso de magnitud, cμ_j>0 pero |c|>2|μ_j|. La igualdad marca ausencia de cambio. Una corrección que reduce MSE no tiene por qué mejorar el percentil 95 del error absoluto; E10 verifica ambos criterios por separado.

Si c varía entre células, el padre satisface ΔMSE=media(c²−2ce), no c_promedio²−2 c_promedio e_promedio. Para cualquier partición disjunta y exhaustiva, ΔMSE_padre=Σ_j(n_j/N)ΔMSE_j. Se reconstruye exactamente desde los hijos. El percentil 95 del padre se reconstruye con los residuos atómicos; no es el promedio de los percentiles de los hijos. Las particiones cruzadas se conservan por separado y no se suman entre sí, porque reutilizan observaciones.

## Qué exigiría una garantía prospectiva

Supongamos que c se elige con la información pasada F, el error futuro tiene segundo momento finito y su media condicional μ=E[e|F] pertenece a un intervalo justificado [L,U]. Entonces el cambio condicional de riesgo es c²−2cμ. La peor variación compatible con el intervalo es c²−2cL para c≥0 y c²−2cU para c≤0.

La corrección minimax es la proyección de 0 sobre [L,U]: c*=L si L>0; c*=U si U<0; c*=0 si L≤0≤U. El peor incremento resultante es −dist(0,[L,U])². En particular, las correcciones seguras positivas cumplen 0≤c≤2L cuando L≥0, y las negativas cumplen 2U≤c≤0 cuando U≤0.

Estas expresiones no producen por sí solas un intervalo válido para la media futura. Un intervalo de la media pasada no se convierte automáticamente en intervalo de la media futura. Si la cobertura del intervalo es probabilística, la conclusión de seguridad se restringe al evento de cobertura; el riesgo incondicional necesita controlar también el evento de fallo. La selección retrospectiva de una jurisdicción exige considerar asimismo cómo se obtuvo ese intervalo.

Sin una restricción verificable sobre el cambio futuro, cualquier c≠0 puede perjudicar: basta una continuación con μ=0, que produce un incremento c². El pasado finito por sí solo no descarta esa continuación. Por tanto, el gate prospectivo exige una hipótesis o evidencia adicional de transporte, un límite de deriva o una estrategia secuencial evaluada con separación temporal apropiada. E10 no sustituye ese requisito por un intervalo inventado ni despliega una corrección elegida con respuestas tardías.

## Jurisdicciones y resolución

Las unidades conservadas son fecha, reloj, campo/archivo, célula, horizonte y alineamiento. Se cruzan con tiempo desde el último pulso, banda de señal definida en TRAIN y tres segmentos de igual duración del intervalo tardío. Las células se identifican dentro de cada archivo; eso no prueba que diferentes segmentos de la misma adquisición correspondan a células distintas. Los días completos siguen siendo las unidades de transporte.

Los nodos con menos de 20 ventanas se conservan con LOW_SUPPORT. Este umbral permite distinguir el soporte del resumen y no certifica precisión inferencial: las ventanas se solapan y comparten células. No se generan p-valores tratando ventanas como réplicas. Los daños locales y las invariancias tienen la misma obligación de conservación.

## Posición respecto de FD7/FD8

E10 evalúa transporte de predicción y calibración sobre registros celulares reales con otros protocolos de pulsos. No contiene una intervención física con los dos brazos FD7/FD8. Su contribución al preprint es especificar y contrastar la jurisdicción del método de calibración y los límites de su transporte. Los certificados de identidad temporal constituyen otra línea de evidencia y mantienen sus propios requisitos.
