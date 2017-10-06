from django.test import TestCase
import os
from lqcharacter import settings
from core.models import Page
from lib.arrange_rect import ArrangeRect



class SimpleTest(TestCase):
    fixtures = [os.path.join(settings.BASE_DIR, 'fixtures/core_fixture.json')]

    def test_basic_rect_ops(self):
        """
        Tests .
        """
        page = Page.objects.first()
        page.rebuild_rect()
        n1 = page.rects.order_by('x').first()
        print(n1.line_no)
        page.reformat_rects()
        n1.refresh_from_db()
        print(n1.op)
        self.assertTrue(n1.op == 0 and n1.line_no == 12)
        n2 = page.rects.order_by('-x')[88]
        print(n2.line_no)
        self.assertEqual(n2.line_no, 7)
        n2 = page.rects.order_by('x').first()
        print(n2.id)
        self.assertTrue(n1.x == n2.x)

    def test_rect_resort(self):
        """
        Tests .
        """
        page = Page.objects.first()
        page.rebuild_rect()
        columns1, column_len1 = ArrangeRect.resort_rects_from_base64(page)
        columns2, column_len2 = ArrangeRect.resort_rects_from_qs(page.rects.all())
        for x in range(len(columns1)):
            self.assertTrue(len(columns1[x + 1]) == len(columns2[x + 1]))
        self.assertEqual(page.rects.all().count(), 171, "页总数应是171")

    def _test_output_all_annotation(self):
        for page in Page.objects.all():
            columns, column_len = ArrangeRect.resort_rects_from_base64(page)
            page.make_annotate(columns)

    def _test_split_cols(self):
        page = Page.objects.first()
        columns = ArrangeRect.resort_rects_from_base64(page)
        page.make_annotate(columns)
