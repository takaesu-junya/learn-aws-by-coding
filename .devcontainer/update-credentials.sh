#!/bin/bash

# credentials.json は、devcontainer.json の initializeCommand で生成される(devcontainer 起動時に生成される)
if [ -f /workspace/.devcontainer/credentials.json ]; then
    credentials=$(cat /workspace/.devcontainer/credentials.json)
    export AWS_ACCESS_KEY_ID=$(echo $credentials | jq -r .AccessKeyId)
    export AWS_SECRET_ACCESS_KEY=$(echo $credentials | jq -r .SecretAccessKey)
    export AWS_SESSION_TOKEN=$(echo $credentials | jq -r .SessionToken)
    export AWS_DEFAULT_REGION=us-west-2

    # 環境変数が正しく設定されたか確認
    aws sts get-caller-identity
fi