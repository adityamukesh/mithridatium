#!/bin/bash
#SBATCH --job-name=mith-agent
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --mem=16G
#SBATCH --time=00:30:00
#SBATCH --output=logs/agent_%j.out

cd ~/mithridatium
source .venv/bin/activate
python -m mithridatium.mcp.detect_agent "Run TED on models/resnet18_poison.pth"
python -m mithridatium.mcp.detect_agent "Run SCALE-UP and TED on models/resnet18_clean.pth"
python -m mithridatium.mcp.repair_agent "Run LMR on models/resnet18_poison.pth with target class 0 and prune ratio 0.05"
python -m mithridatium.mcp.audit_agent "Run STRIP and MMBD on models/resnet18_clean.pth"
