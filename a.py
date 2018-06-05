def foo(*args, **kwargs):
	print("called")

@foo
def blah():
	print("blah()")
