#!/bin/bash
MODEL_URL="https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
MODEL_ZIP="vosk-model-small-en-us-0.15.zip"
MODEL_DIR="model"

echo "Downloading Vosk model..."
curl -LO "$MODEL_URL"

echo "Unzipping..."
unzip -o "$MODEL_ZIP"

echo "Renaming folder..."
rm -rf "$MODEL_DIR"
mv vosk-model-small-en-us-0.15 "$MODEL_DIR"

echo "Cleaning up..."
rm "$MODEL_ZIP"

echo "✅ Model setup complete!"
