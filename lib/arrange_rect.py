import base64
import simplejson as json
import numpy as np
from dotmap import DotMap


class ArrangeRect(object):
    @classmethod
    def resort_rects_from_base64(cls, page):
        json_str = base64.b64decode(page.c_page.first().cut_data)
        cut_result = json.loads(json_str.decode('utf-8'))
        cut_result = list(filter(lambda m: int(m['width'])> 0 and int(m['height']) > 0, cut_result))
        cut_result = list(filter(lambda Y: Y['op'] != 3, cut_result))
        columns, m = dict(), 0
        column_len = dict()
        mean_width = int(np.mean(list(map(lambda X: int(X['width']), cut_result))))
        while cut_result:
            m = m + 1
            columns[m] = cls._pick_one_column(cut_result, mean_width)
            column_len[m] = len(columns[m])
        return columns, column_len

    @classmethod
    def resort_rects_from_qs(cls, queryset):
        cut_result = list(dict(qs) for qs in queryset)
        if not cut_result:
            mean_width = 0
        else:
            mean_width = int(np.mean(list(map(lambda X: int(X['width']), cut_result))))
        columns, m = dict(), 0
        column_len = dict()
        while cut_result:
            m = m + 1
            columns[m] = cls._pick_one_column(cut_result, mean_width)
            column_len[m] = len(columns[m])
        return columns, column_len

    @classmethod
    def _pick_rtop_rectangle(cls, rects, height, width):
        x1 = max(map(lambda Y: int(Y['x']), rects))
        return {'x': x1, 'y': 0, 'width': width, 'height': height}

    @staticmethod
    def _intersects_with(_rect1, _rect2):
        rect1, rect2 = DotMap(_rect1), DotMap(_rect2)
        if (rect2.x < rect1.x + int(rect1.width) and rect1.x < rect2.x + int(rect2.width) and
            rect2.y <= rect1.y + int(rect1.height)):
            return rect1.y <= rect2.y + int(rect2.height)
        else:
            return False

    @staticmethod
    def _inside_with(_large_rect, _rect2):
        _large_rect, rect2 = DotMap(_large_rect), DotMap(_rect2)
        if (_large_rect.x <= rect2.x) and (_large_rect.x + _large_rect.width >= rect2.x + rect2.width) and \
                (_large_rect.y <= rect2.y) and (_large_rect.y + _large_rect.height >= rect2.y + rect2.height):
                return True
        else:
                return False


    @staticmethod
    def dequefilter(_rects, condition):
        _col_rect = list()
        for _ in range(len(_rects)):
            item = _rects.pop()
            if not condition(item):
                _rects.insert(0, item)
            else:
                _col_rect.append(item)
        return _col_rect

    @staticmethod
    def intersect_with(rect):
        def inner_func(rect2):
            return ArrangeRect._intersects_with(rect, rect2)
        return inner_func

    @staticmethod
    def inside_with(rect):
        def inner_func(rect2):
            return ArrangeRect._inside_with(rect, rect2)
        return inner_func

    @classmethod
    def _pick_one_column(cls, cut_result, mean_width):
        max_height = max(map(lambda Y: int(Y['y']) + int(Y['height']), cut_result))
        mean_width = int(np.mean(list(map(lambda X: int(X['width']), cut_result))))
        _rect = ArrangeRect._pick_rtop_rectangle(cut_result, max_height, mean_width)
        col_rect = ArrangeRect.dequefilter(cut_result, ArrangeRect.intersect_with(_rect))
        if not col_rect:
            col_rect = ArrangeRect.dequefilter(cut_result, ArrangeRect.inside_with(_rect))
            print("Hint: inner case!")
        return sorted(col_rect, key=lambda Y: int(Y['y']))
