import streamlit as st
import toml
import importlib
from streamlit_option_menu import option_menu

# Charger config TOML
config = toml.load(".streamlit/config.toml")
menu_conf = config["menu"]

# Menu horizontal
selected = option_menu(
    menu_conf["title"],
    [page["name"] for page in menu_conf["pages"]],
    icons=[page["icon"] for page in menu_conf["pages"]],
    orientation=menu_conf["orientation"]
)

# Router vers la bonne page
for page in menu_conf["pages"]:
    if selected == page["name"]:
        module = importlib.import_module(page["file"])  # ex: "pages.refactoring"
        module.run()
