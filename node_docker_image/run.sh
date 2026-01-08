docker run -itd \
  --name conflux-massive-test \
  --net=host \
  --privileged \
  --ulimit nofile=65535:65535 \
  --ulimit nproc=65535:65535 \
  --ulimit core=-1 \
  -v /tmp/conflux-logs:/root/logs \
  conflux:dev
