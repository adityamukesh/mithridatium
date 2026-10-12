#!/bin/bash
#SBATCH --job-name=mith-agent
#SBATCH --partition=<gpu-partition>
#SBATCH --gres=gpu:1
#SBATCH --mem=16G
#SBATCH --time=00:30:00
#SBATCH --output=logs/agent_%j.out

cd ~/mithridatium
source .venv/bin/activate
python -m mithridatium.mcp.${1:-detect_agent}
