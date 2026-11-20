import React from 'react';
import {AbsoluteFill, Audio, Composition, Sequence, registerRoot, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import timeline from './tempo.json';
import {Closing, Management, Opening, Overview, Registration, Tracking} from './cenas';
import {clamp, ink, paper, phase, rect, sans} from './visual';

const scenes=[Opening, Overview, Registration, Tracking, Management, Closing];
const fps=24;

function Scene({index}) {
  const {width}=useVideoConfig();
  const frame=useCurrentFrame();
  const scene=timeline.scenes[index];
  const seconds=(frame+scene.frame)/fps;
  const time=frame/fps;
  let u=0;
  for(let i=0;i<scene.phrases.length;i++) {
    const {start,end}=scene.phrases[i];
    if(seconds>=start) u=i+clamp((seconds-start)/Math.max(.001,end-start));
  }
  const dark=index===0||index===3;
  const View=scenes[index];
  const first=index===0, last=index===scenes.length-1;
  const remaining=(scene.duration-frame)/fps;
  const shift=first?0:1-phase(time,0,.47);
  const exit=last?0:1-phase(remaining,0,.33);
  return <AbsoluteFill style={{background:dark?ink:paper,fontFamily:sans}}>
    <div style={{...rect(0,0,1600,900),transformOrigin:'0 0',transform:'scale('+width/1600+')'}}>
      <div style={{...rect(0,0,1600,900),opacity:1-.87*Math.max(shift,exit),transform:'translateY('+(shift*14-exit*9)+'px)'}}>
        <View time={time} u={u}/>
      </div>
    </div>
  </AbsoluteFill>;
}

function Captions() {
  const frame=useCurrentFrame();
  const cue=timeline.cues.find(c=>frame/fps>=c.start && frame/fps<c.end);
  if(!cue)return null;
  return <AbsoluteFill style={{alignItems:'center',justifyContent:'flex-end',paddingBottom:38,pointerEvents:'none'}}>
    <div style={{padding:'12px 30px 15px',maxWidth:1500,background:'#15130ff5',color:'#fffaf1',textAlign:'center',font:'500 36px/1.22 '+sans,letterSpacing:'-.01em',borderRadius:10,whiteSpace:'pre-line',textWrap:'balance'}}>{cue.text}</div>
  </AbsoluteFill>;
}

function Transition() {
  const f=useCurrentFrame();
  const sceneIndex=timeline.scenes.findIndex((s,i)=>i>0 && f<s.frame && f>=s.frame-10);
  if(sceneIndex<0)return null;
  const p=phase(f,timeline.scenes[sceneIndex].frame-10,timeline.scenes[sceneIndex].frame-1);
  return <AbsoluteFill style={{background:sceneIndex===3?ink:paper,transform:'translateX('+(1-p)*100+'%)'}}/>;
}

function Film() {
  return <AbsoluteFill style={{background:paper}}>
    {timeline.scenes.map((s,index)=><Sequence key={index} from={s.frame} durationInFrames={s.duration} name={['Uma ocorrência','O painel','Novo chamado','Atendimento','Gestão por bloco','Reparo confirmado'][index]}><Scene index={index}/></Sequence>)}
    <Audio src={staticFile(timeline.voice)}/>
    <Audio src={staticFile('trilha.mp3')}/>
    <Transition/>
    <Captions/>
  </AbsoluteFill>;
}

function Root() {
  return <Composition id="Nexcondo" component={Film} width={1920} height={1080} fps={fps} durationInFrames={timeline.frames}/>;
}
registerRoot(Root);
