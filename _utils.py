from __future__ import print_function
import hashlib
import sys
import os

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def md5(file_name):
	if not os.path.isfile(file_name):
		return None
	else:
		m = hashlib.md5()
		file = open(file_name, 'rb')
		while True:
			data = file.read(4096)
			if not data:
				break
			m.update(data)
		file.close()

		return m.hexdigest()

def file_size(file_name):
	if not os.path.isfile(file_name):
		return 0
	else:
		return os.path.getsize(file_name)