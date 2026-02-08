# MH-Z19C ロガー

## Overview
MH-Z19C から取得したデータを InfluxDB (v2系) に格納するスクリプト。

InfluxDB に格納したレコードを Grafana で表示するためのダッシュボード (JSON) サンプル付き。

## Prerequirements
ハードウェアとして、以下が必要。

- 環境センサーモジュール MH-Z19C
- Raspberry Pi 等の MH-Z19C をコントロールするためのハードウェア

結果格納とダッシュボード表示のために以下が必要。

- InfluxDB OSS 2
- Grafana

また、本スクリプトを実行するために、以下が必要。

- Python 3
- uv

## Setup

クローン後、init.sh を実行し、必要な Python モジュールをダウンロード。
```
cd /opt
git clone https://github.com/gcch/mh-z19c-logger.git
cd mh-z19c-logger
./init.sh
```

設定ファイル `config.ini` を作成。InfluxDB のアクセス情報 `url` `org` `token` `bucket` を設定。
```
cp config.ini.sample config.ini
vi config.ini
```

定期実行のため、cron の設定を実施。
```
echo "* 0 * * * root /opt/mh-z19c-logger/run.sh" > /etc/cron.d/mh-z19c-logger
```





