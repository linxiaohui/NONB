import time
import re

from whoosh.analysis import Tokenizer, Token
import thulac

time.clock = time.perf_counter
thu = thulac.thulac(seg_only=True)


class ChineseAnalyzer(Tokenizer):
    def __call__(self, value, positions=False, chars=False,
                 keeporiginal=False, removestops=True,
                 start_pos=0, start_char=0, mode='', **kwargs):
        t = Token(positions, chars, removestops=removestops, mode=mode, **kwargs)
        # 将图片以base64的方式按markdown语法插入后，显著降低了Note模型保存时分词的效率
        # value为note的markdown格式；在分词时将图片的base64忽略
        image_pattern = re.compile(r"!\[.+?\][(]data:image/png;base64,.+[)]")
        value = image_pattern.sub('', value)
        seglist = thu.cut(value)
        for w, _ in seglist:
            t.original = t.text = w
            t.boost = 1.0
            if positions:
                t.pos = start_pos + value.find(w)
            if chars:
                t.startchar = start_char + value.find(w)
                t.endchar = start_char + value.find(w) + len(w)
            yield t
