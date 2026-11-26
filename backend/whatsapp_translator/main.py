import os
import re
import uuid
import urllib.parse
import urllib.request
import json
import logging
import datetime
import base64
from typing import Optional
from fastapi import FastAPI, Request
from fastapi.responses import Response as PlainResponse, FileResponse, HTMLResponse
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

def transcribe_audio_bytes(audio_bytes: bytes, source_lang: str = "es") -> tuple[str, str]:
    client = get_speech_client()
    if not client or not audio_bytes:
        return ("", source_lang)
    try:
        from google.cloud import speech
        audio = speech.RecognitionAudio(content=audio_bytes)

        # Detect audio container & format based on header magic bytes
        if audio_bytes.startswith(b"RIFF") and b"WAVE" in audio_bytes[:16]:
            sample_rate = 16000
            try:
                sample_rate = int.from_bytes(audio_bytes[24:28], byteorder="little")
            except Exception:
                sample_rate = 16000
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=sample_rate,
                language_code="es-US" if source_lang == "es" else "en-US",
                alternative_language_codes=["es-MX", "es-ES", "en-US"] if source_lang == "es" else ["es-US"],
                enable_automatic_punctuation=True
            )
        elif audio_bytes.startswith(b"\x1a\x45\xdf\xa3"):
            # WebM container with Opus
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
                sample_rate_hertz=48000,
                language_code="es-US" if source_lang == "es" else "en-US",
                alternative_language_codes=["es-MX", "es-ES", "en-US"] if source_lang == "es" else ["es-US"],
                enable_automatic_punctuation=True
            )
        elif audio_bytes.startswith(b"OggS"):
            # Ogg container with Opus (WhatsApp audio)
            sample_rate = 16000
            if b"OpusHead" in audio_bytes[:150]:
                idx = audio_bytes.find(b"OpusHead")
                try:
                    sr = int.from_bytes(audio_bytes[idx+12:idx+16], byteorder="little")
                    if sr in [8000, 12000, 16000, 24000, 48000]:
                        sample_rate = sr
                except Exception:
                    pass
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
                sample_rate_hertz=sample_rate,
                language_code="es-US" if source_lang == "es" else "en-US",
                alternative_language_codes=["es-MX", "en-US"],
                enable_automatic_punctuation=True
            )
        else:
            # Fallback raw PCM LINEAR16 16kHz
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code="es-US" if source_lang == "es" else "en-US",
                alternative_language_codes=["es-MX", "en-US"],
                enable_automatic_punctuation=True
            )

        try:
            response = client.recognize(config=config, audio=audio)
            for result in response.results:
                if result.alternatives:
                    transcript = result.alternatives[0].transcript
                    detected_lang = result.language_code[:2] if result.language_code else source_lang
                    return (transcript, detected_lang)
        except Exception as primary_err:
            logger.warning(f"STT primary attempt failed ({primary_err}), trying alternative sample rate...")
            if audio_bytes.startswith(b"OggS"):
                config.sample_rate_hertz = 48000 if sample_rate == 16000 else 16000
                response = client.recognize(config=config, audio=audio)
                for result in response.results:
                    if result.alternatives:
                        transcript = result.alternatives[0].transcript
                        detected_lang = result.language_code[:2] if result.language_code else source_lang
                        return (transcript, detected_lang)
    except Exception as e:
        logger.error(f"STT Error: {e}")
    return ("", source_lang)

def download_twilio_media(media_url: str) -> Optional[bytes]:
    try:
        import requests
        auth = None
        if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
            auth = (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        elif TWILIO_API_KEY and TWILIO_API_SECRET:
            auth = (TWILIO_API_KEY, TWILIO_API_SECRET)
        res = requests.get(media_url, auth=auth, timeout=12)
        if res.status_code == 200:
            return res.content
        logger.warning(f"Download media returned HTTP {res.status_code}: {res.text[:120]}")
    except Exception as e:
        logger.error(f"Download media error: {e}")
    return None

# ==========================================
# 2-WAY TRANSLATION RELAY (Supervisor <-> Crew)
# ==========================================
SUPERVISOR_PHONE = "18328379801"
SUPERVISOR_NAME = "Mohsin"

# Pre-registered crew members: normalized phone digits -> info
CREW_MEMBERS = {
    "18323908863": {
        "name": "Octavio",
        "lang": "es",
        "role": "Crew Member"
    },
    "18328012101": {
        "name": "Octavio",
        "lang": "es",
        "role": "Crew Member"
    }
}
ACTIVE_CREW_PHONE = "18323908863"

def normalize_phone(phone: str) -> str:
    digits = re.sub(r'[^0-9]', '', phone or '')
    if len(digits) == 10:
        digits = "1" + digits
    return digits

def get_twilio_client():
    try:
        from twilio.rest import Client
        if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
            return Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        elif TWILIO_API_KEY and TWILIO_API_SECRET and TWILIO_ACCOUNT_SID:
            return Client(TWILIO_API_KEY, TWILIO_API_SECRET, TWILIO_ACCOUNT_SID)
    except Exception as e:
        logger.error(f"Error initializing Twilio Client: {e}")
    return None

def send_whatsapp_outbound(to_number: str, text: Optional[str] = None, media_url: Optional[str] = None) -> tuple[bool, Optional[str]]:
    """
    Sends an outbound WhatsApp message via Twilio REST API.
    Sends text and audio as two distinct messages to comply with WhatsApp media constraints.
    """
    client = get_twilio_client()
    if not client:
        logger.warning("Twilio client credentials not configured for outbound relay")
        return False, "Twilio credentials missing"

    clean_digits = normalize_phone(to_number)
    clean_to = f"whatsapp:+{clean_digits}"
    from_wa = f"whatsapp:{CALLER_ID}"

    try:
        if text:
            msg = client.messages.create(
                from_=from_wa,
                to=clean_to,
                body=text
            )
            logger.info(f"Outbound WhatsApp text sent to {clean_to}: sid={msg.sid}")
        if media_url:
            msg = client.messages.create(
                from_=from_wa,
                to=clean_to,
                media_url=[media_url]
            )
            logger.info(f"Outbound WhatsApp audio sent to {clean_to}: sid={msg.sid}")
        return True, None
    except Exception as e:
        logger.error(f"Failed to send outbound WhatsApp to {clean_to}: {e}")
        return False, str(e)

def build_twiml(body: str, media_url: Optional[str] = None) -> str:
    escaped = (
        body.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
    )
    if media_url:
        # In WhatsApp, audio files cannot have text captions (WhatsApp discards <Body> when audio is present).
        # We deliver TWO distinct messages in the TwiML response:
        # 1. The formatted text translation
        # 2. The spoken voice audio note
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>
        <Body>{escaped}</Body>
    </Message>
    <Message>
        <Media>{media_url}</Media>
    </Message>
</Response>"""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>
        <Body>{escaped}</Body>
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
        "endpoints": ["/token", "/voice/outbound", "/voice/inbound", "/translate/speak", "/translate/audio", "/whatsapp", "/sms", "/sms/send", "/sms/history", "/audio/{id}"]
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

    # Block emergency numbers to prevent accidental $75 Twilio fee
    digits_only = re.sub(r'[^0-9]', '', to_number)
    if digits_only in ['911', '1911', '933', '112', '999']:
        logger.warning(f"Blocked emergency call attempt to {digits_only}")
        twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Joanna">Emergency 911 calls are not supported through Amestx Voice. Please hang up and dial 911 directly from your mobile phone or landline.</Say>
    <Hangup/>
</Response>"""
        return PlainResponse(content=twiml, media_type="application/xml")

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
# 1.5 LIVE CALL TRANSLATION & SPEECH SYNTHESIS
# ==========================================
@app.post("/translate/speak")
async def api_translate_and_speak(request: Request):
    """
    Receives text spoken/typed during a phone call, translates it,
    synthesizes a natural voice audio file, and returns the audio URL
    to be injected directly into the live phone call.
    """
    try:
        data = await request.json()
    except Exception:
        body = await request.body()
        data = urllib.parse.parse_qs(body.decode("utf-8", errors="replace"))
        data = {k: v[0] if isinstance(v, list) else v for k, v in data.items()}

    text = (data.get("text") or "").strip()
    source_lang = data.get("source_lang", "auto")
    target_lang = data.get("target_lang", "auto")

    if not text:
        return {"error": "Missing text parameter"}, 400

    if source_lang == "auto" or not source_lang:
        detected = detect_language(text)
        source_lang = detected
        target_lang = "es" if detected == "en" else "en"
    elif target_lang == "auto" or not target_lang:
        target_lang = "es" if source_lang == "en" else "en"

    translated = translate_text(text, source_lang, target_lang)
    audio_url = synthesize_speech(translated, target_lang)

    logger.info(f"In-Call Translation: '{text}' ({source_lang}) -> '{translated}' ({target_lang}) | audio: {audio_url}")

    return {
        "status": "success",
        "original_text": text,
        "translated_text": translated,
        "source_lang": source_lang,
        "target_lang": target_lang,
        "audio_url": audio_url
    }

@app.post("/translate/audio")
async def api_translate_audio(request: Request):
    """
    Receives incoming audio recorded from the live phone call (e.g. listener speaking Spanish),
    transcribes it using Google Cloud Speech-to-Text,
    translates it to English (or specified target language),
    and synthesizes natural voice audio for the caller to hear in the web dialer.
    """
    audio_bytes = None
    source_lang = "es"
    target_lang = "en"

    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            data = await request.json()
            if "audio_base64" in data and data["audio_base64"]:
                raw_b64 = data["audio_base64"]
                if "," in raw_b64:
                    raw_b64 = raw_b64.split(",", 1)[1]
                audio_bytes = base64.b64decode(raw_b64)
            source_lang = data.get("source_lang", "es")
            target_lang = data.get("target_lang", "en")
        except Exception as e:
            logger.error(f"Error parsing json audio: {e}")
            return {"status": "error", "message": f"Malformed JSON: {e}"}, 400
    else:
        audio_bytes = await request.body()
        params = request.query_params
        source_lang = params.get("source_lang", "es")
        target_lang = params.get("target_lang", "en")

    if not audio_bytes or len(audio_bytes) < 80:
        return {"status": "empty", "message": "No audio payload received"}, 400

    transcript, detected = transcribe_audio_bytes(audio_bytes, source_lang=source_lang)
    clean_transcript = transcript.strip()

    if not clean_transcript:
        logger.info("Speech recognition completed: no speech or silence detected.")
        return {
            "status": "no_speech",
            "message": "No speech detected in audio segment",
            "original_text": "",
            "translated_text": "",
            "audio_url": None
        }

    actual_source = detected if detected else source_lang
    actual_target = target_lang
    if actual_source == actual_target:
        actual_target = "en" if actual_source == "es" else "es"

    translated = translate_text(clean_transcript, actual_source, actual_target)
    audio_url = synthesize_speech(translated, actual_target)

    logger.info(f"Incoming Audio Translation: '{clean_transcript}' ({actual_source}) -> '{translated}' ({actual_target}) | audio: {audio_url}")

    return {
        "status": "success",
        "original_text": clean_transcript,
        "translated_text": translated,
        "source_lang": actual_source,
        "target_lang": actual_target,
        "audio_url": audio_url
    }

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

    from_raw = get_val("From") or ""
    body_text = get_val("Body")
    profile_name = get_val("ProfileName") or "User"
    media_url = get_val("MediaUrl0")
    media_type = get_val("MediaContentType0")

    from_digits = normalize_phone(from_raw)
    is_supervisor = (from_digits == SUPERVISOR_PHONE)
    is_crew = (from_digits in CREW_MEMBERS)
    crew_info = CREW_MEMBERS.get(from_digits)

    logger.info(f"Incoming WhatsApp from {profile_name} ({from_raw}, digits={from_digits}): body='{body_text}', media_url='{media_url}', is_sup={is_supervisor}, is_crew={is_crew}")

    # ==========================================
    # 1. VOICE NOTE / AUDIO PROCESSING
    # ==========================================
    if media_url:
        is_audio = False
        if media_type:
            mt = media_type.lower()
            if any(term in mt for term in ["audio", "ogg", "opus", "voice", "mp4", "amr"]):
                is_audio = True
        else:
            is_audio = True

        if is_audio:
            logger.info(f"Downloading WhatsApp voice note: {media_url} (type: {media_type})")
            audio_bytes = download_twilio_media(media_url)
            transcript, detected_lang = ("", "es")
            if audio_bytes:
                logger.info(f"Downloaded {len(audio_bytes)} audio bytes, transcribing...")
                transcript, detected_lang = transcribe_audio_bytes(
                    audio_bytes,
                    source_lang="en" if is_supervisor else "es"
                )

            if transcript:
                target_lang = "es" if detected_lang == "en" else "en"
                translated = translate_text(transcript, detected_lang, target_lang)
                audio_link = synthesize_speech(translated, target_lang)

                if is_supervisor:
                    # Supervisor voice note -> Deliver in Spanish to Crew
                    target_crew = CREW_MEMBERS.get(ACTIVE_CREW_PHONE, {"name": "Octavio"})
                    crew_text = (
                        f"🎙️ *Nota de Voz de {SUPERVISOR_NAME} (Supervisor)*:\n"
                        f"\"{translated}\""
                    )
                    sent, err = send_whatsapp_outbound(ACTIVE_CREW_PHONE, text=crew_text, media_url=audio_link)

                    if sent:
                        reply = (
                            f"✅ *Nota de Voz enviada a {target_crew['name']} (Crew)*:\n"
                            f"🇲🇽 \"{translated}\"\n\n"
                            f"_(Original voice: \"{transcript}\")_"
                        )
                    else:
                        reply = (
                            f"🎙️ *Traducción de tu Nota de Voz*:\n"
                            f"🇲🇽 \"{translated}\"\n\n"
                            f"⚠️ *Aviso de Entrega a {target_crew['name']}*:\n"
                            f"{target_crew['name']} aún no ha iniciado conversación con este número (+1 844-826-3789).\n"
                            f"👉 Pídele que envíe \"Hola\" a este número para activar la línea directa."
                        )
                    return PlainResponse(content=build_twiml(reply, audio_link), media_type="application/xml")

                elif is_crew:
                    # Crew voice note -> Deliver in English to Supervisor
                    crew_name = crew_info["name"] if crew_info else profile_name
                    sup_text = (
                        f"🎙️ *Crew Voice Note from {crew_name}*:\n"
                        f"🇺🇸 \"{translated}\"\n\n"
                        f"_(Original de {crew_name}: \"{transcript}\")_"
                    )
                    send_whatsapp_outbound(SUPERVISOR_PHONE, text=sup_text, media_url=audio_link)

                    reply = (
                        f"✅ *Nota de Voz entregada a {SUPERVISOR_NAME} (Supervisor)*:\n"
                        f"🇺🇸 \"{translated}\""
                    )
                    return PlainResponse(content=build_twiml(reply, audio_link), media_type="application/xml")

                else:
                    # Standalone user
                    if target_lang == "en":
                        reply = f"🎙️ *Voice Note from {profile_name}*:\n\"{transcript}\"\n\n🇺🇸 *English Translation*:\n\"{translated}\""
                    else:
                        reply = f"🎙️ *Nota de Voz de {profile_name}*:\n\"{transcript}\"\n\n🇲🇽 *Traducción al Español*:\n\"{translated}\""
                    logger.info(f"WhatsApp Voice Translated: '{transcript}' ({detected_lang}) -> '{translated}' ({target_lang})")
                    return PlainResponse(content=build_twiml(reply, audio_link), media_type="application/xml")
            else:
                reply = f"🎙️ *Amestx Voice*\nVoice note received from *{profile_name}*, but no speech could be transcribed.\nPlease speak clearly into the microphone or send text."
                return PlainResponse(content=build_twiml(reply), media_type="application/xml")

    # ==========================================
    # 2. TEXT MESSAGE PROCESSING
    # ==========================================
    clean_text = (body_text or "").strip()
    if not clean_text:
        reply = "📞 *Amestx Voice*\nSend any text or voice note in Spanish or English and I will translate it with both text and voice audio."
        return PlainResponse(content=build_twiml(reply), media_type="application/xml")

    # GREETING / ACTIVATION CHECK FOR CREW
    if is_crew:
        lower_txt = clean_text.lower()
        if any(w in lower_txt for w in ["hola", "buenos dias", "buenas tardes", "buenas noches", "start", "join", "hi"]):
            crew_name = crew_info["name"] if crew_info else "Octavio"
            reply = (
                f"👋 *¡Hola {crew_name}! Bienvenido a Amestx Voice.*\n\n"
                f"El puente de comunicación con *{SUPERVISOR_NAME}* está activo.\n"
                f"• Cualquier mensaje de texto o nota de voz que envíes aquí será traducido al inglés y entregado a {SUPERVISOR_NAME}.\n"
                f"• Los mensajes de {SUPERVISOR_NAME} te llegarán aquí traducidos al español con audio."
            )
            # Notify supervisor immediately that crew is online
            notify_sup = (
                f"🟢 *{crew_name} is now connected on WhatsApp!*\n"
                f"The 2-way bilingual bridge is active. Any message you send here will be forwarded to {crew_name} in Spanish."
            )
            send_whatsapp_outbound(SUPERVISOR_PHONE, text=notify_sup)
            return PlainResponse(content=build_twiml(reply), media_type="application/xml")

    lang = detect_language(clean_text)

    # A) SUPERVISOR MESSAGE -> Forward to Crew in Spanish
    if is_supervisor:
        target_crew = CREW_MEMBERS.get(ACTIVE_CREW_PHONE, {"name": "Octavio"})
        translated = translate_text(clean_text, "en", "es")
        audio_link = synthesize_speech(translated, "es")

        crew_msg = (
            f"👷 *Mensaje de {SUPERVISOR_NAME} (Supervisor)*:\n"
            f"\"{translated}\""
        )
        sent, err = send_whatsapp_outbound(ACTIVE_CREW_PHONE, text=crew_msg, media_url=audio_link)

        if sent:
            reply = (
                f"✅ *Enviado a {target_crew['name']} (Crew)*:\n"
                f"🇲🇽 \"{translated}\"\n\n"
                f"_(Original: \"{clean_text}\")_"
            )
        else:
            reply = (
                f"🇲🇽 *Traducción al Español*:\n"
                f"\"{translated}\"\n\n"
                f"⚠️ *Aviso de Entrega a {target_crew['name']}*:\n"
                f"{target_crew['name']} aún no ha iniciado conversación con este número (+1 844-826-3789).\n"
                f"👉 Por favor pide a {target_crew['name']} que envíe \"Hola\" al +1 (844) 826-3789 en WhatsApp una vez para activar la línea."
            )
        logger.info(f"Relayed from {SUPERVISOR_NAME} to {target_crew['name']}: sent={sent}")
        return PlainResponse(content=build_twiml(reply, audio_link), media_type="application/xml")

    # B) CREW MESSAGE -> Forward to Supervisor in English
    elif is_crew:
        crew_name = crew_info["name"] if crew_info else "Octavio"
        translated = translate_text(clean_text, "es", "en")
        audio_link = synthesize_speech(translated, "en")

        sup_msg = (
            f"👷 *Crew Reply from {crew_name}*:\n"
            f"🇺🇸 \"{translated}\"\n\n"
            f"_(Original de {crew_name}: \"{clean_text}\")_"
        )
        send_whatsapp_outbound(SUPERVISOR_PHONE, text=sup_msg, media_url=audio_link)

        reply = (
            f"✅ *Entregado a {SUPERVISOR_NAME} (Supervisor)*:\n"
            f"🇺🇸 \"{translated}\""
        )
        logger.info(f"Relayed from {crew_name} to {SUPERVISOR_NAME}")
        return PlainResponse(content=build_twiml(reply, audio_link), media_type="application/xml")

    # C) DEFAULT STANDALONE TRANSLATION
    else:
        if lang == "es":
            translated = translate_text(clean_text, "es", "en")
            audio_link = synthesize_speech(translated, "en")
            reply = f"🇺🇸 *English Translation*:\n\"{translated}\"\n\n_(Original de {profile_name}: \"{clean_text}\")_"
        else:
            translated = translate_text(clean_text, "en", "es")
            audio_link = synthesize_speech(translated, "es")
            reply = f"🇲🇽 *Traducción al Español*:\n\"{translated}\"\n\n_(Original from {profile_name}: \"{clean_text}\")_"

        logger.info(f"WhatsApp Text Translated: '{clean_text}' ({lang}) -> '{translated}' | audio: {audio_link}")
        return PlainResponse(content=build_twiml(reply, audio_link), media_type="application/xml")

# ==========================================
# 3. DIRECT SMS & MMS TEXTING ENDPOINTS
# ==========================================
SMS_HISTORY = []

def record_sms_message(direction: str, from_num: str, to_num: str, body: str, translation: str = "", sid: str = "", status: str = "delivered"):
    clean_from = normalize_phone(from_num)
    clean_to = normalize_phone(to_num)
    entry = {
        "id": sid or str(uuid.uuid4()),
        "direction": direction,
        "from": clean_from,
        "to": clean_to,
        "body": body,
        "translation": translation,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "status": status
    }
    SMS_HISTORY.append(entry)
    if len(SMS_HISTORY) > 100:
        SMS_HISTORY.pop(0)
    return entry

@app.post("/sms/send")
@app.post("/api/sms/send")
async def send_sms_outbound(request: Request):
    try:
        data = await request.json()
        to_number = data.get("to") or data.get("recipient") or ""
        message_text = (data.get("message") or data.get("text") or "").strip()
        translate = data.get("translate", True)

        if not to_number or not message_text:
            return {"success": False, "error": "Recipient phone number and message text are required."}

        client = get_twilio_client()
        if not client:
            logger.error("Twilio client credentials not configured on server")
            return {"success": False, "error": "Twilio server credentials not configured."}

        clean_digits = normalize_phone(to_number)
        clean_to = f"+{clean_digits}"

        # Bilingual Translation:
        # Detect language of message:
        # If English, translate to Spanish and attach translation.
        # If Spanish, translate to English and attach translation.
        translation_text = ""
        full_body = message_text
        if translate:
            src_lang = detect_language(message_text)
            if src_lang == "es":
                translation_text = translate_text(message_text, "es", "en")
                full_body = f"{message_text}\n\n[Traducción EN]: {translation_text}"
            else:
                translation_text = translate_text(message_text, "en", "es")
                full_body = f"{message_text}\n\n[Traducción ES]: {translation_text}"

        logger.info(f"Sending outbound SMS to {clean_to} from {CALLER_ID}: {full_body[:80]}...")
        msg = client.messages.create(
            from_=CALLER_ID,
            to=clean_to,
            body=full_body
        )
        logger.info(f"Outbound SMS sent to {clean_to}: sid={msg.sid}, status={msg.status}")

        record_sms_message(
            direction="outbound",
            from_num=CALLER_ID,
            to_num=clean_to,
            body=message_text,
            translation=translation_text,
            sid=msg.sid,
            status=msg.status or "sent"
        )

        return {
            "success": True,
            "sid": msg.sid,
            "to": clean_to,
            "status": msg.status,
            "original": message_text,
            "translation": translation_text
        }
    except Exception as e:
        logger.error(f"Error sending outbound SMS: {e}")
        return {"success": False, "error": str(e)}

@app.get("/sms/status/{sid}")
async def get_sms_status(sid: str):
    client = get_twilio_client()
    if not client:
        return {"error": "Twilio client not configured"}
    try:
        msg = client.messages(sid).fetch()
        return {
            "sid": msg.sid,
            "status": msg.status,
            "error_code": msg.error_code,
            "error_message": msg.error_message,
            "to": msg.to,
            "from": msg.from_,
            "date_sent": str(msg.date_sent),
            "date_updated": str(msg.date_updated)
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/twilio/numbers")
async def list_twilio_numbers():
    client = get_twilio_client()
    if not client:
        return {"error": "Twilio client not configured"}
    try:
        incoming = client.incoming_phone_numbers.list(limit=20)
        numbers = []
        for n in incoming:
            numbers.append({
                "phone_number": n.phone_number,
                "friendly_name": n.friendly_name,
                "capabilities": n.capabilities
            })
        return {"numbers": numbers}
    except Exception as e:
        return {"error": str(e)}

@app.get("/sms/history")
async def get_sms_history(phone: Optional[str] = None):
    clean_target = normalize_phone(phone) if phone else None
    if not clean_target:
        return {"messages": SMS_HISTORY[-30:]}
    filtered = [
        m for m in SMS_HISTORY
        if m["to"] == clean_target or m["from"] == clean_target
    ]
    return {"messages": filtered}

@app.post("/sms")
@app.post("/sms/inbound")
async def sms_inbound(request: Request):
    body_bytes = await request.body()
    parsed = urllib.parse.parse_qs(body_bytes.decode("utf-8", errors="replace"))
    body_text = parsed.get("Body", [""])[0].strip()
    from_number = parsed.get("From", [""])[0]

    if not body_text:
        return PlainResponse(content="<Response></Response>", media_type="application/xml")

    clean_from_digits = normalize_phone(from_number)
    lang = detect_language(body_text)
    if lang == "es":
        trans = translate_text(body_text, "es", "en")
        reply = f"[Amestx Voice Translation]\n🇺🇸 EN: \"{trans}\""
    else:
        trans = translate_text(body_text, "en", "es")
        reply = f"[Amestx Voice Translation]\n🇲🇽 ES: \"{trans}\""

    logger.info(f"SMS from {from_number}: '{body_text}' -> '{trans}'")

    # Record in history
    record_sms_message(
        direction="inbound",
        from_num=from_number,
        to_num=CALLER_ID,
        body=body_text,
        translation=trans,
        status="received"
    )

    # Forward to supervisor personal mobile phone (+1 832-837-9801) if not from supervisor
    if clean_from_digits != SUPERVISOR_PHONE:
        try:
            client = get_twilio_client()
            if client:
                fwd_body = f"📩 [Amestx SMS from {from_number}]:\n\"{body_text}\"\n\n[Translation]:\n\"{trans}\""
                client.messages.create(
                    from_=CALLER_ID,
                    to=f"+{SUPERVISOR_PHONE}",
                    body=fwd_body
                )
                logger.info(f"Forwarded SMS from {from_number} to Supervisor +{SUPERVISOR_PHONE}")
        except Exception as fwd_err:
            logger.warning(f"Failed to forward SMS to supervisor: {fwd_err}")

    return PlainResponse(content=build_twiml(reply), media_type="application/xml")

@app.get("/audio/{filename}")
def get_audio(filename: str):
    clean_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '', filename)
    file_path = os.path.join(AUDIO_DIR, clean_name)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/mpeg", headers={"Cache-Control": "public, max-age=86400"})
    return PlainResponse(content="Audio not found", status_code=404)

# ==========================================
# 4. 15-DAY FREE TRIAL REGISTRATION & MONITORING
# ==========================================
TRIALS_FILE = os.path.join(os.path.dirname(__file__), "trials_db.json")

def load_trials():
    if os.path.exists(TRIALS_FILE):
        try:
            with open(TRIALS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_trials(trials):
    try:
        with open(TRIALS_FILE, "w", encoding="utf-8") as f:
            json.dump(trials, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving trials: {e}")

@app.post("/trial/register")
async def register_trial(request: Request):
    """
    Registers a new 15-day free trial user.
    """
    try:
        data = await request.json()
    except Exception:
        body = await request.body()
        data = urllib.parse.parse_qs(body.decode("utf-8", errors="replace"))
        data = {k: v[0] if isinstance(v, list) else v for k, v in data.items()}

    email = (data.get("email") or "").strip().lower()
    first_name = (data.get("firstName") or data.get("first_name") or "").strip()
    last_name = (data.get("lastName") or data.get("last_name") or "").strip()
    phone = (data.get("phone") or "").strip()
    company = (data.get("company") or "").strip()
    area_code = (data.get("areaCode") or data.get("area_code") or "844").strip()

    now = datetime.datetime.now(datetime.timezone.utc)
    expires_at = now + datetime.timedelta(days=15)

    trials = load_trials()
    existing = next((t for t in trials if t.get("email") == email and email), None)
    if existing:
        try:
            exp = datetime.datetime.fromisoformat(existing.get("expires_at"))
            days_left = max(0, int((exp - now).total_seconds() // 86400))
        except Exception:
            days_left = 0
        return {
            "status": "existing",
            "message": f"Welcome back, {existing.get('first_name', 'User')}! You have {days_left} days remaining in your trial.",
            "trial": existing,
            "days_left": days_left,
            "is_valid": days_left > 0
        }

    trial_record = {
        "id": str(uuid.uuid4())[:8],
        "first_name": first_name or "Subscriber",
        "last_name": last_name,
        "full_name": f"{first_name} {last_name}".strip() or "Subscriber",
        "email": email,
        "phone": phone,
        "company": company or "Independent",
        "area_code": area_code,
        "started_at": now.isoformat(),
        "expires_at": expires_at.isoformat(),
        "days_total": 15,
        "status": "active"
    }
    trials.append(trial_record)
    save_trials(trials)
    logger.info(f"New 15-day trial registered: {email} | {trial_record['full_name']} | {company} | {phone}")
    return {
        "status": "success",
        "message": f"Welcome to your 15-day free trial, {trial_record['full_name']}!",
        "trial": trial_record,
        "days_left": 15,
        "is_valid": True
    }

@app.get("/trial/list")
def list_trials():
    """
    Returns the list of all trial registrations and their remaining days.
    """
    trials = load_trials()
    now = datetime.datetime.now(datetime.timezone.utc)
    results = []
    for t in trials:
        try:
            exp = datetime.datetime.fromisoformat(t.get("expires_at"))
            diff_sec = (exp - now).total_seconds()
            days_left = max(0, int(diff_sec // 86400))
            is_active = diff_sec > 0
        except Exception:
            days_left = 0
            is_active = False
        results.append({
            **t,
            "days_left": days_left,
            "is_active": is_active
        })
    return {
        "total_trials": len(results),
        "active_trials": sum(1 for r in results if r["is_active"]),
        "trials": sorted(results, key=lambda x: x.get("started_at", ""), reverse=True)
    }

@app.get("/trial/dashboard")
def trial_dashboard():
    """
    Web dashboard to monitor all 15-day free trial users and expiration dates.
    """
    trials = load_trials()
    now = datetime.datetime.now(datetime.timezone.utc)
    rows_html = ""
    active_count = 0
    for t in sorted(trials, key=lambda x: x.get("started_at", ""), reverse=True):
        try:
            exp = datetime.datetime.fromisoformat(t.get("expires_at"))
            diff_sec = (exp - now).total_seconds()
            days_left = max(0, int(diff_sec // 86400))
            is_active = diff_sec > 0
        except Exception:
            days_left = 0
            is_active = False
        if is_active:
            active_count += 1
            badge = f'<span style="background:#dcfce7;color:#15803d;padding:4px 10px;border-radius:12px;font-weight:700;font-size:11px;">Active ({days_left}d left)</span>'
        else:
            badge = '<span style="background:#fee2e2;color:#b91c1c;padding:4px 10px;border-radius:12px;font-weight:700;font-size:11px;">Expired</span>'
        started = t.get("started_at", "")[:10]
        expires = t.get("expires_at", "")[:10]
        rows_html += f"""
        <tr style="border-bottom:1px solid #e2e8f0;">
            <td style="padding:12px;font-weight:600;">{t.get('full_name')}</td>
            <td style="padding:12px;"><a href="mailto:{t.get('email')}" style="color:#2563eb;text-decoration:none;">{t.get('email')}</a></td>
            <td style="padding:12px;"><a href="tel:{t.get('phone')}" style="color:#2563eb;text-decoration:none;">{t.get('phone')}</a></td>
            <td style="padding:12px;">{t.get('company')}</td>
            <td style="padding:12px;color:#64748b;">{started}</td>
            <td style="padding:12px;color:#64748b;">{expires}</td>
            <td style="padding:12px;">{badge}</td>
        </tr>
        """
    if not rows_html:
        rows_html = '<tr><td colspan="7" style="padding:32px;text-align:center;color:#64748b;font-weight:500;">No trial registrations yet.</td></tr>'

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Amestx Voice • 15-Day Trial Monitor</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f8fafc; color: #0f172a; padding: 32px 16px; margin: 0; }}
            .container {{ max-width: 1040px; margin: 0 auto; }}
            .card {{ background: #fff; border: 1px solid #e2e8f0; border-radius: 20px; padding: 28px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }}
            h1 {{ margin: 0 0 6px 0; font-size: 24px; font-weight: 800; }}
            .stats {{ display: flex; gap: 16px; margin: 24px 0; flex-wrap: wrap; }}
            .stat-box {{ background: #f1f5f9; padding: 18px 24px; border-radius: 14px; flex: 1; min-width: 180px; }}
            .stat-val {{ font-size: 32px; font-weight: 900; color: #1e40af; }}
            .stat-label {{ font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; margin-top: 4px; letter-spacing: 0.5px; }}
            table {{ width: 100%; border-collapse: collapse; text-align: left; font-size: 13px; }}
            th {{ background: #f8fafc; padding: 12px; font-size: 11px; text-transform: uppercase; color: #475569; letter-spacing: 0.5px; border-bottom: 2px solid #e2e8f0; font-weight: 800; }}
            .refresh-btn {{ background: #2563eb; color: #fff; border: none; padding: 10px 18px; border-radius: 10px; font-weight: 700; cursor: pointer; font-size: 13px; transition: 0.2s; }}
            .refresh-btn:hover {{ background: #1d4ed8; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="card">
                <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
                    <div>
                        <h1>📞 Amestx Voice — Trial Users Monitor</h1>
                        <p style="color:#64748b;margin:0;font-size:13px;">Live monitoring of 15-day free trial registrations, company info, and expiration dates.</p>
                    </div>
                    <button onclick="location.reload()" class="refresh-btn">🔄 Refresh Data</button>
                </div>

                <div class="stats">
                    <div class="stat-box">
                        <div class="stat-val">{len(trials)}</div>
                        <div class="stat-label">Total Users Registered</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-val" style="color:#15803d;">{active_count}</div>
                        <div class="stat-label">Active 15-Day Trials</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-val" style="color:#b91c1c;">{len(trials) - active_count}</div>
                        <div class="stat-label">Expired Trials</div>
                    </div>
                </div>

                <div style="overflow-x:auto;">
                    <table>
                        <thead>
                            <tr>
                                <th>Subscriber Name</th>
                                <th>Email</th>
                                <th>Phone</th>
                                <th>Company</th>
                                <th>Started Date</th>
                                <th>Expires Date</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rows_html}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
