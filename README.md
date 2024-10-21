# 签名服务器本地版

```
├── orm
│   ├── database.py  # 数据库配置文件
│   └── sol_request.py  # 用于保存请求记录的表
├── parser
│   └── sol_parser.py  # 用于解析SOL的transation，并签名
├── requirements.txt
├── router
│   └── sol.py  # 定义http路由，http请求主逻辑
├── shield
│   └── shield.py  # 用于读取本地存放私钥的文件
├── sign_server.py # 主程序入口
├── signer
│   └── client.py  # 后台请求签名服示例文件
└── tools
    └── init.py  # 用于初始化私钥，地址等
```

## 运行

### 初始化并运行

```bash
curl -fsSL https://raw.githubusercontent.com/AscentYieldPrivate/signer/refs/heads/main/first_run.sh > first_run.sh && sh first_run.sh
```

这会让你输入私钥，并将私钥加密保存在本地中，最后会让你输入币安的存钱地址和后台密码

这会启动一个本地的签名服务器，监听80端口

### 重启服务


```bash
cd signer && sh restart.sh
```

### 更新服务

```bash
cd signer && git pull && sh restart.sh
```


## 使用 Use

在后台会调用 signer.client 中的WalletForSigner去请求签名服务器

Sol的Transaction会被序列化，并发送到签名服务器，签名服务器会返回签名后的Transaction。

签名服务器内部会校验签名，详见router.sol文件。所有签名记录都会存在本地的sqlite数据库中。


# Signature Server - Local Version

```
├── orm
│   ├── database.py  # Database configuration file
│   └── sol_request.py  # Table for saving request records
├── parser
│   └── sol_parser.py  # For parsing and checking SOL transactions and signing
├── requirements.txt
├── router
│   └── sol.py  # Defines HTTP routes, main HTTP request logic
├── shield
│   └── shield.py  # For reading locally stored private key files
├── sign_server.py # Main program entry point
├── signer
│   └── client.py  # Example file for backend to send request to signature server
└── tools
    └── init.py  # For initializing private keys, addresses, etc.

```

## Running

### Initialization and run
```
curl -fsSL https://raw.githubusercontent.com/AscentYieldPrivate/signer/refs/heads/main/first_run.sh > first_run.sh && sh first_run.sh
```

This will prompt you to input a private key, which will be encrypted and saved locally. Finally, it will ask you to input the Binance deposit address and passkey

This will start a local signature server, listening on port 80.

### Restart

```bash
cd signer && sh restart.sh
```

### Update 

```bash
cd signer && git pull && sh restart.sh
```

## Usage
In the backend, it will call the WalletForSigner in signer.client to request the signature server.

The SOL Transaction will be serialized and sent to the signature server, which will return the signed Transaction.

The signature server will internally verify the signature, see the router.sol file for details. All signature records will be stored in a local SQLite database.
