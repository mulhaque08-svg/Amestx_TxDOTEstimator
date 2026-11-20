/**
 * Amestx Communicator - Real-Time Job Site Voice Translator
 * Two-Phone Peer Sync over WebSockets (MQTT) + Web Speech API + Instant Translation
 */

class AmestxCommunicator {
    constructor() {
        this.roomPin = null;
        this.senderId = 'user_' + Math.random().toString(36).substring(2, 9);
        this.isHost = false;
        this.isSessionLocked = false;
        this.partnerId = null;
        this.pendingRequestData = null;
        this.isConnected = false;
        this.isPartnerConnected = false;
        this.autoVoiceRead = true;
        
        // Default Languages: Me = English, Partner = Spanish
        this.myLang = 'en-US';
        this.partnerLang = 'es-US';

        this.mqttClient = null;
        this.mqttBrokerUrl = 'wss://broker.emqx.io:8084/mqtt'; // Public SSL WebSocket Broker
        this.mqttTopic = null;

        // Speech Recognition & Audio State
        this.recognition = null;
        this.isRecording = false;
        this.isStartingRec = false;
        this.speechTranscript = '';
        this.currentInterim = '';
        this.silenceTimeout = null;
        this.audioUnlocked = false;

        // Message Deduplication & Sending Lock
        this.receivedMessageIds = new Set();
        this.isSendingMessage = false;

        this.initDOM();
        this.initAudioUnlock();
        this.initSpeechRecognition();
        this.initEventListeners();
        this.checkUrlRoomParam();
    }

    initDOM() {
        // Badges & Buttons
        this.statusBadge = document.getElementById('connectionStatusBadge');
        this.statusText = document.getElementById('statusText');
        this.btnOpenPairing = document.getElementById('btnOpenPairing');
        this.headerRoomPin = document.getElementById('headerRoomPin');
        this.btnDisconnect = document.getElementById('btnDisconnect');
        
        // Security Approval Modal
        this.approvalModal = document.getElementById('approvalModal');
        this.reqPartnerLang = document.getElementById('reqPartnerLang');
        this.reqPartnerPin = document.getElementById('reqPartnerPin');
        this.btnAcceptPairing = document.getElementById('btnAcceptPairing');
        this.btnDeclinePairing = document.getElementById('btnDeclinePairing');
        
        // Languages
        this.myLanguageSelect = document.getElementById('myLanguageSelect');
        this.partnerLanguageSelect = document.getElementById('partnerLanguageSelect');
        this.btnSwapLanguages = document.getElementById('btnSwapLanguages');
        this.btnVoiceAutoRead = document.getElementById('btnVoiceAutoRead');

        // Chat
        this.chatFeed = document.getElementById('chatFeed');
        this.welcomeCard = document.getElementById('welcomeCard');
        this.btnStartPairingHero = document.getElementById('btnStartPairingHero');

        // Controls
        this.btnPushToTalk = document.getElementById('btnPushToTalk');
        this.talkButtonText = document.getElementById('talkButtonText');
        this.talkMicIcon = document.getElementById('talkMicIcon');
        this.interimBanner = document.getElementById('interimBanner');
        this.interimText = document.getElementById('interimText');

        // Quick Chips & Typing
        this.chips = document.querySelectorAll('.chip');
        this.btnToggleType = document.getElementById('btnToggleType');
        this.typeDrawer = document.getElementById('typeDrawer');
        this.typeTextInput = document.getElementById('typeTextInput');
        this.btnSendTyped = document.getElementById('btnSendTyped');
        this.btnClearChat = document.getElementById('btnClearChat');

        // Modal
        this.pairingModal = document.getElementById('pairingModal');
        this.btnCloseModal = document.getElementById('btnCloseModal');
        this.createdPinDigits = document.getElementById('createdPinDigits');
        this.qrCodeContainer = document.getElementById('qrCodeContainer');
        this.btnCopyShareLink = document.getElementById('btnCopyShareLink');
        
        this.pinInputs = [
            document.getElementById('pinD1'),
            document.getElementById('pinD2'),
            document.getElementById('pinD3'),
            document.getElementById('pinD4')
        ];
        this.btnSubmitJoinPin = document.getElementById('btnSubmitJoinPin');

        // Invite Feature Elements
        this.btnHeaderInvite = document.getElementById('btnHeaderInvite');
        this.btnInviteWhatsApp = document.getElementById('btnInviteWhatsApp');
        this.btnInviteHero = document.getElementById('btnInviteHero');
        this.welcomePhoneInput = document.getElementById('welcomePhoneInput');
        this.btnWelcomeSendSms = document.getElementById('btnWelcomeSendSms');
        this.invitePhoneInput = document.getElementById('invitePhoneInput');
        this.btnSendSmsInvite = document.getElementById('btnSendSmsInvite');
        this.btnShareNativeInvite = document.getElementById('btnShareNativeInvite');

        // Invitation Arrival Modal (For Friend Opening Link)
        this.invitedArrivalModal = document.getElementById('invitedArrivalModal');
        this.invitedRoomPinDisplay = document.getElementById('invitedRoomPinDisplay');
        this.invitedMyLangSelect = document.getElementById('invitedMyLangSelect');
        this.btnAcceptInvitation = document.getElementById('btnAcceptInvitation');
        this.pendingInvitedRoom = null;
    }

    initAudioUnlock() {
        const unlock = () => {
            if (this.audioUnlocked) return;
            this.audioUnlocked = true;
            try {
                if ('speechSynthesis' in window) {
                    const silentUtterance = new SpeechSynthesisUtterance(' ');
                    silentUtterance.volume = 0.01;
                    window.speechSynthesis.speak(silentUtterance);
                }
            } catch (e) {}
        };
        window.addEventListener('touchstart', unlock, { once: true, passive: true });
        window.addEventListener('click', unlock, { once: true, passive: true });
    }

    initSpeechRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {
            this.recognition = new SpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.interimResults = true;
            this.recognition.lang = this.myLang;

            this.recognition.onstart = () => {
                this.isRecording = true;
                this.isStartingRec = false;
                this.btnPushToTalk.classList.add('recording');
                this.talkButtonText.textContent = "LISTENING... (TAP TO SEND)";
                this.interimBanner.classList.add('active');
                this.interimText.textContent = "Listening to your voice...";
                this.vibrate([60]);
            };

            this.recognition.onresult = (event) => {
                let interim = '';
                let final = '';

                for (let i = event.resultIndex; i < event.results.length; ++i) {
                    if (event.results[i].isFinal) {
                        final += event.results[i][0].transcript;
                    } else {
                        interim += event.results[i][0].transcript;
                    }
                }

                this.currentInterim = interim;

                if (final) {
                    this.speechTranscript = (this.speechTranscript ? this.speechTranscript + ' ' : '') + final;
                    this.currentInterim = '';
                }

                const liveDisplay = ((this.speechTranscript || '') + ' ' + (interim || '')).trim();
                if (liveDisplay) {
                    this.interimText.textContent = `"${liveDisplay}"`;
                }

                // Automatic silence detector: if user pauses speaking for 1.8 seconds, auto-send!
                clearTimeout(this.silenceTimeout);
                this.silenceTimeout = setTimeout(() => {
                    const fullSpoken = ((this.speechTranscript || '') + ' ' + (this.currentInterim || '')).trim();
                    if (this.isRecording && fullSpoken.length > 0) {
                        console.log("Auto-sending after speech pause...");
                        this.stopRecordingAndSend();
                    }
                }, 1800);
            };

            this.recognition.onerror = (event) => {
                console.warn('Speech recognition event error:', event.error);
                clearTimeout(this.silenceTimeout);
                this.isRecording = false;
                this.isStartingRec = false;
                this.btnPushToTalk.classList.remove('recording');
                this.talkButtonText.textContent = "TAP TO TALK";
                this.interimBanner.classList.remove('active');

                if (event.error === 'not-allowed') {
                    alert("Microphone permission was not allowed.\nPlease allow microphone access in your browser settings to speak.");
                } else if (event.error === 'no-speech') {
                    this.interimText.textContent = "No speech detected. Tap mic to try again.";
                }
            };

            this.recognition.onend = () => {
                clearTimeout(this.silenceTimeout);
                this.isRecording = false;
                this.isStartingRec = false;
                this.btnPushToTalk.classList.remove('recording');
                this.finishAndSendTranscript();
            };
        } else {
            console.warn("Web Speech API not supported on this browser.");
        }
    }

    initEventListeners() {
        // Modal Controls
        if (this.btnOpenPairing) this.btnOpenPairing.addEventListener('click', () => this.openPairingModal());
        if (this.btnStartPairingHero) this.btnStartPairingHero.addEventListener('click', () => this.openPairingModal());
        if (this.btnCloseModal) this.btnCloseModal.addEventListener('click', () => this.closePairingModal());

        // 4-Digit Input auto-advancement
        if (this.pinInputs) {
            this.pinInputs.forEach((input, idx) => {
                if (!input) return;
                input.addEventListener('input', (e) => {
                    const val = e.target.value;
                    if (val.length >= 1) {
                        input.value = val.slice(-1);
                        if (idx < 3 && this.pinInputs[idx + 1]) {
                            this.pinInputs[idx + 1].focus();
                        } else {
                            this.handleJoinFromInputs();
                        }
                    }
                });

                input.addEventListener('keydown', (e) => {
                    if (e.key === 'Backspace' && !input.value && idx > 0 && this.pinInputs[idx - 1]) {
                        this.pinInputs[idx - 1].focus();
                    }
                });
            });
        }

        if (this.btnSubmitJoinPin) this.btnSubmitJoinPin.addEventListener('click', () => this.handleJoinFromInputs());

        // Security Approval Modal Buttons
        if (this.btnAcceptPairing) this.btnAcceptPairing.addEventListener('click', () => this.acceptPairingRequest());
        if (this.btnDeclinePairing) this.btnDeclinePairing.addEventListener('click', () => this.declinePairingRequest());

        // Disconnect / End Call Button
        if (this.btnDisconnect) {
            this.btnDisconnect.addEventListener('click', () => {
                if (confirm("Disconnect and end this call?")) {
                    this.endSession(true);
                }
            });
        }

        // Direct WhatsApp 1-Tap Invite Button
        if (this.btnInviteWhatsApp) {
            this.btnInviteWhatsApp.addEventListener('click', () => this.sendWhatsAppInvite());
        }

        // Invite Buttons
        if (this.btnHeaderInvite) {
            this.btnHeaderInvite.addEventListener('click', () => this.triggerInviteShare());
        }
        if (this.btnInviteHero) {
            this.btnInviteHero.addEventListener('click', () => this.triggerInviteShare());
        }
        if (this.welcomePhoneInput) {
            this.welcomePhoneInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.sendWelcomeSms();
            });
        }
        if (this.btnWelcomeSendSms) {
            this.btnWelcomeSendSms.addEventListener('click', () => this.sendWelcomeSms());
        }
        if (this.btnSendSmsInvite) {
            this.btnSendSmsInvite.addEventListener('click', () => this.sendSmsInvite());
        }
        if (this.btnShareNativeInvite) {
            this.btnShareNativeInvite.addEventListener('click', () => this.triggerInviteShare());
        }
        if (this.btnAcceptInvitation) {
            this.btnAcceptInvitation.addEventListener('click', () => this.handleAcceptInvitedArrival());
        }

        // Copy Share Link (Guarded)
        if (this.btnCopyShareLink) {
            this.btnCopyShareLink.addEventListener('click', () => {
                const url = this.getCallUrl();
                navigator.clipboard.writeText(url).then(() => {
                    alert(`✅ Call link copied to clipboard!\n\nSend this link to your friend:\n${url}`);
                }).catch(() => {
                    prompt("Copy this direct call link:", url);
                });
            });
        }

        // Language Selectors
        this.myLanguageSelect.addEventListener('change', (e) => {
            this.myLang = e.target.value;
            if (this.recognition) this.recognition.lang = this.myLang;
            this.broadcastHandshake();
        });

        this.partnerLanguageSelect.addEventListener('change', (e) => {
            this.partnerLang = e.target.value;
        });

        this.btnSwapLanguages.addEventListener('click', () => {
            const temp = this.myLang;
            this.myLang = this.partnerLang;
            this.partnerLang = temp;

            this.myLanguageSelect.value = this.myLang;
            this.partnerLanguageSelect.value = this.partnerLang;

            if (this.recognition) this.recognition.lang = this.myLang;
            this.broadcastHandshake();
            this.vibrate([50]);
        });

        // Audio Auto-Speak Toggle
        this.btnVoiceAutoRead.addEventListener('click', () => {
            this.autoVoiceRead = !this.autoVoiceRead;
            this.btnVoiceAutoRead.classList.toggle('active', this.autoVoiceRead);
            this.btnVoiceAutoRead.querySelector('i').className = this.autoVoiceRead ? 'fa-solid fa-volume-high' : 'fa-solid fa-volume-xmark';
        });

        // Voice Recording Button: Tap to Talk / Hold to Talk supported seamlessly
        let pressTimer = null;
        let isLongPress = false;

        const handleTalkDown = (e) => {
            if (e && e.type === 'touchstart') e.preventDefault();
            this.initAudioUnlock();

            // If already recording in tap toggle mode, a tap stops and sends immediately!
            if (this.isRecording) {
                this.stopRecordingAndSend();
                return;
            }

            isLongPress = false;
            clearTimeout(pressTimer);
            pressTimer = setTimeout(() => {
                isLongPress = true;
            }, 350);

            this.startRecording();
        };

        const handleTalkUp = (e) => {
            if (e && e.type === 'touchend') e.preventDefault();
            clearTimeout(pressTimer);

            if (isLongPress) {
                // User held down like a walkie-talkie for >350ms: release sends it!
                this.stopRecordingAndSend();
            } else {
                // User tapped: keep listening until they tap again or pause speaking!
                console.log("Tap-to-talk listening...");
            }
        };

        if (this.btnPushToTalk) {
            if ('ontouchstart' in window) {
                this.btnPushToTalk.addEventListener('touchstart', handleTalkDown, { passive: false });
                this.btnPushToTalk.addEventListener('touchend', handleTalkUp, { passive: false });
            } else {
                this.btnPushToTalk.addEventListener('mousedown', handleTalkDown);
                this.btnPushToTalk.addEventListener('mouseup', handleTalkUp);
            }
        }

        // Keyboard Drawer
        this.btnToggleType.addEventListener('click', () => {
            this.typeDrawer.classList.toggle('open');
            if (this.typeDrawer.classList.contains('open')) {
                this.typeTextInput.focus();
            }
        });

        this.btnSendTyped.addEventListener('click', () => this.sendTypedMessage());
        this.typeTextInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendTypedMessage();
        });

        // Quick Phrase Chips
        this.chips.forEach(chip => {
            chip.addEventListener('click', () => {
                const text = chip.getAttribute('data-text');
                this.handleOutgoingMessage(text);
                this.vibrate([60]);
            });
        });

        // Clear Chat
        this.btnClearChat.addEventListener('click', () => {
            if (confirm("Clear all conversation messages?")) {
                const msgs = this.chatFeed.querySelectorAll('.chat-msg');
                msgs.forEach(m => m.remove());
                this.welcomeCard.style.display = 'block';
            }
        });
    }

    checkUrlRoomParam() {
        const urlParams = new URLSearchParams(window.location.search);
        const callFromUrl = urlParams.get('call') || urlParams.get('room');
        if (callFromUrl && callFromUrl.length >= 4) {
            this.isHost = false;
            // DIRECT INSTANT AUTO-JOIN (Zero modals, zero PIN entry!)
            console.log(`Auto-joining call ${callFromUrl}...`);
            this.connectToRoom(callFromUrl);
        } else {
            // Silently generate call session in background so Host is ready to invite with 1 tap!
            this.generateNewRoomPin();
        }
    }

    openPairingModal() {
        if (!this.roomPin) {
            this.generateNewRoomPin();
        }
        this.pairingModal.classList.add('open');
    }

    closePairingModal() {
        this.pairingModal.classList.remove('open');
    }

    generateNewRoomPin() {
        this.isHost = true;
        this.isSessionLocked = false;
        this.partnerId = null;
        this.roomPin = Math.floor(1000 + Math.random() * 9000).toString();
        this.createdPinDigits.textContent = this.roomPin;
        this.renderQrCode();
        this.connectToRoom(this.roomPin);
    }

    renderQrCode() {
        if (!window.QRCode) return;
        this.qrCodeContainer.innerHTML = '';
        const targetUrl = `${window.location.origin}${window.location.pathname}?call=${this.roomPin}`;
        new QRCode(this.qrCodeContainer, {
            text: targetUrl,
            width: 150,
            height: 150,
            colorDark: "#000000",
            colorLight: "#ffffff",
            correctLevel: QRCode.CorrectLevel.M
        });
    }

    handleJoinFromInputs() {
        const pin = this.pinInputs.map(input => input.value).join('');
        if (pin.length === 4) {
            this.isHost = false;
            this.closePairingModal();
            this.connectToRoom(pin);
        } else {
            alert("Please enter a valid 4-digit PIN.");
        }
    }

    connectToRoom(pin) {
        this.roomPin = pin;
        if (this.headerRoomPin) this.headerRoomPin.textContent = `Call: ${pin}`;
        if (this.btnHeaderInvite) this.btnHeaderInvite.style.display = 'none';
        this.mqttTopic = `amestx/communicator/room/${pin}`;

        this.updateConnectionStatus('waiting', 'Ready');

        if (this.mqttClient) {
            try { this.mqttClient.end(); } catch (e) {}
        }

        console.log(`Connecting to MQTT broker for call ${pin}...`);
        
        try {
            this.mqttClient = mqtt.connect(this.mqttBrokerUrl, {
                clientId: this.senderId,
                clean: true,
                reconnectPeriod: 2000
            });

            this.mqttClient.on('connect', () => {
                console.log('Connected to MQTT WebSocket Broker!');
                this.isConnected = true;
                
                this.mqttClient.subscribe(this.mqttTopic, (err) => {
                    if (!err) {
                        console.log(`Subscribed to topic: ${this.mqttTopic}`);
                        if (this.isHost) {
                            this.updateConnectionStatus('waiting', 'Ready');
                        } else {
                            this.updateConnectionStatus('waiting', 'Connecting...');
                            this.sendPairRequest();

                            // Auto-retry handshake up to 4 times every 1.2s in case host was connecting
                            let retries = 0;
                            const retryTimer = setInterval(() => {
                                retries++;
                                if (this.isPartnerConnected || retries >= 4 || !this.isConnected) {
                                    clearInterval(retryTimer);
                                } else {
                                    this.sendPairRequest();
                                }
                            }, 1200);
                        }
                    }
                });
            });

            this.mqttClient.on('message', (topic, payload) => {
                try {
                    const data = JSON.parse(payload.toString());
                    if (data.senderId !== this.senderId) {
                        this.handleIncomingMqttMessage(data);
                    }
                } catch (e) {
                    console.error("Failed to parse message:", e);
                }
            });

            this.mqttClient.on('error', (err) => {
                console.warn('MQTT Connection Error:', err);
            });

            this.mqttClient.on('close', () => {
                this.isConnected = false;
                this.updateConnectionStatus('disconnected', 'Off');
            });

        } catch (err) {
            console.error("MQTT Connect exception:", err);
        }
    }

    sendPairRequest() {
        if (!this.mqttClient || !this.isConnected) return;
        const payload = {
            type: 'PAIR_REQUEST',
            senderId: this.senderId,
            language: this.myLang,
            pin: this.roomPin,
            timestamp: Date.now()
        };
        this.mqttClient.publish(this.mqttTopic, JSON.stringify(payload));
    }

    broadcastHandshake() {
        if (!this.mqttClient || !this.isConnected) return;
        const payload = {
            type: 'HANDSHAKE',
            senderId: this.senderId,
            language: this.myLang,
            timestamp: Date.now()
        };
        this.mqttClient.publish(this.mqttTopic, JSON.stringify(payload));
    }

    handleIncomingMqttMessage(data) {
        // If message has a specific target recipient and it's not me, ignore
        if (data.targetId && data.targetId !== this.senderId) return;

        // 1. Host receives PAIR_REQUEST from Phone 2
        if (data.type === 'PAIR_REQUEST') {
            if (!this.isHost) return;

            // If session is ALREADY LOCKED to another partner -> REJECT ANY 3RD PARTY!
            if (this.isSessionLocked && this.partnerId && data.senderId !== this.partnerId) {
                this.mqttClient.publish(this.mqttTopic, JSON.stringify({
                    type: 'PAIR_REJECTED',
                    targetId: data.senderId,
                    senderId: this.senderId,
                    reason: 'LOCKED'
                }));
                return;
            }

            // AUTO-CONNECT FRIEND INSTANTLY (Zero friction, no pairing screens!)
            this.partnerId = data.senderId;
            this.isSessionLocked = true;
            this.isPartnerConnected = true;

            if (data.language && data.language !== this.myLang) {
                this.partnerLang = data.language;
                this.partnerLanguageSelect.value = data.language;
            }

            this.mqttClient.publish(this.mqttTopic, JSON.stringify({
                type: 'PAIR_ACCEPTED',
                targetId: data.senderId,
                senderId: this.senderId,
                hostLang: this.myLang
            }));

            if (this.approvalModal) this.approvalModal.classList.remove('open');
            if (this.pairingModal) this.pairingModal.classList.remove('open');
            if (this.invitedArrivalModal) this.invitedArrivalModal.classList.remove('open');
            if (this.welcomeCard) this.welcomeCard.style.display = 'none';
            this.updateConnectionStatus('locked', 'In Call');
            this.vibrate([100, 50, 100]);
            this.speakText("Friend joined call. Ready to talk.", this.myLang);
            return;
        }

        // 2. Partner receives PAIR_ACCEPTED from Host
        if (data.type === 'PAIR_ACCEPTED') {
            this.partnerId = data.senderId;
            this.isSessionLocked = true;
            this.isPartnerConnected = true;
            if (this.welcomeCard) this.welcomeCard.style.display = 'none';
            if (this.pairingModal) this.pairingModal.classList.remove('open');
            if (this.invitedArrivalModal) this.invitedArrivalModal.classList.remove('open');
            this.updateConnectionStatus('locked', 'In Call');

            if (data.hostLang && data.hostLang !== this.myLang) {
                this.partnerLang = data.hostLang;
                this.partnerLanguageSelect.value = data.hostLang;
            }

            this.vibrate([100, 50, 100]);
            this.speakText("Connected to call. Ready to talk.", this.myLang);
            return;
        }

        // 3. Partner receives PAIR_REJECTED
        if (data.type === 'PAIR_REJECTED') {
            if (data.reason === 'LOCKED') {
                alert("🚫 This call is already active between two other phones.");
            } else {
                alert("❌ Call connection was declined.");
            }
            this.updateConnectionStatus('disconnected', 'Off');
            if (this.mqttClient) {
                try { this.mqttClient.end(); } catch (e) {}
            }
            return;
        }

        // 4. HANDSHAKE (Language sync)
        if (data.type === 'HANDSHAKE') {
            if (data.language && data.language !== this.myLang) {
                this.partnerLang = data.language;
                this.partnerLanguageSelect.value = data.language;
            }
            return;
        }

        // 5. CHAT_MESSAGE: Strict 1-to-1 Security Check
        if (data.type === 'CHAT_MESSAGE') {
            // Drop rogue messages from anyone other than my approved partner
            if (this.isSessionLocked && this.partnerId && data.senderId !== this.partnerId) {
                console.warn("Security Alert: Blocked unauthorized third-party message!");
                return;
            }

            // Deduplication: prevent rendering or speaking duplicate messages
            if (this.receivedMessageIds.has(data.id)) return;
            this.receivedMessageIds.add(data.id);

            this.isPartnerConnected = true;
            this.updateConnectionStatus('locked', 'In Call');
            this.renderIncomingMessage(data);
            return;
        }

        // 6. SESSION_ENDED: Partner disconnected
        if (data.type === 'SESSION_ENDED') {
            alert("Call ended by your friend.");
            this.endSession(false);
            return;
        }
    }

    acceptPairingRequest() {
        if (!this.pendingRequestData) return;

        const data = this.pendingRequestData;
        this.partnerId = data.senderId;
        this.isSessionLocked = true;
        this.isPartnerConnected = true;

        if (data.language && data.language !== this.myLang) {
            this.partnerLang = data.language;
            this.partnerLanguageSelect.value = data.language;
        }

        // Send confirmation back to partner
        this.mqttClient.publish(this.mqttTopic, JSON.stringify({
            type: 'PAIR_ACCEPTED',
            targetId: data.senderId,
            senderId: this.senderId,
            hostLang: this.myLang
        }));

        this.approvalModal.classList.remove('open');
        this.closePairingModal();
        if (this.btnHeaderInvite) this.btnHeaderInvite.style.display = 'none';
        this.updateConnectionStatus('locked', `🔒 ${this.roomPin}`);
        this.vibrate([100, 50, 100]);
        this.speakText("Partner connected and locked", this.myLang);
    }

    declinePairingRequest() {
        if (!this.pendingRequestData) return;

        this.mqttClient.publish(this.mqttTopic, JSON.stringify({
            type: 'PAIR_REJECTED',
            targetId: this.pendingRequestData.senderId,
            senderId: this.senderId,
            reason: 'DECLINED'
        }));

        this.pendingRequestData = null;
        this.approvalModal.classList.remove('open');
    }

    endSession(broadcast = true) {
        if (broadcast && this.mqttClient && this.isConnected && this.mqttTopic) {
            try {
                this.mqttClient.publish(this.mqttTopic, JSON.stringify({
                    type: 'SESSION_ENDED',
                    senderId: this.senderId
                }));
            } catch (e) {}
        }

        this.isSessionLocked = false;
        this.partnerId = null;
        this.isPartnerConnected = false;
        this.roomPin = null;
        this.isHost = false;
        this.pendingRequestData = null;
        this.pendingInvitedRoom = null;

        if (this.mqttClient) {
            try { this.mqttClient.end(); } catch (e) {}
            this.mqttClient = null;
            this.isConnected = false;
        }

        if (this.headerRoomPin) this.headerRoomPin.textContent = 'Call';
        if (this.btnHeaderInvite) this.btnHeaderInvite.style.display = 'none';

        // Reset URL without reload
        if (window.history.replaceState) {
            window.history.replaceState({}, document.title, window.location.pathname);
        }

        if (this.approvalModal) this.approvalModal.classList.remove('open');
        if (this.pairingModal) this.pairingModal.classList.remove('open');
        if (this.invitedArrivalModal) this.invitedArrivalModal.classList.remove('open');
        if (this.welcomeCard) this.welcomeCard.style.display = 'block';

        this.speakText("Call ended.", this.myLang);

        // Instantly generate a fresh call room so Host is ready for the next call!
        this.generateNewRoomPin();
    }

    handleAcceptInvitedArrival() {
        if (!this.pendingInvitedRoom) return;
        this.myLang = this.invitedMyLangSelect.value;
        this.myLanguageSelect.value = this.myLang;
        if (this.recognition) this.recognition.lang = this.myLang;

        this.invitedArrivalModal.classList.remove('open');
        this.connectToRoom(this.pendingInvitedRoom);
    }

    getCallUrl() {
        if (!this.roomPin) {
            this.generateNewRoomPin();
        }
        return `${window.location.origin}${window.location.pathname}?call=${this.roomPin}`;
    }

    sendWhatsAppInvite() {
        const callUrl = this.getCallUrl();
        const msg = `Join my live voice translation call on Amestx:\n${callUrl}`;
        const whatsappUrl = `https://api.whatsapp.com/send?text=${encodeURIComponent(msg)}`;
        window.location.href = whatsappUrl;
    }

    sendWelcomeSms() {
        const rawPhone = this.welcomePhoneInput ? this.welcomePhoneInput.value.trim() : '';
        const phone = rawPhone.replace(/[^0-9+]/g, '');
        const callUrl = this.getCallUrl();
        const msg = `Join my live voice translation call on Amestx: ${callUrl}`;
        
        // iOS requires '&body=' when a number is present; Android requires '?body='
        const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
        let smsUrl;
        if (phone) {
            smsUrl = isIOS ? `sms:${phone}&body=${encodeURIComponent(msg)}` : `sms:${phone}?body=${encodeURIComponent(msg)}`;
        } else {
            smsUrl = isIOS ? `sms:&body=${encodeURIComponent(msg)}` : `sms:?body=${encodeURIComponent(msg)}`;
        }
        window.location.href = smsUrl;
    }

    sendSmsInvite() {
        const rawPhone = this.invitePhoneInput ? this.invitePhoneInput.value.trim() : '';
        const phone = rawPhone.replace(/[^0-9+]/g, '');
        const callUrl = this.getCallUrl();
        const msg = `Join my live voice translation call on Amestx: ${callUrl}`;
        
        const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
        let smsUrl;
        if (phone) {
            smsUrl = isIOS ? `sms:${phone}&body=${encodeURIComponent(msg)}` : `sms:${phone}?body=${encodeURIComponent(msg)}`;
        } else {
            smsUrl = isIOS ? `sms:&body=${encodeURIComponent(msg)}` : `sms:?body=${encodeURIComponent(msg)}`;
        }
        window.location.href = smsUrl;
    }

    triggerInviteShare() {
        const callUrl = this.getCallUrl();
        const fullMsg = `Join my live voice translation call on Amestx: ${callUrl}`;

        if (navigator.share) {
            // Avoid duplicate links: pass clean title & url property
            navigator.share({
                title: 'Amestx Communicator Call',
                text: 'Join my live voice translation call on Amestx:',
                url: callUrl
            }).catch((err) => {
                if (err && err.name !== 'AbortError') {
                    this.fallbackShare(callUrl, fullMsg);
                }
            });
        } else {
            this.fallbackShare(callUrl, fullMsg);
        }
    }

    fallbackShare(directUrl, msg) {
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(directUrl).then(() => {
                alert(`✅ Call link copied to clipboard!\n\nSend this link to your friend:\n${directUrl}`);
            }).catch(() => {
                prompt("Copy and send this call link to your friend:", directUrl);
            });
        } else {
            prompt("Copy and send this call link to your friend:", directUrl);
        }
    }

    updateConnectionStatus(state, label) {
        if (this.statusBadge) this.statusBadge.className = `status-badge ${state}`;
        if (this.statusText) this.statusText.textContent = label;

        // Disconnect / End Call button is visible during Ready and In Call
        if (this.btnDisconnect) {
            if (state === 'locked' || state === 'waiting') {
                this.btnDisconnect.style.display = 'inline-flex';
            } else {
                this.btnDisconnect.style.display = 'none';
            }
        }

        // Never display old PIN / Pair button in header
        if (this.btnOpenPairing) {
            this.btnOpenPairing.style.display = 'none';
        }
    }

    startRecording() {
        if (!this.recognition) {
            this.typeDrawer.classList.add('open');
            this.typeTextInput.focus();
            return;
        }

        if (this.isRecording || this.isStartingRec) return;
        this.isStartingRec = true;
        this.speechTranscript = '';

        try {
            this.recognition.lang = this.myLang;
            this.recognition.start();
        } catch (e) {
            console.warn("Speech recognition start issue:", e);
            this.isStartingRec = false;
        }
    }

    stopRecordingAndSend() {
        clearTimeout(this.silenceTimeout);
        if (!this.recognition) return;

        if (this.isRecording || this.isStartingRec) {
            this.isRecording = false;
            this.isStartingRec = false;
            this.btnPushToTalk.classList.remove('recording');
            this.talkButtonText.textContent = "SENDING...";
            this.interimBanner.classList.remove('active');

            try {
                this.recognition.stop();
            } catch (e) {
                this.finishAndSendTranscript();
            }
        }
    }

    finishAndSendTranscript() {
        this.talkButtonText.textContent = "TAP TO TALK";
        let fullText = (this.speechTranscript || '').trim();
        if (this.currentInterim && this.currentInterim.trim()) {
            fullText = (fullText ? fullText + ' ' : '') + this.currentInterim.trim();
        }
        this.speechTranscript = '';
        this.currentInterim = '';

        if (fullText && fullText.length > 0) {
            this.handleOutgoingMessage(fullText);
        }
    }

    sendTypedMessage() {
        const text = this.typeTextInput.value.trim();
        if (text) {
            this.handleOutgoingMessage(text);
            this.typeTextInput.value = '';
        }
    }

    async handleOutgoingMessage(originalText) {
        if (!originalText || !originalText.trim()) return;
        originalText = originalText.trim();

        // Prevent accidental duplicate firing
        if (this.isSendingMessage) return;
        this.isSendingMessage = true;
        setTimeout(() => { this.isSendingMessage = false; }, 500);

        this.welcomeCard.style.display = 'none';

        // Translate to partner language
        const targetLangCode = this.partnerLang.split('-')[0];
        const sourceLangCode = this.myLang.split('-')[0];

        let translatedText = originalText;
        try {
            translatedText = await this.translateText(originalText, sourceLangCode, targetLangCode);
        } catch (e) {
            console.warn("Translation fallback:", e);
        }

        const msgData = {
            id: 'msg_' + Date.now(),
            type: 'CHAT_MESSAGE',
            senderId: this.senderId,
            originalText: originalText,
            translatedText: translatedText,
            sourceLang: this.myLang,
            targetLang: this.partnerLang,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };

        // Render in my own chat feed
        this.renderMyMessage(msgData);

        // Publish to partner over MQTT
        if (this.mqttClient && this.isConnected) {
            this.mqttClient.publish(this.mqttTopic, JSON.stringify(msgData));
        } else {
            console.warn("MQTT not connected, cannot transmit message.");
        }
    }

    async translateText(text, fromLang, toLang) {
        if (fromLang === toLang) return text;

        try {
            // Free Instant Google Translate Endpoint
            const url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=${fromLang}&tl=${toLang}&dt=t&q=${encodeURIComponent(text)}`;
            const response = await fetch(url);
            const data = await response.json();
            
            if (data && data[0] && data[0][0] && data[0][0][0]) {
                let full = '';
                data[0].forEach(item => { if (item[0]) full += item[0]; });
                return full || text;
            }
        } catch (err) {
            // Fallback to MyMemory Free API
            try {
                const memUrl = `https://api.mymemory.translated.net/get?q=${encodeURIComponent(text)}&langpair=${fromLang}|${toLang}`;
                const res = await fetch(memUrl);
                const json = await res.json();
                if (json && json.responseData && json.responseData.translatedText) {
                    return json.responseData.translatedText;
                }
            } catch (e) {}
        }

        return text;
    }

    renderMyMessage(msg) {
        const bubble = document.createElement('div');
        bubble.className = 'chat-msg me';
        bubble.innerHTML = `
            <div class="msg-header">
                <span>YOU (${this.getLangShortName(this.myLang)})</span>
                <span class="msg-time">${msg.timestamp}</span>
            </div>
            <div class="msg-translated">${this.escapeHtml(msg.originalText)}</div>
            <div class="msg-original">
                <span>Trans: ${this.escapeHtml(msg.translatedText)}</span>
                <button class="btn-replay-audio" title="Play Speech"><i class="fa-solid fa-volume-high"></i></button>
            </div>
        `;

        bubble.querySelector('.btn-replay-audio').addEventListener('click', () => {
            this.speakText(msg.translatedText, this.partnerLang);
        });

        this.chatFeed.appendChild(bubble);
        this.scrollToBottom();
    }

    renderIncomingMessage(msg) {
        this.welcomeCard.style.display = 'none';

        const bubble = document.createElement('div');
        bubble.className = 'chat-msg partner';
        bubble.innerHTML = `
            <div class="msg-header">
                <span>PARTNER (${this.getLangShortName(msg.sourceLang)})</span>
                <span class="msg-time">${msg.timestamp}</span>
            </div>
            <div class="msg-translated">${this.escapeHtml(msg.translatedText)}</div>
            <div class="msg-original">
                <span>Orig: ${this.escapeHtml(msg.originalText)}</span>
                <button class="btn-replay-audio" title="Replay Speech"><i class="fa-solid fa-volume-high"></i></button>
            </div>
        `;

        bubble.querySelector('.btn-replay-audio').addEventListener('click', () => {
            this.speakText(msg.translatedText, this.myLang);
        });

        this.chatFeed.appendChild(bubble);
        this.scrollToBottom();

        // Auto Speak out loud in my language
        if (this.autoVoiceRead) {
            this.speakText(msg.translatedText, this.myLang);
        }
        this.vibrate([100, 50, 100]);
    }

    speakText(text, langCode) {
        if (!('speechSynthesis' in window)) return;
        try {
            window.speechSynthesis.cancel(); // Clear any stalled utterance to avoid audio freeze
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = langCode;
            utterance.rate = 1.0;

            const voices = window.speechSynthesis.getVoices();
            if (voices && voices.length > 0) {
                const matchingVoice = voices.find(v => v.lang.startsWith(langCode.substring(0, 2)));
                if (matchingVoice) utterance.voice = matchingVoice;
            }

            window.speechSynthesis.speak(utterance);
        } catch (e) {
            console.warn("Speech synthesis error:", e);
        }
    }

    scrollToBottom() {
        this.chatFeed.scrollTop = this.chatFeed.scrollHeight;
    }

    getLangShortName(code) {
        if (code.startsWith('en')) return 'English';
        if (code.startsWith('es')) return 'Español';
        if (code.startsWith('ur')) return 'اردو (Urdu)';
        if (code.startsWith('hi')) return 'हिन्दी (Hindi)';
        if (code.startsWith('vi')) return 'Tiếng Việt';
        if (code.startsWith('fr')) return 'Français';
        if (code.startsWith('pt')) return 'Português';
        if (code.startsWith('zh')) return '中文';
        if (code.startsWith('ar')) return 'العربية';
        return code;
    }

    escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    vibrate(pattern) {
        if ('vibrate' in navigator) {
            navigator.vibrate(pattern);
        }
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    window.communicatorApp = new AmestxCommunicator();
});
