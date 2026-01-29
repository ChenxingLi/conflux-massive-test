from dataclasses import dataclass

DEFAULT_VPC_CIDR = "10.0.0.0/16"

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