FROM --platform=linux/amd64 debian:bookworm-slim

# ツールインストール, ロケール設定, タイムゾーン設定
RUN apt-get update && apt-get install --no-install-recommends -y \
    ca-certificates \
    locales \
    jq \
    bash-completion \
    curl \
    unzip \
    less \
    python3 \
    python3-pip \
    python3.11-venv \
    \
    # AWS CLI インストール
    && curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    \
    # ロケール設定
    && sed -i 's/^# *\(ja_JP.UTF-8 UTF-8\)/\1/' /etc/locale.gen \
    && locale-gen \
    && localedef -i ja_JP -f UTF-8 ja_JP.UTF-8 \
    && echo 'LANG=ja_JP.UTF-8' > /etc/default/locale \
    && echo 'LC_ALL=ja_JP.UTF-8' >> /etc/default/locale \
    && echo 'LANG=ja_JP.UTF-8' > /etc/locale.conf \
    && echo 'LC_ALL=ja_JP.UTF-8' >> /etc/locale.conf \
    && ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime \
    \
    # 不要なキャッシュを削除し、コンテナサイズを軽量化
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Node.js のインストール
RUN curl -fsSL https://deb.nodesource.com/setup_22.x -o nodesource_setup.sh \
    && bash nodesource_setup.sh \
    && apt-get install -y nodejs \
    && rm -rf nodesource_setup.sh \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# AWS CDK のインストール
RUN npm install -g aws-cdk

# 環境変数設定
ENV LANG=ja_JP.UTF-8
ENV LANGUAGE=ja_JP.UTF-8
ENV LC_ALL=ja_JP.UTF-8

COPY config /root/.aws/config
COPY .bashrc /root/.bashrc

WORKDIR /workspace