# #TOKEN_CONTRACTS = [
#     "0x3C1d826b43b6a7B7E077bcfDB6E68e1D3fC9bcc5",  # 代币合约地址1
#     "0x4e0dEBF0c8795A7861A64Df7F136f989921d0247",  # 代币合约地址2
#     "0x18c31CbfF3E717c3BEC29AAfF613b9987e7d73a8",   # 代币合约地址3
#     "0x11bf51dE22429AEA0fBED3adc255548Cdcd40Ef0",
#     "0x3C1d826b43b6a7B7E077bcfDB6E68e1D3fC9bcc5",
#     "0x3940Db8B5D08eE9Abd8507c3D71eFcA522ACee6f",
#     "0x354835899dA3f5D5d33E4eE899473805a7b6C69d",
#     "0xBf4Db8b7A679F89Ef38125d5F84dd1446AF2ea3B",
#     "0xFA1306D0778A18C9cd1b4d969C7090ce72f93EE4",
    
# ]
from web3 import Web3
import pandas as pd
from collections import defaultdict

# 设置 Base 链的 RPC 节点
RPC_URL = "https://mainnet.base.org"
web3 = Web3(Web3.HTTPProvider(RPC_URL))

# 配置代币合约地址列表（Base 链上的目标代币地址）
TOKEN_CONTRACTS = [
    "0x3C1d826b43b6a7B7E077bcfDB6E68e1D3fC9bcc5",  # 代币合约地址1
    "0x4e0dEBF0c8795A7861A64Df7F136f989921d0247",  # 代币合约地址2
    "0x18c31CbfF3E717c3BEC29AAfF613b9987e7d73a8",   # 代币合约地址3
    "0x11bf51dE22429AEA0fBED3adc255548Cdcd40Ef0",
    "0x3C1d826b43b6a7B7E077bcfDB6E68e1D3fC9bcc5",
    "0x3940Db8B5D08eE9Abd8507c3D71eFcA522ACee6f",
    "0x354835899dA3f5D5d33E4eE899473805a7b6C69d",
    "0xBf4Db8b7A679F89Ef38125d5F84dd1446AF2ea3B",
    "0xFA1306D0778A18C9cd1b4d969C7090ce72f93EE4",
    
]

def fetch_transfer_events(token_address, start_block, end_block):
    try:
        print(f"开始获取代币 {token_address} 的 Transfer 事件日志...")
        token_address = Web3.to_checksum_address(token_address)
        print(f"Checksum 地址: {token_address}")

        # 生成正确的 Transfer 事件主题哈希（确保带有 0x 前缀）
        transfer_topic = "0x" + Web3.keccak(text="Transfer(address,address,uint256)").hex()
        print(f"生成的 Transfer 事件主题哈希: {transfer_topic}")  # 调试输出

        filter_params = {
            "fromBlock": start_block,
            "toBlock": end_block,
            "address": token_address,
            "topics": [transfer_topic]
        }

        print(f"Filter 参数: {filter_params}")
        logs = web3.eth.get_logs(filter_params)
        print(f"获取到日志数量: {len(logs)}")

        addresses = set()
        for log in logs:
            topics = log["topics"]
            if len(topics) >= 3:
                from_address = Web3.to_checksum_address("0x" + topics[1].hex()[26:])
                to_address = Web3.to_checksum_address("0x" + topics[2].hex()[26:])
                addresses.add(from_address)
                addresses.add(to_address)
        print(f"提取到地址数量: {len(addresses)}")
        return addresses

    except Exception as e:
        print(f"获取代币 {token_address} 的地址时发生错误: {e}")
        return set()

# 主函数
def main():
    # 确保 RPC 节点连接成功
    if not web3.is_connected():
        print("无法连接到 Base 链的 RPC 节点，请检查 RPC URL 是否正确。")
        return

    # 打印当前区块高度
    latest_block = web3.eth.block_number
    print(f"当前链上最新区块高度: {latest_block}")

    # 设置查询区块范围
    start_block = latest_block - 5000  # 从最近的5000个区块开始
    end_block = latest_block          # 到最新区块

    print(f"查询区块范围: {start_block} 到 {end_block}")

    # 存储每个代币的交互地址
    token_interactions = defaultdict(set)

    for token in TOKEN_CONTRACTS:
        print(f"正在获取代币 {token} 的交互地址...")
        token_interactions[token] = fetch_transfer_events(token, start_block, end_block)

    # 找出同时交互的地址
    if len(token_interactions) > 1:
        common_addresses = set.intersection(*token_interactions.values())
        print(f"同时交互的地址数量: {len(common_addresses)}")
    else:
        common_addresses = set()
        print("没有足够的数据进行交集运算。")

    # 保存结果到文件
    if common_addresses:
        df = pd.DataFrame(common_addresses, columns=["Wallet Address"])
        df.to_csv("common_wallets.csv", index=False)
        print("结果已保存到 common_wallets.csv")
    else:
        print("没有找到同时交互的钱包地址。")

if __name__ == "__main__":
    main()