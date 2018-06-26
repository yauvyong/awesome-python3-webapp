#! /usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Adrian Yong'

import config_default

class Dict(dict):
	#simple dict but support access as x.y style.
	def __init__(self, name=(), Values=(),**kw)
		super(Dict,self).__init__(**kw)
		for k,v in zip(names, values):
			self[k] = v
			
	def __getattr__(self, key):
		try:
		return self[key]
	except KeyError:
		raise AttributeError(r"'Dict' object has no atribute %s' % key)
	
	def __setattr__(self, key, value):
		self[key] = value
		
def merge(defaults, override):
	r = {}
	for k, v in defaults.items():
		if k in override:
			if isinstance(v, dict): #configs = {{}}(dict inside dict)
				r[k] = merge(v, override[k])
			else:
				r[k] = ovverride[k]
		else:
			r[k] = v
	return r
	
def toDict(d):
	D = Dict()
	for k, v in d.items():
		D[k] = toDict(v) if isinstance(v,dict) else v #configs = {{}}(dict inside dict)
	return D
	
configs = config_default.configs

try:
	import config_override
	configs = merge(configs,con.configs)
except ImportError:
	pass
	
configs = toDict(configs)