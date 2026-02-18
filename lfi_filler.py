#!/usr/bin/env python3
import sys

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <username>")
    sys.exit(1)

username = sys.argv[1]
home = f"/home/{username}"

paths = [
    # SSH-related
    f"{home}/.ssh/id_rsa",
    f"{home}/.ssh/id_ecdsa",
    f"{home}/.ssh/id_ecdsa_sk",
    f"{home}/.ssh/id_dsa",
    f"{home}/.ssh/id_ed25519",
    f"{home}/.ssh/identity",
    f"{home}/.ssh/*.pem",
    f"{home}/.ssh/authorized_keys",
    f"{home}/.ssh/known_hosts",
    f"{home}/.ssh/config",

    # Shell / app history
    f"{home}/.bash_history",
    f"{home}/.zsh_history",
    f"{home}/.sh_history",
    f"{home}/.fish_history",
    f"{home}/.history",
    f"{home}/.mysql_history",
    f"{home}/.psql_history",
    f"{home}/.rediscli_history",
    f"{home}/.viminfo",
    f"{home}/.lesshst",
    f"{home}/.python_history",

    # Shell configs
    f"{home}/.bashrc",
    f"{home}/.bash_profile",
    f"{home}/.profile",
    f"{home}/.zshrc",
    f"{home}/.zprofile",
    f"{home}/.zlogin",

    # Env files
    f"{home}/.env.local",
]

for p in paths:
    print(p)
