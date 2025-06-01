from src.responder import Responder

responder = Responder()
while True:
    prompt = input("🎤 You: ")
    responder.respond(prompt)
