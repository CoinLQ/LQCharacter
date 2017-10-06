# LQCharacter

[![python](https://img.shields.io/badge/python-3.5-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-v1.11-orange.svg)](https://www.djangoproject.com/)
[![Build Status](https://travis-ci.org/CoinLQ/LQCharacter.svg?branch=master)](https://travis-ci.org/CoinLQ/LQCharacter)
[![codecov](https://codecov.io/gh/CoinLQ/AnyCollating/branch/master/graph/badge.svg)](https://codecov.io/gh/CoinLQ/AnyCollating)
[![license-BSD](https://img.shields.io/badge/license-BSD-green.svg)](LICENSE)


切分与识别

## 安装环境搭建
基本思路是通过virtualenvwrapper在本地创建一个独立的env环境，用docker-compose来启用一些项目所需的容器服务，比如mysql，redis等等。并将端口映射到本地。

### 安装 python3
略
### 安装 virtualenvwrapper及启用环境下的pip

```
cd /tmp
wget https://bootstrap.pypa.io/get-pip.py
python get-pip.py
```
```
pip install virtualenvwrapper
mkvirtualenv character --python=python3
```
### 安装python依赖包
```
  workon character
  pip install -r requirements.txt
  pip install https://github.com/CoinLQ/xadmin/archive/master.zip
  pip install https://github.com/CoinLQ/db_file_storage/archive/master.zip
```
### 安装docker-compose
略
### 启动docker
```
docker-compose up -d
```
### 加载测试数据
```
  python manage.py makemigrations
  python manage.py migrate
  python manage.py loaddata ./fixtures/core_fixture.json
```
### 应用环境设置(可能)
把下列环境变量加入你的rc文件中，
```
export OSS_API_KEY=<input>
export OSS_API_SECRET=<input>
```
###
### 启动应用
```
  python manage.py runserver
```
### 本地测试
```
DJANGO_SETTINGS_MODULE=lqcharacter.ci_settings coverage run manage.py test
```
