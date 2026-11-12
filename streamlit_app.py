"""Bilingual interface for the certified FD7 witness."""

import json

import altair as alt
import streamlit as st

from tools.fd7_demo import evaluate


SITE = 'https://facundofirmenich.github.io/ChronoWitness/'
REPO = 'https://github.com/FacundoFirmenich/ChronoWitness'

st.set_page_config(page_title='ChronoWitness · FD7', layout='centered')
requested = st.query_params.get('lang', 'en')
language = st.radio('Language / Idioma', ('English', 'Castellano'), index=int(requested == 'es'),
                    horizontal=True, key='language')
spanish = language == 'Castellano'


def tr(en, es):
    return es if spanish else en


st.title(tr('FD7 · One cycle, two trajectories', 'FD7 · Un ciclo, dos trayectorias'))
st.write(tr(
    'Follow two binary input schedules through the same four-state reader. Compare visits to state 3, then test what changes when you flip one symbol.',
    'Seguí dos secuencias binarias por el mismo lector de cuatro estados. Compará las visitas al estado 3 y probá qué cambia al invertir un símbolo.',
))
mode = st.radio(tr('Input schedules', 'Secuencias de entrada'),
                (tr('Certified pair', 'Par certificado'), tr('Flip one symbol', 'Invertir un símbolo')),
                horizontal=True, key='mode')
edited = mode == tr('Flip one symbol', 'Invertir un símbolo')
if edited:
    left, right = st.columns(2)
    arm = left.selectbox(tr('Arm to edit', 'Brazo que se edita'), ('A', 'B'), key='arm')
    phase = right.slider(tr('Phase to edit (starts at 0)', 'Fase que se edita (empieza en 0)'), 0, 23, 1, key='edit_phase')
    result = evaluate(arm, phase)
else:
    result = evaluate()

columns = st.columns(3)
for column, name in zip(columns, ('A', 'B')):
    column.metric(tr(f'Arm {name} · visits', f'Brazo {name} · visitas'), f"{result['arms'][name]['visits']}/{result['period']}")
columns[2].metric(tr('A − B · state-3 occupation', 'A − B · ocupación del estado 3'), result['contrast'])

data = [{'arm': name, 'phase': phase, 'state': state}
        for name, record in result['arms'].items() for phase, state in enumerate(record['path'])]
chart = alt.Chart(alt.Data(values=data)).mark_line(interpolate='step-after', point=True).encode(
    x=alt.X('phase:Q', title=tr('Phase', 'Fase'), scale=alt.Scale(domain=[0, 24]), axis=alt.Axis(tickMinStep=1)),
    y=alt.Y('state:Q', title=tr('Reader state', 'Estado del lector'), scale=alt.Scale(domain=[0, 3]), axis=alt.Axis(tickMinStep=1)),
    color=alt.Color('arm:N', title=tr('Arm', 'Brazo'), scale=alt.Scale(domain=['A', 'B'], range=['#2168bd', '#8a4fa9'])),
    strokeDash=alt.StrokeDash('arm:N', legend=None),
    tooltip=[alt.Tooltip('arm:N', title=tr('Arm', 'Brazo')), alt.Tooltip('phase:Q', title=tr('Phase', 'Fase')),
             alt.Tooltip('state:Q', title=tr('State', 'Estado'))],
).properties(height=240)
st.altair_chart(chart, width='stretch')

focus = st.slider(tr('Inspect a transition', 'Inspeccionar una transición'), 0, 23, 1, key='focus')
for name, record in result['arms'].items():
    st.write(f"**{name}** · {tr('input', 'entrada')} `{record['word'][focus]}` · "
             f"{tr('state', 'estado')} `{record['path'][focus]} → {record['path'][focus + 1]}`")

if edited:
    st.caption(tr('Edited scenario. Occupation is measured over one window starting at state 0. The FD7 pair certificate applies to the original pair.',
                  'Escenario editado. La ocupación se mide en una ventana que empieza en el estado 0. El certificado FD7 corresponde al par original.'))
else:
    st.caption(tr('Certified pair. Both paths return to state 0. The terminal state at phase 24 is displayed and excluded from the occupation counts.',
                  'Par certificado. Ambas trayectorias vuelven al estado 0. El estado terminal de la fase 24 se muestra y queda fuera del recuento de ocupación.'))

st.download_button(tr('Download result as JSON', 'Descargar resultado en JSON'),
                   json.dumps(result, indent=2, ensure_ascii=False) + '\n',
                   file_name='chronowitness-fd7.json', mime='application/json')
lang = 'es' if spanish else 'en'
st.markdown(f"[{tr('Interactive 3D render', 'Render 3D interactivo')}]({SITE}render-fd7.html?lang={lang}) · "
            f"[{tr('Epistemic graph', 'Grafo epistémico')}]({SITE}epistemic-graph.html?lang={lang}) · "
            f"[SuperGraph]({SITE}supergraph.html?lang={lang}) · "
            f"[{tr('Source and certificates', 'Fuentes y certificados')}]({REPO})")
