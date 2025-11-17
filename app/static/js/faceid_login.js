// faceid_login.js - Sistema de Login com Reconhecimento Facial
(function() {
    'use strict';

    // Elementos DOM
    const elements = {
        faceidLoginBtn: document.getElementById('faceid-login-btn'),
        toggleTraditionalBtn: document.getElementById('toggle-traditional-login'),
        traditionalSection: document.getElementById('traditional-login-section'),
        faceidModal: document.getElementById('faceid-camera-modal'),
        closeFaceidModal: document.getElementById('close-faceid-modal'),
        faceidVideo: document.getElementById('faceid-video'),
        faceidCanvas: document.getElementById('faceid-canvas'),
        faceidStatus: document.getElementById('faceid-status'),
        forgotPasswordBtn: document.getElementById('forgot-password'),
        forgotModal: document.getElementById('forgot-modal'),
        closeModalBtn: document.getElementById('close-modal')
    };

    let stream = null;
    let captureInterval = null;
    let isProcessing = false;

    // Configura event listeners
    function setupEventListeners() {
        // Toggle login tradicional
        if (elements.toggleTraditionalBtn && elements.traditionalSection) {
            elements.toggleTraditionalBtn.addEventListener('click', () => {
                elements.traditionalSection.classList.toggle('hidden');
                elements.toggleTraditionalBtn.textContent = elements.traditionalSection.classList.contains('hidden') ? 'Não possui FaceID?' : 'Voltar para FaceID';
            });
        }

        // Abre modal FaceID
        if (elements.faceidLoginBtn && elements.faceidModal) {
            elements.faceidLoginBtn.addEventListener('click', async () => {
                elements.faceidModal.classList.remove('hidden');
                await initFaceIDCamera();
            });
        }

        // Fecha modal FaceID
        if (elements.closeFaceidModal) {
            elements.closeFaceidModal.addEventListener('click', closeFaceIDModal);
        }

        // Modal esqueci senha
        if (elements.forgotPasswordBtn && elements.forgotModal) {
            elements.forgotPasswordBtn.addEventListener('click', (e) => {
                e.preventDefault();
                elements.forgotModal.classList.remove('hidden');
            });
        }

        if (elements.closeModalBtn && elements.forgotModal) {
            elements.closeModalBtn.addEventListener('click', () => elements.forgotModal.classList.add('hidden'));
        }

        // Clique fora do modal para fechar
        [elements.faceidModal, elements.forgotModal].forEach(modal => {
            if (modal) {
                modal.addEventListener('click', (e) => {
                    if (e.target === modal) modal.classList.add('hidden');
                });
            }
        });
    }

    // Atualiza status visual
    function updateStatus(message, type = 'info') {
        if (!elements.faceidStatus) return;
        const icons = {
            info: 'fas fa-spinner fa-spin mr-2',
            success: 'fas fa-check-circle mr-2',
            error: 'fas fa-exclamation-circle mr-2',
            warning: 'fas fa-exclamation-triangle mr-2'
        };
        const colors = {
            info: 'style="background: rgba(59, 130, 246, 0.1);" text-blue-800',
            success: 'style="background: rgba(34, 197, 94, 0.1);" text-green-800',
            error: 'bg-red-50 text-red-800',
            warning: 'style="background: rgba(245, 158, 11, 0.1);" style="color: var(--text);"'
        };
        elements.faceidStatus.className = `mb-4 p-3 rounded-lg text-center ${colors[type]}`;
        elements.faceidStatus.innerHTML = `<i class="fas ${icons[type]}"></i>${message}`;
    }

    // Inicializa câmera
    async function initFaceIDCamera() {
        try {
            updateStatus('Inicializando câmera...', 'info');
            stream = await navigator.mediaDevices.getUserMedia({
                video: { width: { ideal: 1280 }, height: { ideal: 720 }, facingMode: 'user' }
            });
            elements.faceidVideo.srcObject = stream;
            elements.faceidVideo.onloadedmetadata = () => {
                elements.faceidCanvas.width = elements.faceidVideo.videoWidth;
                elements.faceidCanvas.height = elements.faceidVideo.videoHeight;
                updateStatus('Posicione seu rosto e aguarde...', 'success');
                startAutoCapture();
            };
        } catch (error) {
            console.error('Erro ao acessar câmera:', error);
            updateStatus('Erro ao acessar câmera. Verifique as permissões.', 'error');
            setTimeout(closeFaceIDModal, 2000);
        }
    }

    // Inicia captura automática
    function startAutoCapture() {
        captureInterval = setInterval(() => {
            if (!isProcessing) captureAndAuthenticate();
        }, 2000);
    }

    // Captura frame e tenta autenticar
    async function captureAndAuthenticate() {
        if (isProcessing || !stream) return;
        isProcessing = true;
        try {
            const ctx = elements.faceidCanvas.getContext('2d');
            ctx.drawImage(elements.faceidVideo, 0, 0);
            const imageData = elements.faceidCanvas.toDataURL('image/jpeg', 0.85);
            updateStatus('Analisando rosto...', 'info');
            const response = await fetch('/api/faceid/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image: imageData })
            });
            const result = await response.json();
            if (result.success) {
                updateStatus(`✅ ${result.message}`, 'success');
                clearInterval(captureInterval);
                setTimeout(() => window.location.href = '/dashboard', 1000);
            } else {
                const status = response.status;
                const msg = result.message || 'Aguardando reconhecimento...';
                updateStatus(status === 503 ? '❌ Erro de conexão com banco de dados' :
                             status === 404 ? '⚠️ Nenhum FaceID cadastrado. Use login tradicional.' :
                             `🔍 ${msg}`, status === 503 || status === 404 ? 'error' : 'warning');
                if (status === 503 || status === 404) {
                    clearInterval(captureInterval);
                    setTimeout(() => {
                        closeFaceIDModal();
                        if (status === 503) alert('Erro ao conectar ao banco de dados. Use login tradicional.');
                    }, 2000);
                }
            }
        } catch (error) {
            console.error('Erro na autenticação:', error);
            updateStatus('❌ Erro de conexão. Verifique sua internet.', 'error');
            clearInterval(captureInterval);
            setTimeout(closeFaceIDModal, 2000);
        } finally {
            isProcessing = false;
        }
    }

    // Fecha modal e limpa recursos
    function closeFaceIDModal() {
        clearInterval(captureInterval);
        captureInterval = null;
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            stream = null;
        }
        if (elements.faceidModal) elements.faceidModal.classList.add('hidden');
        isProcessing = false;
        if (elements.faceidVideo) elements.faceidVideo.srcObject = null;
    }

    // Limpa recursos ao sair da página
    window.addEventListener('beforeunload', closeFaceIDModal);

    // Inicializa
    setupEventListeners();
})();