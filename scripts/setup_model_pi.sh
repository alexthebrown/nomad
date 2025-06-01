#!/bin/bash
MODEL_URL="https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
MODEL_ZIP="vosk-model-small-en-us-0.15.zip"
MODEL_DIR="model"

echo "🔽 Downloading Vosk model..."
wget -O "$MODEL_ZIP" "$MODEL_URL"

echo "📦 Unzipping model..."
unzip -o "$MODEL_ZIP"

echo "📁 Setting up model directory..."
rm -rf "$MODEL_DIR"
mv vosk-model-small-en-us-0.15 "$MODEL_DIR"

echo "🧹 Cleaning up zip file..."
rm "$MODEL_ZIP"

echo "✅ Vosk model is ready in the '$MODEL_DIR' folder."
