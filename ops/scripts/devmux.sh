#!/usr/bin/env bash
SESSION=notetaker
# start session
if ! tmux has-session -t $SESSION 2>/dev/null; then
tmux new-session -d -s $SESSION -n backend
tmux send-keys -t $SESSION "source .venv/bin/activate && make backend" C-m
tmux new-window -t $SESSION -n rag
tmux send-keys -t $SESSION:2 "source .venv/bin/activate && make rag" C-m
tmux new-window -t $SESSION -n latex
tmux send-keys -t $SESSION:3 "make latex" C-m
tmux new-window -t $SESSION -n ui
tmux send-keys -t $SESSION:4 "make ui" C-m
tmux new-window -t $SESSION -n logs
tmux send-keys -t $SESSION:5 "tail -f logs/*.log 2>/dev/null || watch ls -la" C-m
fi
tmux attach -t $SESSION
