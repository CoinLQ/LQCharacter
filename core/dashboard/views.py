from django.views.generic import ListView, CreateView, \
    UpdateView, DeleteView, TemplateView, DetailView
from django.shortcuts import render

class IndexView(TemplateView):
    template_name = "dashboard/index.html"

def detail(request, page_id):
    return render(request,"dashboard/index.html",{'page_id': page_id})
