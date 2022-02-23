import logging

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from note.models import Note, Category, Tag

logger = logging.getLogger(__name__)


class NoteListView(ListView):
    # template_name属性用于指定使用哪个模板进行渲染
    template_name = 'note/index.html'
    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    context_object_name = 'note_list'

    # 页面类型，分类目录或标签列表等
    page_type = ''
    paginate_by = settings.PAGINATE_BY
    page_kwarg = 'page'

    def get_view_cache_key(self):
        return self.request.get['pages']

    @property
    def page_number(self):
        page_kwarg = self.page_kwarg
        page = self.kwargs.get(
            page_kwarg) or self.request.GET.get(page_kwarg) or 1
        return page

    def get_context_data(self, **kwargs):
        return super(NoteListView, self).get_context_data(**kwargs)


class IndexView(NoteListView):
    """
    首页
    """
    def get_queryset(self):
        note_list = Note.objects.filter(status='p')
        return note_list


class CategoryDetailView(NoteListView):
    """
    分类目录列表
    """
    page_type = "分类目录归档"

    def get_queryset(self):
        slug = self.kwargs['category_name']
        category = get_object_or_404(Category, name=slug)
        categoryname = category.name
        self.categoryname = categoryname
        categorynames = list(
            map(lambda c: c.name, category.get_sub_categorys()))
        article_list = Note.objects.filter(
            category__name__in=categorynames, status='p')
        return article_list

    def get_context_data(self, **kwargs):

        categoryname = self.categoryname
        try:
            categoryname = categoryname.split('/')[-1]
        except BaseException:
            pass
        kwargs['page_type'] = CategoryDetailView.page_type
        kwargs['tag_name'] = categoryname
        return super(CategoryDetailView, self).get_context_data(**kwargs)


class TagDetailView(NoteListView):
    """
    标签列表页面
    """
    page_type = '分类标签归档'

    def get_queryset(self):
        slug = self.kwargs['tag_name']
        tag = get_object_or_404(Tag, name=slug)
        tag_name = tag.name
        self.name = tag_name
        article_list = Note.objects.filter(
            tags__name=tag_name, status='p')
        return article_list

    def get_context_data(self, **kwargs):
        # tag_name = self.kwargs['tag_name']
        tag_name = self.name
        kwargs['page_type'] = TagDetailView.page_type
        kwargs['tag_name'] = tag_name
        return super(TagDetailView, self).get_context_data(**kwargs)


class ArchivesView(NoteListView):
    """
    归档页面
    """
    page_type = '归档'
    paginate_by = None
    page_kwarg = None
    template_name = 'note/archives.html'

    def get_queryset(self):
        return Note.objects.filter(status='p').all()


class NoteDetailView(DetailView):
    """
    笔记展示页面
    """
    template_name = 'note/detail.html'
    model = Note
    slug_url_kwarg = 'file_name'
    slug_field = 'file_name'
    context_object_name = "note"

    def get_object(self, queryset=None):
        obj = super(NoteDetailView, self).get_object()
        obj.viewed()
        self.object = obj
        return obj

    def get_context_data(self, **kwargs):
        kwargs['next_article'] = self.object.next_article
        kwargs['prev_article'] = self.object.prev_article

        return super(NoteDetailView, self).get_context_data(**kwargs)


def page_not_found_view(
        request,
        exception,
        template_name='note/error_page.html'):
    if exception:
        logger.error(exception)
    url = request.get_full_path()
    return render(request,
                  template_name,
                  {'message': f'您访问的地址 {url} 不存在',
                   'statuscode': '404'},
                  status=404)


def server_error_view(request, template_name='note/error_page.html'):
    return render(request,
                  template_name,
                  {'message': '发生未知的错误',
                   'statuscode': '500'},
                  status=500)


def permission_denied_view(
        request,
        exception,
        template_name='note/error_page.html'):
    if exception:
        logger.error(exception)
    return render(
        request, template_name, {
            'message': '没有权限访问此页面', 'statuscode': '403'}, status=403)
