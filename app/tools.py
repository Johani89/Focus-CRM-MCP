from .client import FocusClient
from .config import get_settings

_client = None

def client():
    global _client
    if _client is None: _client = FocusClient(get_settings())
    return _client

def need(args, name):
    if name not in args or args[name] in (None, ''): raise ValueError(f'Missing required argument: {name}')
    return args[name]

async def dispatch(name, args):
    c = client(); args = args or {}
    if name == 'focus.health': return await c.health()
    if name == 'focus.workplan.list': return await c.list_workplan(args)
    if name == 'focus.workplan.complete': return await c.complete_task(need(args,'task_id'), args.get('do_not_send', True), **{k:v for k,v in args.items() if k not in ('task_id','do_not_send')})
    if name == 'focus.customer.get': return await c.get_customer(need(args,'customer_id'))
    if name == 'focus.customer.notes': return await c.get_notes(need(args,'customer_id'))
    if name == 'focus.note.add': return await c.add_note(need(args,'customer_id'), need(args,'note'))
    if name == 'focus.sms.send': return await c.send_sms(need(args,'customer_id'), need(args,'message'))
    if name == 'focus.email.send': return await c.send_email(need(args,'customer_id'), need(args,'subject'), need(args,'body'))
    if name == 'focus.followup.set': return await c.set_followup(need(args,'customer_id'), args.get('days',1), **{k:v for k,v in args.items() if k not in ('customer_id','days')})
    if name == 'focus.appointment.create': return await c.create_appointment(need(args,'customer_id'), **{k:v for k,v in args.items() if k != 'customer_id'})
    if name == 'focus.call.log': return await c.log_call(need(args,'customer_id'), need(args,'outcome'), args.get('note',''), **{k:v for k,v in args.items() if k not in ('customer_id','outcome','note')})
    raise KeyError(name)

TOOLS = [
 {'name':'focus.health','description':'Check FOCUS connector configuration.'},
 {'name':'focus.workplan.list','description':'List Daily Work Plan tasks.'},
 {'name':'focus.workplan.complete','description':'Complete a Work Plan task; do_not_send defaults true.'},
 {'name':'focus.customer.get','description':'Read a customer record.'},
 {'name':'focus.customer.notes','description':'Read customer notes.'},
 {'name':'focus.note.add','description':'Add a customer note.'},
 {'name':'focus.sms.send','description':'Send an SMS through FOCUS.'},
 {'name':'focus.email.send','description':'Send an email through FOCUS.'},
 {'name':'focus.followup.set','description':'Set customer follow-up; defaults to one day.'},
 {'name':'focus.appointment.create','description':'Create a customer appointment.'},
 {'name':'focus.call.log','description':'Log a customer call outcome.'},
]
