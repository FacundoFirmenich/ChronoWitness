# ChronoWitness para investigar y contribuir

[English](COMMUNITY_RESEARCH.md) · [Caso guía FD7](DEMO_FD7_ES.md) · [Reproducción](GUIA_ES.md)

ChronoWitness ofrece entradas de prueba exactas, modelos de lector e instrumento, cotas de observación y una forma de inspeccionar cómo se estableció cada resultado. Empezá por el [caso FD7](DEMO_FD7_ES.md) y seguí la ruta que corresponda a tu pregunta.

| Uso científico | Punto de entrada | Evidencia que conviene conservar |
|---|---|---|
| Diseño temporal y discriminación de modelos | [Testigos exactos y umbrales](RESULTADOS_CIENTIFICOS.md) | Par de entradas, clase de lector, observable y certificado |
| Adquisición finita e inferencia estadística | [Guía de observación y ensayo](GUIA_DEL_ENSAYO.md) | Supuestos de entrega, ventana, ley de las puntuaciones y umbral |
| Calibración local en registros celulares | [Observaciones celulares](OBSERVACIONES_CELULARES.md) | Adquisición, horizonte, alineación, soporte local y métrica de cola |

Estas tres líneas tienen implementaciones y resultados propios dentro del programa de investigación ChronoWitness. El [SuperGraph](https://facundofirmenich.github.io/ChronoWitness/supergraph.html?lang=es) las conecta por sus supuestos y fuentes. El proyecto CRISPR Observability desarrolla el motor compartido. ChronoWitness ejecutó casos temporales en su adaptador y ofrece aquí un editor FD7 para navegador.

El programa más amplio coordina tres proyectos. **ChronoWitness** aporta discriminación de modelos temporales, **ExposureBounds** aporta cotas de la entrada entregada y **Living Order** mantiene su interfaz científica y el historial de fuentes. La coordinación abarca supuestos y evidencia. El laboratorio molecular y el editor temporal FD7 tienen contratos de entrada distintos.

Para un estudio nuevo, fijá la entrada temporal y la cantidad a comparar antes de leer los resultados. Registrá qué se observa directamente, qué clase de modelos define el nulo y qué adquisición o contexto delimita el contraste. Exportá los parámetros y adjuntá la fuente o el certificado cuando informes un resultado. En datos celulares públicos, conservá la identidad de las adquisiciones compartidas y de las ventanas solapadas.

Usá la demo web o abrí el paquete nativo para Windows x64, Linux x64 o macOS Apple Silicon o Intel. El repositorio también incluye el editor Streamlit, su receta Docker y el contenedor de reproducción. El desarrollo local se hizo en un **portátil de 2016**, con Intel i5-6200U y 8–16 GB de RAM DDR3. Las campañas de mayor tamaño también usaron CPU alojada. Consultá las [releases nativas y los recibos de verificación](https://github.com/FacundoFirmenich/ChronoWitness/releases).

El código original tiene licencia MIT. Citá la [versión del software](../CITATION.cff) y el estudio o conjunto de datos correspondiente. Las contribuciones pueden ser científicas, editoriales o técnicas. Una primera contribución útil es un informe de reproducción en tu plataforma o un contraste que documente en qué condiciones cambia el resultado. [Guía de contribución](../CONTRIBUTING.md) · [Issues](https://github.com/FacundoFirmenich/ChronoWitness/issues) · [Discussions](https://github.com/FacundoFirmenich/ChronoWitness/discussions)
