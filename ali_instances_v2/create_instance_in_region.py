from itertools import product
import math
import threading
from typing import List


from loguru import logger

from ali_instances_v2.aliyun_provider.client_factory import AliyunClient
from ali_instances_v2.aliyun_provider.instance import create_instances_in_zone
from ali_instances_v2.infra_builder.interface import IEcsClient
from host_spec import HostSpec

from .region_create_manager import RegionCreateManager

from .types import RegionInfo, InstanceConfig, InstanceType
    
            
    
def create_instances_in_region(client: IEcsClient, cfg: InstanceConfig, region_info: RegionInfo, instance_types: List[InstanceType], nodes: int):
    mgr = RegionCreateManager(region_info.id, nodes)
    thread1 = threading.Thread(target=mgr.describe_instances_loop, args=(client,))
    thread1.start()
    thread2 = threading.Thread(target=mgr.wait_for_ssh_loop)
    thread2.start()

    
    # TODO: 使用 stock 询价方式确定 default type?
    default_instance_type = instance_types[0]
    amount = math.ceil(nodes / default_instance_type.nodes)
    _try_create_in_single_zone(client, mgr, cfg, region_info, default_instance_type, amount)
    
    
    # 排列组合所有区域，可以在这里配置更复杂的尝试策略
    zone_plan = product(instance_types, region_info.zones.values())
    
    instance_type, zone_info = next(zone_plan)
    
    while True:
        rest_nodes = mgr.get_rest_nodes()
        if rest_nodes <= 0:
            logger.success(f"Region {region_info.id} launch complete")
            return _make_host_spec(mgr, region_info)
            
        instance_ids = client.create_instances_in_zone(cfg, region_info, zone_info, instance_type, amount, allow_partial_success=True)
        if len(instance_ids) < amount:
            # 当前实例组合可用已经耗尽，尝试下一组
            try:
                instance_type, zone_info = next(zone_plan)
            except StopIteration:
                # 全部实例组合耗尽
                break
    
    # 如果全部实例组合耗尽，会到达这里
    rest_nodes = mgr.get_rest_nodes(wait_for_pendings=True)
    if rest_nodes > 0:
        logger.error(f"Cannot launch enough nodes, request {nodes}, actual {mgr.ready_nodes}")
        
    return _make_host_spec(mgr, region_info)
            
def _make_host_spec(mgr: RegionCreateManager, region_info: RegionInfo):
    ready_instances = mgr.copy_ready_instances()
    return [HostSpec(ip=ip, 
                     nodes_per_host=instance.type.nodes, 
                     ssh_user="root", 
                     ssh_key_path=region_info.key_path, 
                     provider = "aliyun",
                     region=region_info.id, 
                     instance_id=instance.instance_id)
            for (instance, ip) in ready_instances]
    
def _try_create_in_single_zone(client: IEcsClient, mgr: RegionCreateManager, cfg: InstanceConfig, region_info: RegionInfo, instance_type: InstanceType, amount: int):
    for zone_info in region_info.zones.values():
        ids = client.create_instances_in_zone(cfg, region_info, zone_info, instance_type, amount)
        if len(ids) == 0:
            continue
        elif len(ids) < amount:
            # TODO: 关闭部分成功的 instance?
            logger.warning(f"Only partial create instance success, even if minimum required ({region_info.id}/{zone_info.id})")
        else:
            mgr.submit_pending_instances(ids, instance_type)
            # 无论这些实例是否都成功，不会再走 create_in_single_zone 的逻辑
            return