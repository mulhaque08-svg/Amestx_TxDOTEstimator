import os
import re
import uuid
import urllib.parse
import urllib.request
import json
import logging
from typing import Optional
from fastapi import FastAPI, Request
from fastapi.responses import Response as PlainResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("amestx_translator")

app = FastAPI(title="Amestx Voice & AI Translation Engine", version="3.0.0")

# Enable CORS for browser WebRTC dialer
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AUDIO_DIR = "/tmp/amestx_audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

# Twilio Credentials (loaded securely from environment variables)
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "")
TWILIO_API_KEY = os.environ.get("TWILIO_API_KEY", "")
TWILIO_API_SECRET = os.environ.get("TWILIO_API_SECRET", "")
TWILIO_TWIML_APP_SID = os.environ.get("TWILIO_TWIML_APP_SID", "")

CALLER_ID = "+18448263789"
PUBLIC_BASE_URL = os.environ.get("PUBLIC_BASE_URL", "https://amestx-translator-869440210153.us-central1.run.app")

speech_client = None
tts_client = None

def get_speech_client():
    global speech_client
    if speech_client is None:
        try:
            from google.cloud import speech
            speech_client = speech.SpeechClient()
        except Exception as e:
            logger.warning(f"Google Cloud SpeechClient: {e}")
    return speech_client

def get_tts_client():
    global tts_client
    if tts_client is None:
        try:
            from google.cloud import texttospeech
            tts_client = texttospeech.TextToSpeechClient()
        except Exception as e:
            logger.warning(f"Google Cloud TextToSpeechClient: {e}")
    return tts_client

SPANISH_CHARS = set("áéíóúñÁÉÍÓÚÑ¿¡")
SPANISH_KEYWORDS = {
    "el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "en", "para", "por",
    "con", "sin", "sobre", "ya", "si", "no", "que", "como", "cuando", "donde", "quien",
    "buenos", "buenas", "dias", "tardes", "noches", "hola", "amigo", "jefe", "patron",
    "concreto", "cemento", "varilla", "camion", "trabajo", "estacion", "llegamos", "llego",
    "vamos", "estamos", "aqui", "alli", "alla", "ocupo", "necesito", "hora", "falta",
    "colado", "zanja", "tubo", "grava", "arena", "nivel", "rasante", "plano", "cuadrilla"
}

def detect_language(text: str) -> str:
    if not text:
        return "es"
    if any(c in SPANISH_CHARS for c in text):
        return "es"
    words = re.findall(r'\b[a-zA-ZáéíóúñÁÉÍÓÚÑ]+\b', text.lower())
    if not words:
        return "es"
    spanish_hits = sum(1 for w in words if w in SPANISH_KEYWORDS)
    if spanish_hits >= 2 or (spanish_hits / max(len(words), 1)) >= 0.20:
        return "es"
    return "en"

def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    if not text or source_lang == target_lang:
        return text
    try:
        encoded = urllib.parse.quote(text)
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={source_lang}&tl={target_lang}&dt=t&q={encoded}"
        req = urllib.request.Request(url, headers={"User-Agent": "AmestxTranslator/3.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            if data and isinstance(data, list) and len(data) > 0 and isinstance(data[0], list):
                parts = [s[0] for s in data[0] if s and len(s) > 0 and s[0]]
                if parts:
                    return "".join(parts)
    except Exception as e:
        logger.warning(f"Translation primary: {e}")
    try:
        encoded = urllib.parse.quote(text)
        url = f"https://api.mymemory.translated.net/get?q={encoded}&langpair={source_lang}|{target_lang}"
        req = urllib.request.Request(url, headers={"User-Agent": "AmestxTranslator/3.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            res_json = json.loads(response.read().decode("utf-8"))
            if res_json and "responseData" in res_json and res_json["responseData"].get("translatedText"):
                return res_json["responseData"]["translatedText"]
    except Exception as e:
        logger.error(f"Translation fallback: {e}")
    return text

def synthesize_speech(text: str, target_lang: str) -> Optional[str]:
    if not text or len(text.strip()) == 0:
        return None
    audio_filename = f"{uuid.uuid4().hex[:12]}.mp3"
    audio_path = os.path.join(AUDIO_DIR, audio_filename)
    
    client = get_tts_client()
    if client:
        try:
            from google.cloud import texttospeech
            input_text = texttospeech.SynthesisInput(text=text)
            voice_name = "es-US-Neural2-B" if target_lang == "es" else "en-US-Neural2-J"
            voice = texttospeech.VoiceSelectionParams(
                language_code="es-US" if target_lang == "es" else "en-US",
                name=voice_name,
                ssml_gender=texttospeech.SsmlVoiceGender.MALE
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=1.02
            )
            response = client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_config)
            with open(audio_path, "wb") as out:
                out.write(response.audio_content)
            return f"{PUBLIC_BASE_URL}/audio/{audio_filename}"
        except Exception as e:
            logger.warning(f"Google TTS: {e}")

    try:
        encoded = urllib.parse.quote(text[:200])
        lang = "es" if target_lang == "es" else "en"
        tts_url = f"https://translate.google.com/translate_tts?ie=UTF-8&tl={lang}&client=tw-ob&q={encoded}"
        req = urllib.request.Request(tts_url, headers={"User-Agent": "Mozilla/5.0 Amestx/3.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            with open(audio_path, "wb") as f:
                f.write(response.read())
        return f"{PUBLIC_BASE_URL}/audio/{audio_filename}"
    except Exception as e:
        logger.error(f"Fallback TTS: {e}")
    return None

def transcribe_audio_bytes(audio_bytes: bytes) -> tuple[str, str]:
    client = get_speech_client()
    if not client:
        return ("", "es")
    try:
        from google.cloud import speech
        audio = speech.RecognitionAudio(content=audio_bytes)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
            sample_rate_hertz=16000,
            language_code="es-US",
            alternative_language_codes=["en-US"],
            enable_automatic_punctuation=True
        )
        response = client.recognize(config=config, audio=audio)
        for result in response.results:
            if result.alternatives:
                transcript = result.alternatives[0].transcript
                detected_lang = result.language_code[:2] if result.language_code else "es"
                return (transcript, detected_lang)
    except Exception as e:
        logger.error(f"STT Error: {e}")
    return ("", "es")

def download_twilio_media(media_url: str) -> Optional[bytes]:
    try:
        import requests
        auth = (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN) if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN else None
        res = requests.get(media_url, auth=auth, timeout=8)
        if res.status_code == 200:
            return res.content
    except Exception as e:
        logger.error(f"Download media error: {e}")
    return None

def build_twiml(body: str, media_url: Optional[str] = None) -> str:
    escaped = (
        body.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
    )
    media_tag = f"\n        <Media>{media_url}</Media>" if media_url else ""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>
        <Body>{escaped}</Body>{media_tag}
    </Message>
</Response>"""

@app.get("/")
@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "Amestx Voice & AI Translation Engine",
        "version": "3.0.0",
        "number": CALLER_ID,
        "endpoints": ["/token", "/voice/outbound", "/voice/inbound", "/whatsapp", "/sms", "/audio/{id}"]
    }

# ==========================================
# 0. WEBRTC ACCESS TOKEN FOR BROWSER DIALER
# ==========================================
@app.get("/token")
@app.post("/token")
def get_voice_token(identity: Optional[str] = "amestx_agent"):
    """
    Generates a secure Twilio Voice AccessToken JWT for the web browser dialer.
    """
    try:
        token = AccessToken(
            TWILIO_ACCOUNT_SID,
            TWILIO_API_KEY,
            TWILIO_API_SECRET,
            identity=identity,
            ttl=3600
        )
        voice_grant = VoiceGrant(
            outgoing_application_sid=TWILIO_TWIML_APP_SID,
            incoming_allow=True
        )
        token.add_grant(voice_grant)
        jwt_token = token.to_jwt()
        logger.info(f"Generated Voice JWT token for identity: {identity}")
        return {"token": jwt_token, "identity": identity, "caller_id": CALLER_ID}
    except Exception as e:
        logger.error(f"Error generating voice token: {e}")
        return {"error": str(e)}, 500

# ==========================================
# 1. VOICE CALLING ENDPOINTS (Twilio WebRTC)
# ==========================================
@app.post("/voice/outbound")
async def voice_outbound(request: Request):
    """
    Handles outbound phone calls placed from the Amestx Web Dialer.
    Dials the destination number while presenting CALLER_ID (+18448263789).
    """
    body_bytes = await request.body()
    parsed = urllib.parse.parse_qs(body_bytes.decode("utf-8", errors="replace"))
    to_number = parsed.get("To", [""])[0]

    # Clean destination phone number
    clean_number = re.sub(r'[^0-9+]', '', to_number)
    if not clean_number.startswith("+"):
        clean_number = "+1" + clean_number if len(clean_number) == 10 else "+" + clean_number

    logger.info(f"Outbound call placed to: {clean_number} via Caller ID {CALLER_ID}")
    
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Dial callerId="{CALLER_ID}">
        <Number>{clean_number}</Number>
    </Dial>
</Response>"""
    return PlainResponse(content=twiml, media_type="application/xml")

@app.post("/voice/inbound")
async def voice_inbound(request: Request):
    """
    Handles inbound phone calls dialed to +1 (844) 826-3789.
    Rings the Amestx Web Dialer client.
    """
    logger.info("Inbound call received on Amestx Voice number")
    twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Joanna">Thank you for calling Amestx Voice. Connecting your call now.</Say>
    <Dial>
        <Client>amestx_agent</Client>
    </Dial>
</Response>"""
    return PlainResponse(content=twiml, media_type="application/xml")

# ==========================================
# 2. WHATSAPP WEBHOOK (Unchanged & Dedicated)
# ==========================================
@app.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    body_bytes = await request.body()
    body_str = body_bytes.decode("utf-8", errors="replace")
    parsed = urllib.parse.parse_qs(body_str)
    
    def get_val(name: str):
        v = parsed.get(name, [])
        return v[0] if v else None

    body_text = get_val("Body")
    profile_name = get_val("ProfileName") or "User"
    media_url = get_val("MediaUrl0")
    media_type = get_val("MediaContentType0")

    if media_url and media_type and "audio" in media_type.lower():
        audio_bytes = download_twilio_media(media_url)
        transcript, detected_lang = ("", "es")
        if audio_bytes:
            transcript, detected_lang = transcribe_audio_bytes(audio_bytes)
        
        if transcript:
            target_lang = "en" if detected_lang == "es" else "es"
            translated = translate_text(transcript, detected_lang, target_lang)
            audio_link = synthesize_speech(translated, target_lang)
            
            if target_lang == "en":
                reply = (
                    f"🎙️ *Voice Note from {profile_name}*:\n"
                    f"\"{transcript}\"\n\n"
                    f"🇺🇸 *English Translation*:\n"
                    f"\"{translated}\""
                )
            else:
                reply = (
                    f"🎙️ *Nota de Voz de {profile_name}*:\n"
                    f"\"{transcript}\"\n\n"
                    f"🇲🇽 *Traducción al Español*:\n"
                    f"\"{translated}\""
                )
            return PlainResponse(content=build_twiml(reply, audio_link), media_type="application/xml")
        else:
            reply = f"🎙️ *Amestx Voice*\nVoice note received from *{profile_name}*.\nPlease speak closer to your microphone or send text."
            return PlainResponse(content=build_twiml(reply), media_type="application/xml")

    clean_text = (body_text or "").strip()
    if not clean_text:
        reply = "📞 *Amestx Voice*\nSend any text or voice note in Spanish or English and I will translate it with both text and voice audio."
        return PlainResponse(content=build_twiml(reply), media_type="application/xml")

    lang = detect_language(clean_text)
    if lang == "es":
        translated = translate_text(clean_text, "es", "en")
        audio_link = synthesize_speech(translated, "en")
        reply = f"🇺🇸 *English Translation*:\n\"{translated}\"\n\n_(Original de {profile_name}: \"{clean_text}\")_"
    else:
        translated = translate_text(clean_text, "en", "es")
        audio_link = synthesize_speech(translated, "es")
        reply = f"🇲🇽 *Traducción al Español*:\n\"{translated}\"\n\n_(Original from {profile_name}: \"{clean_text}\")_"

    return PlainResponse(content=build_twiml(reply, audio_link), media_type="application/xml")

# ==========================================
# 3. DIRECT SMS & MMS TEXTING ENDPOINTS
# ==========================================
@app.post("/sms")
@app.post("/sms/inbound")
async def sms_inbound(request: Request):
    body_bytes = await request.body()
    parsed = urllib.parse.parse_qs(body_bytes.decode("utf-8", errors="replace"))
    body_text = parsed.get("Body", [""])[0].strip()
    from_number = parsed.get("From", [""])[0]

    if not body_text:
        return PlainResponse(content="<Response></Response>", media_type="application/xml")

    lang = detect_language(body_text)
    if lang == "es":
        trans = translate_text(body_text, "es", "en")
        reply = f"[Amestx Voice Translation]\n🇺🇸 EN: \"{trans}\""
    else:
        trans = translate_text(body_text, "en", "es")
        reply = f"[Amestx Voice Translation]\n🇲🇽 ES: \"{trans}\""

    logger.info(f"SMS from {from_number}: '{body_text}' -> '{trans}'")
    return PlainResponse(content=build_twiml(reply), media_type="application/xml")

@app.get("/audio/{filename}")
def get_audio(filename: str):
    clean_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '', filename)
    file_path = os.path.join(AUDIO_DIR, clean_name)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/mpeg", headers={"Cache-Control": "public, max-age=86400"})
    return PlainResponse(content="Audio not found", status_code=404)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
