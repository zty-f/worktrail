#!/bin/zsh
set -eu
prs_root="$(cd "$(dirname "$0")" && pwd)"
prs_bundled="$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"
if [[ -x "$prs_root/.venv/bin/python" ]]; then
  prs_python="$prs_root/.venv/bin/python"
elif [[ -x "$prs_bundled" ]]; then
  prs_python="$prs_bundled"
else
  prs_python="$(command -v python3)"
fi
prs_workspace="$prs_root/runs/demo-$(date +%Y%m%d-%H%M%S)"
cd "$prs_root"
"$prs_python" scripts/review.py doctor --outputs all
"$prs_python" scripts/create_demo.py "$prs_workspace"
"$prs_python" scripts/review.py build "$prs_workspace"
"$prs_python" scripts/review.py verify "$prs_workspace"
open "$prs_workspace/output/index.html"
print '新模拟案例已完成。原始示例保持可查看。'
