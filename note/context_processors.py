from datetime import datetime

from .models import Category, Note


def note_processor(requests):
    value = {
        'SITE_NAME': '技术笔记',
        'SITE_DESCRIPTION': '记录技术笔记',
        'SITE_KEYWORDS': 'Python',
        'SITE_BASE_URL': requests.scheme + '://' + requests.get_host() + '/',
        'ARTICLE_SUB_LENGTH': 100,
        'nav_category_list': Category.objects.all(),
        'nav_pages': Note.objects.filter(status='p'),
        "CURRENT_YEAR": datetime.now().year
    }
    return value
