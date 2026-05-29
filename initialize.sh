#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
LAUNCHER="$ROOT_DIR/launcher.py"
BOOTSTRAP_VENV="$ROOT_DIR/.bootstrap-venv"

if [[ ! -f "$LAUNCHER" ]]; then
  echo "Error: launcher.py not found in $ROOT_DIR"
  exit 1
fi

have() {
  command -v "$1" >/dev/null 2>&1
}

detect_pm() {
  if have apt-get; then
    echo apt
  elif have dnf; then
    echo dnf
  elif have yum; then
    echo yum
  elif have pacman; then
    echo pacman
  else
    echo none
  fi
}

PM="$(detect_pm)"
if [[ "$PM" == "none" ]]; then
  echo "Error: no supported package manager found (apt, dnf, yum, pacman)."
  exit 1
fi

run_root() {
  if [[ "${EUID:-$(id -u)}" -eq 0 ]]; then
    "$@"
  elif have sudo; then
    sudo "$@"
  else
    echo "Error: this step needs root privileges or sudo."
    exit 1
  fi
}

install_pkgs() {
  case "$PM" in
    apt)
      run_root apt-get update
      run_root apt-get install -y "$@"
      ;;
    dnf)
      run_root dnf install -y "$@"
      ;;
    yum)
      run_root yum install -y "$@"
      ;;
    pacman)
      run_root pacman -Sy --noconfirm --needed "$@"
      ;;
  esac
}

ensure_python() {
  local pybin=""
  if have python3; then
    pybin="$(command -v python3)"
  elif have python; then
    pybin="$(command -v python)"
  fi

  if [[ -z "$pybin" ]]; then
    case "$PM" in
      apt)
        install_pkgs python3 python3-venv python3-pip
        ;;
      dnf|yum)
        install_pkgs python3 python3-pip
        ;;
      pacman)
        install_pkgs python python-pip
        ;;
    esac
  fi

  if have python3; then
    pybin="$(command -v python3)"
  elif have python; then
    pybin="$(command -v python)"
  fi

  if [[ -z "$pybin" ]]; then
    echo "Error: Python could not be installed or found."
    exit 1
  fi

  local ver major minor
  ver="$("$pybin" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
  major="${ver%%.*}"
  minor="${ver#*.}"

  if (( major < 3 )) || (( major == 3 && minor < 11 )); then
    echo "Error: Python $ver found, but launcher.py requires 3.11+."
    exit 1
  fi

  echo "$pybin"
}

ensure_node() {
  if have node && have npm; then
    return 0
  fi

  case "$PM" in
    apt)
      install_pkgs nodejs npm
      ;;
    dnf|yum)
      install_pkgs nodejs npm
      ;;
    pacman)
      install_pkgs nodejs npm
      ;;
  esac

  if ! have node || ! have npm; then
    echo "Error: Node.js/npm could not be installed or found."
    exit 1
  fi
}

ensure_utils() {
  case "$PM" in
    apt)
      install_pkgs psmisc lsof
      ;;
    dnf|yum)
      install_pkgs psmisc lsof
      ;;
    pacman)
      install_pkgs psmisc lsof
      ;;
  esac
}

ensure_venv_support() {
  local pybin="$1"

  if "$pybin" -m venv --help >/dev/null 2>&1; then
    return 0
  fi

  case "$PM" in
    apt)
      install_pkgs python3-venv
      ;;
    dnf|yum|pacman)
      :
      ;;
  esac

  if ! "$pybin" -m venv --help >/dev/null 2>&1; then
    echo "Error: the Python venv module is unavailable."
    exit 1
  fi
}

PYBIN="$(ensure_python)"
ensure_node
ensure_utils
ensure_venv_support "$PYBIN"

if [[ ! -x "$BOOTSTRAP_VENV/bin/python" ]]; then
  "$PYBIN" -m venv "$BOOTSTRAP_VENV"
fi

"$BOOTSTRAP_VENV/bin/python" -m pip install --upgrade pip setuptools wheel rich

exec "$BOOTSTRAP_VENV/bin/python" "$LAUNCHER" "$@"
