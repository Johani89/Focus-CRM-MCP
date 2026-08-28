import asyncio, json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from .config import get_settings
from .tools import TOOLS, dispatch
from .client import FocusError

s = get_settings()
app = FastAPI(title=s.app_name, version=s.app_version)

@app.get('/health')
async def health(): return {'status':'ok','service':s.app_name,'version':s.app_version,'focus_configured':s.configured,'tools':len(TOOLS)}

@app.get('/')
async def root(): return {'service':s.app_name,'version':s.app_version,'tools':[t['name'] for t in TOOLS]}

@app.get('/.well-known/mcp.json')
async def manifest(): return {'name':s.app_name,'version':s.app_version,'transport':'sse','sse':'/sse/','call_tool':'/call_tool/','tools':TOOLS}

@app.api_route('/call_tool/', methods=['POST','HEAD','OPTIONS'])
async def call_tool(request: Request):
    if request.method != 'POST': return JSONResponse({'ok':True})
    try:
        body = await request.json(); name = body.get('name') or body.get('tool'); args = body.get('arguments') or body.get('args') or {}
        if not name: return JSONResponse({'error':'Missing tool name'}, status_code=400)
        result = await dispatch(name,args)
        return {'content':[{'type':'text','text':json.dumps(result,default=str)}]}
    except KeyError as e: return JSONResponse({'error':f'Unknown tool: {e.args[0]}'}, status_code=404)
    except ValueError as e: return JSONResponse({'error':str(e)}, status_code=400)
    except FocusError as e: return JSONResponse({'error':str(e)}, status_code=502)
    except Exception as e: return JSONResponse({'error':f'Internal error: {type(e).__name__}'}, status_code=500)

@app.get('/sse/')
async def sse():
    async def stream():
        yield ': connected\n\n'; yield 'event: endpoint\ndata: /call_tool/\n\n'
        while True:
            await asyncio.sleep(15); yield ': ping\n\n'
    return StreamingResponse(stream(), media_type='text/event-stream')
