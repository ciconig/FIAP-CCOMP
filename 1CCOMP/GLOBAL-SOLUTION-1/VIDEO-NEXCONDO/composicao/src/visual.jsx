import React from 'react';
import {Img, staticFile} from 'remotion';

export const paper = '#f4eee3';
export const ink = '#211d19';
export const muted = '#676054';
export const orange = '#fa7946';
export const rust = '#af3d1b';
export const green = '#76d7a3';
export const sans = '"Segoe UI", Arial, sans-serif';
export const serif = 'Georgia, "Times New Roman", serif';
export const mono = 'Consolas, "Courier New", monospace';
export const clamp = n => Math.min(1, Math.max(0, n));
export const ease = n => { const t = clamp(n); return t * t * (3 - 2 * t); };
export const phase = (v, start, end) => ease((v - start) / (end - start));
export const mix = (a, b, t) => a + (b - a) * t;
export const rect = (left, top, width, height) => ({position: 'absolute', left, top, width, height});

export function Logo({x, y, w, light = false, style}) {
  return <Img src={staticFile('nexcondo.svg')} style={{...rect(x,y,w,w*496/4240), objectFit:'contain',filter:light?'brightness(0) invert(93%) sepia(16%) saturate(241%)':'brightness(0)',...style}}/>;
}

export function Label({children, x, y, color = muted, size = 16, style}) {
  return <div style={{...rect(x,y,'auto','auto'), fontFamily:mono, fontSize:size, letterSpacing:'0.105em', lineHeight:1.2, textTransform:'uppercase', color, whiteSpace:'nowrap',...style}}>{children}</div>;
}

export function Header({title, dark = false}) {
  const line = dark ? '#61554a' : '#bcb3a5';
  return <>
    <Logo x={64} y={41} w={176} light={dark}/>
    <div style={{...rect(265,43,1,20), background:line}}/>
    <Label x={288} y={45} size={14} color={dark?'#d2c5b6':muted}>{title}</Label>
    <Label x={0} y={45} size={14} style={{right:64,textAlign:'right'}} color={dark?'#d2c5b6':muted}>NexoTech · Interface web</Label>
    <div style={{...rect(64,87,1472,1),background:line,opacity:.65}}/>
  </>;
}

export function Title({x, y, children, size = 78, width = 570, color = ink, progress = 1}) {
  return <div style={{...rect(x,y+(1-progress)*26,width,'auto'),fontFamily:sans, fontSize:size, fontWeight:600, letterSpacing:'-.061em', lineHeight:1.04,color,opacity:progress}}>{children}</div>;
}

// The exterior frame clips a camera into the original browser capture.
// Positions and sizes inside the camera are in the viewport's CSS pixels.
export function Window({x,y,w,h, sx=0,sy=0,scale=1, layers, children, radius=16, style}) {
  return <div style={{...rect(x,y,w,h),borderRadius:radius,overflow:'hidden',background:'#19120e',boxShadow:'0 12px 40px #180e0819',...style}}>
    <div style={{...rect(-sx*scale,-sy*scale,1536,864),transformOrigin:'0 0',transform:'scale('+scale+')'}}>
      {layers.filter(l=>l && (l[1]===undefined || l[1]>.001)).map(([name,opacity],i)=>
        <Img key={name} src={staticFile('ui/'+name+'.png')} style={{...rect(0,0,1536,864),opacity:opacity??1}}/>)}
      {children}
    </div>
  </div>;
}

export function Pointer({x,y,click=0,opacity=1}) {
  return <div style={{...rect(x,y,36,40),opacity}}>
    {click>0 && click<1 && <div style={{...rect(-34*click,-34*click,68*click,68*click), border:'2px solid '+orange,borderRadius:'50%', opacity:1-click}}/>}
    <svg width="25" height="32" viewBox="0 0 25 32" style={{filter:'drop-shadow(0 2px 3px #0009)', transform:'scale('+(1-.15*Math.sin(click*Math.PI))+')',transformOrigin:'0 0'}}>
      <path d="M2 2L21 17.5L12.5 18.2L16.4 27L12.1 29L8.1 19.7L2 25Z" fill="#fff9e9" stroke="#2d2119" strokeWidth="1.8" strokeLinejoin="round"/>
    </svg>
  </div>;
}

export function cursorPath(t, points) {
  if(t<=points[0][0]) return points[0].slice(1);
  for(let i=1;i<points.length;i++) {
    const [time,x,y]=points[i], [lastTime,lastX,lastY]=points[i-1];
    if(t<=time) {const p=phase(t,lastTime,time);return [mix(lastX,x,p),mix(lastY,y,p)];}
  }
  return points[points.length-1].slice(1);
}

function Car({x,y,tint}) {
  return <g transform={'translate('+x+' '+y+')'} stroke={tint} fill="none" strokeWidth="1.5">
    <rect x="-18" y="-37" width="36" height="74" rx="10" fill={tint} fillOpacity=".14"/>
    <path d="M-14 -13Q0 -20 14 -13L12 -3Q0 -7 -12 -3ZM-13 18Q0 22 13 18L12 24Q0 28 -12 24ZM-15 -4L-15 13M15 -4L15 13"/>
  </g>;
}

// A drawn floor plan connects the initial location with the repaired light.
export function Garage({x,y,w,h,time,lit=false}) {
  const reveal=phase(time,-.5,1.6);
  const light=lit?phase(time,-.3,1.5):1-phase(time,.7,1.8);
  const line=lit?'#666251':'#777367', stroke=lit?'#37362b':'#ded3bc';
  const accent=lit?'#257b50':orange;
  return <svg style={{...rect(x,y,w,h),overflow:'visible'}} viewBox="0 0 700 550" fill="none">
    <defs>
      <pattern id={'dots'+lit} width="19" height="19" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".9" fill={line} opacity=".55"/></pattern>
      <radialGradient id={'glow'+lit}><stop stopColor={lit?'#f4ba62':'#e8a567'} stopOpacity=".65"/><stop offset="1" stopColor="#f7be64" stopOpacity="0"/></radialGradient>
      <pattern id={'hatch'+lit} width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(35)"><path d="M0 0v8" stroke={line} strokeWidth="2"/></pattern>
    </defs>
    <rect x="8" y="11" width="684" height="515" fill={'url(#dots'+lit+')'}/>
    <g transform="translate(58,80)" opacity={reveal}>
      <path d="M0 0H530V112H407V331H263V349H0Z" fill={lit?'#d9d6c7':'#34332c'} stroke={stroke} strokeWidth="4" strokeLinejoin="round"/>
      <path d="M0 18H504M16 0V330M293 0V87M286 112H530M407 319H263M284 231H405" stroke={line} strokeWidth="2"/>
      {[0,1,2,3].map(i=><g key={i} transform={'translate('+(30+i*63)+' 19)'}><path d="M0 0V98H56V0" stroke={line} strokeWidth="2"/></g>)}
      {[0,1,2].map(i=><g key={i} transform={'translate('+(30+i*67)+' 250)'}><path d="M0 99V0H60V99" stroke={line} strokeWidth="2"/></g>)}
      <Car x={58} y={65} tint={line}/><Car x={184} y={65} tint={line}/><Car x={125} y={300} tint={line}/>
      <path d="M321 22H495V81H321Z" fill={'url(#hatch'+lit+')'} stroke={line}/>
      <path d="M35 177H231Q278 177 278 211V280" stroke={line} strokeWidth="2.4" strokeDasharray="12 13"/>
      <path d="M267 267L278 281L290 267" stroke={line} strokeWidth="2.4"/>
      <rect x="248" y="337" width="34" height="22" fill={lit?'#d9d6c7':'#34332c'}/>
      <circle cx="281" cy="267" r="105" fill={'url(#glow'+lit+')'} opacity={light}/>
      <circle cx="281" cy="267" r="38" stroke={accent} opacity=".5" strokeDasharray="3 6"/>
      <circle cx="281" cy="267" r="22" fill={lit?'#c5ddc7':'#542c1f'} stroke={accent} strokeWidth="2"/>
      {lit?<path d="M271 267l7 7 14-16" stroke={accent} strokeWidth="3"/>:<g stroke={accent} strokeWidth="2.5"><path d="M275 267q-7-11 5-14 13-1 10 10l-4 6v3h-10z"/><path d="M277 277h7"/></g>}
      <path d="M302 266H349L382 236H505" stroke={accent} strokeWidth="1.5" pathLength="1" strokeDasharray="1" strokeDashoffset={1-phase(time,.65,2)}/>
      <g opacity={phase(time,1.1,2.1)}>
        <text x="391" y="224" fill={accent} fontFamily={mono} letterSpacing="1.5" fontSize="14">{lit?'LUZ RESTABELECIDA':'PONTO DE LUZ'}</text>
        <text x="3" y="385" fill={stroke} fontFamily={mono} letterSpacing="2.5" fontSize="14">BLOCO B  /  GARAGEM</text>
      </g>
      <g stroke={line}><path d="M-19 0V346M-25 0h12M-25 346h12M0 -18h530M0 -23v10M530 -23v10"/></g>
    </g>
  </svg>;
}
