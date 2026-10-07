'use client';
import {useEffect, useState} from 'react';

export const contractHandoffKey = 'kinq_contract_account_handoff';

export async function memberRequest(path, {csrf, ...options} = {}) {
  const response = await fetch(path, {...options, credentials:'same-origin', cache:'no-store', headers:{
    'Content-Type':'application/json', ...(csrf ? {'X-CSRF-Token':csrf} : {}), ...options.headers,
  }});
  if (!response.ok) {
    let message = response.status === 401 ? 'Connecte-toi pour retrouver tes contrats.' : 'Le service est indisponible. Réessaie dans un instant.';
    try {const body=await response.json(); if (typeof body.detail === 'string') message=body.detail;} catch {}
    const error = new Error(message); error.status = response.status; throw error;
  }
  return response.headers.get('content-type')?.includes('application/pdf') ? response.blob() : response.json();
}

export function useMember() {
  const [attempt,setAttempt] = useState(0);
  const [state,setState] = useState({loading:true,member:null,error:''});
  useEffect(()=>{let active=true; memberRequest('/api/member/me').then(member=>{
    if(active) setState({loading:false,member,error:''});
  }).catch(error=>{if(active)setState({loading:false,member:null,error:error.status===401 ? '' : error.message});});
    return ()=>{active=false;};
  },[attempt]);
  return {...state,retry:()=>{setState(previous=>({...previous,loading:true,error:''}));setAttempt(n=>n+1);}};
}
