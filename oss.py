import oss2
import os

auth = oss2.Auth(os.environ.get('OSS_API_KEY', 'key'), os.environ.get('OSS_API_SECRET', 'pass'))
bucket = oss2.Bucket(auth, 'oss-cn-shanghai.aliyuncs.com', 'tripitaka')


def get_oss_by_name(image_name):
    file_name_list = image_name.split("-")[0].split("_")
    return 'lqhansp/' + "/".join(file_name_list) + "/" + image_name


def UploadImage(local_path):
    filelist = os.listdir(local_path)
    for file_ele in filelist:
        if file_ele.split(".")[-1] == 'jpg':
            bucket.put_object_from_file(get_oss_by_name(file_ele), local_path + file_ele)
