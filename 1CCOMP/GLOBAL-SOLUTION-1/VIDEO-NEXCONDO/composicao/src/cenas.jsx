import React from 'react';
import geometry from './geometria.json';
import {Garage, Header, Label, Logo, Pointer, Title, Window, cursorPath, ease, green, ink, mix, mono, muted, orange, paper, phase, rect, rust, sans, serif} from './visual';

const center = box => [box[0]+box[2]/2,box[1]+box[3]/2];
const line = (x,y,w,color) => <div style={{...rect(x,y,w,1),background:color}}/>;
const dots = color => 'radial-gradient('+color+' 1px, transparent 1px)';
const italic = (text, color) => <span style={{fontFamily:serif,fontStyle:'italic',fontWeight:400,letterSpacing:'-.055em',color}}>{text}</span>;

export function Opening({time,u}) {
  const r=phase(time,-.1,.85), q=phase(u,1.0,1.42);
  return <>
    <Header title="Uma ocorrência" dark/>
    <Label x={76} y={188} color={orange}>Áreas comuns</Label>
    <Title x={68} y={238} width={815} size={103} color={paper} progress={r}>Uma luz<br/>{italic('apagou.',orange)}</Title>
    <div style={{...rect(80,645,620,90),opacity:q,transform:'translateY('+(1-q)*14+'px)'}}>
      <div style={{...rect(0,5,4,50),background:orange}}/>
      <span style={{position:'absolute',left:22,fontFamily:serif,fontStyle:'italic',fontSize:39,color:paper}}>“Alguém já avisou?”</span>
    </div>
    <Garage x={735} y={136+(1-r)*22} w={810} h={636} time={time}/>
  </>;
}

export function Overview({time,u}) {
  const intro=phase(time,-.1,.9),zoom=phase(u,.78,1.72);
  const scale=mix(.928,1.32,zoom);
  return <>
    <Header title="O painel"/>
    <Title x={65} y={112} size={76} width={1450} progress={intro}>Do aviso {italic('ao chamado.',rust)}</Title>
    <div style={{...rect(66,220,1468,552),borderRadius:20,background:'#c3b39b',overflow:'hidden'}}>
      <div style={{...rect(0,0,'100%','100%'),backgroundImage:dots('#73665555'),backgroundSize:'15px 15px'}}/>
      <Window x={mix(22,0,zoom)} y={mix(24,0,zoom)+(1-intro)*52} w={mix(1424,1468,zoom)} h={690}
        sx={mix(0,10,zoom)} sy={mix(0,94,zoom)} scale={scale} layers={ [['dashboard']] } radius={mix(13,0,zoom)}/>
    </div>
  </>;
}

// Reveal a selected control or typed text inside its real browser coordinates.
function Slice({name,box,amount=1}) {
  if(amount<=0) return null;
  const [x,y,w,h]=box;
  return <div style={{...rect(x,y,w*amount,h),overflow:'hidden'}}>
    <Window x={0} y={0} w={w} h={h} sx={x} sy={y} layers={[[name]]} radius={0} style={{boxShadow:'none'}}/>
  </div>;
}

export function Registration({time,u}) {
  const g=geometry['novo-preenchido'],modal=g['#modal'];
  const cat=g['#op-categoria [data-valor="iluminacao"]'],priority=g['#op-prioridade [data-valor="alta"]'];
  const block=g['#sel-bloco'],area=g['[name=area]'],desc=g['[name=descricao]'],send=g['#btn-registrar'];
  const a=phase(time,-.15,.85), done=phase(u,1.82,2.06);
  const zoom=Math.min(1.22,620/modal[3]);
  const sx=modal[0]+modal[2]/2-940/(2*zoom),sy=modal[1]+modal[3]/2-654/(2*zoom);
  const path=[[0,modal[0]+modal[2]-25,modal[1]+22],[.18,...center(cat)],[.27,...center(cat)],
    [.43,...center(priority)],[.50,...center(priority)],[.68,...center(block)],[.82,...center(area)],[.95,...center(area)],
    [1.12,desc[0]+130,desc[1]+24],[1.57,desc[0]+130,desc[1]+24],[1.82,...center(send)],[3,...center(send)]];
  const [px,py]=cursorPath(u,path);
  const step=u<.43?'Iluminação':u<.82?'Prioridade alta':u<1.81?'Bloco B · Garagem':'CH-015';
  const click=[.22,.46,.72,1.82].map(t=>phase(u,t,t+.14)).find(n=>n>0 && n<1)??0;
  // The text uses the actual field background and caret while characters appear.
  const typed='Luminária apagada na entrada da garagem';
  const chars=Math.floor(typed.length*phase(u,1.02,1.53));
  return <>
    <Header title="Novo chamado"/>
    <Label x={71} y={207} color={rust}>Pelo morador</Label>
    <Title x={65} y={258} size={74} width={495} progress={a}>Registrar<br/>{italic('o problema.',rust)}</Title>
    {line(71,535,450,'#b7ac9d')}
    <Label x={71} y={560} size={15}>{u<1.81?'No formulário':'Protocolo gerado'}</Label>
    <div style={{...rect(68,597,473,'auto'),fontSize:u<1.81?40:64,fontWeight:600,letterSpacing:'-.05em',color:ink}}>{step}</div>
    <Window x={594} y={119+(1-a)*22} w={940} h={654} sx={sx} sy={sy} scale={zoom} layers={ [['novo-vazio']] }>
      <Slice name="novo-parcial" box={cat} amount={phase(u,.22,.245)}/>
      <Slice name="novo-parcial" box={priority} amount={phase(u,.46,.485)}/>
      <Slice name="novo-parcial" box={block} amount={phase(u,.72,.75)}/>
      <Slice name="novo-parcial" box={area} amount={phase(u,.84,.94)}/>
      {u>1.0 && <div style={{...rect(desc[0]+3,desc[1]+3,desc[2]-7,desc[3]-7),background:'#110b09',boxSizing:'border-box',padding:'7px 9px',font:'13px/1.5 "Segoe UI",sans-serif',color:'#f5ece7'}}>{typed.slice(0,chars)}{chars<typed.length?'│':''}</div>}
      <Pointer x={px} y={py} click={click} opacity={1-done}/>
    </Window>
    {done>0 && <div style={{...rect(594,119,940,654),borderRadius:16,opacity:done,background:'#2b2720',color:paper,overflow:'hidden'}}>
      <div style={{...rect(0,0,940,654),backgroundImage:dots('#cebb8c39'),backgroundSize:'22px 22px'}}/>
      <div style={{...rect(103,146,734,356),background:'#f4eee3',borderRadius:8,color:ink,boxShadow:'0 16px 48px #0003',transform:'translateY('+(1-done)*24+'px)'}}>
        <Label x={44} y={44} color={rust}>Chamado registrado</Label>
        <div style={{...rect(39,78,670,'auto'),fontFamily:mono,fontWeight:600,fontSize:105,letterSpacing:'-.07em'}}>CH-015</div>
        {line(45,225,644,'#bcb2a1')}
        <div style={{...rect(44,252,620,'auto'),fontSize:27}}>Luminária apagada na entrada da garagem</div>
        <Label x={45} y={305} size={15}>Bloco B · Garagem</Label>
      </div>
    </div>}
  </>;
}

function StatusTrack({u}) {
  const steps=[['Aberto',0],['Em atendimento',.76],['Resolvido',1.78]];
  const stage=u>=1.78?2:u>=.76?1:0;
  return <div style={{...rect(74,469,540,230)}}>
    <div style={{...rect(10,13,2,145),background:'#61594c'}}/>
    <div style={{...rect(10,13,2,72*(phase(u,.68,.82)+phase(u,1.7,1.84))),background:green}}/>
    {steps.map(([label],i)=><div key={label} style={{...rect(0,i*72,'100%',40),display:'flex',alignItems:'center',gap:19}}>
      <div style={{width:22,height:22,borderRadius:20,boxSizing:'border-box',background:i<=stage?green:ink,border:'2px solid '+(i<=stage?green:'#8e8170'),position:'relative'}}>
        {i<stage && <span style={{position:'absolute',left:2,top:-4,color:'#264332',fontSize:18}}>✓</span>}
      </div>
      <span style={{fontSize:31,color:i<=stage?paper:'#aa9e8d',fontWeight:i===stage?600:400,letterSpacing:'-.025em'}}>{label}</span>
    </div>)}
  </div>;
}

export function Tracking({time,u}) {
  const a=phase(time,-.15,.85),open=phase(u,.28,.4),working=phase(u,.76,.80),note=phase(u,1.37,1.46),fixed=phase(u,1.78,1.84);
  const g=geometry.aberto, gf=geometry['atendimento-preenchido'],gfim=geometry.resolvido;
  const sx=g['#gaveta'][0]-83;
  const yHist=gfim['#gaveta .secao:last-child'][1];
  const sy=mix(-12,Math.max(0,yHist-226),phase(u,1.96,2.48));
  const scale=1.21;
  const startBtn=center(g['#gaveta [data-para]']),endBtn=center(gf['#gaveta [data-para="resolvido"]']);
  const [px,py]=cursorPath(u,[[0,1320,205],[.48,1380,235],[.72,...startBtn],[.90,...startBtn],[1.2,...center(gf['#g-dia'])],[1.4,...center(gf['#g-obs'])],[1.65,...center(gf['#g-obs'])],[1.76,...endBtn],[3,...endBtn]]);
  const pane={x:768,y:121+(1-a)*20,w:766,h:650};
  const list=geometry.busca['.lista-cartao'];
  return <>
    <Header title="Atendimento" dark/>
    <Label x={73} y={195} color={orange}>Acompanhamento por protocolo</Label>
    <Title x={68} y={251} size={99} color={paper} progress={a}>CH-015</Title>
    <div style={{...rect(74,380,659,'auto'),color:'#ddcdb9',fontSize:29}}>Bloco B <span style={{color:orange}}> / </span> Garagem</div>
    <StatusTrack u={u}/>
    <div style={{...rect(pane.x,pane.y,pane.w,pane.h),background:'#3b352c',backgroundImage:dots('#a2957766'),backgroundSize:'20px 20px',borderRadius:16,overflow:'hidden'}}>
      <Label x={46} y={106} size={18} color="#f1e6d5">Busca pelo protocolo</Label>
      <Window x={47} y={177} w={671} h={382} sx={list[0]-18} sy={list[1]-20} scale={1.56} layers={ [['busca']] }/>
    </div>
    {open>0 && <Window {...pane} sx={sx} sy={sy} scale={scale} layers={ [['aberto'],['atendimento',working],['atendimento-preenchido',note],['resolvido',fixed]] } style={{opacity:open,transform:'translateX('+(1-open)*38+'px)'}}>
      <Pointer x={px} y={py} click={u<1?phase(u,.76,.87):phase(u,1.78,1.94)} opacity={open*(1-fixed)}/>
    </Window>}
  </>;
}

export function Management({time,u}) {
  const a=phase(time,-.2,.85),chart=phase(u,1.86,2.14),filter=phase(u,2.35,2.40);
  const row=geometry['mapa-final']['#matriz'];
  const chip=center(geometry['bloco-b-final']['[data-bloco="Bloco B"]']);
  const [px,py]=cursorPath(u,[[0,780,310],[2.1,760,262],[2.32,...chip],[3,...chip]]);
  const panToList=phase(u,2.5,2.9);
  const sel=filter>.5;
  return <>
    <Header title="Gestão por bloco"/>
    <Title x={65} y={112} size={70} width={1470} progress={a}>Onde concentrar {italic('o próximo reparo?',rust)}</Title>
    <div style={{...rect(65,226,1470,545),background:'#2c271f',borderRadius:16,overflow:'hidden',color:paper}}>
      <div style={{...rect(0,0,'100%','100%'),backgroundImage:dots('#ceb58b33'),backgroundSize:'18px 18px'}}/>
      <Label x={45} y={55} size={15} color={orange}>{chart<.5?'Mapa por bloco':'Visão do painel'}</Label>
      <div style={{...rect(40,110,430,'auto'),fontSize:chart<.5?62:73,fontWeight:600,lineHeight:1.03,letterSpacing:'-.06em'}}>{chart<.5?<>Todo o<br/>condomínio.</>:sel?<>Bloco B</>:<>Todos os<br/>blocos.</>}</div>
      <div style={{...rect(45,389,375,'auto'),fontSize:25,lineHeight:1.35,color:'#dcceba'}}>{chart<.5?'Chamados agrupados por local e situação.':sel?'5 chamados neste bloco, dos quais 2 foram resolvidos.':'O filtro atualiza os indicadores e a lista de chamados.'}</div>
      <div style={{...rect(470,30,968,485),borderRadius:11,overflow:'hidden',background:'#17110e'}}>
        {chart<1 && <Window x={0} y={0} w={968} h={485} sx={8} sy={Math.max(0,row[1]-79)} scale={.875} layers={ [['mapa-final']] } radius={0}/>}
        {chart>0 && <Window x={0} y={0} w={968} h={485} sx={mix(8,405,panToList)} sy={142} scale={.865} layers={ [['resultado'],['bloco-b-final',filter]] } radius={0} style={{opacity:chart}}>
          <Pointer x={px} y={py} click={phase(u,2.35,2.52)} opacity={chart*(1-panToList)}/>
        </Window>}
      </div>
    </div>
  </>;
}

export function Closing({time,u}) {
  const a=phase(time,-.1,.9),brand=phase(u,.84,1.13);
  return <>
    <Header title="Reparo confirmado"/>
    <div style={{opacity:1-brand}}>
      <Garage x={755} y={151} w={773} h={607} time={time} lit/>
      <Label x={72} y={218} color="#216d49">Bloco B · Garagem</Label>
      <Title x={67} y={270} size={89} width={715} progress={a}>A luz<br/>{italic('voltou.', '#246348')}</Title>
      <div style={{...rect(74,596,610,'auto'),fontFamily:mono,fontSize:24,color:muted}}>CH-015 <span style={{color:'#226544'}}> / Resolvido</span></div>
    </div>
    {brand>0 && <div style={{...rect(0,88,1600,700),opacity:brand,transform:'translateY('+(1-brand)*30+'px)'}}>
      <div style={{...rect(716,102,168,6),background:rust}}/>
      <Logo x={280} y={198} w={1040}/>
      <div style={{...rect(100,383,1400,'auto'),fontFamily:serif,fontStyle:'italic',fontSize:50,textAlign:'center',letterSpacing:'-.036em',color:ink}}>Chamados organizados. Comunidade conectada.</div>
      <Label x={0} y={528} color={muted} style={{width:'100%',textAlign:'center'}}>Uma solução NexoTech</Label>
    </div>}
  </>;
}
