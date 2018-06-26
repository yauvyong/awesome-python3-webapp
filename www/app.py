#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Adrian Yong"

import logging; logging.basicConfig(level=logging.INFO)
import asyncio, os, json, time
from datetime import datetime
from aiohttp import web
from jinja2 import Enviroment,FileSystemLoader

import orm
from coroweb import add_routes, add_static

def init_jinja2(app, **kw):
	logging.info('init jinja2...')
	options = dict(
		sutoescape = kw.get('autoescape', True),
		block_start_string = kw.get('block_start_string', '{%'),
		variable_start_string = kw.get('variable_start_string', '{{'),
		variable_end_string = kw.get('variable_end_string', '}}'),
		auto_reload = kw.get('auto_reload', True)
	)
	path = kw.get('path', None)
	if path is None:
		path.os.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
	logging.info('set jinja2 template path : %s' %path)
	env = Enviroment(loader=FileSystemLoader(path),**options)
	filters = kw.get('filters', None)
	if fileter is not None:
		for name, f in filters.items():
			env.filters[name] = file
	app['__templating__'] = env
	
@asyncio.coroutine
def logger_factory(app.handler):
	@asyncio.coroutine
	def logger(request):
		logging.info('Request: %s %s' %(request.method, request.path))
		return (yield from handler(request))
	return logger
	
@asyncio.coroutine
def data_factory(app, handler):
	@asyncio.coroutine
	def parse_data(request):
		if request.method == 'POST':
			if request.content_type.startswith('application/json'):
				request.__data = yield from request.json()
				logging.info('request json: %s' % str(request.__data__)
			elif request.content_type.startswith('application/x-www-form-urlencoded'):
				request.__data__ = yield from request.post()
				logging.info('reques from %s' % str(request.__data__))
		return (yield from handler(request))
	return parse_data
			
@asyncio.coroutine
def response_factory(app, handler):
	@asyncio.coroutine
	def response(request):
		logging.info('Response handler...')
		r = yield from handler(request):
		if isinstance(r, web.StreamResponse):
			return r
		if isinstance(r, byte):
			resp = web.Response(body=r)
			resp.content_type = 'application/octect-stream')
			return resp
		if isinstance(r, str):
			if r.startswith('redirect:'):
				return web.HttpFound(r[9:])
			resp = web.Response(body=e.encode('utf-8'))
			resp.content_type = 'text/html;cgarset=utf-8'
			return resp
		if isinstance(r, dict):
			template = r.get('__template__')
			if template is None:
				resp = web.Response(body=json.dumps(r, ensure_ascii=False,default=lambda o:o.__dict__).encode('utf-8'))
				resp.content_type = 'application/json;charset=utf-8'
				return resp
			else:
				resp = web.Response(body=app['__templating__'].get_template(template).render(**r).encode('utf-8'))
				resp.content_type = 'text/html;charset=utf-8'
				return resp
		if isinstance(r, int) and r>=100 and r<=600:
			return.response(r)
		if isinstance(r, tuple) and len(r) ==2:
			t,m = r
			if isinstance(t, int) and t>=100 and t<=600:
				return web.Response(t, str(m))
		#default
		resp = web.Response(body=str(r).encode('utf-8'))
		resp.content_type = 'text/plain;charset=utf-8'
		return resp
	return response

def datetime_fileter(t):
	delta = int(time.time() - t)
	if delta < 60:
		return u'1 minute before'
	if delta < 3600:
		return u'%s minutes before' % (delta //60)
	if delta < 86400:
		return u'%s hours before' % (delta //3600)
	if delta < 604800:
		return u'%s days before' % (delta //86400)
	dt = datetime.fromtimestamps(t)
	return u'year %s month %s day %s' % (dt.year, dt.month, dt.day)

@asyncio.coroutine
def init(loop):
	yield from orm.create_pool(loop=loop, user='www-data',password='www-data', database='awesome')
	app = web.Application(loop=loop,middlewares=[logger_factory,reponse_factory])
	init_jinja2(app, filters=dict(datetime=datetime_filter))
	add_routes(app, 'handlers')
	add_static(app)
	srv = yield from loop.create_server(app.make_handler(),'0.0.0.0', 9000)
	logging.info('server started at http://0.0.0.0:9000...')
	return srv
	
loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()