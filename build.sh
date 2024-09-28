read -sp "Token: " token

echo '{"token":"'$token'"}' > resource/token.json

python -m venv .venv

. .venv/bin/activate

pip install discord.py
pip install ping3
