'''
Author: Hrlu
Date: 2021-04-24 20:16:04
LastEditors: Please set LastEditors
LastEditTime: 2021-04-28 20:24:54
Description: hrlu.cn
'''
import hashlib

from random import choice


def make_sha16(string):
    assert isinstance(string, str), "argument string must be type of str."

    string = string.encode()
    return hashlib.sha256(string).hexdigest()[:16]

class Base62:
    keys = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    
    @classmethod
    def BaseID(cls, *args, **kwargs):
        return ''.join(choice(cls.keys) for _ in range(7))



