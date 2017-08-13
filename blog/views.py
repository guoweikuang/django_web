# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from blog.models import Article
from blog.models import Category
from blog.models import Tag
from blog.models import BlogComment
from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormView
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from blog.forms import BlogCommentForm
import markdown2
# Create your views here.


class IndexView(ListView):
    """
    首页视图，用于展示从数据库读取的文章
    """

    # template_name属性用于指定使用哪个模板进行渲染
    template_name = "blog/index.html"
    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    context_object_name = "article_list"

    def get_queryset(self):
        """
        过滤数据，获取所有已发布文章，并且将内容转成markdown形式
        """
        article_list = Article.objects.filter(status='p')
        for article in article_list:
            # 将markdown标记的文本转为html文本
            article.body = markdown2.markdown(article.body, extras=['fenced-code-blocks'], )
        return article_list

    def get_context_data(self, **kwargs):
        """
        增加额外的数据，这里返回一个文章分类，以字典的形式
        """
        kwargs['category_list'] = Category.objects.all().order_by('name')
        kwargs['date_archive'] = Article.objects.archive()
        kwargs['tag_list'] = Tag.objects.all().order_by('name')
        return super(IndexView, self).get_context_data(**kwargs)


class ArticleDetailView(DetailView):
    """
    Django有基于类的视图DetailView,用于显示一个对象的详情页，
    我们继承它指定视图获取哪个model
    """
    model = Article
    template_name = "blog/detail.html"
    # 在模板中需要使用的上下文名字
    context_object_name = "article"

    # 这里注意，pk_url_kwarg用于接收一个来自url中的主键，然后会根据这个主键进行查询
    # 我们之前在urlpatterns已经捕获article_id
    pk_url_kwarg = 'article_id'

    def get_object(self, queryset=None):
        """
        # 指定以上几个属性，已经能够返回一个DetailView视图了，
        为了让文章以markdown形式展现，我们重写get_object()方法。
        :param queryset:
        :return:
        """
        obj = super(ArticleDetailView, self).get_object()
        obj.increase_views()
        obj.body = markdown2.markdown(obj.body, extras=['fenced-code-blocks'],)
        return obj

    def get_context_data(self, **kwargs):
        kwargs['comment_list'] = self.object.blogcomment_set.all()
        kwargs['form'] = BlogCommentForm()
        return super(ArticleDetailView, self).get_context_data(**kwargs)


class CategoryView(ListView):
    template_name = 'blog/index.html'
    context_object_name = "article_list"

    def get_queryset(self):
        # 注意在url里我们捕获了分类的id作为关键字参数（cate_id）传递给了CategoryView，传递的参数在kwargs属性中获取
        article_list = Article.objects.filter(category=self.kwargs['cate_id'])
        for article in article_list:
            article.body = markdown2.markdown(article.body, extras=['fenced-code-blocks'],)
        return article_list

    def get_context_data(self, **kwargs):
        kwargs['category_list'] = Category.objects.all().order_by('name')
        return super(CategoryView, self).get_context_data(**kwargs)


class TagView(ListView):
    template_name = 'blog/index.html'
    context_object_name = "article_list"

    def get_queryset(self):
        """
        根据指定标签获取该标签下的全部文章
        :return:
        """
        article_list = Article.objects.filter(tags=self.kwargs['tag_id'], status='p')
        for article in article_list:
            article.body = markdown2.markdown(article.body, extras=['fenced-code-blocks'],)
        return article_list

    def get_context_data(self, **kwargs):
        kwargs['tag_list'] = Tag.objects.all().order_by('name')
        return super(TagView, self).get_context_data(**kwargs)


class ArchiveView(ListView):
    template_name = 'blog/index.html'
    context_object_name = 'article_list'

    def get_queryset(self):
        # 接收从url传递的year和month参数，转为int类型
        year = int(self.kwargs['year'])
        month = int(self.kwargs['month'])
        # 按照year和month过滤文章
        article_list = Article.objects.filter(created_time__year=year, created_time__month=month)
        for article in article_list:
            article.body = markdown2.markdown(article.body, extras=['fenced-code-blocks'], )
        return article_list

    def get_context_data(self, **kwargs):
        kwargs['tag_list'] = Tag.objects.all().order_by('name')
        return super(ArchiveView, self).get_context_data(**kwargs)


class CommentPostView(FormView):
    form_class = BlogCommentForm

    # 指定评论提交成功后跳转渲染的模板文件。
    # 我们的评论表单放在detail.html中，评论成功后返回到原始提交页面
    template_name = 'blog/detail.html'

    def form_valid(self, form):
        """ 提交数据验证合法后的逻辑 """

        # 首先根据 url 传入的参数（在 self.kwargs 中）获取到被评论的文章
        target_article = get_object_or_404(Article, pk=self.kwargs['article_id'])

        # 调用ModelForm的save方法保存评论，设置commit=False则先不保存到数据库，
        # 而是返回生成的comment实例，直到真正调用save方法时才保存到数据库。
        comment = form.save(commit=False)

        # 把评论和文章关联
        comment.article = target_article
        comment.save()

        # 评论生成成功，重定向到被评论的文章页面，get_absolute_url 请看下面的讲解。
        self.success_url = target_article.get_absolute_url()
        return HttpResponseRedirect(self.success_url)

    def form_invalid(self, form):
        """ 提交数据验证不合法后的逻辑 """
        target_article = get_object_or_404(Article, pk=self.kwargs['article_id'])

        # 不保存评论，回到原来提交评论的文章详情页面
        return render(self.request, 'blog/detail.html', {
            'form': form,
            'article': target_article,
            'comment_list': target_article.blogcomment_set.all(),
        })
