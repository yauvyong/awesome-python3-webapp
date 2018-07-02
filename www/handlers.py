#! /usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Adrian Yong'

'url handlers'

import re, time, json, logging, hashlib,base64, asyncio

from coroweb import get, post
from models import User, Comment, Blog, next_id
from config import configs

OOKIE_NAME = 'awesession'
_COOKIE_KEY = config.session.secret

_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')

def user2cookies(user, max_age):
	#build string by : id-expires-sha1
	expires = str(int(time.time() + max_age))
	s = '%s-%s-%s-%s' % (user.id, user.passwd,expires, _COOKIE_KEY)
	L = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
	return '-'.join(L)

@asyncio.coroutine
def cookie2user(cookie_str):
	if not cooki_str:
		return None
	try:
		L = cookie_str.split('-')
		if len(L) !=3:
			return None
		uid, espires, sha1 =L
		if int(expires)< time.time():
			return None
		user = yield from User.find(uid)
		if user is None:
			return None
		s = '%s-%s-%s-%s' % (uid, user.passwd,expires,_COOKIE_KEY)
		if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
			return None
		user.passwd = '******'
		return user
	except Execption as e:
		logging.exception(e)
		return None

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

@post('/api/users')
def api_register_user(*,email,name,passwd):
	if not name or not name.strip():
		raise APIValueError('name')
	if not email or not _RE_EMAIL.match(email):
		raise APIValueError('email')
	if not passwd or not _RE_SHA1.match(passwd):
		raise APIValueError('passwd')
	users = yield from User.findAll('email=?',[email])
	if len(users)>0:
		raise APIError('register: failed', 'email', 'Email is laready in use.')
	uid = next_id()
	sha1_passwd = '%s%s' % (uid, passwd)
	user = User(id=uid, name=name.strip(),email=email,passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(), image='image:none')
	yield from user.save()
	
	r = web.Response()
	r.set_cookie(COOKIE_NAME, user2cokies(user,86400),max_age=86400,httponly=True)
	user.passwd='******'
	r.content_type = 'application/json'
	r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
	return r
		
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

@post('/api/authenticate')
def authnticate(*, email, passwd):
	if not email:
		raise APIValueError('email', 'Invalid email.')
	if not passwd:
		rasie APIValueError('passwd', ' Invalid password.')
	users = yield from User.findAll('email=?',[email])
	if len(users) ==0:
		raise ApiValueError('email','Email not exits')
	user =users[0]
	
	sha1 = hashlib.sha1()
	sha1.update(user.id.encode('utf-8'))
	sha1.update(b':')
	sha1.update(passwd.encode('utf-8'))
	if user.passwd != sha1.hexdigest():
		raise APIValueError('passwd', 'Invalid password')
		
		r = web.Response()
		r.set_cookie(COOKIE_NAME, user2cookie(user,86400),max_age=86400,httponly=True)
		user.passwd = '******'
		r.content_type = 'application/json'
		r.body = json.dumps(user,ensure_ascii=False).encode('utf-8')
		return r