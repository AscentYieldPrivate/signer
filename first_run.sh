sudo apt update
sudo apt install python3 pip git python3-venv tmux -y
git clone https://github.com/AscentYieldPrivate/signer
sudo setcap 'cap_net_bind_service=+ep' $(readlink -f $(which python3))
cd signer
python3 -m venv ./venv
. ./venv/bin/activate
pip install -r requirements.txt
tmux new-session -s init 'python3 sign_server.py init'
tmux new-session -s run 'python3 sign_server.py run'
