import asyncio
from kazoo.client import KazooClient

class NodeRegistry:
    """
        节点注册表，用于存储节点的信息。

    """
    def __init__(self, zk_hosts: str, node_path: str):
        self.zk = KazooClient(hosts=zk_hosts)
        self.node_path = node_path

    def start(self) -> int:
        """
            启动节点注册表。

        """
        self.zk.start()

    def stop(self) -> None:
        """
            停止节点注册表。

        """
        self.zk.stop()
    
    def register_node(self, node_id: str, node_data: bytes) -> None:
        """
            注册节点。
        """
        node_path = f"{self.node_path}/{node_id}"
        self.zk.ensure_path(node_path)
        self.zk.set(node_path, node_data)
    
    def unregister_node(self, node_id: str) -> None:
        """
            注销节点。

        """
        node_path = f"{self.node_path}/{node_id}"
        self.zk.delete(node_path)

    def discover_nodes(self) -> list:
        """
            发现所有节点。

        """
        node_ids =  self.zk.get_children(self.node_path)
        nodes = []
        for node_id in node_ids:
            node_path = f"{self.node_path}/{node_id}"
            node_data, _ = self.zk.get(node_path)
            nodes.append((node_id, node_data))
        return nodes
    