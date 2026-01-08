#!/bin/bash

python3 stat_latency_map_reduce.py ./log ./output/blocks.log

cat ./log/conflux.log | grep "new block inserted into graph" > ./output/conflux.log.new_blocks
cp ./log/metrics.log ./output/metrics.log