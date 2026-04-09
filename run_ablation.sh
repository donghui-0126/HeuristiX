#!/bin/bash
# Ablation experiments for HeuristiX
# Usage: ./run_ablation.sh

set -a; source .env; set +a

GENS=15
POP=6

echo "=== Experiment 1: Adaptive RAG (late-stage only) ==="
python3 -m heuristix.cli --generations $GENS --population $POP --rag-mode adaptive 2>&1 | tee /tmp/hx-exp-adaptive.log

echo ""
echo "=== Experiment 2: Failure-only RAG ==="
# Clean graph + embeddings between experiments
rm -rf /home/amuredo/amuredo-alphalogic/data/amure_graph/*
rm -f data/embeddings.json
curl -s -X POST http://localhost:9090/api/graph/save > /dev/null
python3 -m heuristix.cli --generations $GENS --population $POP --rag-mode failure-only 2>&1 | tee /tmp/hx-exp-failure-only.log

echo ""
echo "=== Experiment 3: Full RAG, 30 generations ==="
rm -rf /home/amuredo/amuredo-alphalogic/data/amure_graph/*
rm -f data/embeddings.json
curl -s -X POST http://localhost:9090/api/graph/save > /dev/null
python3 -m heuristix.cli --generations 30 --population $POP --rag-mode full 2>&1 | tee /tmp/hx-exp-long.log

echo ""
echo "=== All experiments complete ==="
echo "Results:"
echo "Adaptive:     $(grep 'Makespan:' /tmp/hx-exp-adaptive.log | tail -1)"
echo "Failure-only: $(grep 'Makespan:' /tmp/hx-exp-failure-only.log | tail -1)"
echo "Full 30gen:   $(grep 'Makespan:' /tmp/hx-exp-long.log | tail -1)"
