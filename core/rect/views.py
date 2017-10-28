# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.generic import TemplateView


class ConfidenceView(TemplateView):
    template_name = "rect/confidence.html"

    def get_context_data(self, **kwargs):
            context = super(ConfidenceView, self).get_context_data(**kwargs)
            context['page_title'] = u'切分图列表'
            return context


def detail(request, rect_id):
    return render(request, "rect/detail.html", {'page_id': rect_id, 'page_title': '切分区域校对'})
