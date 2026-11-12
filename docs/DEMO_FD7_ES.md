# Caso guía · FD7, un ciclo y dos trayectorias

[English](FD7_DEMO.md) · [Guía para la comunidad y la investigación](COMUNIDAD_INVESTIGACION_ES.md)

Dos secuencias de 24 símbolos coinciden en todos los conteos de palabras cíclicas hasta orden siete. Hacé pasar ambas por el mismo lector sincronizante de cuatro estados y comprobá si ocupan el estado 3 durante la misma fracción del ciclo. El caso enlaza el certificado exacto, una trayectoria 3D y un argumento que se puede inspeccionar.

1. Abrí el [render FD7](https://facundofirmenich.github.io/ChronoWitness/render-fd7.html?lang=es). Rotá la vista y elegí la fase 1. Los ejes muestran fase, brazo y estado del lector. El estado al final de la trayectoria cierra el ciclo y queda fuera del recuento de ocupación.
2. En Streamlit, dejá seleccionado **Par certificado**. El brazo A visita el estado 3 tres veces y el B lo visita dos veces. La diferencia exacta de ocupación es **1/24**. Seleccioná una fase para ver el símbolo de entrada y las dos transiciones.
3. Elegí **Invertir un símbolo**, brazo **A**, fase **1**. La herramienta cambia `0` por `1`. Con el mismo lector y estado inicial, ambos recuentos en la ventana quedan en **2/24** y el contraste vale **0**. La exportación registra el símbolo modificado y el alcance del cálculo.
4. Descargá el JSON y abrí el [grafo epistémico](https://facundofirmenich.github.io/ChronoWitness/epistemic-graph.html?lang=es). Seguí la estructura de FD7 y el testigo de cuatro estados hasta sus certificados. Abrí el [SuperGraph](https://facundofirmenich.github.io/ChronoWitness/supergraph.html?lang=es) para ver cómo se conectan supuestos, observación, inferencia y adquisición. La rama de observaciones celulares muestra qué mediciones requeriría una comparación física.

## Abrir el editor

Desde una copia del repositorio que contenga `streamlit_app.py`, ejecutá estos comandos con Python 3.12.

```sh
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

Para usar Docker, ejecutá los siguientes comandos desde la misma copia y abrí `http://localhost:8501`.

```sh
docker build -f Dockerfile.streamlit -t chronowitness-demo .
docker run --rm -p 127.0.0.1:8501:8501 chronowitness-demo
```

Para el visor sin conexión y el menú de cómputo, extraé la [release nativa](https://github.com/FacundoFirmenich/ChronoWitness/releases) de tu plataforma y abrí el ejecutable. Elegí `es atlas` para el grafo y el testigo 3D, o `es 1` para el bloque exacto de lectores. El editor Streamlit se distribuye como código fuente y como receta de contenedor.

El JSON incluye las secuencias, trayectorias, tabla de transición, contraste exacto y rutas de las fuentes. Para comparar ediciones, usá el mismo estado inicial, ventana y lector. La identidad de dos estados corresponde a las secuencias certificadas y al observable periódico especificado. El escenario editado se calcula en ventana finita. Los registros celulares públicos tienen su propio alcance empírico.

## Ejecutar el mismo modelo por terminal

El editor del navegador y este punto de entrada al laboratorio temporal usan el mismo evaluador. Guardá el JSON de salida para documentar un escenario o reutilizarlo.

```sh
python -m tools.fd7_demo
python -m tools.fd7_demo --arm A --phase 1
```

El Read Observability Lab v0.4 compartido tiene su propio contrato de entradas moleculares. El caso ChronoWitness usa símbolos temporales y estados de lector. Este repositorio lo ofrece mediante el editor del navegador y el comando anterior. [Motor del laboratorio compartido](https://github.com/FacundoFirmenich/crispr-observability/tree/lab-engine-multientrada-v04/engine)
