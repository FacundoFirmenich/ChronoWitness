# E9: cierre científico de la evaluación en ERK humano

La ejecución primaria E9 terminó en Colab y pasó la reconstrucción independiente de residuos, decisiones locales y métricas. El proyecto incorpora evidencia de otro dominio celular y otro laboratorio; esa evidencia delimita el transporte de la calibración.

El banco primario contiene 30 archivos separados por días completos: dos días de entrenamiento, uno de calibración y dos reservados. La evaluación combina 12 archivos reservados, tres horizontes (5, 10 y 20 minutos) y ambos alineamientos de entrada, dando 72 contextos correlacionados. No son 72 réplicas biológicas independientes.

| Criterio descriptivo | Sin protección | Protección local |
|---|---:|---:|
| Contextos con RMSE >1% peor que el modelo base | 64/72 | 24/72 |
| Contextos con percentil 95 del error absoluto >1% peor que el base | 57/72 | 19/72 |
| Intersecciones locales con percentil 95 >1% peor que el base | 242/360 | 108/360 |

La protección reduce los daños de la corrección temprana, pero no demuestra beneficio uniforme frente al modelo base. Mejora estrictamente el RMSE base en 4 de 72 contextos. La peor intersección protegida conserva una razón de percentiles 95 de 1,1138627424: empeoramiento del 11,39%.

La reconstrucción anidada identifica 67 daños locales de q95 superiores al 1% dentro de 38 contextos cuyo q95 agregado no supera el 1% de empeoramiento. Estas jurisdicciones no quedarían señaladas por aplicar ese mismo umbral solamente al agregado. Es una comprobación descriptiva de los residuos ya obtenidos, no una muestra independiente ni un nuevo ensayo.

Las 360 intersecciones cruzan tiempo desde el último pulso y banda de señal actual, conservando día, protocolo, campo, horizonte y alineamiento. Cada una tiene al menos 20 ventanas para el resumen descriptivo; ese umbral no transforma ventanas solapadas en réplicas independientes. Los nodos por célula y otros nodos de menor soporte también se conservaron, con su estado, en el paquete.

El predictor con historia de entrada supera al predictor sin entrada en 21 de los 72 contextos. Este resultado se refiere a esta familia lineal regularizada, este observable y estas ventanas. No demuestra que la vía ERK carezca de memoria ni que los estímulos no tengan efecto.

El mecanismo metodológico es claro: la corrección aditiva aprendida temprano puede dejar de ser adecuada en segmentos posteriores. La protección seleccionada con un segmento intermedio atenúa ese riesgo, pero algunos daños sobreviven en la evaluación tardía. No se atribuye todavía su causa a un mecanismo biológico concreto. Distinguir deriva del observable, inadecuación del predictor y cambio de respuesta requiere análisis posteriores con nueva separación de desarrollo y evaluación.

El protocolo fue fijado antes de calcular errores. Se mantuvieron todas las trayectorias exportadas estructuralmente utilizables, incluidos los indicadores de exclusión por respuesta débil del estudio original. Se utilizó el cociente entre señal nuclear e intensidad contemporánea de imagen; no se utilizó una normalización de toda la trayectoria ni imágenes futuras como predictores. El orden subminuto entre flash e imagen no está resuelto en el export: ambos alineamientos se retuvieron, sin seleccionar el más favorable.

Se reemplazaron búsquedas repetidas en pandas por indexación vectorizada. Antes de reanudar se comprobó igualdad exacta de matrices, objetivos y metadatos sobre 20.000 ventanas reales de entrenamiento. La primera ejecución lenta se interrumpió y su historial se preservó. La verificación posterior de los 72 archivos de residuos comprueba decisiones, soporte y reconstrucción de métricas; no constituye un segundo ajuste independiente de todos los modelos.

El cálculo vectorizado tardó 351,55 segundos y alcanzó 1.291,20 MiB (1,26 GiB) de RSS. La auditoría previa del archivo y los 30 CSV tardó 255,23 segundos, incluyendo descarga; alcanzó 212,30 MiB. La sesión dispone de 2 CPU y aproximadamente 13 GB de RAM. Estos tiempos excluyen montaje, transferencia, desarrollo y verificaciones posteriores.

El ZIP fuente completo tiene 723.609.060 bytes, MD5 4aef737b263424dbdb06e15f827ccad2 y SHA-256 ca2bee5a5ac5f3b4d51d794faa9dcd75410a2512fa29f26155f3aaba15fd2317. El paquete de resultados y fuentes contiene 165 entradas y 40.144.199 bytes, SHA-256 f0c3103e6b2e214b69d8786029985be184352dfe1098fd04d9addbd6044d1bb8. Se verificó íntegramente tras recuperarlo de Colab y tras releerlo desde Drive. La custodia del archivo fuente se documenta separadamente por partes.

Para el preprint, E9 refuerza la evidencia empírica de transporte limitado y la necesidad de conservar los daños locales. No es validación celular directa de FD7/FD8: los registros siguen usando otro protocolo físico de estímulo. Los resultados de E6/E8 y los certificados matemáticos no cambian.

La siguiente decisión científica es localizar las jurisdicciones adversas por día, reloj, fase y nivel de señal, y determinar si conviene revisar el predictor o la política de calibración. Esa revisión será desarrollo sobre E9 y necesitará otra evaluación reservada para obtener nueva autoridad confirmatoria. No se reetiquetarán estos días ya evaluados como un test intacto.

Fuentes: Nałęcz-Jawecki et al. (2023), https://doi.org/10.1371/journal.pcbi.1011155; datos CC-BY-4.0, https://doi.org/10.5281/zenodo.7808385. Código de auditoría y evaluación original de ChronoWitness: MIT.
