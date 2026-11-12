'use strict';
const D=JSON.parse(document.getElementById('ledger').textContent);
const $=id=>document.getElementById(id);
const graph=$('graph');
const nodes=new Map(D.nodes.map(n=>[n.id,n]));
const groups={formal:['Formal results','Resultados formales','#8fbcff'],
  assay:['Measurement and inference','Medición e inferencia','#b8aaff'],
  observed:['Observed transport','Transporte observado','#91daf1'],
  limits:['Limits and adverse findings','Límites y resultados adversos','#efb0dc']};
const status={EXACT:['Exact','Exacto'],CERTIFIED:['Certified','Certificado'],CONDITIONAL:['Conditional','Condicional'],
  OBSERVED:['Observed','Observado'],NOT_MET:['Criterion not met','Criterio incumplido'],
  NOT_EVALUATED:['Not evaluated','No evaluado'],UNRESOLVED:['Unresolved','Sin resolver'],
  ARTIFACT:['Source file','Archivo fuente'],DECLARED:['Declared, unexecuted','Declarado, sin ejecutar'],
  SIMULATED:['Simulated','Simulado']};
const kinds={claim:['Results','Resultados'],gate:['AND gates','Compuertas Y'],acquisition:['Acquisitions','Adquisiciones'],
  source:['Source artifacts','Archivos fuente'],revision:['Revision conditions','Condiciones de revisión']};
const strings={
  title:['ChronoWitness SuperGraph','SuperGraph de ChronoWitness'],intro:['Explore formal results, observation, measured evidence and open conditions.','Explorá los resultados formales, la observación, la evidencia medida y las condiciones abiertas.'],
  map:['Spatial atlas','Atlas espacial'],argument:['Scientific argument','Argumento científico'],witness:['FD7 witness in 3D','Testigo FD7 en 3D'],
  focus:['Focus graph','Ampliar mapa'],lock:['Lock layout','Bloquear disposición'],fit:['Fit connections','Encuadrar conexiones'],
  hint:['Drag to rotate. Drag a node to move it, or hold Shift to move its group. Pinch or use + and − to zoom. Depth is a navigation choice.','Arrastrá para rotar. Arrastrá un nodo para moverlo o mantené Shift para mover su grupo. Usá dos dedos o + y − para acercar. La profundidad sirve para navegar.'],
  previous:['Previous','Anterior'],next:['Next','Siguiente'],play:['Play tour','Reproducir recorrido'],pause:['Pause','Pausar'],exit:['End tour','Salir del recorrido'],
  share:['Link to claim','Enlace a la afirmación'],levels:[['Reader','Technical','Audit'],['Lectura','Técnico','Auditoría']],
  allGroups:['All categories','Todas las categorías'],allStatus:['All statuses','Todos los estados'],select:['Select a claim','Seleccioná una afirmación'],
  search:['Find a claim','Buscar una afirmación'],none:['Choose a claim or start a guided route.','Elegí una afirmación o iniciá un recorrido guiado.'],
  evidence:['Open evidence source','Abrir fuente de evidencia'],links:['Typed connections','Conexiones tipadas'],
  and:['All premises are required','Todas las premisas son necesarias'],
  tourHint:['The tour is a reading order. Arrows in the map are scientific relations.','El recorrido propone un orden de lectura. Las flechas del mapa representan relaciones científicas.'],
};
const query=new URLSearchParams(location.search);
const renderPage=document.body.dataset.screen==='render';
const renderText={
  home:['Open SuperGraph','Abrir SuperGraph'],renderTitle:['FD7 · One cycle, two trajectories','FD7 · Un ciclo, dos trayectorias'],
  renderIntro:['Rotate the exact witness and inspect each of its 24 phases.','Rotá el testigo exacto e inspeccioná sus 24 fases.'],
  openRender:['Open interactive 3D','Abrir 3D interactivo'],figurePdf:['Download vector PDF','Descargar PDF vectorial'],
  phaseLabel:['Cycle phase','Fase del ciclo']
};
const initial={lang:'en',level:0,group:'',status:'',kind:'',expanded:false,mode:'map',selected:null,locked:false,wide:false,offsets:{},groupOffsets:{}};
let saved={};
try{saved=JSON.parse(localStorage.getItem('cw-supergraph-v1')||'{}');}catch{}
const S={...initial,...saved};
if(document.body.dataset.screen==='supergraph')Object.assign(S,{expanded:true,mode:'map',group:'',kind:'',status:'',selected:null,wide:false});
if(['en','es'].includes(query.get('lang')))S.lang=query.get('lang');
if(nodes.has(query.get('claim'))){S.selected=query.get('claim');S.mode='argument';}
if(renderPage||query.get('view')==='render'){S.mode='witness';S.selected='witness';S.wide=false;}
if(!nodes.has(S.selected))S.selected=null;
let yaw=-.26,pitch=.25,zoom=1,pan=[0,0],focus=false,selectedEdge=null,route=-1,step=0,timer=null,tourSnapshot=null,phase=null;
const ix=()=>S.lang==='es'?1:0;
const pick=arr=>arr[ix()];
const T=k=>pick(strings[k]);
const title=n=>ix()?n.title_es:n.title;
const relation=e=>ix()?e.relation_es:e.relation;
function save(){try{if(!renderPage)localStorage.setItem('cw-supergraph-v1',JSON.stringify(S));}catch{}}
function element(tag,text,parent){
  const el=document.createElement(tag);el.textContent=text;if(parent)parent.append(el);return el;
}
function button(text,fn,parent){
  const b=element('button',text,parent);b.type='button';b.onclick=fn;return b;
}
function option(parent,value,text){const o=element('option',text,parent);o.value=value;return o;}
function svg(tag,attrs,parent=graph){
  const n=document.createElementNS('http://www.w3.org/2000/svg',tag);
  for(const [k,v] of Object.entries(attrs))n.setAttribute(k,String(v));
  parent.append(n);return n;
}
function project([x,y,z]){
  const u=x*Math.cos(yaw)+z*Math.sin(yaw),w=z*Math.cos(yaw)-x*Math.sin(yaw);
  const v=y*Math.cos(pitch)-w*Math.sin(pitch),d=y*Math.sin(pitch)+w*Math.cos(pitch);
  const k=12/(12-d);
  return [450+pan[0]+u*75*k*zoom,280+pan[1]-v*75*k*zoom,d,k];
}
function reset(){yaw=-.26;pitch=.25;zoom=1;pan=[0,0];}
function closure(id){
  const result=new Set([id]), stack=[id];
  while(stack.length){
    const next=stack.pop();
    for(const e of D.edges)if(e.to===next&&!['provenance','revision','containment'].includes(e.kind)&&!result.has(e.from)){
      result.add(e.from);stack.push(e.from);
    }
  }
  return result;
}
function visible(){
  if(S.mode==='argument'&&S.selected)return D.nodes.filter(n=>closure(S.selected).has(n.id));
  if(focus&&S.selected){
    const connected=new Set([S.selected]);
    for(const e of D.edges)if([e.from,e.to].includes(S.selected)){connected.add(e.from);connected.add(e.to);}
    return D.nodes.filter(n=>connected.has(n.id));
  }
  const q=$('search').value.trim().toLocaleLowerCase();
  return D.nodes.filter(n=>(S.expanded||S.group||S.kind||S.status||q||n.overview)&&
     (!S.group||n.group===S.group)&&(!S.status||n.status===S.status)&&(!S.kind||n.kind===S.kind)&&
     (n.kind!=='source'||(S.expanded&&!S.group)||S.kind==='source'||S.status==='ARTIFACT'||!!q)&&
     (!q||[n.id,n.title,n.title_es,n.meaning,n.meaning_es].join(' ').toLocaleLowerCase().includes(q)));
}
function select(id,keepRoute=false){
  if(!keepRoute)endTour();
  S.selected=id;selectedEdge=null;
  if(S.mode==='witness'&&id!=='witness')S.mode='map';
  if(S.mode==='map'&&!visible().some(n=>n.id===id)){
    S.group='';S.status='';S.kind=nodes.get(id).kind;$('search').value='';focus=false;
  }
  refresh();
}
function activate(el,fn){
  el.setAttribute('tabindex','0');el.setAttribute('role','button');
  el.addEventListener('click',fn);
  el.addEventListener('keydown',e=>{if(['Enter',' '].includes(e.key)){e.preventDefault();fn();}});
}
function label(x,y,text,attrs={}){
  svg('text',{x,y,fill:'#ecf0ff','font-family':'system-ui','text-anchor':'middle',...attrs}).textContent=text;
}
function drawWitness(){
  const colors=['#8fbcff','#d7a3ee'];
  for(const [j,arm] of Object.entries(['A','B'])){
    const a=D.witness.arms[arm],lane=(Number(j)-.5)*2.5;
    const at=(k,state)=>project([(k-12)/3.25,(state-1.5)*.91,lane]);
    const points=[at(0,a.path[0])];
    for(let k=0;k<24;k++){
      const p=at(k,a.path[k]),q=at(k+1,a.path[k]),r=at(k+1,a.path[k+1]);
      svg('polyline',{points:[p,q,r].map(t=>t.slice(0,2).join(',')).join(' '),stroke:colors[j],fill:'none',
                      opacity:a.word[k]==='1'?1:.5,'stroke-width':2.6});
      if(a.path[k]===3){const [x,y]=at(k+.5,3);svg('circle',{cx:x,cy:y,r:5.5,fill:'#f5afd9',stroke:colors[j]});}
      points.push(r);
    }
    if(phase!==null){
      const [x,y]=at(phase+.5,a.path[phase]);
      svg('circle',{cx:x,cy:y,r:10,fill:'none',stroke:'#f6e8ff','stroke-width':2.3,'data-phase-marker':arm});
    }
    label(points[0][0],points[0][1]+24,'FD7-'+arm+' · '+a.visits+'/24',{'font-size':16,'font-weight':650});
  }
  label(450,513,ix()?'Fase del ciclo × estado × brazo. Contraste de ocupación del estado 3 = 1/24.':
    'Cycle phase × state × arm. State-3 occupation contrast = 1/24.',{'font-size':16});
}
function draw(){
  graph.replaceChildren();
  svg('rect',{width:900,height:560,fill:'#182243'});
  if(S.mode==='witness'){drawWitness();return;}
  const list=visible(), positions=new Map();
  const dense=list.length>15;
  const cols=Math.min(7,Math.ceil(Math.sqrt(list.length*1.6)));
  const rows=Math.ceil(list.length/cols);
  const keys=Object.keys(groups);
  const clusters=[[-2.95,1.5,-1.5],[2.4,1.55,.1],[-2.45,-1.52,1.6],[2.6,-1.52,-.6]];
  const confined=S.group||focus||S.mode==='argument';
  for(const [i,n] of list.entries()){
    const member=list.filter(x=>x.group===n.group),j=member.indexOf(n);
    const angle=2*Math.PI*(confined?i/list.length:j/member.length)+.45;
    const center=confined?[0,0,0]:clusters[keys.indexOf(n.group)];
    const p=dense?project([(i%cols-(cols-1)/2)*1.48,((rows-1)/2-Math.floor(i/cols))*Math.min(1.05,6.5/rows),
      (keys.indexOf(n.group)-1.5)*.42]):project([center[0]+Math.cos(angle)*(confined?3.6:1.1),center[1]+Math.sin(angle)*(confined?2.2:.75),
      center[2]+Math.sin(2*angle)*(confined?1.4:.52)]);
    const own=S.offsets[n.id]||[0,0],group=S.groupOffsets[n.group]||[0,0];
    p[0]+=own[0]+group[0];p[1]+=own[1]+group[1];positions.set(n.id,p);
  }
  const defs=svg('defs',{}),marker=svg('marker',{id:'arrow',viewBox:'0 0 10 10',refX:8,refY:5,markerWidth:6,markerHeight:6,orient:'auto'},defs);
  svg('path',{d:'M 0 0 L 10 5 L 0 10 z',fill:'#baa9f2'},marker);
  for(const e of D.edges){
    if(!positions.has(e.from)||!positions.has(e.to))continue;
    const a=positions.get(e.from),b=positions.get(e.to),traced=[e.from,e.to].includes(S.selected);
    const dx=b[0]-a[0],dy=b[1]-a[1],size=Math.hypot(dx,dy)||1;
    const tx=b[0]-dx/size*30,ty=b[1]-dy/size*21;
    const line=svg('path',{d:'M '+a[0]+' '+a[1]+' Q '+((a[0]+tx)/2)+' '+((a[1]+ty)/2-20)+' '+tx+' '+ty,
      fill:'none',stroke:traced?(e.to===S.selected?'#8fc7ff':'#edb0de'):'#796eb4','stroke-width':traced?3:1.5,
      'stroke-dasharray':e.kind==='provenance'||e.kind==='revision'?'5 4':'none',opacity:dense&&!traced?.46:1,
      'marker-end':'url(#arrow)',class:'edge'+(traced?' trace':''),'data-edge':e.id,'aria-label':relation(e)});
    activate(line,()=>{selectedEdge=e;show();});
  }
  for(const n of list.slice().sort((a,b)=>positions.get(a.id)[2]-positions.get(b.id)[2])){
    const [x,y,,k]=positions.get(n.id),color=groups[n.group][2];
    const g=svg('g',{transform:'translate('+x+' '+y+')',class:'node','data-node':n.id,'aria-label':title(n)});
    const name=title(n),w=dense?102:Math.min(181,Math.max(92,name.length*6.3+15)),h=dense?25:36,limit=dense?17:28;
    svg('rect',{x:-w/2,y:-h/2,width:w,height:h,rx:n.premises?2:12,fill:n.id===S.selected?'#50437a':'#2a3764',
      stroke:color,'stroke-width':n.id===S.selected?3:1.3},g);
    const text=svg('text',{x:0,y:4,fill:'#f4f1ff','font-family':'system-ui','font-size':dense?9:Math.min(13,12*k),'text-anchor':'middle'},g);
    text.textContent=name.length>limit?name.slice(0,limit-1)+'…':name;
    svg('title',{},g).textContent=name;
    activate(g,()=>select(n.id));
  }
  if(!list.length)label(450,280,ix()?'Sin resultados para estos filtros.':'No claims match these filters.',{'font-size':17});
}
function show(){
  const d=$('detail');d.replaceChildren();
  if(selectedEdge){
    element('h2',relation(selectedEdge),d);
    for(const id of [selectedEdge.from,selectedEdge.to])button(title(nodes.get(id)),()=>select(id),d);
    return;
  }
  const n=nodes.get(S.selected);
  if(!n){element('p',T('none'),d);return;}
  const badge=element('span',pick(status[n.status]),d);badge.className='badge';
  element('h2',title(n),d);
  element('p',ix()?n.meaning_es:n.meaning,d);
  if(n.id==='witness')button(T('witness'),()=>mode('witness'),d);
  if(n.id==='reserve-local'||(n.id==='harm'&&S.level>=1)){
    const c=D.local_case;
    element('p',c.context+' · n='+c.n+' · q95 '+c.parent_ratio.toFixed(6)+' → '+c.ratio.toFixed(6),d);
  }
  for(const row of n.contexts||[]){
    const card=element('div','',d);card.className='context';
    element('strong',row.context,card);
    const metrics=element('dl','',card);
    for(const [key,value] of [
      [ix()?'Horizonte / alineación':'Horizon / alignment',row.horizon+' / '+row.alignment],
      [ix()?'Observaciones':'Observations',row.n],['RMSE / '+(ix()?'base':'baseline'),row.rmse_ratio.toFixed(6)],
      ['q95 / '+(ix()?'base':'baseline'),row.q95_ratio.toFixed(6)],
      [ix()?'Deterioros locales / con soporte':'Local harms / supported',row.local_tail_harms_1pct+' / '+row.supported_local_nodes]
    ]){element('dt',key,metrics);element('dd',String(value),metrics);}
  }
  if(n.premises){
    element('h3',T('and'),d);
    for(const id of n.premises)button(title(nodes.get(id)),()=>select(id),d);
  }
  const a=element('a',T('evidence'),d);
  a.href=(location.protocol==='file:'?'../':'https://github.com/FacundoFirmenich/ChronoWitness/blob/HEAD/')+n.source;
  if(S.level===2)element('p','SHA-256 '+n.sha256,d);
  if(S.level>=1||n.kind==='source'){
    element('h3',T('links'),d);
    for(const e of D.edges.filter(e=>[e.from,e.to].includes(n.id))){
      const other=nodes.get(e.from===n.id?e.to:e.from);
      const b=button((e.from===n.id?'→ ':'← ')+relation(e)+' · '+title(other),()=>select(other.id),d);b.className='relation';
    }
  }
  const link=new URL(location.href);link.searchParams.set('claim',n.id);link.searchParams.set('lang',S.lang);
  $('share').href=link.href;
}
function mode(name){S.mode=name;focus=false;reset();if(name==='witness')S.selected='witness';refresh();}
function refresh(){
  document.documentElement.lang=S.lang;
  for(const id of ['title','intro','map','argument','witness','focus','lock','fit','hint','previous','next','exit','share'])$(id).textContent=T(id);
  for(const [id,labels] of Object.entries(renderText))$(id).textContent=pick(labels);
  if(renderPage){$('title').textContent=pick(renderText.renderTitle);$('intro').textContent=pick(renderText.renderIntro);}
  document.title=$('title').textContent;
  $('home').href='supergraph.html?lang='+S.lang;
  $('openRender').href=$('renderPreview').href='render-fd7.html?lang='+S.lang;
  $('renderImage').src=D.render_previews[S.lang];$('renderImage').alt=pick(renderText.renderTitle);
  $('quickPdf').href=$('figurePdf').href='https://github.com/FacundoFirmenich/ChronoWitness/releases/download/v0.15.0/FD7_WITNESS_3D_'+S.lang.toUpperCase()+'.pdf';
  $('quickPdf').textContent=pick(renderText.figurePdf);
  document.body.dataset.mode=S.mode;
  $('phaseControl').hidden=S.mode!=='witness';
  $('count').hidden=S.mode==='witness';
  $('count').textContent=visible().length+' / '+D.nodes.length+(ix()?' nodos visibles · ':' visible nodes · ')+D.edges.length+(ix()?' aristas totales':' total edges');
  $('lens').replaceChildren();
  button(ix()?'Resumen':'Overview',()=>setLens(false),$('lens'));
  button(ix()?'Mapa completo':'Complete map',()=>setLens(true),$('lens'));
  for(const [key,item] of Object.entries(groups))button(pick(item),()=>setLens(true,key),$('lens'));
  $('play').textContent=T(timer?'pause':'play');
  $('language').textContent=ix()?'English':'Español';
  $('search').placeholder=T('search');
  $('inspector').hidden=S.wide;
  $('grid').classList.toggle('wide',S.wide);
  for(const id of ['map','argument','witness'])$(id).setAttribute('aria-pressed',String(S.mode===id));
  $('lock').setAttribute('aria-pressed',String(S.locked));
  $('focus').setAttribute('aria-pressed',String(S.wide));
  for(const [id,items,all,value] of [['group',groups,'allGroups',S.group],['status',status,'allStatus',S.status],['kind',kinds,'allGroups',S.kind]]){
    const select=$(id);select.replaceChildren();option(select,'',id==='kind'?(ix()?'Todas las capas':'All evidence layers'):T(all));
    for(const [k,v] of Object.entries(items))option(select,k,pick(v));
    select.value=value;
  }
  $('acquisitions').replaceChildren();
  option($('acquisitions'),'',ix()?'Reserva E11 por adquisición':'E11 reserve by acquisition');
  for(const date of D.acquisitions)option($('acquisitions'),date,date);
  if(S.selected?.startsWith('acquisition-'))$('acquisitions').value=nodes.get(S.selected).date;
  const claims=$('selectClaim');claims.replaceChildren();option(claims,'',T('select'));
  for(const n of visible())option(claims,n.id,title(n));
  if([...claims.options].some(o=>o.value===S.selected))claims.value=S.selected;
  [...$('levels').children].forEach((b,i)=>{b.textContent=T('levels')[i];b.setAttribute('aria-pressed',String(i===S.level));});
  $('routes').replaceChildren();
  for(const [i,r] of D.routes.entries())button(r[S.lang],()=>{
    endTour(true);tourSnapshot={selected:S.selected,mode:S.mode,focus,selectedEdge};
    route=i;step=0;advance(0);
  },$('routes'));
  $('tour').hidden=route<0;
  if(route>=0){
    const r=D.routes[route];$('station').textContent=r[S.lang]+' · '+(step+1)+'/'+r.steps.length+' · '+T('tourHint');
    $('previous').disabled=step===0;$('next').disabled=step===r.steps.length-1;
  }
  updatePhase();save();draw();show();
}
function setLens(expanded,group=''){
  endTour();S.expanded=expanded;S.group=group;S.status='';S.kind='';$('search').value='';
  S.selected=null;selectedEdge=null;mode('map');
}
function endTour(restore=false){
  clearInterval(timer);timer=null;route=-1;
  if(restore&&tourSnapshot){
    S.selected=tourSnapshot.selected;S.mode=tourSnapshot.mode;focus=tourSnapshot.focus;selectedEdge=tourSnapshot.selectedEdge;
  }
  tourSnapshot=null;
}
function advance(delta){
  if(route<0)return;
  const steps=D.routes[route].steps;step=Math.max(0,Math.min(steps.length-1,step+delta));
  S.mode='argument';select(steps[step],true);
}
$('play').onclick=()=>{
  if(timer){clearInterval(timer);timer=null;refresh();return;}
  timer=setInterval(()=>{if(step===D.routes[route].steps.length-1){clearInterval(timer);timer=null;refresh();}else advance(1);},9000);
  refresh();
};
$('previous').onclick=()=>advance(-1);$('next').onclick=()=>advance(1);
$('exit').onclick=()=>{endTour(true);refresh();};
document.addEventListener('visibilitychange',()=>{if(document.hidden&&timer){clearInterval(timer);timer=null;refresh();}});
for(const id of ['map','argument','witness'])$(id).onclick=()=>mode(id);
$('language').onclick=()=>{S.lang=ix()?'en':'es';refresh();};
$('lock').onclick=()=>{S.locked=!S.locked;refresh();};
$('focus').onclick=()=>{S.wide=!S.wide;refresh();};
$('fit').onclick=()=>{reset();focus=!!S.selected&&S.mode==='map';refresh();};
$('group').onchange=e=>{S.group=e.target.value;focus=false;S.mode='map';refresh();};
$('status').onchange=e=>{S.status=e.target.value;focus=false;S.mode='map';refresh();};
$('kind').onchange=e=>{S.kind=e.target.value;focus=false;S.mode='map';refresh();};
$('acquisitions').onchange=e=>{
  if(e.target.value){
    S.mode='map';S.group='';S.kind='acquisition';S.status='';focus=false;$('search').value='';
    select('acquisition-'+e.target.value);
  }
};
function updatePhase(){
  $('phaseReadout').textContent=phase===null?(ix()?'Ciclo completo':'Full cycle'):
    phase+' / 23 · '+['A','B'].map(arm=>arm+': '+D.witness.arms[arm].path[phase]+' → '+D.witness.arms[arm].path[phase+1]).join(' · ');
}
$('phase').oninput=e=>{phase=e.target.valueAsNumber<0?null:e.target.valueAsNumber;updatePhase();draw();};
$('search').oninput=()=>{focus=false;S.mode='map';draw();const list=$('selectClaim');list.replaceChildren();option(list,'',T('select'));for(const n of visible())option(list,n.id,title(n));};
$('selectClaim').onchange=e=>{if(e.target.value)select(e.target.value);};
for(const b of $('levels').children)b.onclick=()=>{S.level=Number(b.dataset.level);refresh();};
function magnify(f){zoom=Math.max(.6,Math.min(2.4,zoom*f));draw();}
$('plus').onclick=()=>magnify(1.18);$('minus').onclick=()=>magnify(1/1.18);
$('turn').onclick=()=>{yaw+=.25;draw();};
function download(name,text,type){
  const a=document.createElement('a');a.download=name;a.href=URL.createObjectURL(new Blob([text],{type}));a.click();
  setTimeout(()=>URL.revokeObjectURL(a.href),500);
}
$('json').onclick=()=>download('ChronoWitness-ledger.json',JSON.stringify(D,null,2),'application/json');
$('svg').onclick=()=>download('ChronoWitness-view.svg',new XMLSerializer().serializeToString(graph),'image/svg+xml');
const pointers=new Map();
let drag=null;
graph.addEventListener('pointerdown',e=>{
  const n=e.target.closest('[data-node]');
  pointers.set(e.pointerId,[e.clientX,e.clientY]);
  if(pointers.size===1)drag={id:n?.dataset.node,x:e.clientX,y:e.clientY,shift:e.shiftKey,moved:false};
});
graph.addEventListener('pointermove',e=>{
  if(!pointers.has(e.pointerId)||!drag)return;
  if(pointers.size===2){
    const other=[...pointers.entries()].find(([id])=>id!==e.pointerId)[1],old=pointers.get(e.pointerId);
    magnify(Math.hypot(e.clientX-other[0],e.clientY-other[1])/Math.max(1,Math.hypot(old[0]-other[0],old[1]-other[1])));
    pointers.set(e.pointerId,[e.clientX,e.clientY]);drag.moved=true;return;
  }
  const dx=e.clientX-drag.x,dy=e.clientY-drag.y;
  if(!drag.moved&&Math.hypot(dx,dy)<4)return;
  drag.moved=true;
  if(!graph.hasPointerCapture(e.pointerId))graph.setPointerCapture(e.pointerId);
  const scale=900/graph.getBoundingClientRect().width;
  if(drag.id&&!S.locked){
    const store=drag.shift?S.groupOffsets:S.offsets,key=drag.shift?nodes.get(drag.id).group:drag.id;
    const v=store[key]||[0,0];store[key]=[v[0]+dx*scale,v[1]+dy*scale];
  }else if(drag.shift){pan=[pan[0]+dx*scale,pan[1]+dy*scale];}
  else{yaw+=dx*.009;pitch=Math.max(-1.25,Math.min(1.25,pitch+dy*.008));}
  drag.x=e.clientX;drag.y=e.clientY;pointers.set(e.pointerId,[e.clientX,e.clientY]);draw();
});
for(const event of ['pointerup','pointercancel'])graph.addEventListener(event,e=>{pointers.delete(e.pointerId);if(!pointers.size){drag=null;save();}});
graph.addEventListener('keydown',e=>{
  const directions={ArrowLeft:[-.16,0],ArrowRight:[.16,0],ArrowUp:[0,.14],ArrowDown:[0,-.14]};
  if(directions[e.key]){e.preventDefault();const [a,b]=directions[e.key];yaw+=a;pitch=Math.max(-1.25,Math.min(1.25,pitch+b));draw();}
  if(e.key==='+')magnify(1.18);if(e.key==='-')magnify(1/1.18);if(e.key==='0'){reset();draw();}
});
window.CWAtlas={state:()=>structuredClone(S),visible:()=>visible().map(n=>n.id),select};
refresh();
