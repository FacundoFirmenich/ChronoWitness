# E3-A: decisión de calibración y transporte temporal

La posición científica mejora de forma acotada: E3 identifica una regla temprana que selecciona una corrección beneficiosa en un experimento principal y conserva los otros dos. La sensibilidad completa revela deterioros residuales. Es una candidata retrospectiva; no una garantía general de transporte ni validación celular directa de FD7.

Se ejecutó el código congelado en el commit 15f90663027089d4205011f761e5d6151913aed4, con tres predictores históricos, dos alineamientos, tres horizontes y siete experimentos. Se generaron 630 filas de métricas y 126 decisiones. La selección de regularización del predictor excluyó íntegramente cada experimento de entrenamiento evaluado, con validación interna entre los tres restantes. Los predictores para los tres experimentos de evaluación conservaron el ajuste original con cuatro experimentos. Se reprodujeron 162 filas estáticas de E2.

La decisión compara métodos ajustados hasta target72 y evaluados en un segmento temprano separado, antes de target120. La corrección elegida se reajusta hasta120; el tramo de evaluación tiene origen desde132 y sus primeras características empiezan en121. La regla no observa los resultados de ese tramo para elegir el método.

## Resultado principal

| Experimento | RMSE original | RMSE de la regla | Decisión | Reducción RMSE |
|---|---:|---:|---|---:|
| 2022-04-15 | 447.430 | 438.749 | nonnegative_affine | 1.940% |
| 2022-04-21 | 413.252 | 413.252 | raw | 0.000% |
| 2022-04-23 | 406.829 | 406.829 | raw | 0.000% |

El umbral seleccionado es una reducción temprana de MSE estrictamente superior a 5%. No es el criterio descriptivo de RMSE de E1 ni un nivel de significación. En los cuatro experimentos de entrenamiento, todos los umbrales de 0 a 0,05 produjeron las mismas decisiones y riesgos; el desempate predefinido eligió el mayor. Por tanto, 0,05 no está identificado como un umbral biológico único. La media de ratios MSE en esos cuatro experimentos fue 0,9964135: una mejora pequeña, basada en un experimento corregido y tres conservados.

## Sensibilidad completa: los tres experimentos conocidos

| Política | Mejora / empeora / conserva, de 54 | Peor aumento de RMSE |
|---|---|---:|
| Desplazamiento siempre, reajustado hasta120 | 41 / 13 / 0 | 0,245% |
| Afín siempre, reajustada hasta120 | 31 / 23 / 0 | 1,247% |
| Regla con reajuste hasta120 | 13 / 3 / 38 | 0,609% |
| Misma regla conservando coeficientes hasta72 | 12 / 4 / 38 | 3,225% |

La regla reduce la frecuencia de correcciones perjudiciales en este conjunto, pero no elimina el daño ni domina al desplazamiento en todos los criterios. En particular, el desplazamiento siempre tiene un peor caso menor en esta comparación. Conservar los coeficientes muy tempranos puede ser peor que reajustarlos; el segmento usado para estimar parámetros importa, además de decidir si corregir.

Estas 54 combinaciones comparten datos y no son réplicas independientes. El diseño utiliza solamente tres predictores históricos y el corte120 para sus comparadores estáticos; sus recuentos no son directamente intercambiables con las 270 comparaciones por método de E2, que incluían cinco predictores y tres cortes.

El objetivo optimizado es MSE predictivo. Para el objetivo mecanístico FD7 importa además el sesgo condicional: en el experimento del 15 de abril, la afín obtiene menor RMSE que el desplazamiento, pero deja un sesgo absoluto mayor (39,28 frente a 11,56). E3 no convierte una mejora de predicción en una cota física de error de observación. La reducción de RMSE y la cualificación del test FD7 son tareas relacionadas pero distintas.

## Validación y recursos

Se verificó lectura completa del ZIP, CRC, hashes de todos los archivos contra el manifiesto remoto, coincidencia de fuentes con el protocolo congelado, exclusión de experimentos, separación temporal y reconstrucción independiente de las decisiones a partir de las pérdidas tempranas. El código comprobó coincidencia numérica de los predictores finales con E1 y de las 162 filas estáticas con E2. No se retocaron umbrales tras ver resultados.

Colab CPU completó el proceso en 87,01 segundos: preparación 3,13 s, descarga y verificación 63,04 s y etapa E3 20,65 s. El análisis interno midió 18,58 s. La máquina tenía dos CPU lógicas y 13.286.932 KiB de RAM; el mayor RSS de procesos hijos fue 573.000 KiB. El tiempo total de interacción, verificación y entrega es mayor. No se ha medido un cargo facturado exclusivo de esta sesión.

## Decisión científica

Cerrar esta E3-A conservando todos los resultados. Es un avance hacia selección prudente de calibración, no razón para buscar retrospectivamente otra regla hasta obtener superioridad universal. El siguiente paso con mayor valor es cualificar en una plataforma real la adquisición, la calibración y la intervención FD7, con datos nuevos. Si se amplía el desarrollo retrospectivo, debe declararse como tal y justificarse por una hipótesis nueva concreta.

El paquete acompaña un expediente de laboratorio y una evaluación de vías de colaboración, acceso financiado y servicio. No se han enviado comunicaciones ni contratado experimentos. Los manuscritos permanecen privados y no se ha emitido una nueva release de paper.
