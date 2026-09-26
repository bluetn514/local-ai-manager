export type SystemData = { os: string; cpu: {name:string;usage_percent:number}; memory:{total_bytes:number;used_bytes:number;usage_percent:number}; gpu:{available:boolean;name:string;usage_percent:number|null;temperature_c:number|null;memory_total_mb:number|null;memory_used_mb:number|null} }
export type OllamaStatus = { installed:boolean;running:boolean;version:string|null }
export type Model = {name:string;display_name:string;tag:string;size:number;modified_at:string|null;loaded:boolean|null;quantization:string|null}
export type LogEntry = {id:number;timestamp:string;level:'INFO'|'WARNING'|'ERROR';message:string}
type Envelope<T> = {ok:true;data:T}|{ok:false;error:string}
export async function api<T>(path:string, method='GET', body?:object):Promise<T> {
  const response = await fetch('/api'+path,{method,headers:{'Content-Type':'application/json'},body:body?JSON.stringify(body):undefined})
  const result:Envelope<T> = await response.json()
  if (!response.ok || !result.ok) throw new Error('error' in result ? result.error : `HTTP ${response.status}`)
  return result.data
}
export async function stream(path:string, body:object, onEvent:(event:Record<string,unknown>)=>void):Promise<void> {
  const response=await fetch('/api'+path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)})
  if(!response.ok){const error=await response.json();throw new Error(error.error||`HTTP ${response.status}`)}
  if(!response.body) throw new Error('Streaming unavailable')
  const reader=response.body.getReader(), decoder=new TextDecoder();let buffer=''
  while(true){const {done,value}=await reader.read();if(done)break;buffer+=decoder.decode(value,{stream:true});const lines=buffer.split('\n');buffer=lines.pop()||'';for(const line of lines)if(line.trim()){const event=JSON.parse(line) as Record<string,unknown>;if(event.error)throw new Error(String(event.error));onEvent(event)}}
}
export const bytes=(value:number|null|undefined)=>value==null?'—':value>=1e9?`${(value/1e9).toFixed(1)} GB`:`${(value/1e6).toFixed(1)} MB`
