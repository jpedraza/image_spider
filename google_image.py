# -*- coding: utf-8 -*-
__author__ = 'lufo'

import google

options = google.ImageOptions()
options.image_type = google.ImageType.CLIPART
options.larger_than = google.LargerThan.MP_4
options.color = "green"
results = google.Google.search_images("banana", options)
print results

