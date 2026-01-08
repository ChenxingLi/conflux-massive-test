from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from typing import List, Tuple

from loguru import logger

from remote_simulation import docker_cmds
from utils import shell_cmds
from utils.wait_until import wait_until

from .remote_node import RemoteNode


def check_nodes_synced(executor: ThreadPoolExecutor, nodes: List[RemoteNode]):
    def get_best_block(node: RemoteNode):
        try: 
            return node.rpc.cfx_getBestBlockHash()
        except Exception as e:
            logger.info(f"Fail to connect {node.rpc.addr}: {e}")

    best_blocks = list(executor.map(get_best_block, nodes))

    logger.debug("best blocks: {}".format(Counter(best_blocks).most_common(5)))
    
    most_common_cnt = Counter(best_blocks).most_common(1)[0][1]

    if most_common_cnt == len(nodes):
        logger.info("所有节点已同步")
        return True
    else:
        return False


def wait_for_nodes_synced(nodes: List[RemoteNode], *, max_workers: int = 300, retry_interval: int = 5, timeout: int = 120):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        wait_until(lambda: check_nodes_synced(executor, nodes), timeout=timeout, retry_interval=retry_interval)

def init_tx_gen(nodes: List[RemoteNode], txgen_account_count:int, max_workers: int = 300):
    def execute(args: Tuple[int, RemoteNode]):
        idx, node = args
        return node.init_tx_gen(idx * txgen_account_count)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(execute, enumerate(nodes))

    fail_cnt = list(results).count(False)

    if fail_cnt == len(nodes):
        logger.error(f"全部节点初始化交易生成失败")
    elif fail_cnt > 0:
        logger.warning(f"部分节点初始化交易生成失败，数量 {fail_cnt}")
    else:
        logger.success(f"全部节点初始化交易生成成功")

def _stop_node_and_collect_log(node: RemoteNode, *, local_path: str = "./logs"):
    try:
        shell_cmds.ssh(node.host, "ubuntu", docker_cmds.stop_node_and_collect_log(node.index))
        logger.debug(f"节点 {node.id} 已完成日志生成")
        shell_cmds.rsync_download(f"./output{node.index}/", f"./{local_path}/{node.id}/", node.host)

        return 0
    except Exception as e:
        logger.warning(f"节点 {node.id} 日志生成遇到问题: {e}")
        return 1
    
def collect_logs(nodes: List[RemoteNode], max_workers: int = 300):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(_stop_node_and_collect_log, nodes)
    
    fail_cnt = sum(results)