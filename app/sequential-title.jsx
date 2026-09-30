'use client';
import {useEffect,useRef,useState} from 'react';

export default function SequentialTitle({children}) {
  const label=useRef(null);
  const [lines,setLines]=useState([]);
  useEffect(()=>{
    const element=label.current;
    let active=true;
    const measure=()=>{
      if(!active || !element.firstChild) return;
      const node=element.firstChild;
      const base=element.getBoundingClientRect();
      const measured=[];
      for(let index=0;index<node.textContent.length;index++) {
        if(/\s/.test(node.textContent[index])) continue;
        const range=document.createRange();range.setStart(node,index);range.setEnd(node,index+1);
        const rect=range.getBoundingClientRect();
        if(!rect.width) continue;
        let line=measured.find(item=>Math.abs(item.bottom-rect.bottom)<3);
        if(!line){line={left:rect.left,right:rect.right,bottom:rect.bottom};measured.push(line);}
        else{line.left=Math.min(line.left,rect.left);line.right=Math.max(line.right,rect.right);}
      }
      measured.sort((a,b)=>a.bottom-b.bottom);
      const total=measured.reduce((sum,item)=>sum+item.right-item.left,0);
      let travelled=0;
      setLines(measured.map(item=>{
        const width=item.right-item.left;
        const line={left:item.left-base.left,top:item.bottom-base.top-2,width,duration:width/total*200,start:travelled/total*200,reverse:(total-travelled-width)/total*200};
        travelled+=width;return line;
      }));
    };
    const observer=new ResizeObserver(measure);observer.observe(element);
    document.fonts.ready.then(measure);
    return()=>{active=false;observer.disconnect();};
  },[children]);
  return <span ref={label} className="nt-sequential-title">{children}{lines.map((line,index)=><span aria-hidden="true" key={index} className="nt-title-stroke" style={{left:line.left,top:line.top,width:line.width,'--stroke-duration':`${line.duration}ms`,'--stroke-start':`${line.start}ms`,'--stroke-return':`${line.reverse}ms`}}/>)}</span>;
}
