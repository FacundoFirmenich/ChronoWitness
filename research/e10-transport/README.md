# E10 · Transporte temporal y riesgo local

E10 evalúa los modelos y políticas congelados de E9 en 36 archivos de otras dos adquisiciones, con relojes de estímulo de 5, 7, 20 y 30 minutos. Conserva 216 combinaciones de archivo, horizonte y alineamiento. La auditoría posterior reconstruye métricas desde residuos, decisiones de protección y descomposición exacta del cambio de error cuadrático.

Las unidades de transporte son dos días, no 216 réplicas. Los campos y los diferentes relojes de una fecha pueden compartir células o segmentos de adquisición. La evaluación es retrospectiva, del mismo laboratorio y con protocolos distintos de FD7/FD8.

## Reproducción en Colab CPU

Los archivos necesarios son `e9_core.py`, `MODEL_SELECTION.json`, `E9_NUMERICAL_PROTOCOL.json`, `E10_COHORT.json`, `E10_PROTOCOL.json`, `run_e10.py` y `analyze_e10.py`. Los coeficientes se distribuyen íntegros; no se ajusta un modelo nuevo. El protocolo conserva la suma SHA-256 de esos coeficientes y del protocolo heredado.

En el directorio que contiene estos archivos, crear el paquete de entrada:

```python
import zipfile
names = ['e9_core.py', 'MODEL_SELECTION.json', 'E9_NUMERICAL_PROTOCOL.json',
         'E10_COHORT.json', 'E10_PROTOCOL.json']
with zipfile.ZipFile('E10_INPUTS.zip', 'x', zipfile.ZIP_DEFLATED) as z:
    for name in names:
        z.write(name, name)
```

Copiar el ZIP y ambos scripts a `/content` de Colab. Ejecutar `python /content/run_e10.py`; cuando termine con estado COMPLETE, ejecutar `python /content/analyze_e10.py`. El segundo script requiere NumPy, pandas y matplotlib. `COMPLETE.json` registra versiones efectivamente utilizadas para la evaluación. La fuente original se descarga directamente de Zenodo y se acepta únicamente si su tamaño y SHA-256 coinciden con el protocolo. Los resultados se escriben en `/content/chronowitness-e10-20261111`.

Para repetir una ejecución se debe utilizar un runtime nuevo o un directorio propio aislado: no mezclar resultados de campañas distintas. La ejecución no monta Drive por sí sola. La custodia de esta campaña se realiza mediante el conector autenticado y se verifica leyendo los bytes remotos.

## Evidencia y conservación

`SCHEMA_AUDIT.json` identifica los archivos admitidos. `SUPPORT.json` conserva la distribución de ventanas por etapa y contexto. Los archivos de residuos contienen identidad de célula y tiempo, observable, objetivo, jurisdicción y error de cada método. Las decisiones por célula conservan soporte temprano, corrección, métricas de validación y aceptación. `VERIFICATION.json` comprueba su reconstrucción sin afirmar un segundo ajuste de modelos.

`CELL_RISK_DECOMPOSITION.csv.gz` separa dirección incompatible y exceso de corrección. `NESTED_NODES.csv` conserva padres, intersecciones de pulso/señal y segmentos temporales, incluidos LOW_SUPPORT. Las particiones se reconstruyen individualmente sin sumar observaciones repetidas entre particiones. `THRESHOLD_SENSITIVITY.json` registra umbrales descriptivos de 0%, 1% y 5%.

La nota `FRONTERA_MATEMATICA_ES.md` expone el criterio exacto de riesgo y las condiciones adicionales que exigiría una garantía prospectiva. `NEXT_RESERVE_METADATA.json` identifica registros de intervalos todavía no evaluados predictivamente, manteniendo una discrepancia de fechas sin resolver.

## Atribución y licencia

Código original de ChronoWitness: MIT, conforme a la licencia del repositorio. Datos de Nałęcz-Jawecki y colaboradores: [Zenodo, versión 1.1](https://doi.org/10.5281/zenodo.7808385), CC-BY-4.0. Referencia científica: [The MAPK/ERK channel capacity exceeds 6 bit/hour](https://doi.org/10.1371/journal.pcbi.1011155). La configuración original utilizada para atribuir fechas corresponde al commit `03f9a059d91caa2b72873e2317134ea7f7500203` de `pawelnalecz/pulsatile-information`.

Las licencias de las fuentes originales se conservan; MIT no sustituye CC-BY-4.0. Este directorio contiene código y documentación de investigación, no los manuscritos privados ni el anexo comercial.
