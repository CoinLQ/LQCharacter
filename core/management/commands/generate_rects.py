from django.core.management.base import BaseCommand
from core.models import Page


class Command(BaseCommand):
    def handle(self, *args, **options):
        for page in Page.objects.all():
            if len(page.rects.all()) == 0:
                print(page.id)
                page.rebuild_rect()
                page.reformat_rects()

