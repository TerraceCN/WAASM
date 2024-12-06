# WAAMS

WAAMS (Which asshole is attacking my site) is a simple tool used to save data from the Cloudflare Logs API locally at regular intervals, making it easy for users to analyze the logs to determine the source of an attack and configure a targeted WAF for defense.

# Requirements

Python 3.11 or higher.

# How to use

1. Clone this repo.
2. Copy `config.example.toml` to `config.toml` and fill in the required fields.
3. Install dependencies with `pip install -r requirements.txt`.
4. Run `python main.py` to run once.

You need to pair it with a timed task to fetch data continuously, such as `crontab` or `qinglong`.

