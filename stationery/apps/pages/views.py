from django.views.generic import DetailView, TemplateView

from pages.models import Page


class IndexView(TemplateView):
    template_name = 'pages/index.html'


class PageView(DetailView):
    model = Page
    template_name = 'pages/static.html'
