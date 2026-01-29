from pydantic import BaseModel
from typing import List

import tomllib


class Region(BaseModel):
    name: str
    count: int

class CandidateInstanceType(BaseModel):
    name: str
    nodes: int

class CloudRequestConfig(BaseModel):
    provider: str
    default_user_name: str
    user_tag: str
    image_name: str
    ssh_key_path: str
    regions: List[Region] = []
    instance_types: List[CandidateInstanceType] = []

class RequestConfig(BaseModel):
    aliyun: CloudRequestConfig
    aws: CloudRequestConfig

if __name__=="__main__":
    with open("request_config.toml", "rb") as f:
        data = tomllib.load(f)
    print(RequestConfig(**data))