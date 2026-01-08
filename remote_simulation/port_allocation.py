
BASE_PORT = 11000

def _node_base_port(n):
    return 11000 + n * 10

def p2p_port(n=0):
    return _node_base_port(n)

def rpc_port(n=0):
    return _node_base_port(n) + 1

def remote_rpc_port(n=0):
    return _node_base_port(n) + 2

def pubsub_port(n=0):
    return _node_base_port(n) + 3

def evm_rpc_port(n=0):
    return _node_base_port(n) + 4

def evm_rpc_ws_port(n=0):
    return _node_base_port(n) + 5