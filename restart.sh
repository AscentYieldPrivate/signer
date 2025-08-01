. ./venv/bin/activate
pip install -r requirements.txt
sudo setcap 'cap_net_bind_service=+ep' $(readlink -f $(which python3))
if tmux has-session -t run 2>/dev/null; then
    tmux kill-session -t run
fi
tmux new-session -s run 'python3 sign_server.py run'
