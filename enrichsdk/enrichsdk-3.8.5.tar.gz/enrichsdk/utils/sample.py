import os
import sys
import json
import s3fs


def s3_sample_crawl(root, depth=3, ext="json"):

    s3 = s3fs.S3FileSystem(anon=False)

    prefix = root.replace("s3://", "")
    print("Crawling")
    for subroot, dirs, files in s3.walk(root, maxdepth=depth):
        relpath = os.path.relpath(subroot, start=prefix)
        if len(files) > 0:
            print(relpath)
        for f in files[:3]:
            basename = os.path.basename(f)
            print("  ", basename, ":", os.path.join("s3://", subroot, f))


def s3_sample_cat(path):

    s3 = s3fs.S3FileSystem(anon=False)
    content = s3.cat(path)
    content = content.decode("utf-8")
    print(content)


def sample_cat(path):

    s3 = s3fs.S3FileSystem(anon=False)

    if path.startswith("s3://"):
        if "AWS_PROFILE" not in os.environ:
            print("Please define AWS_PROFILE")
            return
        return s3_sample_cat(path)
    else:
        print("Unknown root. Only s3://<path> is supported for now")


def sample_crawl(root, ext):

    if root.startswith("s3://"):
        if "AWS_PROFILE" not in os.environ:
            print("Please define AWS_PROFILE")
            return
        return s3_sample_crawl(root=root, ext=ext)
    else:
        print("Unknown root. Only s3://<path> is supported for now")
