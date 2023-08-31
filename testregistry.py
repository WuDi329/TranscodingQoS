from node.noderegistry import NodeRegistry
import asyncio

def main():
    # 创建节点注册表对象
    registry = NodeRegistry(zk_hosts="49.52.27.50:2181", node_path="/nodes")

    # 启动节点注册表
    registry.start()

    # 注册节点
    registry.register_node("node1", b"node1_data")
    registry.register_node("node2", b"node2_data")

    # 发现节点
    nodes = registry.discover_nodes()
    print("Discovered nodes:", nodes)

    # 注销节点
    registry.unregister_node("node1")
    registry.unregister_node("node2")

    # 停止节点注册表
    registry.stop()

main()