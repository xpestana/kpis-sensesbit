set shell := ["sh", "-c"]

_default:
  @just --choose


# Install project on local machine change OS variable to your OS
[unix]
install OS="arch":
    #!/usr/bin/sh
    curl -LsSf https://astral.sh/uv/install.sh | sh

    if [ "{{OS}}" = "debian"  ||  "{{OS}}" = "ubuntu" ]; then
        sudo apt-get update
        sudo apt-get -y install podman
    fi
    if [ "{{OS}}" = "arch" ]; then
        sudo pacman -Syy podman
    fi

    if ! grep -Eq '^unqualified-search-registries' /etc/containers/registries.conf; then
        echo 'unqualified-search-registries = ["docker.io", "sensesbit.com", "sensesbit.es"]' | sudo tee -a /etc/containers/registries.conf
    fi

    uv sync

[linux]
dev:
    #!/usr/bin/sh
    podman network create sensesbit || true
    podman run --name postgres --net sensesbit -p 5432:5432 -e POSTGRES_PASSWORD=postgres -v postgres:/var/lib/postgresql --replace -d postgres:17
    podman run --name drizzle-gate --net sensesbit -p 4983:4983 -e PORT=4983 -e MASTERPASS=your_master_password -e STORE_PATH=./app -v drizzle-gateway:/app --replace -d ghcr.io/drizzle-team/gateway:latest

    uv sync
    uv run fastapi dev --reload src/main.py

    