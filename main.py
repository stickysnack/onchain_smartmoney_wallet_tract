from web3 import Web3
import pandas as pd
from collections import defaultdict

# 设置你的以太坊节点
# 替换为你自己的 Infura 或其他节点的 HTTP URL
RPC_URL = "https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID"
web3 = Web3(Web3.HTTPProvider(RPC_URL))

# 配置代币合约地址列表（替换为目标代币地址）
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

# 获取某个代币的 Transfer 事件日志
def fetch_transfer_events(token_address, start_block, end_block):
    token_contract = web3.eth.contract(address=Web3.toChecksumAddress(token_address), abi=[
        {
            "anonymous": False,
            "inputs": [
                {"indexed": True, "internalType": "address", "name": "from", "type": "address"},
                {"indexed": True, "internalType": "address", "name": "to", "type": "address"},
                {"indexed": False, "internalType": "uint256", "name": "value", "type": "uint256"}
            ],
            "name": "Transfer",
            "type": "event"
        }
    ])
    transfer_event = token_contract.events.Transfer()
    logs = transfer_event.get_logs(fromBlock=start_block, toBlock=end_block)
    addresses = set()
    for log in logs:
        addresses.add(log['args']['from'])
        addresses.add(log['args']['to'])
    return addresses

# 主函数
def main():
    start_block = 10000000  # 设置起始区块
    end_block = 10010000    # 设置结束区块（范围越大越慢）

    # 存储每个代币的交互地址
    token_interactions = defaultdict(set)

    for token in TOKEN_CONTRACTS:
        print(f"正在获取代币 {token} 的交互地址...")
        token_interactions[token] = fetch_transfer_events(token, start_block, end_block)

    # 找出同时交互的地址
    common_addresses = set.intersection(*token_interactions.values())
    print(f"同时交互的地址数量: {len(common_addresses)}")
    
    # 保存结果到文件
    if common_addresses:
        df = pd.DataFrame(common_addresses, columns=["Wallet Address"])
        df.to_csv("common_wallets.csv", index=False)
        print("结果已保存到 common_wallets.csv")

if __name__ == "__main__":
    main()