#!/bin/bash

# Forge 软件发布管理平台 - SSL 证书生成脚本
# 此脚本用于生成开发环境的自签名SSL证书

echo "正在生成自签名SSL证书..."

# 创建证书目录
mkdir -p ../nginx/certs

# 证书配置
CERT_COUNTRY="CN"
CERT_STATE="Shanghai"
CERT_LOCALITY="Shanghai"
CERT_ORGANIZATION="Forge Team"
CERT_ORGANIZATIONAL_UNIT="Forge"
CERT_COMMON_NAME="localhost"
CERT_EMAIL="admin@forge.com"

# 私钥文件
PRIVATE_KEY="../nginx/certs/localhost.key"
# 证书签名请求文件
CSR_FILE="../nginx/certs/localhost.csr"
# 证书文件
CERT_FILE="../nginx/certs/localhost.crt"

# 生成私钥
openssl genrsa -out $PRIVATE_KEY 2048

# 生成证书签名请求
openssl req -new -key $PRIVATE_KEY -out $CSR_FILE -subj "/C=$CERT_COUNTRY/ST=$CERT_STATE/L=$CERT_LOCALITY/O=$CERT_ORGANIZATION/OU=$CERT_ORGANIZATIONAL_UNIT/CN=$CERT_COMMON_NAME/emailAddress=$CERT_EMAIL"

# 生成自签名证书
openssl x509 -req -days 3650 -in $CSR_FILE -signkey $PRIVATE_KEY -out $CERT_FILE

# 清理CSR文件
rm $CSR_FILE

# 设置适当的权限
chmod 600 $PRIVATE_KEY
chmod 644 $CERT_FILE

echo "SSL证书已生成:"
echo "私钥: $PRIVATE_KEY"
echo "证书: $CERT_FILE"
echo ""
echo "注意: 这是自签名证书，仅用于开发环境。在生产环境中，请使用受信任的CA签发的证书。"