# -*- coding: utf-8 -*-
__author__ = 'lufo'

from py_bing_search import PyBingSearch

bing = PyBingSearch('QkcWAM6VJ/S0LJI9wvVGN4UNQUwikMb4zY/kUVe/hAw')
result_list, next_uri = bing.search("Python Software Foundation", limit=50, format='json')

for result in result_list:
    print result.url
