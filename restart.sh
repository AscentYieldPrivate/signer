. ./venv/bin/activate
pip install -r requirements.txt
sudo setcap 'cap_net_bind_service=+ep' $(readlink -f $(which python3))
tmux kill-window -t run:0
tmux new-session -s run 'python3 sign_server.py run'
