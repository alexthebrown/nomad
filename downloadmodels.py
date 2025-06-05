from huggingface_hub import hf_hub_download

# Specify the repository and filename
repo_id = "TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF"
filename = "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"

# Download the model
model_path = hf_hub_download(repo_id=repo_id, filename=filename)

print(f"Model downloaded to: {model_path}")
