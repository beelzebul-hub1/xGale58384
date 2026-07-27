# -*- coding: utf-8 -*-

import json
import time
import logging
import os
import threading
import requests
from flask import Flask
from colorama import Fore

from TwitchChannelPointsMiner import TwitchChannelPointsMiner
from TwitchChannelPointsMiner.logger import LoggerSettings, ColorPalette
from TwitchChannelPointsMiner.classes.Chat import ChatPresence
from TwitchChannelPointsMiner.classes.Discord import Discord
from TwitchChannelPointsMiner.classes.Webhook import Webhook
from TwitchChannelPointsMiner.classes.Telegram import Telegram
from TwitchChannelPointsMiner.classes.Matrix import Matrix
from TwitchChannelPointsMiner.classes.Pushover import Pushover
from TwitchChannelPointsMiner.classes.Gotify import Gotify
from TwitchChannelPointsMiner.classes.Settings import Priority, Events, FollowersOrder
from TwitchChannelPointsMiner.classes.entities.Bet import Strategy, BetSettings, Condition, OutcomeKeys, FilterCondition, DelayMode
from TwitchChannelPointsMiner.classes.entities.Streamer import Streamer, StreamerSettings


# ---------------- FLASK ----------------
app = Flask(__name__)

@app.route("/")
def health():
    return "OK", 200


def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


threading.Thread(target=run_flask, daemon=True).start()
# --------------------------------------


# ---------------- MINER ----------------
twitch_miner = TwitchChannelPointsMiner(
    username="xGale58384",
    password="Splashing8-Cheese5-Escargot5-Distrust6-Uranium8",
    claim_drops_startup=False,
    priority=[
        Priority.STREAK,
        Priority.DROPS,
        Priority.ORDER
    ],
    enable_analytics=False,
    disable_ssl_cert_verification=False,
    disable_at_in_nickname=False,
    logger_settings=LoggerSettings(
        save=True,
        console_level=logging.INFO,
        console_username=False,
        auto_clear=True,
        file_level=logging.DEBUG,
        emoji=True,
        less=True,
        colored=True,
        color_palette=ColorPalette(
            STREAMER_online="GREEN",
            streamer_offline="red",
            BET_wiN=Fore.MAGENTA
        )
    ),
    streamer_settings=StreamerSettings(
        make_predictions=False,
        follow_raid=True,
        claim_drops=True,
        watch_streak=True,
        community_goals=False,
        chat=ChatPresence.ONLINE,
        bet=BetSettings(
            strategy=Strategy.SMART,
            percentage=5,
            percentage_gap=20,
            max_points=50000,
            stealth_mode=True,
            delay_mode=DelayMode.FROM_END,
            delay=6,
            minimum_points=20000,
            filter_condition=FilterCondition(
                by=OutcomeKeys.TOTAL_USERS,
                where=Condition.LTE,
                value=800
            )
        )
    )
)
# --------------------------------------


# -------- POINTS EXPORTER -------------
def export_points_loop():
    while True:
        try:
            data = {
                "account": twitch_miner.username,
                "updated": int(time.time()),
                "channels": {},
                "streamer_status": {}
            }

            for streamer in twitch_miner.streamers:
                username = getattr(streamer, "username", None)

                points = (
                    getattr(streamer, "channel_points", None)
                    or getattr(streamer, "points", None)
                    or getattr(streamer, "_points", None)
                )

                # get online status - try multiple attribute names
                online = (
                    getattr(streamer, "online", None)
                    or getattr(streamer, "is_online", None)
                    or False
                )

                if username:
                    if points is not None:
                        data["channels"][username] = int(points)
                    data["streamer_status"][username] = bool(online)

            # local backup
            with open(f"points_{twitch_miner.username}.json", "w") as f:
                json.dump(data, f)

            # send to website
            try:
                requests.post(
                    "https://render-1-ethy.onrender.com/api/update",
                    json=data,
                    timeout=10
                )
                print("sent:", data)

            except Exception as e:
                print("send error:", e)

        except Exception as e:
            print("export error:", e)

        time.sleep(60)


threading.Thread(target=export_points_loop, daemon=True).start()
# --------------------------------------


# ---------------- RUN -----------------
twitch_miner.mine([
        Streamer("shayph"),
        Streamer("copieburger"),
        Streamer("waffletrades_"),
    ],
    followers=False,
    followers_order=FollowersOrder.ASC
)
# --------------------------------------
