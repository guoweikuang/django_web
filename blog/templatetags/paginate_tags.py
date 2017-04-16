# -*- coding: utf-8 -*-
from django import template
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

# 这是定义模板标签要用到的
register = template.Library()


# 这个装饰器表明这个函数是一个模板标签，takes_context = True 表示接收上下文对象，
# 就是前面所说的封装了各种变量的 Context 对象。
@register.simple_tag(takes_context=True)
def paginate(context, object_list, page_count):
    left = 3  # 当前页码左边显示几个页码号 -1，比如3就显示2个
    right = 3  # 当前页码右边显示几个页码号 -1

    paginator = Paginator(object_list, page_count)
    page = context['request'].GET.get('page')

    try:
        object_list = paginator.page(page)
        context['current_page'] = int(page)
        """
        调用了两个辅助函数，根据当前页得到了左右的页码号，
        比如设置成获取左右两边2个页码号，那么假如当前页是5，
        则 pages = [3,4,5,6,7],当然一些细节需要处理，比如如果当前页是2，那么获取的是pages = [1,2,3,4]
        """
        pages = get_left(context['current_page'], left, paginator.num_pages) + get_right(context['current_page'], right,
                                                                                         paginator.num_pages)
    except PageNotAnInteger:
        object_list = paginator.page(1)
        context['current_page'] = 1
        pages = get_right(context['current_page'], right, paginator.num_pages)
    except EmptyPage:
        object_list = paginator.page(paginator.num_pages)
        context['current_page'] = paginator.num_pages
        pages = get_left(context['current_page'], left, paginator.num_pages)

    context['article_list'] = object_list
    context['pages'] = pages
    context['last_page'] = paginator.num_pages
    context['first_page'] = 1
    try:
        """
        获取 pages 列表第一个值和最后一个值，主要用于在是否该插入省略号的判断，
        在模板文件中将会体会到它的用处。注意这里可能产生异常，因为pages可能是一个空列表，
        比如本身只有一个分页，那么pages就为空，
        因为我们永远不会获取页码为1的页码号（至少有1页，1的页码号已经固定写在模板文件中）
        """
        context['pages_first'] = pages[0]
        context['pages_last'] = pages[-1] + 1
    except IndexError:
        context['pages_first'] = 1
        context['pages_last'] = 2

    return ''  # 必须加这个，否则首页会显示个None


def get_left(current_page, left, num_pages):
    """
    辅助函数，获取当前页码的值得左边两个页码值，
    要注意一些细节，比如不够两个那么最左取到2，
    为了方便处理，包含当前页码值，比如当前页码值为5，那么pages = [3,4,5]
    :param current_page:
    :param left:
    :param num_pages:
    :return:
    """
    if current_page == 1:
        return []
    elif current_page == num_pages:
        l = [i - 1 for i in range(current_page, current_page - left, -1) if i - 1 > 1]
        l.sort()
        return l
    l = [i for i in range(current_page, current_page - left, -1) if i > 1]
    l.sort()
    return l


def get_right(current_page, right, num_pages):
    """
    辅助函数，获取当前页码的值得右边两个页码值，要注意一些细节，比如不够两个那么最右取到最大页码值。
    不包含当前页码值。比如当前页码值为5，那么pages = [6,7]
    :param current_page:
    :param right:
    :param num_pages:
    :return:
    """
    if current_page == num_pages:
        return []
    return [i + 1 for i in range(current_page, current_page + right - 1) if i < num_pages - 1]
