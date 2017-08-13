FROM python:2.7

MAINTAINER guoweikuang "guoweikuang2015@gmail.com"


ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple django==1.8.4
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pygments
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple markdown2
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple dj-static 
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple whitenoise
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pytz
ADD . /code/


