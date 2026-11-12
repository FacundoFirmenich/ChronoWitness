# ChronoWitness en castellano

[English](GETTING_STARTED.md) · [Inicio](../README.es.md) · [Atlas web](https://facundofirmenich.github.io/ChronoWitness/?lang=es)

## Elegí una ejecución

Extraé todo el ZIP nativo para tu plataforma. Abrí el iniciador de esa carpeta o el ejecutable ChronoWitness. En una consulta elegís idioma y alcance.

| Opción | Operación | Qué leer |
|---|---|---|
| `es example` | Ejemplo exacto breve | Identidad de dos estados, transporte a un reportero y contraste certificado |
| `es 1` | Identidades de lectores | Enumeración determinista, verificaciones Markovianas y dinámica lector-instrumento |
| `es 2` | Observación e inferencia | Ventanas finitas, errores de entrega, conteos, censura y pruebas secuenciales |
| `es 3` | Diseño certificado y potencia | Certificado del generador, potencia exacta de cruce y controles |
| `es 4` | Ensayo y aplicación | Momentos por propagación, validación Monte Carlo y análisis de bloques |
| `es 1,3` | Selección de bloques | Sólo los programas de los bloques elegidos |
| `es todo` | Núcleo público completo | Regeneración y comparación con las referencias distribuidas |
| `es atlas` | Atlas local sin conexión | Fuentes, relaciones, premisas, recorridos y trayectoria 3D FD7 |

La edición nativa incluye el intérprete, las dependencias numéricas y los motores C++ compilados para la plataforma. La prueba completa compara los resultados con las referencias del repositorio. Los resultados nuevos se guardan en `source/research/results` y el recibo enumera los archivos escritos durante la ejecución. Los estudios de adquisición E4–E11 tienen sus propios protocolos, archivos y requisitos. No forman parte de esa única ejecución del núcleo.

Si preferís las fuentes, ejecutá `python workbench.py --lang es --blocks example` con Python 3.12. Los bloques de observación y diseño también pueden lanzarse con `--blocks 2,3`. Para el núcleo completo desde fuentes, iniciá Docker y ejecutá `python launch.py --mode full`. Esa ruta compila además el C++17 en el contenedor. La compilación directa desde fuentes necesita C++17 y `requirements-assay.txt`.

## Qué puede decir el contraste

Las dos palabras FD7 tienen 24 símbolos y coinciden en conteos cíclicos hasta longitud siete. El nulo uniforme en parámetros pertenece a la clase de lectores y al observable declarados. El umbral determinista de cuatro estados se refiere a la ley de perfiles balanceados por fase. En las clases positivas de Markov y cinética continua estudiadas, se construyen testigos separadores de tres estados.

La igualdad de medias se conserva a través de una cascada lineal estable común en régimen periódico. Para una ventana finita se necesitan correcciones de extremos o cotas de transitorio. La corrección exacta sólo es identificable desde los extremos medidos si el funcional requerido pertenece al espacio fila de esa observación. La entrega, la saturación y las colas de conteos se incorporan mediante cotas explícitas. La prueba secuencial usa bloques, un soporte acotado y un presupuesto condicional de sesgo. Su validez depende de que se cumplan esos contratos.

El testigo sincronizante 3D muestra fase, brazo y estado discreto. El estado 3 se visita 3 veces bajo A y 2 bajo B, en 24 pasos por ciclo. La diferencia exacta de ocupación es 1/24. El eje de los brazos es categórico. Las figuras se regeneran con `python tools/render_witness_3d.py --formats svg pdf png --output figures` desde una instalación con las dependencias de figuras.

## Leer el atlas y auditar el resultado

Elegí una pregunta guiada o un ámbito. La vista de argumento sigue las aristas que aportan evidencia o hipótesis. Una conjunción requiere todas sus premisas. Los recorridos ofrecen un orden de lectura separado. La vista de auditoría muestra los hashes de las fuentes. El mapa permite rotar, acercar, mover nodos o grupos y exportar la vista SVG y el registro JSON. Se puede explorar también con el selector de afirmaciones.

Los casos de E11 conservan la cronología, las condiciones de soporte y el deterioro de cola. En las intersecciones finas, la política causal reduce los deterioros de q95 superiores al 1 % de 266 a 81 frente a la política fija, sobre 2.268 intersecciones evaluables. Los recuentos corresponden a jurisdicciones que pueden compartir observaciones. El conjunto celular publicado no ejecutó los dos brazos emparejados FD7/FD8.

### Documentación técnica y fuentes

| Tema | Registro de referencia |
|---|---|
| Identidades, umbrales y condiciones | [Resultados científicos](SCIENTIFIC_RESULTS.md) |
| Ejemplo paso a paso | [Worked example](WORKED_EXAMPLE.md) |
| Observación y decisión | [Assay guide](ASSAY_GUIDE.md) |
| Momentos, simulación y potencia | [Trajectory assay](TRAJECTORY_ASSAY.md) |
| Resultados locales observados | [Estudios celulares](CELLULAR_OBSERVATIONS.md) y [cierre E11 en castellano](../research/e11-causal/CIERRE_SUSTANTIVO_E11_ES.md) |
| Bibliografía | [Contexto](LITERATURE_CONTEXT.md) y [referencias](REFERENCES.md) |
| Regeneración de figuras | [Figure reproduction](FIGURE_REPRODUCTION.md) |

Las citas, registros de datos, código y recibos conservan sus identificadores y su idioma de procedencia.
