docker build \
  --build-arg BRANCH=block_event_record \
  --build-arg REPO_URL=https://github.com/ChenxingLi/conflux-rust \
  --build-arg https_proxy=http://192.168.1.169:1082 \
  --build-arg http_proxy=http://192.168.1.169:1082 \
  --build-arg no_proxy=localhost,127.0.0.1 \
  -t conflux:dev .