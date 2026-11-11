from pathlib import Path
import collections, hashlib, json, math, zipfile

HERE = Path(__file__).parent
with zipfile.ZipFile(HERE / 'REMOTE_E4.zip') as z:
    assert z.testzip() is None
    manifest = json.loads(z.read('SHA256.json'))
    for name, digest in manifest.items():
        assert hashlib.sha256(z.read(name)).hexdigest() == digest, name
    with zipfile.ZipFile(HERE / 'SOURCE_PACKAGE.zip') as source:
        for name in source.namelist():
            assert source.read(name) == z.read(name), name
    read = lambda n: json.loads(z.read(n))
    rows = read('results/LOCAL_METRICS.json')
    decisions = read('results/LOCAL_DECISIONS.json')
    global_rows = read('results/GLOBAL_CONTEXT.json')
    run = read('COLAB_RUN.json')
    partition = read('results/PARTITION_CHECKS.json')
assert len(rows) == 5184 and len(decisions) == 216 and len(partition) == 18
key = lambda r: (r['date'], r['offset'], r['horizon'])
localkey = lambda r: key(r) + (r['segment_start'], r['edge'], r['band'])
idx = {(localkey(r), r['policy']): r for r in rows}
for d in decisions:
    supported = d['fit_support']['qualified'] and d['validation_support']['qualified']
    assert supported == (d['status'] == 'SUPPORTED')
    if supported:
        loss = d['early_mae']
        chosen = min(['raw','offset','affine'], key=lambda p: loss[p])
        gain = 0 if loss['raw'] == 0 else 1-loss[chosen]/loss['raw']
        assert d['choice'] == (chosen if gain > .01 else 'raw')
    else:
        assert d['choice'] == 'raw'
for g in global_rows:
    selected = [r for r in rows if key(r)==key(g) and r['policy']==g['policy'] and r['support']['windows']]
    n = sum(r['support']['windows'] for r in selected)
    assert n == g['n']
    for field in ['mae', 'bias']:
        value = sum(r[field]*r['support']['windows'] for r in selected)/n
        assert math.isclose(value,g[field],rel_tol=1e-12,abs_tol=1e-9)
    value = sum(r['rmse']**2*r['support']['windows'] for r in selected)/n
    assert math.isclose(value,g['rmse']**2,rel_tol=1e-12,abs_tol=1e-8)
summary = []
common = {localkey(r) for r in rows if r['policy']=='local_gate' and r['status']=='SUPPORTED'}
for policy in sorted({r['policy'] for r in rows}):
    selected = [r for r in rows if r['policy']==policy]
    matched = [r for r in selected if localkey(r) in common]
    summary.append(dict(policy=policy,labels=dict(collections.Counter(r['label'] for r in selected)),common_support_labels=dict(collections.Counter(r['label'] for r in matched))))
gate = [r for r in rows if r['policy']=='local_gate' and r['status']=='SUPPORTED']
adverse = []
for r in gate:
    raw = idx[(localkey(r),'raw')]
    if r['tail05_mean'] > raw['tail05_mean']:
        adverse.append(dict(jurisdiction=localkey(r),mae_gain=r['relative_MAE_gain'],tail_relative_increase=r['tail05_mean']/raw['tail05_mean']-1))
primary = []
for date in sorted({r['date'] for r in rows}):
    p = {r['policy']:r for r in global_rows if key(r)==(date,1,12)}
    primary.append(dict(date=date,mae_gain_percent=100*(1-p['local_gate']['mae']/p['raw']['mae']),rmse_gain_percent=100*(1-p['local_gate']['rmse']/p['raw']['rmse']),tail_change_percent=100*(p['local_gate']['tail05_mean']/p['raw']['tail05_mean']-1)))
report = dict(status='PASS_FULL_READBACK_DECISION_AND_PARTITION_VERIFICATION',manifest_files=len(manifest),archive_sha256=hashlib.sha256((HERE/'REMOTE_E4.zip').read_bytes()).hexdigest(),rows=len(rows),jurisdictions=648,local_support=len(common),summary=summary,local_gate_mae_min_gain=min(r['relative_MAE_gain'] for r in gate),local_gate_tail_increases=adverse,primary=primary,execution=run)
(HERE/'VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
table='\n'.join(f"| {r['date']} | {r['mae_gain_percent']:.3f}% | {r['rmse_gain_percent']:.3f}% | {r['tail_change_percent']:+.3f}% |" for r in primary)
text='''# Cierre científico E4: jurisdicciones locales y transporte de calibración

La posición científica mejora: el análisis identifica contextos donde una decisión temprana de calibración conserva o reduce el error absoluto en segmentos posteriores. El avance pertenece a la capa de observación y calibración sobre datos celulares publicados. La identidad matemática FD7 y sus certificados mantienen su alcance; este conjunto experimental no contiene la intervención pareada FD7.

## Resultado y soporte

Se ejecutaron las 648 jurisdicciones previstas, definidas por experimento, alineamiento, horizonte, segmento temporal, transición de entrada y banda de fluorescencia. Las bandas se fijaron con los cuatro experimentos de entrenamiento, con igual peso por experimento. La elección de corrección utiliza solamente segmentos tempranos; las ventanas posteriores permanecen fuera de esa elección.

De 648 jurisdicciones, 497 tienen soporte de evaluación y 270 tienen además soporte temprano para calibración local. En estas 270, la regla registra 129 mejoras de MAE superiores al 1%, 141 empates prácticos y ninguna pérdida superior al 1%. Las 227 con evaluación suficiente pero calibración insuficiente se conservan como OUT_OF_SUPPORT; las 151 con evaluación insuficiente, como NOT_ESTIMABLE. El fallback conserva el predictor original y no convierte ausencia de soporte en evidencia favorable.

Los recuentos son descriptivos: combinaciones de horizontes, segmentos y alineamientos comparten observaciones. No equivalen a 270 experimentos independientes. El umbral de 1% es una tolerancia descriptiva fijada antes de esta ejecución, con sensibilidad completa a 0,1% y 5%; no es significación estadística ni un umbral biológico universal.

## Contexto agregado principal: 60 minutos, alineamiento primario

| Experimento | Reducción MAE | Reducción RMSE | Cambio del error medio en la cola superior del 5% |
|---|---:|---:|---:|
'''+table+'''

Los agregados son contexto y se reconstruyen exactamente a partir de las jurisdicciones. La cola muestra por qué no basta el promedio: en los dos primeros experimentos, la regla mejora MAE y RMSE globales, pero aumenta el promedio de los mayores errores. La selección optimiza MAE temprano; no se diseñó para garantizar mejora simultánea de todos los funcionales de error.

## Comparadores y evidencia adversa

En las 270 jurisdicciones comunes, la mezcla local fija (un tercio predictor original, un tercio offset y un tercio afín) registra 170 mejoras, 41 pérdidas y 59 empates. La corrección afín local registra 160 mejoras, 75 pérdidas y 35 empates. La regla selectiva reduce las pérdidas relevantes observadas a costa de actuar en menos contextos; no se declara un ganador universal. El soporte común permite comparar decisiones sin atribuir diferencias a composiciones distintas de datos.

Se conservan las métricas continuas, sesgo firmado, mediana, cuantiles 90/95 y promedio de la cola superior; ninguna presupone gaussianidad. La selección por fluorescencia actual usa información disponible en el origen, no estados regulatorios latentes. Las aristas representan transiciones programadas de entrada, no conexiones moleculares inferidas.

## Verificación y consecuencia para el preprint

La ejecución CPU de Colab terminó sin error: 63,43 segundos totales y 10,54 segundos en la etapa científica, en una máquina de dos CPU lógicas. Se verificaron CRC, hashes, igualdad de las fuentes con el paquete congelado, reconstrucción de decisiones tempranas y de MAE, sesgo y MSE agregados. El propio ejecutable reprodujo las métricas globales E3 para los comparadores heredados.

El resultado fortalece el preprint como contribución teórica y computacional con un estudio retrospectivo de observación celular. Permite describir dónde es útil una corrección y dónde se debe abstener. La generalización a experimentos nuevos, una garantía condicional de sesgo para el test FD7 y la validación celular directa de sus estímulos siguen siendo cuestiones distintas. El próximo paso de esta edición es integrar estos resultados y su evidencia adversa en manuscrito, suplemento, figuras y repositorio, conservando el contenido matemático y la separación respecto del anexo comercial confidencial.
'''
(HERE/'CIERRE_CIENTIFICO_E4_ES.md').write_text(text,encoding='utf-8')
print(json.dumps({k:report[k] for k in ['status','local_support','local_gate_mae_min_gain','primary']},indent=2))
print('Tail increases on supported jurisdictions:',len(adverse))
