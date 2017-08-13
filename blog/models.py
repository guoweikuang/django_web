# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from collections import defaultdict
from django.db import models
from django.core.urlresolvers import reverse


class ArticleManage(models.Manager):
    """
        继承自默认的 Manager ，为其添加一个自定义的 archive 方法
    """
    def archive(self):
        date_list = Article.objects.datetimes('created_time', 'month', order='DESC')
        # 获取到降序排列的精确到月份且已去重的文章发表时间列表
        # 并把列表转为一个字典，字典的键为年份，值为该年份下对应的月份列表
        date_dict = defaultdict(list)
        for d in date_list:
            date_dict[d.year].append(d.month)

        # 模板不支持defaultdict，因此我们把它转换成一个二级列表，由于字典转换后无序，因此重新降序排序
        return sorted(date_dict.items(), reverse=True)


# Create your models here.
class Article(models.Model):
    STATUS_CHOICES = (
        ('d', 'Draft'),
        ('p', 'Publish')
    )
    title = models.CharField('标题', max_length=140)
    body = models.TextField('正文')

    # 文章创建时间，DateTimeField用于存储时间，
    # 设定auto_now_add参数为真，则在文章被创建时会自动添加创建时间
    created_time = models.DateTimeField('创建时间')

    # 文章最后一次编辑时间，auto_now=True表示每次修改文章时自动添加修改的时间
    last_modified_time = models.DateTimeField('修改时间')

    """
         choices 参数需要的值，choices选项会使该field在被渲染成form时
         被渲染为一个select组件，这里我定义了两个状态，
         一个是Draft（草稿），一个是Published（已发布），
         select组件会有两个选项：Draft 和 Published。
         但是存储在数据库中的值分别是'd'和'p'，这就是 choices的作用。
    """
    status = models.CharField('文章状态', max_length=1, choices=STATUS_CHOICES)

    # 文章摘要，help_text 在该 field 被渲染成 form 是显示帮助信息
    abstract = models.CharField('摘要', max_length=60, blank=True, null=True,
                                help_text="可选，如若为空将摘取正文的前60个字符")
    views = models.PositiveIntegerField('浏览量', default=0)
    likes = models.PositiveIntegerField('点赞数', default=0)
    topped = models.BooleanField('置顶', default=False)

    """
        文章的分类，ForeignKey即数据库中的外键。
        外键的定义是：如果数据库中某个表的列的值是另外一个表的主键。
        外键定义了一个一对多的关系，这里即一篇文章对应一个分类，而一个分类下可能有多篇文章.
        详情参考django官方文档关于ForeinKey的说明，
        on_delete=models.SET_NULL表示删除某个分类（category）后该分类下所有的Article的外键设为null（空）
    """
    category = models.ForeignKey('Category', verbose_name='分类',
                                 null=True, on_delete=models.SET_NULL)
    tags = models.ManyToManyField('Tag', verbose_name='标签集合', blank=True)
    objects = ArticleManage()

    # def __unicode__(self):
    # 	""" 该函数用于和交互解释器中显示字符串 """
    # 	return self.title

    def __str__(self):
        return self.title

    class Meta:
        # Meta 包含一系列选项，这里的 ordering 表示排序，- 号表示逆序。即当从数据库中取出文章时，
        # 其是按文章最后一次修改时间逆序排列的。
        ordering = ['-last_modified_time']

    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'article_id': self.pk})

    def increase_views(self):
        self.views += 1
        self.save(update_fields=['views'])
class Tag(models.Model):
    """
    tag(标签）对应的数据库model
    """
    name = models.CharField('标签名', max_length=20)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_modified_time = models.DateTimeField('修改时间', auto_now=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    """ 存储文章的分类信息 """
    name = models.CharField('分类', max_length=20)
    created_time = models.DateTimeField("创建时间", auto_now=True)
    last_modified_time = models.DateTimeField("修改时间", auto_now=True)

    # def __unicode__(self):
    # 	return self.name

    def __str__(self):
        return self.name


class BlogComment(models.Model):
    user_name = models.CharField('评论者名字', max_length=100)
    user_email = models.CharField('评论者邮箱', max_length=250)
    body = models.TextField('评论内容')
    created_time = models.DateTimeField('评论时间', auto_now_add=True)
    article = models.ForeignKey('Article', verbose_name='评论所属文章', on_delete=models.CASCADE)

    def __str__(self):
        return self.body[:20]
