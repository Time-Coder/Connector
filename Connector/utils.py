from __future__ import print_function
import hashlib
import sys
import os
import netifaces


def get_ip():
    for interface in netifaces.interfaces():
        addresses = netifaces.ifaddresses(interface)
        all_infos = addresses.setdefault(netifaces.AF_INET, [{'addr': ''}])
        for info in all_infos:
            if info['addr'] not in ['127.0.0.1', '']:
                return info['addr']
    return '127.0.0.1'


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
    return (os.path.getsize(file_name) if os.path.isfile(file_name) else 0)
