# NONB: Not Only Note or Blog
本项目主要用来维护个人笔记，用于替代Hexo完成笔记的展示。

## 主要功能：
- 支持页面，分类，标签
- 页面支持`Markdown`，支持代码高亮
- 支持全文搜索
- 侧边栏功能，最新文章，最多阅读，标签云等

## 安装与启动
   * `pip install -r requirements.txt`
   * `python manage.py makemigrations`
   * `python manage.py migrate`
   * `python manage.py runserver`

## uwsgi部署
**注意修改路径**

```uwsgi.ini

master=True
processes=1
http=:8000
project=NONB
module=%(project).wsgi
```

执行命令：

`uwsgi --ini uwsgi.ini --static-map /static=$(pwd)/note/static`

## uwsgi+nginx部署
`uwsgi.ini`与上述一致，启动uwsgi的命令为`uwsgi --ini uwsgi.ini`。

将静态文件的处理交给nginx
```nginx.conf

        location  /static {
            alias   /root/nonb/note/static;
            try_files $uri $uri/ /index.html;
            index  index.html index.htm;

        }
        location / {
                proxy_pass http://127.0.0.1:8000;
        }

```

## systemd
使用虚拟环境的情况下，`systemd`直接使用虚拟环境中的`python`或`uwsgi`

```uwsgi.service
[Unit]
Description=uWSGI Emperor
After=syslog.target

[Service]
WorkingDirectory=/root/nonb/
ExecStart=/root/note-env/bin/uwsgi --ini /root/nonb/uwsgi.ini 
Restart=always
KillSignal=SIGQUIT
Type=notify
StandardError=syslog
NotifyAccess=all

[Install]
WantedBy=multi-user.target
```

## 数据导入
支持将基于hexo编写的`Markdown`文件导入至系统中。

# 说明
本项目在初始化时学习参考了[DjangoBlog](https://github.com/liangliangyy/DjangoBlog)并根据需要进行了裁剪。
