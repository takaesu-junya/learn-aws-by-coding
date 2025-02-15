FROM tomomano/labc:latest

# ツールインストール, ロケール設定, タイムゾーン設定
RUN apt-get update && apt-get install --no-install-recommends -y \
    locales \
    jq \
    bash-completion \
    && sed -i 's/^# *\(ja_JP.UTF-8 UTF-8\)/\1/' /etc/locale.gen \
    && locale-gen \
    && localedef -i ja_JP -f UTF-8 ja_JP.UTF-8 \
    && echo 'LANG=ja_JP.UTF-8' > /etc/default/locale \
    && echo 'LC_ALL=ja_JP.UTF-8' >> /etc/default/locale \
    && echo 'LANG=ja_JP.UTF-8' > /etc/locale.conf \
    && echo 'LC_ALL=ja_JP.UTF-8' >> /etc/locale.conf \
    \
    # 不要なキャッシュを削除し、コンテナサイズを軽量化
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# 環境変数設定
ENV LANG=ja_JP.UTF-8
ENV LANGUAGE=ja_JP.UTF-8
ENV LC_ALL=ja_JP.UTF-8

COPY config /root/.aws/config
COPY .bashrc /root/.bashrc

WORKDIR /workspace