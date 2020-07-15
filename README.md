# Convective Alert Discord Bot
*DISCLAIMER: This is for entertainment purposes only. Do not rely on this for weather information.*

A python3 Discord bot that provides [convective outlook](https://en.wikipedia.org/wiki/Storm_Prediction_Center#Convective_outlooks) alerts based on US ZIP codes. It uses the [Iowa Environmental Mesonet](https://mesonet.agron.iastate.edu) API. Users can get alerted automatically each day or request an outlook on demand.

I welcome contributions as there is a lot of room for improvment.

## Setup
Packages you'll need to install: `discord.py`, `tinydb`, `pgeocode`, and `aiocron`. In `bot.py`, you'll need to set your token and the ID of the channel you'd like the alerts to go to. Read the [Discord Developer Docs](https://discord.com/developers/docs/intro) on how to get a token for your bot. Enable [Discord Developer Mode](https://discordia.me/en/developer-mode) to get the channel ID.

Once the bot is up and running, use the `!help` command to get started.