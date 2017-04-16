# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Article, Category, Tag
# Register your models here.
# import sys

# reload(sys)
# sys.setdefaultencoding('utf-8')

admin.site.register(Article)
admin.site.register(Category)
admin.site.register(Tag)


