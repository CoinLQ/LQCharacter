import time
import functools
from django.core.cache import cache
from django.contrib.contenttypes.models import ContentType



class RedisKey(object):
    RETRIEVE_RECT = 'retrieve_rect'
    RETRIEVE_RECT_P2 = 'retrieve_rect_p2'
    OCCUPANCY_TIMEOUT = 2 * 3600

    RETRIEVE_SPLTASK = 'retrieve_spl_task'
    TASK_OCCUPANCY_TIMEOUT = 6 * 24 * 3600


def task_id(user_id):
    cache_key = "%s:u%s" % (RedisKey.RETRIEVE_SPLTASK, user_id)
    return cache.get(cache_key)


def page_id(user_id):
    cache_key = "%s:u%s" % (RedisKey.RETRIEVE_RECT, user_id)
    return cache.get(cache_key)


def timeit(method):
    @functools.wraps(method)
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        print("%r (%r, %r) %2.2f sec" % (method.__name__, args, kw, te - ts))
        return result

    return timed


def retrieve_rects(user):
    """
    尝试从cache获取未超时的page，page已被处理完，重新取page
    cache超时，重新取page，以前的page如未处理完，在某个时间点统一释放
    """
    user_id = user.id
    rects = ()
    cache_key = "%s:u%s" % (RedisKey.RETRIEVE_RECT, user_id)
    page_klass = ContentType.objects.get(app_label='core', model='page').model_class()
    page_id = cache.get(cache_key)
    if not page_id:
        page = obtain_rect()
    else:
        page = page_klass.objects.get(pk=page_id)
        rects = page.rects.filter(op=0).all()
        if ((not rects) or (page.locked > 1)):
            page = obtain_rect()

    if page:
        cache.set(cache_key, str(page.id), timeout=RedisKey.OCCUPANCY_TIMEOUT)
        rects = page.rects.filter(op=0).all()

    image_url = page and page.get_image_url
    return page.rects.all(), image_url


def obtain_rect():
    """
    取一个未锁定的页，有可能返回空值,
    取得后临时锁定为1；
    当完全处理完毕，locked改为2，表示rects都已被处理。
    否则被重置为0。第二天重新被处理
    """
    page_klass = ContentType.objects.get(app_label='core', model='page').model_class()
    with cache.lock(RedisKey.RETRIEVE_RECT):
        page = page_klass.objects.filter(locked=0).all().first()
        if page:
            page.locked = 1
            page.save()
    return page


def clear_retrieve_rect_keys():
    cache.delete_pattern("%s:*" % RedisKey.RETRIEVE_RECT)
    page_klass = ContentType.objects.get(app_label='core', model='page').model_class()
    page_klass.objects.filter(locked=1).update(locked=0)

#  ##########


def retrieve_split_task(user):
    user_id = user.id
    rects = ()
    cache_key = "%s:u%s" % (RedisKey.RETRIEVE_SPLTASK, user_id)
    splittask_klass = ContentType.objects.get(app_label='core', model='splittask').model_class()
    splittask_id = cache.get(cache_key)
    if not splittask_id:
        task = obtain_split_task(user)
    else:
        task = splittask_klass.objects.get(pk=splittask_id)
        rects = task.rects.filter(op=0).all()
        if ((not rects) or (task.locked > 1)):
            task = obtain_split_task(user)

    if task:
        cache.set(cache_key, str(task.id), timeout=RedisKey.TASK_OCCUPANCY_TIMEOUT)
        rects = task.rects.filter(op=0).all()

    return rects


def obtain_split_task(user):
    splittask_klass = ContentType.objects.get(app_label='core', model='splittask').model_class()
    with cache.lock(RedisKey.RETRIEVE_SPLTASK):
        splittask = splittask_klass.objects.filter(locked=0).order_by('confidence').first()
        if splittask:
            splittask.locked = 1
            splittask.owner = user
            splittask.save()
    return splittask

