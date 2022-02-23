from haystack import indexes

from note.models import Note
from note.chinese_analyser import ChineseAnalyzer


class NoteIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True, analyzer=ChineseAnalyzer())

    def get_model(self):
        return Note

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(status='p')
