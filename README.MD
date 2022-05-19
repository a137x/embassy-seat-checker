![Logo](https://pieraksts.mfa.gov.lv/img/coat-of-arms-LR.png)

# Slot checker at EMBASSY OF THE REPUBLIC OF LATVIA IN THE RUSSIAN FEDERATION
https://pieraksts.mfa.gov.lv/ru/moskva

A fan project that helped friends to get a seats for interview in Latvian embassy in Moscow.
Telegram bot that notifies if there is any available slot.

## Requirements
- Python 3.8+
- Telegram bot created via https://t.me/BotFather
- chrome-browser driver installed in your host:
    `sudo curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add`
    `sudo bash -c "echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' >> /etc/apt/sources.list.d/google-chrome.list"`
    `sudo apt -y update`
    `sudo apt -y install google-chrome-stable`

## Installation and start
- create and enter env: `python3 -m venv venv` `source ./venv/bin/activate`
- install requirements: `pip install requirements.txt`
- to start in background (disconnect from current ssh session): `bash /root/stpbot/start.sh & disown`
- patience

MIT License

