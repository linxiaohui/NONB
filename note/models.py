from django.db import models
from django.utils.timezone import now
from django.urls import reverse


class Note(models.Model):
    """定义笔记的模型"""
    id = models.AutoField(primary_key=True)
    file_name = models.CharField('名字', max_length=200, unique=True)
    pub_time = models.DateTimeField('发布时间', default=now)
    last_mod_time = models.DateTimeField('最后修改时间', default=now)
    title = models.CharField('标题', max_length=200)
    abstract = models.CharField('摘要', max_length=200)
    body = models.TextField('正文')
    status = models.CharField('状态', max_length=1, default='p')
    views = models.PositiveIntegerField('浏览量', default=0)
    category = models.ForeignKey(
        'Category',
        verbose_name='分类',
        on_delete=models.CASCADE,
        blank=False,
        null=False)
    tags = models.ManyToManyField('Tag', verbose_name='标签', blank=True)

    def body_to_string(self):
        return self.body

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-last_mod_time']
        verbose_name = "笔记"
        verbose_name_plural = verbose_name
        get_latest_by = 'id'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def viewed(self):
        self.views += 1
        self.save(update_fields=['views'])

    def next_article(self):
        # 下一篇
        return Note.objects.filter(
            id__gt=self.id, status='p').order_by('id').first()

    def prev_article(self):
        # 前一篇
        return Note.objects.filter(id__lt=self.id, status='p').first()

    def get_absolute_url(self):
        return reverse('note:detailbyid', kwargs={
            'file_name': self.file_name,
            'year': self.pub_time.year,
            'month': self.pub_time.month,
            'day': self.pub_time.day
        })


class Category(models.Model):
    """笔记分类"""
    id = models.AutoField(primary_key=True)
    name = models.CharField('分类名', max_length=30, unique=True)
    parent_category = models.ForeignKey(
        'self',
        verbose_name="父级分类",
        blank=True,
        null=True,
        on_delete=models.CASCADE)
    index = models.IntegerField(default=0, verbose_name="权重排序-越大越靠前")

    class Meta:
        ordering = ['-index']
        verbose_name = "分类"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def get_category_tree(self):
        """递归获得分类目录的父级"""
        categorys = []

        def parse(category):
            categorys.append(category)
            if category.parent_category:
                parse(category.parent_category)
        parse(self)
        return categorys

    def get_sub_categorys(self):
        """
        获得当前分类目录所有子集
        :return:
        """
        categorys = []
        all_categorys = Category.objects.all()

        def parse(category):
            if category not in categorys:
                categorys.append(category)
            childs = all_categorys.filter(parent_category=category)
            for child in childs:
                if category not in categorys:
                    categorys.append(child)
                parse(child)

        parse(self)
        return categorys

    def get_absolute_url(self):
        return reverse(
            'note:category_detail', kwargs={
                'category_name': self.name})


class Tag(models.Model):
    """笔记标签"""
    id = models.AutoField(primary_key=True)
    name = models.CharField('标签名', max_length=30, unique=True)

    def __str__(self):
        return self.name

    def get_note_count(self):
        return Note.objects.filter(tags__name=self.name).distinct().count()

    def get_absolute_url(self):
        return reverse('note:tag_detail', kwargs={'tag_name': self.name})

    class Meta:
        ordering = ['name']
        verbose_name = "标签"
        verbose_name_plural = verbose_name
