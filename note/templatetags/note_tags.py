import logging
import random

from django import template
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import stringfilter
from django.urls import reverse
from django.utils.safestring import mark_safe

from note.models import Note, Category, Tag

logger = logging.getLogger(__name__)
register = template.Library()


@register.simple_tag
def datetimeformat(data):
    try:
        return data.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        logger.error(e)
        return ""


@register.filter()
@stringfilter
def custom_markdown(content):
    from note.utils import CommonMarkdown
    return mark_safe(CommonMarkdown.get_markdown(content))


@register.simple_tag
def get_markdown_toc(content):
    from note.utils import CommonMarkdown
    body, toc = CommonMarkdown.get_markdown_with_toc(content)
    return mark_safe(toc)


@register.filter(is_safe=True)
@stringfilter
def truncatechars_content(content):
    """
    获得文章内容的摘要
    :param content:
    :return:
    """
    from django.template.defaultfilters import truncatechars_html
    return truncatechars_html(content, 100)


@register.filter(is_safe=True)
@stringfilter
def truncate(content):
    from django.utils.html import strip_tags

    return strip_tags(content)[:150]


@register.inclusion_tag('note/tags/tag_list.html')
def load_articletags(note):
    """标签"""
    tags = note.tags.all()
    tags_list = []
    for tag in tags:
        url = tag.get_absolute_url()
        count = tag.get_note_count()
        tags_list.append((
            url, count, tag, random.choice(['default', 'primary', 'success', 'info', 'warning', 'danger'])
        ))
    return {
        'article_tags_list': tags_list
    }


@register.inclusion_tag('note/tags/sidebar.html')
def load_sidebar(user, linktype):
    """加载侧边栏"""
    logger.info('load sidebar')
    recent_articles = Note.objects.filter(status='p')[:10]
    sidebar_categorys = Category.objects.all()
    most_read_articles = Note.objects.filter(status='p').order_by('-views')[:10]
    dates = Note.objects.datetimes('pub_time', 'month', order='DESC')
    # 标签云 计算字体大小
    # 根据总数计算出平均值 大小为 (数目/平均值)*步长
    increment = 5
    tags = Tag.objects.all()
    sidebar_tags = None
    if tags and len(tags) > 0:
        s = [t for t in [(t, t.get_note_count()) for t in tags] if t[1]]
        count = sum([t[1] for t in s])
        dd = 1 if (count == 0 or not len(tags)) else count / len(tags)
        import random
        sidebar_tags = list(
            map(lambda x: (x[0], x[1], min(60, (x[1] / dd) * increment + 10)), s))
        random.shuffle(sidebar_tags)

    value = {
        'recent_articles': recent_articles,
        'sidebar_categorys': sidebar_categorys,
        'most_read_articles': most_read_articles,
        'article_dates': dates,
        'sidebar_tags': sidebar_tags,
        'user': user
    }
    return value


@register.inclusion_tag('note/tags/meta_info.html')
def load_note_metas(note):
    """
    获得文章meta信息
    """
    return {
        'note': note
    }


@register.inclusion_tag('note/tags/pagination.html')
def load_pagination_info(page_obj, page_type, tag_name):
    previous_url = ''
    next_url = ''
    if page_type == '':
        if page_obj.has_next():
            next_number = page_obj.next_page_number()
            next_url = reverse('note:index_page', kwargs={'page': next_number})
        if page_obj.has_previous():
            previous_number = page_obj.previous_page_number()
            previous_url = reverse(
                'note:index_page', kwargs={
                    'page': previous_number})
    if page_type == '分类标签归档':
        tag = get_object_or_404(Tag, name=tag_name)
        if page_obj.has_next():
            next_number = page_obj.next_page_number()
            next_url = reverse(
                'note:tag_detail_page',
                kwargs={
                    'page': next_number,
                    'tag_name': tag.name})
        if page_obj.has_previous():
            previous_number = page_obj.previous_page_number()
            previous_url = reverse(
                'note:tag_detail_page',
                kwargs={
                    'page': previous_number,
                    'tag_name': tag.name})

    if page_type == '分类目录归档':
        category = get_object_or_404(Category, name=tag_name)
        if page_obj.has_next():
            next_number = page_obj.next_page_number()
            next_url = reverse(
                'note:category_detail_page',
                kwargs={
                    'page': next_number,
                    'category_name': category.name})
        if page_obj.has_previous():
            previous_number = page_obj.previous_page_number()
            previous_url = reverse(
                'note:category_detail_page',
                kwargs={
                    'page': previous_number,
                    'category_name': category.name})

    return {
        'previous_url': previous_url,
        'next_url': next_url,
        'page_obj': page_obj
    }


@register.inclusion_tag('note/tags/info.html')
def load_note_detail(note, isindex):
    """
    加载文章详情
    isindex:是否列表页，若是列表页只显示摘要
    """
    return {
        'note': note,
        'isindex': isindex,
    }


@register.inclusion_tag('note/tags/abstract.html')
def load_note_abstract(note, query1):
    """
    加载文章详情
    isindex:是否列表页，若是列表页只显示摘要
    """
    return {
        'note': note,
        'query': query1,
    }


@register.simple_tag
def query(qs, **kwargs):
    """ template tag which allows queryset filtering. Usage:
          {% query books author=author as mybooks %}
          {% for book in mybooks %}
            ...
          {% endfor %}
    """
    return qs.filter(**kwargs)


@register.filter
def addstr(arg1, arg2):
    """concatenate arg1 & arg2"""
    return str(arg1) + str(arg2)
