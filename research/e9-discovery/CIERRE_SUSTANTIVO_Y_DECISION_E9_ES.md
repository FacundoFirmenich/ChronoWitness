# Próxima ampliación de ChronoWitness: señalización humana y jurisdicciones celulares

Fecha de auditoría: 11 de noviembre de 2026.

**La investigación está mejor posicionada: encontramos un nuevo dominio celular de otro laboratorio con datos públicos utilizables y una partición por días de adquisición que permite preparar una evaluación externa real. La primera elección es MCF-10A / optoFGFR / ERK.** La búsqueda también identifica una ampliación espacial especialmente pertinente y un conjunto pequeño de osciladores para estudiar la relación entre respuestas individuales y agregadas.

Este cierre acredita descubrimiento, acceso parcial verificado, estructura de datos, procedencia y selección de cohortes. La evaluación predictiva E9 todavía no se ejecutó. Los resultados y daños locales de E6/E8 conservan su estado anterior; encontrar otro dominio no los corrige ni los invalida.

## Comparación de candidatos

| Prioridad | Dominio y fuente primaria | Evidencia recuperada | Ampliación que permite | Condición pendiente |
|---|---|---|---|---|
| 1 | [MCF-10A: optoFGFR y ERK](https://doi.org/10.1371/journal.pcbi.1011155), [datos Zenodo v1.1](https://doi.org/10.5281/zenodo.7808385) | Inventario completo del ZIP: 81 CSV. Dos CSV leídos completos, CRC y SHA-256 verificados; cabeceras de otras familias e inputs de 15 registros examinados. | Transporte temporal y de calibración local en señalización humana; contraste entre pulsos regulares e intervalos variables. | Importación completa, verificación de alineamiento y protocolo numérico antes de puntuar el test. |
| 2 | [MDCK: emisoras, receptoras, cAMP y ERK](https://doi.org/10.1371/journal.pcbi.1009873), [Dryad](https://doi.org/10.7272/Q6QC01RN) | Metadatos del archivo de imágenes y código de procesamiento; dos ejemplos MATLAB contienen coordenadas, marcas bPAC y máscaras nucleares. | Cartografía espacial y temporal: emisor/receptor, distancia, contexto e intervención. | Descargas de Dryad fallaron: API 401 y enlace público 403. Los ejemplos pequeños no contienen la tabla completa de ERK y estímulos. |
| 3 | [Relojes celulares optogenéticos](https://doi.org/10.7554/eLife.97754), [datos de mother machine](https://cdn.elifesciences.org/articles/97754/elife-97754-data3-v1.xlsx) | XLSX descargado y estructura verificada: 6 canales de sincronización y 10 de entrainment, muestreo de 9 minutos y ventanas de iluminación anotadas. | Banco pequeño para contrastes locales de fase y respuestas a pulsos frente a la agregación. | Pocas adquisiciones; una hoja por condición no equivale a múltiples experimentos independientes. |
| 4 | [Transferencia dinámica de regulación eucariota](https://doi.org/10.1016/j.cels.2021.08.003), [archivo Zenodo](https://doi.org/10.5281/zenodo.5116822) | Artículo y metadatos: 119 condiciones de estímulo, citometría y archivo de 4,94 GB. | Nuevo dominio de distribuciones de respuesta y familias de estímulo. | Archivo íntegro no inspeccionado. Las mediciones de citometría no siguen a la misma célula en el tiempo. |
| Referencia | [Decodificación de promotores de mamíferos](https://doi.org/10.1093/nar/gkad273) | El artículo declara que no depositó datos en repositorios externos. | Contextualización de promotor, transcripción y traducción. | No hay una cohorte pública de trayectorias emparejadas verificada en esta búsqueda. |
| Reserva | [Transcripción naciente en levadura / PP7](https://doi.org/10.1016/j.molcel.2018.04.012) | Artículo completo inspeccionado; plataforma científicamente relevante. | Acercamiento al observable transcripcional. | No se localizó un repositorio público de entradas y trayectorias emparejadas; eso no demuestra que no exista. |

## Qué está comprobado en ERK

Las células humanas MCF-10A reciben flashes azules de 100 ms que activan optoFGFR; ERK se observa mediante ERK-KTR con muestreo de un minuto. Es un dominio experimental distinto del banco bacteriano previo. Su contribución potencial a ChronoWitness es comprobar si la organización temporal y local de la evaluación sigue siendo útil bajo otro mecanismo, reportero y laboratorio.

El ZIP contiene 66 CSV de codificación binaria, 6 de intervalos variables y 9 de intervalos con separación mínima. Los dos archivos completos examinados tienen 99.701 y 100.000 filas, 500 trayectorias cada uno, coordenadas nucleares, señal nuclear y de imagen, tiempos y `is_light_pulse`. En cada archivo, 400 trayectorias llevan `is_preselected=True` y 100 llevan `False`.

El estudio seleccionó primero 500 trayectorias por duración y estabilidad del área nuclear y después descartó las 100 con menor respuesta según la energía de la derivada. Nuestro análisis puede conservar las 500 exportadas, sin excluir por respuesta débil. Esto amplía la evaluación respecto del subconjunto publicado de 400; no recupera las células eliminadas antes de exportar las 500.

La inspección del código distingue tres normalizaciones: `Q3` usa una ventana centrada, `Q4` la media de toda la trayectoria y `Q3backw` una ventana retrospectiva. Las dos primeras no son admisibles como normalización prospectiva. **El CSV exportado utiliza `Q3backw`: no se ha demostrado una fuga futura en esa columna exportada.** La implementación de E9 deberá reconstruir y verificar las variantes causales desde los campos originales. Tampoco puede utilizar la intensidad futura de imagen como predictor disponible en el origen.

## Independencia y selección de la cohorte

La correspondencia entre nombres y fechas procede del [código original fijado por commit](https://github.com/pawelnalecz/pulsatile-information/tree/03f9a059d91caa2b72873e2317134ea7f7500203). Algunos nombres `rep` corresponden a posiciones del mismo día. El manifiesto evita convertir esas etiquetas en independencia experimental.

La selección primaria reúne los relojes de 3, 10 y 15 minutos, dos campos por reloj y cinco días:

| Función | Días de adquisición | CSV | Papel |
|---|---|---:|---|
| Entrenamiento | 27 y 28 de abril de 2021 | 12 | Ajuste de modelos propios de este dominio y particiones aprendidas. |
| Calibración y selección | 29 de abril de 2021 | 6 | Decisiones metodológicas sin acceder a los resultados del test. |
| Evaluación reservada | 1 y 2 de mayo de 2021 | 12 | Contraste posterior con todas las condiciones del día juntas. |

Los 16 CSV con relojes de 5/7 minutos pertenecen al 7 de abril de 2021. Los 20 con relojes de 20/30 minutos proceden del 3 de septiembre de 2019. Se conservan como dominios auxiliares de protocolo, sin repartir posiciones del mismo día entre entrenamiento y test. Los dos CSV completos de la auditoría son auxiliares de 5 minutos: no se calcularon errores ni se seleccionaron políticas con respuestas de los días reservados.

Dos días de test aportan una evaluación externa acotada. El número de células o ventanas no multiplica el número de días independientes.

## Localidad, anidaciones y aristas de comparación

La organización básica será dominio → día → protocolo → campo → célula → segmento temporal, cruzada con horizonte, tiempo desde el último pulso, historia de entradas y soporte de calibración. Se conservan conjuntos mayores, intersecciones e identidades originales.

Las comparaciones entre predictor base, calibración sin protección y política local protegida deberán usar las mismas células y ventanas disponibles. Cada daño local, cola de error y pérdida de cobertura seguirá visible aunque mejore el promedio. MAE y RMSE globales se reconstruirán como descripciones complementarias. Los cuantiles parentales se recalcularán a partir de los residuos originales; no se obtendrán promediando cuantiles de hojas.

Las divisiones se fijarán por metadatos, historia observable o cortes aprendidos exclusivamente en entrenamiento. `NOT_ESTIMABLE` y `OUT_OF_SUPPORT` conservarán su evidencia y razón. Las jurisdicciones solapadas no serán réplicas y las posiciones nucleares no se presentarán como contactos celulares medidos.

En MDCK esa arquitectura tendría una lectura espacial más directa: célula emisora o receptora, distancia, condición farmacológica/genética y segmento de respuesta. El material pequeño recuperado permite confirmar parte de la estructura espacial, pero no sustituye la reconstrucción de las trayectorias de ERK y sus estímulos desde las imágenes.

## Compatibilidad con FD7 y FD8

La familia binaria utiliza una secuencia de 19 slots y su complemento; no es un ensayo de los brazos FD7/FD8. La otra familia tiene registros largos con intervalos variables y merecía un examen específico.

Se inspeccionó la primera trayectoria exportada de cada uno de los 15 CSV de intervalos: 1.620 minutos continuos por archivo y 830 eventos de pulso en total. Dos implementaciones independientes coinciden: **cero ciclos completos FD7/FD8 en esas trayectorias, considerando todas las rotaciones y anchos enteros de slot de 1 a 30 minutos**, sin omitir pulsos intermedios. El resultado se limita a ese soporte y esa rejilla; no es una prueba universal sobre cualquier archivo, ancho o diseño posible.

Además, un flash de 100 ms y una iluminación sostenida son entradas físicas diferentes. Un alfabeto de bloques «flash más relajación» podría motivar una extensión matemática, pero exige demostrar de nuevo el transporte del nulo y del observable correspondiente. La similitud de una secuencia binaria no otorga esa demostración.

Por tanto, la búsqueda abre una evaluación celular sustantiva en otro dominio, pero todavía no acredita validación directa de la intervención FD7/FD8.

## Recursos y próximo paso

| Material | Tamaño comprobado | Uso previsto |
|---|---:|---|
| ZIP ERK completo | 723.609.060 bytes | Descarga y checksum completos en cómputo remoto. |
| 30 CSV de cohorte primaria | 173.465.795 bytes comprimidos; 477.974.660 descomprimidos | Procesamiento secuencial por archivo; el mayor CSV primario ocupa 21.745.088 bytes. |
| Todos los CSV ERK | 1.966.937.883 bytes descomprimidos | Familias auxiliares; no cargarlos juntos en memoria. |
| XLSX de relojes | 125.909 bytes | Análisis auxiliar independiente. |
| Imágenes MDCK | 9.242.972.535 bytes | Descarga remota y procesamiento de imágenes tras resolver acceso. |

La auditoría de dos CSV y cabeceras transfirió aproximadamente 9,53 MB; la de inputs de intervalos, 8,48 MB. No se descargaron localmente los archivos de 724 MB, 4,94 GB o 9,24 GB. No hay una estimación medida de horas de E9 ni una prueba de pico de RAM de su implementación futura. La evaluación propuesta utiliza CPU y procesamiento secuencial; un piloto deberá medir memoria y tiempo antes de dimensionar la campaña completa.

**La siguiente acción decisiva es implementar E9 en ERK con este manifiesto de días, verificar el alineamiento y congelar el protocolo numérico antes de puntuar los dos días reservados.** Deben ajustarse modelos propios de ERK; trasladar directamente coeficientes o cortes bacterianos no estaría justificado. Se reutilizan la disciplina temporal y la estructura de evaluación local, sometiéndolas a contraste en el nuevo dominio.

El protocolo de fuentes y cohortes, el inventario, los recibos de acceso y la auditoría de compatibilidad acompañan este cierre. Los manuscritos, la declaración de resultados previos y la validación matemática de FD7/FD8 conservan su contenido hasta que existan resultados nuevos.
