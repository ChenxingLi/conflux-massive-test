#!/usr/bin/env python3
import pickle
from typing import List

from remote_simulation.block_generator import generate_blocks_async
from remote_simulation.launch_conflux_node import launch_remote_nodes
from remote_simulation.network_connector import connect_nodes
from remote_simulation.network_topology import NetworkTopology
from remote_simulation.config_builder import SimulateOptions, ConfluxOptions, generate_config_file
from remote_simulation.tools import collect_logs, init_tx_gen, wait_for_nodes_synced


from loguru import logger

from utils.tempfile import TempFile
from aws_instances.launch_ec2_instances import Instances



if __name__ == "__main__":
    # 1. 启动远程服务器
    # 为了快速实验，从 pickle 文件中读取已经创建好的服务器

    with open("instances.pkl", "rb") as file:
        instances: Instances = pickle.load(file)
    
    logger.info(f"实例列表集合 {instances.ip_addresses}")
    ip_addresses: List[str] = instances.ip_addresses # pyright: ignore[reportAssignmentType]

    # 2. 生成配置
    simulation_config = SimulateOptions(target_nodes=200, nodes_per_host=2, num_blocks=200, connect_peers=8, target_tps=3000, storage_memory_gb=16, generation_period_ms=250)
    node_config = ConfluxOptions(tx_pool_size=1_000_000)

    config_file = generate_config_file(simulation_config, node_config)

    logger.success(f"完成配置文件 {config_file.path}")

    # 3. 启动节点
    nodes = launch_remote_nodes(ip_addresses, simulation_config.nodes_per_host, config_file, pull_docker_image=True)
    if len(nodes) < simulation_config.target_nodes:
        raise Exception("Not all nodes started")
    logger.success("所有节点已启动，准备连接拓扑网络")

    # 4. 手动连接网络
    topology = NetworkTopology.generate_random_topology(len(nodes), simulation_config.connect_peers)
    connect_nodes(nodes, topology)
    logger.success("拓扑网络构建完毕")
    wait_for_nodes_synced(nodes)

    # 5. 开始运行实验
    init_tx_gen(nodes, node_config.txgen_account_count)
    logger.success("开始运行区块链系统")
    generate_blocks_async(nodes, simulation_config.num_blocks, simulation_config.generation_period_ms)
    wait_for_nodes_synced(nodes)
    logger.success("测试完毕，准备采集日志数据")

    # 6. 获取结果
    logger.info(f"Node goodput: {nodes[0].rpc.test_getGoodPut()}")
    collect_logs(nodes)

    # stop_remote_nodes(ip_addresses)
    # destory_remote_nodes(ip_addresses)

