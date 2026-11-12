# Reproducción de figuras

[English](FIGURE_REPRODUCTION.md)

Instalá `requirements-figures.txt`. Para la trayectoria exacta del testigo FD7, ejecutá `python tools/render_witness_3d.py --formats svg pdf png --output figures`. Obtendrás las versiones en castellano e inglés a partir de las transiciones del testigo de cuatro estados y los perfiles certificados.

Para las vistas de conjunto públicas, ejecutá `python tools/render_figures.py`. El script lee el certificado FD7 y los resúmenes distribuidos de E11. Genera la estructura de las entradas, las colas locales por adquisición y el resumen visual en inglés en PDF, SVG y PNG de 400 dpi. `PROVENANCE.json` registra los hashes de entrada.

Para las 24 figuras distintas del manuscrito y suplemento en inglés, extraé `research/FIGURE_SOURCES.zip` en otra carpeta. Instalá `requirements-figures.txt` y ejecutá `python reproduce_figures.py` desde la carpeta extraída. `INPUT_MANIFEST.json` identifica el código y las entradas medidas o certificadas. `COMMANDS.json` fija el orden de ejecución. Esta ruta reproduce las figuras desde entradas congeladas. Las ejecuciones científicas anteriores tienen sus propios procedimientos.

La aritmética matemática se mantiene exacta hasta la conversión para el trazado. Las figuras empíricas conservan los identificadores de adquisición, el soporte y los resultados adversos. Los cuantiles de un conjunto mayor se recalculan a partir de los datos de ese conjunto. La entrada de E8 para el trazado es un miembro extraído del archivo de campaña.

La paleta usa azul, índigo, violeta, rosa y fondos claros. Etiquetas, posiciones y estilos de línea complementan el color. Para publicación usá PDF o SVG vectorial. Los archivos PNG sirven para revisión.
