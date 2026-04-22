docker build \
  --build-arg CACHEBUST=$(date +%s) \
  --build-arg BRANCH=massive-test \
  --build-arg REPO_URL=https://github.com/ChenxingLi/conflux-rust \
  --build-arg https_proxy=http://192.168.1.169:1082 \
  --build-arg http_proxy=http://192.168.1.169:1082 \
  --build-arg no_proxy=localhost,127.0.0.1 \
  -t conflux:dev .