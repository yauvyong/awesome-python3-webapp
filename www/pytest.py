import inspect

def get_required_kw_args(fn):
	args = []
	params = inspect.signature(fn).parameters
	for name, param in params.items():
		print(name,param)
		print(param.kind)
		if param.kind == inspect.Parameter.KEYWORD_ONLY and param.default == inspect.Parameter.empty:
			args.append(name)
			
	print(args)
	return tuple(args)
	
def get_named_kw_args(fn):
	args = []
	params = inspect.signature(fn).parameters
	for name, param in params.items():
		print(name,param)
		if param.kind == inspect.Parameter.KEYWORD_ONLY:
			args.append(name)
			print(param.kind)
	print(args)
	return tuple(args)

def has_named_kw_args(fn):
	params = inspect.signature(fn).parameters
	for name, param in params.items():
		print(name,param)
		if param.kind == inspect.Parameter.KEYWORD_ONLY:
			print(param.kind)
			print(True)
			return True

def has_var_kw_arg(fn):
	params = inspect.signature(fn).parameters
	for name, param in params.items():
		print(name,param)
		if param.kind == inspect.Parameter.VAR_KEYWORD:
			print(param.kind)
			print(True)
			return True

def has_request_arg(fn):
	sig = inspect.signature(fn)
	params = sig.parameters
	found = False
	for name, param in params.items():
		print(name,param)
		if name == 'request':
			found = True
			continue
		if found and (param.kind != inspect.Parameter.VAR_POSITIONAL and param.kind != inspect.Parameter.KEYWORD_ONLY and param.kind != inspect.Parameter.VAR_KEYWORD):
			raise ValueError('request parameter must be the last named parameter in function: %s%s' % (fn.__name__, str(sig)))
	print(found)
	return found
	
def test(request, *, b:int, **kwargs):
	pass

get_required_kw_args(test)
#get_named_kw_args(test)
#has_named_kw_args(test)
#has_var_kw_arg(test)
#has_request_arg(test)