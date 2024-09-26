python -m venv .venv

. .venv/bin/activate

pip install discord.py
pip install ping3

read token

echo '{"token":"'$token'"}' > resource/token.json