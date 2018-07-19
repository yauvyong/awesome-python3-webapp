#! /usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Adrian Yong'

'url handlers'

import re, time, json, logging, hashlib,base64, asyncio
import markdown2

from aiohttp import web
from apis import APIValueError, APIResourceNotFoundError,APIError,APIPermissionError,Page

from coroweb import get, post
from models import User, Comment, Blog, next_id
from config import configs

COOKIE_NAME = 'awesession'
_COOKIE_KEY = configs.session.secret

_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')

def check_admin(request):
	if request.__user__ is None or not request.__user__.admin:
		raise APIPermissionError()

def get_page_index(page_str):
	p=1
	try:
		p = int(page_str)
	except ValueError as e:
		pass
	if p<1:
		p=1
	return p

def user2cookies(user, max_age):
	#build string by : id-expires-sha1
	expires = str(int(time.time() + max_age))
	s = '%s-%s-%s-%s' % (user.id, user.passwd,expires, _COOKIE_KEY)
	L = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
	return '-'.join(L)

@asyncio.coroutine
def cookie2user(cookie_str):
	if not cookie_str:
		return None
	try:
		L = cookie_str.split('-')
		if len(L) !=3:
			return None
		uid, expires, sha1 = L
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
	except Exception as e:
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
		'blogs': blogs,
		'user': request.__user__
		}

@get('/signout')
def signout(request):
	referer = request.headers.get('Referer')
	r = web.HTTPFound(referer or '/')
	r.set_cookie(COOKIE_NAME,'-deleted-',max_age=0, httponly=True)
	logging.info('user signed out')
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

@get('/blog/{id}')
def get_blog(id, request):
	blog = yield from Blog.find(id)
	comments = yield from Comment.findAll('blog_id=?',[id],orderBy='created_at desc')
	for c in comments:
		c.html_content = text2html(c.content)
	blog.html_content = markdown2.markdown(blog.content)
	return{
		'__template__': 'blog.html',
		'blog': blog,
		'comments': comments,
		'user': request.__user__
	}
	
@get('/manage/blogs/create')
def manage_create_blog(request):
	return {
		'__template__': 'manage_blog_edit.html',
		'id': '',
		'action': '/api/blogs',
		'user': request.__user__
	}

@get('/manage/blogs/edit/{id}')
def manage_edit_blog(*,id,request):
	return {
		'__template__': 'manage_blog_edit.html',
		'id': id,
		'action': '/api/blogs/'+id,
		'user': request.__user__
	}

@get('/api/blogs')
def api_blogs(*, page='1'):
	page_index = get_page_index(page)
	num = yield from Blog.findNumber('count(id)')
	p = Page(num,page_index)
	if num == 0:
		return dict(page=p,blogs=())
	blogs = yield from Blog.findAll(orderBy='created_at desc', limit=(p.offset,p.limit))
	return dict(page=p, blogs=blogs)

@get('/api/users')
def api_users(*, page='1'):
	page_index = get_page_index(page)
	num = yield from User.findNumber('count(id)')
	p = Page(num,page_index)
	if num == 0:
		return dict(page=p,users=())
	users = yield from User.findAll(orderBy='created_at desc', limit=(p.offset,p.limit))
	return dict(page=p, users=users)
	
@get('/api/blogs/{id}')
def api_get_blog(*,id):
	blog = yield from Blog.find(id)
	return blog
		
	
@get('/manage/blogs')
def manage_blogs(*,page='1',request):
	return {
		'__template__': 'manage_blog.html',
		'page_index': get_page_index(page),
		'user': request.__user__
	}
	
@get('/manage/users')
def manage_users(*,page='1',request):
	return {
		'__template__': 'manage_user.html',
		'page_index': get_page_index(page),
		'user': request.__user__
	}
	
@post('/api/users')
@asyncio.coroutine	
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
	sha1_passwd = '%s:%s' % (uid, passwd)
	user = User(id=uid, name=name.strip(),email=email,passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(), image='image:none')
	yield from user.save()
	
	r = web.Response()
	r.set_cookie(COOKIE_NAME, user2cookies(user,86400),max_age=86400,httponly=True)
	user.passwd='******'
	r.content_type = 'application/json'
	r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
	return r
	
@post('/api/authenticate')
@asyncio.coroutine	
def authenticate(*, email, passwd):
	if not email:
		raise APIValueError('email', 'Invalid email.')
	if not passwd:
		raise APIValueError('passwd', ' Invalid password.')
	users = yield from User.findAll('email=?',[email])
	if len(users) ==0:
		raise APIValueError('email','Email not exits')
	user =users[0]
	
	sha1 = hashlib.sha1()
	sha1.update(user.id.encode('utf-8'))
	sha1.update(b':')
	sha1.update(passwd.encode('utf-8'))
	if user.passwd != sha1.hexdigest():
		raise APIValueError('passwd', 'Invalid password')
		
	r = web.Response()
	r.set_cookie(COOKIE_NAME, user2cookies(user,86400),max_age=86400,httponly=True)
	user.passwd = '******'
	r.content_type = 'application/json'
	r.body = json.dumps(user,ensure_ascii=False).encode('utf-8')
	return r

@post('/api/blogs')
@asyncio.coroutine
def api_create_blog(request, *, name, summary, content):
	check_admin(request)
	if not name or not name.strip():
		raise APIValueError('name', 'name cannot be empty')
	if not summary or not summary.strip():
		raise APIValueError('summary', 'summary cannot be empty')
	if not content or not content.strip():
		raise APIValueError('content', 'content cannot be empty')
	blog = Blog(user_id=request.__user__.id, user_name=request.__user__.name, user_image = request.__user__.image, name=name.strip(), summary=summary.strip(),content=content.strip())
	yield from blog.save()
	return blog

@post('/api/blogs/{rid}')
@asyncio.coroutine
def api_edit_blog(rid,request, *, name, summary, content):
	check_admin(request)
	if not name or not name.strip():
		raise APIValueError('name', 'name cannot be empty')
	if not summary or not summary.strip():
		raise APIValueError('summary', 'summary cannot be empty')
	if not content or not content.strip():
		raise APIValueError('content', 'content cannot be empty')
	blog = yield from Blog.find(rid)
	blog.name = name.strip()
	blog.summary = summary.strip()
	blog.content = content.strip()
	yield from blog.update()
	return blog	

@post('/api/blogs/{id}/comments')
@asyncio.coroutine
def api_add_comments(id, request, *, content):
	if not content or not content.strip():
		raise APIValueError('comment', 'comment cannot be empty')
	comment = Comment(user_id=request.__user__.id, user_name=request.__user__.name, user_image = request.__user__.image, blog_id=id, content=content)
	yield from comment.save()
	return comment

@post('/api/blogs/{id}/delete')
@asyncio.coroutine
def api_delete_blog(id, request):
	check_admin(request)
	blog = yield from Blog.find(id)
	yield from blog.remove()
	return dict(id=id)
	
@post('/api/users/{id}/delete')
@asyncio.coroutine
def api_delete_user(id, request):
	check_admin(request)
	user = yield from User.find(id)
	yield from user.remove()
	return dict(id=id)