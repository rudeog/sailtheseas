#!/bin/bash

# Check if Python is in the PATH
if ! command -v python3 &> /dev/null; then
  echo "Python 3 not found. Please install Python 3 and ensure it's in your PATH."
  echo "Visit https://www.python.org/downloads/"
  read -p "Press any key to continue..."
  exit 1
fi
script_dir=$(dirname "$0")
cd "$script_dir/src"
python3 -m main
read -p "Press any key to continue..."
