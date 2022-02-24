#!/usr/bin/env python
"""
将基于hexo的markdown文件导入到数据库中
本代码演示了如何在Django项目外使用模型
"""

import os
import re
import sys
import glob
from datetime import datetime
from typing import List, Tuple

import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'NONB.settings'
django.setup()

from note.models import Note, Category, Tag


def extract_md(filename: str) -> Tuple[str, str, str, str, List[str], str]:
    with open(filename, "r", encoding="UTF-8") as fp:
        line = fp.readline()
        # 跳过第一行
        while line:
            line = fp.readline()
            if line.startswith('--'):
                break
            print(line)
            k, v = line.split(":", 1)
            k, v = k.strip(), v.strip()
            if k == "title":
                title = v.replace('"', '')
            if k == "date":
                date = v.replace('+08:00', '').strip()
            if k == "categories":
                category = v
            if k == "tags":
                tags = v.replace('[', '').replace(']', '').split(',')
        body = fp.read()
        # 将 {% post_link 2020-01-01-xxxxx nnnnn %} 修改为 [nnnnn](/note/2020/1/1/2020-01-01-xxxxx.html)
        inner_link_pattern = re.compile(
            r'\{\%[ ]*post_link[ ]+(\d{4})-(\d{2})-(\d{2})-([^ ]+)[ ]+([^ ]+|"[^"]+")[ ]*\%\}')

        def _convert(matched):
            _yyyy = matched.group(1)
            _mm = matched.group(2)
            _dd = matched.group(3)
            _filename = matched.group(4)
            _title = matched.group(5).strip('"')
            return f"[{_title}](/note/{int(_yyyy)}/{int(_mm)}/{int(_dd)}/{_yyyy}-{_mm}-{_dd}-{_filename}.html)"
        body = inner_link_pattern.sub(_convert, body)

        # 将{% post_path 2021-06-01-python-packages %}#pyftpdlib
        # 修改为 /note/2021/6/1/2021-06-01-python-packages.html#pyftpdlib
        inner_link_pattern2 = re.compile(
            r'\{\%[ ]*post_path[ ]+(\d{4})-(\d{2})-(\d{2})-([^ ]+)[ ]*\%\}#([^ ]+)')

        def _convert2(matched):
            _yyyy = matched.group(1)
            _mm = matched.group(2)
            _dd = matched.group(3)
            _filename = matched.group(4)
            _anchor = matched.group(5)
            return f"/note/{int(_yyyy)}/{int(_mm)}/{int(_dd)}/{_yyyy}-{_mm}-{_dd}-{_filename}.html#{_anchor}"
        body = inner_link_pattern2.sub(_convert2, body)

    return os.path.basename(filename), title, date, category, tags, body


def get_or_create_category(category: str) -> int:
    """获取分类的ID，若分类不存在则创建"""
    cat = Category.objects.get_or_create(name=category)
    return cat[0].id


def get_or_create_tag(tag: str) -> int:
    """获取标签的ID，若不存在则创建"""
    t = Tag.objects.get_or_create(name=tag)
    return t[0].id


def insert_into_db(filename: str, title: str, date: str, category: str, tags: List[str], body: str) -> None:
    pub_time = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    last_mod_time = pub_time
    # 获取category_id
    cat = Category.objects.get_or_create(name=category.strip())
    category_id = cat[0].id
    n = Note(file_name=os.path.splitext(filename)[0], last_mod_time=last_mod_time, pub_time=pub_time,
             title=title, body=body, status='p', category_id=category_id
             )
    n.save()
    for tag in tags:
        tag_name = tag.strip()
        t = Tag.objects.get_or_create(name=tag_name)
        n.tags.add(t[0])


if __name__ == "__main__":
    file_list = glob.glob(os.path.join(sys.argv[1], "**"), recursive=True)
    file_list = sorted(file_list, key=lambda fn: os.path.basename(fn))
    for f in file_list:
        if f.endswith(".md") or f.endswith(".markdown"):
            k = extract_md(f)
            print(k)
            insert_into_db(*k)
