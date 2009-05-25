#!/usr/bin/python
import etl

from etl.component import component
from etl.connector import connector
from datetime import datetime
import getpass

user = raw_input('Enter gmail username: ')
user = user + '@gmail.com'
password = getpass.unix_getpass("Enter your password:")
cal_conn=etl.connector.gcalendar_connector(user, password)
cal_service = cal_conn.open()
gcalendar_in_events= etl.component.input.gcalendar_in(cal_conn,'Get user events')

log1=etl.component.transform.logger(name='After write')
log=etl.component.transform.logger(name='After map')

map = etl.component.transform.map({'main':{
    'id': "tools.uniq_id(main.get('name', 'anonymous'), prefix='event_')",
    'name': "main.get('name','anonymous')",
    'date_begin':'''datetime.fromtimestamp("main.get('date_begin')").strftime("%Y-%m-%d %H:%M:%S")''',
    'date_end':'''datetime.fromtimestamp("main.get('date_end')").strftime("%Y-%m-%d %H:%M:%S")''',
#    'date_begin':'''datetime.datetime(*main.get('date_begin').timetuple()[:6]).strftime('%Y-%m-%d %H:%M:%S')''',
#    'date_end':'''datetime.datetime(*main.get('date_end').timetuple()[:6]).strftime('%Y-%m-%d %H:%M:%S')''',
    "product_id":"main.get('product_id', 'Google Tasks')",
}})


ooconnector = etl.connector.openobject_connector('http://localhost:8069', 'test', 'admin', 'admin', con_type='xmlrpc')

oo_out_event= etl.component.output.openobject_out(
     ooconnector,
     'event.event',
     { 'id':'id', 'name':'name', 'date_begin':'date_begin', 'date_end':'date_end','product_id':'product_id'
        })



tran=etl.transition(gcalendar_in_events, map)
tran=etl.transition(map, oo_out_event)
job1=etl.job([gcalendar_in_events, log1, oo_out_event, log])
print job1
job1.run()
#print job1.get_statitic_info()
