from django.views.generic import ListView, CreateView, \
    UpdateView, DeleteView, TemplateView, DetailView

class IndexView(TemplateView):
    template_name = "dashboard/index.html"
