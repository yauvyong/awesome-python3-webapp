#! /usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Adrian Yong'

'url handlers'

import re, time, json, logging, hashlib,base64, asyncio

from coroweb import get, post
from models import User, Comment, Blog, next_id

@get('/')
@asyncio.coroutine
def index(request):
	summary = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
	
	blogs = [
		Blog(id='1', name='Test Blog',summary=summary, created_at=time.time()-120),
		Blog(id='2', name='Something new',summary=summary, created_at=time.time()-720),
		Blog(id='3', name='Learn Swift',summary=summary, created_at=time.time()-3600)
		]
	
	return {
		'__template__': 'blogs.html',
		'blogs': blogs
		}

@get('/signin')
@asyncio.coroutine		
def signin(request):
	return {
		'__template__': 'signin.html'
		}
		
@get('/register')
@asyncio.coroutine		
def register(request):
	return {
		'__template__': 'register.html'
		}
		
@get('/api/users')
@asyncio.coroutine
def api_get_user(*, Page=1):
	users = yield from User.findAll(orderBy='created_at desc')
	for u in users:
		u.passwd = '******'
	return dict(users=users)
	
