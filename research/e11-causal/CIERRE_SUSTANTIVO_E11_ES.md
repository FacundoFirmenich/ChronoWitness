# E11: transporte de calibración causal y jurisdicciones anidadas

El proyecto queda mejor posicionado que al cierre de E10: una corrección que actualiza sus decisiones con errores celulares ya observados mejora el RMSE en 80 de 84 contextos reservados frente al predictor base y en 79 frente a la protección fija. La mejora convive con excepciones locales identificadas; por eso el resultado central es el transporte observado de una política concreta, acompañado de su cartografía de riesgo.

## Pregunta y diseño

¿Puede sustituirse el sesgo temprano fijo por una corrección local de memoria limitada que se adapte sin utilizar objetivos futuros? Se conservaron los coeficientes, normalizaciones y cortes de señal del TRAIN de E9. Se desarrollaron ocho políticas sobre 48 archivos de cuatro fechas ya conocidas. Las 14 adquisiciones de reserva no se utilizaron para seleccionar la política ni reajustar sus parámetros. Los 84 contextos combinan esas adquisiciones con horizontes de 5, 10 y 20 minutos y dos alineamientos.

La regla seleccionada, `w180_nested_s25`, conserva hasta 180 minutos de errores del predictor base del mismo identificador celular. En cada origen t sólo admite errores con objetivo s+h<t. Busca primero célula × fase de pulso × banda de señal TRAIN, luego célula × fase y finalmente célula; exige seis intervalos de predicción cuyo interior no se solapa, hasta un máximo de doce. Dos bloques históricos deben concordar en el signo de su error medio. Propone una corrección del 25% del menor de ambos módulos y comprueba el q95 del error absoluto en cada bloque. Si una jurisdicción tiene soporte pero falla el signo o la cola, se abstiene; no retrocede para forzar una corrección.

El criterio de selección priorizó el peor día en fracción de jurisdicciones pulso–señal con deterioro de q95 superior al 1%, seguido de la media diaria de esa fracción y del logaritmo medio de RMSE relativo. Todas las candidatas fueron admisibles. La ganadora no domina cada métrica: la memoria de 360 minutos con la misma contracción mejora más el RMSE medio de desarrollo, pero resulta peor en el criterio local prioritario. La selección quedó congelada a las 14:37:29 UTC del 11 de noviembre de 2026, antes de puntuar la reserva.

## Resultado reservado

| Medida | Protección fija | Política causal |
|---|---:|---:|
| Contextos con RMSE inferior al predictor base | 71/84 | 80/84 |
| Fechas con media de RMSE relativo inferior a uno | 12/14 | 14/14 |
| Contextos con daño de RMSE superior al 1% | 0/84 | 0/84 |
| Contextos con daño de q95 superior al 1% | 0/84 | 0/84 |
| Ventanas en que se aplica una corrección | 36,06% | 60,11% |

Se compararon 3.726.248 ventanas tardías sobre el mismo soporte. Son observaciones solapadas y dependientes, no millones de réplicas. La política causal supera a la protección fija en 79/84 contextos. La mejora geométrica media del RMSE respecto al base es del 2,73%, ponderando igualmente las fechas. Los 10.000 remuestreos pareados por adquisición dan un rango percentil descriptivo de mejora de 1,95–3,57%. Este rango describe estabilidad del banco observado; no prueba representatividad poblacional ni independencia de las ventanas.

Como comparaciones adicionales sobre el mismo soporte, la política causal mejora el RMSE frente a persistencia en 84/84 contextos y frente al predictor sin historia de entrada en 56/84. El predictor base con historia de entrada sólo supera al correspondiente predictor sin entrada en 40/84: disponer de la entrada no produce una ventaja uniforme. Estas comparaciones no son una ablación de la política causal.

## Localidad y anidación: lo que un agregado escondería

Aquí daño significa q95 del error absoluto superior al del predictor base en más del 1%. Es un umbral descriptivo predefinido, no un nivel de significación. Se publican también las sensibilidades a 0% y 5%.

| Jurisdicción | Nodos con soporte | Daños con protección fija | Daños con política causal |
|---|---:|---:|---:|
| Contexto completo | 84 | 0 | 0 |
| Fase de pulso × banda de señal | 756 | 64 | 6 |
| Segmento temporal | 252 | 0 | 1 |
| Segmento × fase × señal | 2.268 | 266 | 81 |

Las 81 excepciones de la partición más fina aparecen en 45 contextos cuyo resultado agregado no cruza el 1%. El promedio describe una mejora real y, a la vez, no autoriza cada una de sus partes. La partición por segmento conserva además una excepción donde la protección fija no tenía ninguna: la revisión tampoco domina todos los nodos.

Al umbral del 5% queda una excepción fina: `min10_optmean_rep1_h5_a0`, fecha 2020-01-31, tercer segmento, al menos 15 minutos desde el pulso y banda media de señal. Sus 1.224 ventanas muestran una razón de q95 de 1,0516603382: deterioro del 5,166%. Se conserva como adverso, sin redondearlo para aprobarlo.

El mapa local ilustrativo muestra otro caso: `min3_mean50_h20_a0`, fecha 2019-10-03, 0–4 minutos después del pulso y banda baja. Su razón local es 1,0131402 sobre 2.379 ventanas, mientras el padre tiene razón 0,9958152. Fue elegido retrospectivamente por máximo daño entre las intersecciones pulso–señal con soporte; es un caso diagnóstico, no una muestra representativa ni una nueva prueba.

Los nodos con menos de veinte ventanas permanecen como LOW_SUPPORT. Ese mínimo no es una garantía de precisión inferencial. Los MSE de los padres se reconstruyeron desde particiones disjuntas; los percentiles se calcularon desde errores individuales, sin promediar percentiles de hijos. Las inclusiones y solapamientos se conservan sin sumar una misma observación como réplica adicional.

## Resultados por adquisición

Las razones RMSE son medias de los seis contextos de cada fecha. Las fracciones de daño corresponden a las intersecciones pulso–señal y al umbral del 1%.

| Fecha | RMSE causal/base | RMSE fija/base | Daño local causal | Daño local fija |
|---|---:|---:|---:|---:|
| 2019-10-03 | 0.993507 | 0.999460 | 1.852% | 5.556% |
| 2019-10-08 | 0.989182 | 1.001479 | 0.000% | 18.519% |
| 2019-10-18 | 0.987669 | 1.000577 | 0.000% | 14.815% |
| 2019-11-09 | 0.975876 | 0.999846 | 0.000% | 7.407% |
| 2019-11-14 | 0.937294 | 0.999610 | 0.000% | 11.111% |
| 2020-01-31 | 0.964385 | 0.999374 | 3.704% | 11.111% |
| 2021-03-15 | 0.965594 | 0.999793 | 0.000% | 7.407% |
| 2021-03-18 | 0.978674 | 0.999244 | 0.000% | 20.370% |
| 2021-03-30 | 0.992679 | 0.999759 | 0.000% | 7.407% |
| 2021-04-06 | 0.963154 | 0.999711 | 1.852% | 3.704% |
| 2021-04-21 | 0.981624 | 0.999881 | 0.000% | 1.852% |
| 2021-04-26 | 0.953893 | 0.999575 | 1.852% | 3.704% |
| 2021-09-09 | 0.967697 | 0.999836 | 1.852% | 5.556% |
| 2021-09-10 | 0.971796 | 0.999737 | 0.000% | 0.000% |

## Alcance científico y epistemológico

Los registros proceden de células humanas MCF-10A con estimulación optoFGFR y lectura ERK-KTR, publicados por Nałęcz-Jawecki et al. en *The MAPK/ERK channel capacity exceeds 6 bit/hour* ([artículo](https://doi.org/10.1371/journal.pcbi.1011155), [datos v1.1](https://doi.org/10.5281/zenodo.7808385), CC-BY-4.0). Son observaciones celulares reales con estimulación temporal, no trayectorias sintéticas. El predictor usa las futuras entradas programadas, como E9; no intenta adivinar intervenciones desconocidas.

Las 14 fechas pertenecen a un mismo estudio y laboratorio. Dos, 2021-09-09 y 2021-09-10, son posteriores al desarrollo y ambas corresponden al protocolo min25; las otras doce representan transporte retrospectivo. No se extrapola ese pequeño subconjunto a una validación prospectiva general. `min15_optmean_rep1.csv` permanece excluido por discrepancia entre dos fechas de su configuración original.

La política causal usa errores tardíos anteriores ya observados; la protección fija no se actualiza con ellos. La comparación evalúa el régimen completo de realimentación, memoria, contracción y localidad. Para identificar por separado el aporte de la anidación haría falta una ablación con el mismo acceso a información y una nueva reserva. La concordancia histórica de errores tampoco constituye un intervalo válido para la media futura ni una garantía de ausencia de daño. El documento matemático asociado distingue la identidad de riesgo condicional de esa hipótesis adicional.

Estos datos no contienen los brazos físicos FD7/FD8. E11 fortalece el componente empírico de transporte y calibración del preprint; no convierte los certificados de identidad temporal en una validación celular directa de FD7, ni demuestra un mecanismo de memoria celular.

## Verificación, incidencia y recursos

Se verificó el SHA-256 del archivo fuente completo, se auditaron 62 CSV admitidos y se comprobó la congelación de predictor, protocolo y política. La ejecución contrastó la política con una implementación de referencia y con enmascaramiento de errores futuros sobre observaciones reales. La auditoría posterior reconstruyó métricas atómicas, maduración temporal e identidades anidadas para los 84 contextos.

El primer análisis posterior falló al tabular una selección vacía: pandas interpretó una máscara sin tipo booleano como selección de columnas. Se reparó mediante conversión explícita a bool y selección por `.loc`. Se conservaron el código anterior, su log y el incidente. La corrección no modificó datos, predictor, política, selección, umbrales ni predicciones. La regresión sobre un subconjunto vacío de resultados reales y la auditoría completa terminaron correctamente. Una corrección editorial posterior reparó el recorte y la codificación de las etiquetas de las figuras; el paquete científico original permanece inmutable.

Colab CPU: preflight 351,45 s; desarrollo 523,47 s; reserva 557,68 s; auditoría final correcta 69,33 s. La reserva alcanzó 669,84 MiB de RSS y la auditoría 213,59 MiB. Estos tiempos no incluyen la primera auditoría fallida, transferencias, custodia ni preparación documental.

El paquete íntegro contiene 135 entradas y 250.091.898 bytes. Sus siete partes se leyeron completamente desde Drive y su concatenación coincide con SHA-256 `85db21e961f580371c85e9bfd0ef38730cd7d4bce5b1cbb3bc80bc7caa802cba`. La publicación pública comprende código MIT, protocolos y resultados de evaluación. Los manuscritos y el anexo comercial mantienen su custodia privada.

## Decisión para el preprint

E11 queda cerrado como evaluación reservada de esta política. El paso que aporta valor ahora es integrar el resultado, su cartografía local y la derivación condicional en el manuscrito y el suplemento, conservando la distinción entre identidad FD7 y transporte de calibración. No se necesita retocar la política para presentar el avance. Una nueva versión entrenada con esta reserva requeriría otra evaluación para reclamar confirmación. No hay un impedimento computacional observado; los límites pendientes son de alcance empírico, identificación de componentes y resolución de la fecha en cuarentena.
