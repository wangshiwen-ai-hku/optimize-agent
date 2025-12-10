#!/bin/bash
# 快速启动 Tutor 模式

echo "🎓 Starting Math Tutor..."
echo ""

if [ $# -eq 0 ]; then
    echo "Usage: ./run_tutor.sh <material_file1> [material_file2] ..."
    echo ""
    echo "Example:"
    echo "  ./run_tutor.sh examples/materials/linear_programming.txt"
    exit 1
fi

python -m src.agent.main tutor "$@"
