from django.views.generic import ListView, CreateView, \
    UpdateView, DeleteView, TemplateView, DetailView


class IndexView(TemplateView):
    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
            context = super(IndexView, self).get_context_data(**kwargs)
            context['page_title'] = u'欢迎'
            return context