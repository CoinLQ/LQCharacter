# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = "page/index.html"

    def get_context_data(self, **kwargs):
            context = super(IndexView, self).get_context_data(**kwargs)
            context['page_title'] = u'页面列表'
            return context


def detail(request, page_id):
    return render(request, "page/detail.html", {'page_id': page_id, 'page_title': '页面校对'})
