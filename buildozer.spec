name: Build Android APK

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python 3.10
        uses: actions/setup-python@v5
        with:
          python-version: "3.10"

      - name: Install dependencies
        run: |
          sudo apt update
          sudo apt install -y build-essential libffi-dev libssl-dev ccache git unzip zip zlib1g-dev openjdk-17-jdk libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
          pip install --upgrade pip setuptools
          pip install Cython==0.29.36
          pip install buildozer==1.5.0

      - name: Build with Buildozer
        run: |
          buildozer -v android debug
