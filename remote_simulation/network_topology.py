from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple

from loguru import logger

from remote_simulation.remote_node import RemoteNode


@dataclass
class NetworkTopology:
    """网络拓扑数据结构"""
    # 节点索引 -> 对等节点索引列表
    peers: Dict[int, Dict[int, int]] = field(default_factory=dict)

    @classmethod
    def generate_random_topology(cls, num_nodes: int, sample: int = 3, latency_min: int = 0, latency_max: int = 300) -> 'NetworkTopology':
        return TopologyGenerator(num_nodes, sample, latency_min, latency_max)._generate()
    
    def add_connection(self, from_node: int, to_node: int, latency: int) -> None:
        """添加一条双向连接"""
        # 添加对等关系
        if from_node not in self.peers:
            self.peers[from_node] = dict()
            
        if to_node not in self.peers:
            self.peers[to_node] = dict()

        # 避免重复连接
        if to_node in self.peers[from_node] or from_node in self.peers[to_node]:
            return
        
        # 设置双向延迟
        self.peers[from_node][to_node] = latency
        self.peers[to_node][from_node] = latency

    def get_peers(self, node_idx:int) -> Set[int]:
        return set(self.peers.get(node_idx, dict()).keys())
    
    def get_peers_with_latency(self, node_idx:int) -> List[Tuple[int, int]]:
        return list(self.peers.get(node_idx, dict()).items())


import random
from typing import List


class TopologyGenerator:
    """网络拓扑生成器"""
    
    def __init__(
        self,
        num_nodes: int,
        sample: int = 3,
        latency_min: int = 0,
        latency_max: int = 300
    ):
        """
        Args:
            num_nodes: 节点总数
            sample: 每个节点的目标出站连接数
            latency_min: 最小延迟（毫秒）
            latency_max: 最大延迟（毫秒）
        """
        self.num_nodes = num_nodes
        self.sample = min(num_nodes - 1, sample)
        self.latency_min = latency_min
        self.latency_max = latency_max

    def _generate(self) -> NetworkTopology:
        """
        生成网络拓扑
        
        策略：
        1. 建立环形连接（保证全连通）
        2. 随机添加额外连接（增强鲁棒性）
        
        Returns:
            NetworkTopology: 生成的网络拓扑
        """
        topology = NetworkTopology()

        logger.info(f"Generate topology, nodes {self.num_nodes}, peers {self.sample}, latency {self.latency_min} ~ {self.latency_max} ms")
        
        # 第一步：建立环形基础拓扑
        self._create_ring_topology(topology)
        
        # 第二步：添加随机连接
        self._add_random_connections(topology)
        
        return topology
    
    def _create_ring_topology(self, topology: NetworkTopology) -> None:
        """建立环形拓扑，确保网络连通性"""
        for i in range(self.num_nodes):
            next_node = (i + 1) % self.num_nodes
            latency = random.randint(self.latency_min, self.latency_max)
            topology.add_connection(i, next_node, latency)
    
        
    def _add_random_connections(self, topology: NetworkTopology) -> None:
        """为节点添加随机对等连接"""
        for node_idx in range(self.num_nodes):
            # 已经有1个环形连接，再添加 (sample - 1) 个
           self._add_random_connections_for_node(topology, node_idx)
    

    def _add_random_connections_for_node(self, topology: NetworkTopology, node_idx: int) -> None:
        """为每个节点添加随机对等连接"""
        # 已经有1个环形连接，再添加 (sample - 1) 个
        current_peers = topology.get_peers(node_idx)
        
        for _ in range(self.sample - len(current_peers)):
            peer = self._select_random_peer(node_idx, current_peers)
            if peer is None:
                logger.debug(f"Early return with not enough peers {len(current_peers)} < {self.sample}")
                return
            latency = random.randint(self.latency_min, self.latency_max)
            topology.add_connection(node_idx, peer, latency)
            current_peers.add(peer)
    
    def _select_random_peer(
        self, 
        node_idx: int, 
        existing_peers: set[int]
    ) -> int | None:
        """随机选择一个可用的对等节点"""
        available = [
            i for i in range(self.num_nodes)
            if i != node_idx and i not in existing_peers
        ]
        return random.choice(available) if available else None
