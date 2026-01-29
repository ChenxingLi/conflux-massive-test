from dataclasses import dataclass
from typing import List
from alibabacloud_ecs20140526.models import DescribeVpcsResponseBodyVpcsVpc, DescribeVpcsRequest, CreateVpcRequest

from ali_instances_v2.client_factory import ClientFactory
from ali_instances_v2.infra_builder.types import VpcInfo, DEFAULT_VPC_CIDR
from utils.wait_until import wait_until
    
def as_vpc_info(rep: DescribeVpcsResponseBodyVpcsVpc):
    assert type(rep.vpc_id) is str
    assert type(rep.vpc_name) is str
    assert type(rep.status) is str
    
    return VpcInfo(vpc_id=rep.vpc_id, vpc_name=rep.vpc_name)

def get_vpcs_in_region(c: ClientFactory, region_id: str) -> List[VpcInfo]:
    client = c.build(region_id)

    result = []
    
    page_number = 1
    while True:
        rep = client.describe_vpcs(DescribeVpcsRequest(region_id=region_id, page_number=page_number, page_size=50))
        result.extend([as_vpc_info(vpc) for vpc in rep.body.vpcs.vpc])
        if rep.body.total_count <= page_number * 50:
            break
        page_number += 1
    
    return result


def create_vpc(c: ClientFactory, region_id: str, vpc_name: str, cidr_block: str = DEFAULT_VPC_CIDR):
    client = c.build(region_id)
    rep = client.create_vpc(CreateVpcRequest(region_id=region_id, vpc_name=vpc_name, cidr_block=cidr_block))
    vpc_id = rep.body.vpc_id
    
    assert type(vpc_id) is str
    
    def _available() -> bool:
        resp = client.describe_vpcs(DescribeVpcsRequest(region_id=region_id, vpc_id=vpc_id))
        vpcs = resp.body.vpcs.vpc 
        return len(vpcs) > 0 and vpcs[0].status == "Available"
    
    wait_until(_available, timeout=120, retry_interval=3)
    
    return vpc_id
    