from pydantic import BaseModel, Field

class DownloadTaskModel(BaseModel):
    url: str = Field(..., title="下载网址")
    path: str = Field(..., title="下载地址")
    headers: dict = Field(None, title="请求头信息")

class MergeTaskModel(BaseModel):
    filepath: str = Field(..., title="合并的文件路径")
    #  cache_dir: str = Field(..., title="缓存目录")
    merge_files: list[str] = Field(..., title="合并文件列表")

