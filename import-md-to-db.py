#!/usr/bin/env python
"""
将基于hexo的markdown文件导入到数据库中
本代码演示了如何在Django项目外使用模型
"""

import os
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
    file_list = glob.iglob(os.path.join(sys.argv[1], "**"), recursive=True)
    for f in file_list:
        if f.endswith(".md") or f.endswith(".markdown"):
            k = extract_md(f)
            print(k)
            insert_into_db(*k)
