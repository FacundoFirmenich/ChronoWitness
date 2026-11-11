from pathlib import Path,PurePosixPath
import hashlib,json,math,zipfile,collections
HERE=Path(__file__).parent
with zipfile.ZipFile(HERE/'REMOTE_E3.zip') as z:
    assert z.testzip() is None
    files={n:z.read(n) for n in z.namelist()}
manifest=json.loads(files['SHA256.json'])
for n,digest in manifest.items():
    assert not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts
    assert hashlib.sha256(files[n]).hexdigest()==digest,n
freeze=json.loads((HERE/'FREEZE_RECEIPT.json').read_text())
for n,digest in freeze['sources'].items():assert hashlib.sha256(files[n]).hexdigest()==digest
run=json.loads(files['results/RUN.json']);hardware=json.loads(files['COLAB_RUN.json'])
assert run['status']=='COMPLETE_RETROSPECTIVE_E3_A' and hardware['status']=='COMPLETE_E3_COLAB'
rows=json.loads(files['results/METRICS.json']);dec=json.loads(files['results/DECISIONS.json'])
windows=json.loads(files['results/WINDOWS.json']);fits=json.loads(files['results/BASE_FITS.json'])
select=json.loads(files['results/THRESHOLD_SELECTION.json'])
assert len(rows)==630 and len(dec)==len(windows)==126
for r in windows:
    assert r['latest_fit_target']<r['earliest_validation_feature']
    assert r['latest_refit_target']<r['earliest_late_feature']
for r in fits:
    if r['role']=='training_oof':assert r['date'] not in r['fitting_dates'] and len(r['fitting_dates'])==3
methods=['raw','offset','nonnegative_affine']
key=lambda r:(r['date'],r['offset'],r['horizon'],r['model'])
index={(key(r),r['method']):r for r in rows}
theta=select['chosen']
for d in dec:
    choice=min(methods,key=lambda m:d['early_validation_mse'][m])
    gain=1-d['early_validation_mse'][choice]/d['early_validation_mse']['raw']
    choice=choice if theta!='always_raw' and gain>theta else 'raw'
    assert choice==d['choice']
    chosen=index[(key(d),choice)];gated=index[(key(d),'gated_refit')]
    for f in ['rmse','mae','bias','n','predicted_negative','predicted_above_4095']:assert chosen[f]==gated[f]
def riskkey(r):return r['mean_ratio'],r['worst_ratio'],-(float('inf') if r['threshold']=='always_raw' else r['threshold'])
assert min(select['training_only_risks'],key=riskkey)['threshold']==theta
summary=[]
for method in ['offset','nonnegative_affine','gated_refit','gated_frozen']:
    selected=[r for r in rows if r['role']=='seen_test' and r['method']==method]
    gains=[100*(1-r['rmse']/index[(key(r),'raw')]['rmse']) for r in selected]
    summary.append(dict(method=method,n=len(gains),better=sum(x>1e-10 for x in gains),worse=sum(x<-1e-10 for x in gains),unchanged=sum(abs(x)<=1e-10 for x in gains),worst_gain_percent=min(gains),best_gain_percent=max(gains),mean_MSE_ratio=sum((r['rmse']/index[(key(r),'raw')]['rmse'])**2 for r in selected)/len(selected)))
primary=[r for r in rows if r['role']=='seen_test' and r['model']=='history_input' and r['offset']==1 and r['horizon']==12]
receipt=dict(status='PASS_COMPLETE_READBACK_AND_DECISION_VERIFICATION',archive_sha256=hashlib.sha256((HERE/'REMOTE_E3.zip').read_bytes()).hexdigest(),files_checked=len(manifest),protocol_sha256=freeze['sources']['PROTOCOL.json'],summary=summary,primary=primary,execution=hardware)
(HERE/'VERIFICATION.json').write_text(json.dumps(receipt,indent=2)+'\n')
table=[]
for date in ['2022-04-15','2022-04-21','2022-04-23']:
    r={x['method']:x for x in primary if x['date']==date}
    choice=next(x['choice'] for x in dec if x['date']==date and x['model']=='history_input' and x['horizon']==12 and x['offset']==1)
    table.append(f"| {date} | {r['raw']['rmse']:.3f} | {r['gated_refit']['rmse']:.3f} | {choice} | {100*(1-r['gated_refit']['rmse']/r['raw']['rmse']):.3f}% |")
text='''# E3-A: decisión de calibración y transporte temporal

La posición científica mejora de forma acotada: E3 identifica una regla temprana que selecciona una corrección beneficiosa en un experimento principal y conserva los otros dos. La sensibilidad completa revela deterioros residuales. Es una candidata retrospectiva; no una garantía general de transporte ni validación celular directa de FD7.

Se ejecutó el código congelado en el commit 15f90663027089d4205011f761e5d6151913aed4, con tres predictores históricos, dos alineamientos, tres horizontes y siete experimentos. Se generaron 630 filas de métricas y 126 decisiones. La selección de regularización del predictor excluyó íntegramente cada experimento de entrenamiento evaluado, con validación interna entre los tres restantes. Los predictores para los tres experimentos de evaluación conservaron el ajuste original con cuatro experimentos. Se reprodujeron 162 filas estáticas de E2.

La decisión compara métodos ajustados hasta target72 y evaluados en un segmento temprano separado, antes de target120. La corrección elegida se reajusta hasta120; el tramo de evaluación tiene origen desde132 y sus primeras características empiezan en121. La regla no observa los resultados de ese tramo para elegir el método.

## Resultado principal

| Experimento | RMSE original | RMSE de la regla | Decisión | Reducción RMSE |
|---|---:|---:|---|---:|
'''+ '\n'.join(table)+'''

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
'''
(HERE/'CIERRE_CIENTIFICO_E3_ES.md').write_text(text,encoding='utf-8')
print(json.dumps(dict(status=receipt['status'],summary=summary),indent=2))
