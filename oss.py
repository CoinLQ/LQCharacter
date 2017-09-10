import oss2
import os
from .core.models import Page, CutBatchOP,BatchVersion

def put_json_into_db(batch_version, json_path):
    data_list = []
    for json_file in os.listdir(json_path):
        if json_file.split(".")[-1] == 'base64':
            with open(json_path + '/' + json_file) as json_data:
                p = Page(batch_version= batch_version, image = json_file.split(".")[0]+".jpg")
                c = CutBatchOP(page=p,cut_data=json_data)
                data_list.append(c)
    CutBatchOP.objects.bulk_create(data_list)

def UploadImage(local_path):
    auth = oss2.Auth('LTAIyXhhTQhZUhBW', 'x6jpClbi6gnqMGspFZOPEszCaTB30o')
    bucket = oss2.Bucket(auth, 'oss-cn-shanghai.aliyuncs.com', 'tripitaka')
    filelist = os.listdir(local_path)
    for file_ele in filelist:
        if file_ele.split(".")[-1] is 'jpg':
            bucket.put_object_from_file('lqhansp/' + file_ele, local_path + file_ele)

def batch_import(self, local_path, request):
    os.system("ruby /home/buddhist/AI/QIEZI/process.rb " + local_path)
    b = BatchVersion(des="batch_v_1", organiztion='lqs')
    b.save()
    put_json_into_db(b, local_path)
    UploadImage(local_path)
    #'K0001_110-0.jpg', '/data/share/dzj_characters/images/K0001_110-0.jpg'

local_path = '/data/share/dzj_characters/images/'

batch_import(local_path)
