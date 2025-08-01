. ./venv/bin/activate
pip install -r requirements.txt
sudo setcap 'cap_net_bind_service=+ep' $(readlink -f $(which python3))
current_path=$(pwd | tr -d '/')
if tmux has-session -t $current_path 2>/dev/null; then
    tmux kill-session -t $current_path
fi
tmux new-session -s $current_path 'python3 sign_server.py run'
