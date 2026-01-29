from dataclasses import dataclass
from typing import Dict, Set

from ali_instances_v2.infra_builder.crypto import get_fingerprint_from_key, get_public_key_body


@dataclass
class InstanceStatus:
    running_instances: Dict[str, str]
    pending_instances: Set[str]
    
@dataclass
class KeyPairRequestConfig:
    key_path: str
    key_pair_name: str
    
    @property
    def finger_print(self):
        return get_fingerprint_from_key(self.key_path, "md5")
        
    @property
    def public_key(self):
        return get_public_key_body(self.key_path)

@dataclass
class ImageInfo:
    image_id: str
    image_name: str
    
@dataclass
class KeyPairInfo:
    finger_print: str
    
    
@dataclass
class SecurityGroupInfo:
    security_group_id: str
    security_group_name: str
    
    
@dataclass
class VSwitchInfo:
    v_switch_id: str
    v_switch_name: str
    zone_id: str
    cidr_block: str
    status: str
    
    
@dataclass
class VpcInfo:
    vpc_id: str
    vpc_name: str