document.addEventListener('DOMContentLoaded', async () => {
  // Carregar modelos do face-api.js (uma vez)
  await faceapi.nets.ssdMobilenetv1.loadFromUri('/static/models');

  // Elementos DOM
  const elements = {
    form: document.getElementById('loginForm'),
    cameraContainer: document.getElementById('camera-container'),
    video: document.getElementById('video'),
    loginBtn: document.getElementById('login-btn'),
    email: document.getElementById('email'),
    password: document.getElementById('password'),
    forgotPassword: document.getElementById('forgot-password'),
    forgotModal: document.getElementById('forgot-modal'),
    closeModal: document.getElementById('close-modal')
  };

  let stream = null;
  let detectionTimeout = null;

  // Event listeners
  if (elements.form) {
    elements.form.addEventListener('submit', handleLoginSubmit);
  }

  if (elements.forgotPassword && elements.forgotModal) {
    elements.forgotPassword.addEventListener('click', (e) => {
      e.preventDefault();
      elements.forgotModal.classList.remove('hidden');
    });
  }

  if (elements.closeModal && elements.forgotModal) {
    elements.closeModal.addEventListener('click', () => {
      elements.forgotModal.classList.add('hidden');
    });
  }

  // Clique fora do modal
  [elements.forgotModal].forEach(modal => {
    if (modal) {
      modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.classList.add('hidden');
      });
    }
  });

  async function handleLoginSubmit(e) {
    e.preventDefault();
    const email = elements.email?.value.trim();
    const password = elements.password?.value;

    if (!email || !password) {
      showAlert('Preencha email e senha');
      return;
    }

    // TODO: Remover verificação client-side em produção; backend deve validar
    if (email !== 'admin@gmail.com' || password !== 'admin123') {
      showAlert('Credenciais inválidas. Use: admin@gmail.com / admin123');
      return;
    }

    // Mostrar câmera
    updateLoginBtn('Verificando...', true);
    await initCamera();
    startFaceDetection();
  }

  async function initCamera() {
    try {
      stream = await navigator.mediaDevices.getUserMedia({ video: true });
      elements.video.srcObject = stream;
      elements.cameraContainer.classList.remove('hidden');
    } catch (err) {
      console.error('Erro ao acessar câmera:', err);
      showAlert('Permita acesso à câmera para verificação facial');
      resetLogin();
    }
  }

  function startFaceDetection() {
    detectionTimeout = setTimeout(async () => {
      try {
        const detection = await faceapi.detectSingleFace(elements.video);
        if (detection) {
          showAlert('Rosto detectado! Logando...');
          // Submete para backend (ou redireciona)
          elements.form.submit();
        } else {
          showAlert('Nenhum rosto detectado. Tente novamente.');
          resetLogin();
        }
      } catch (err) {
        console.error('Erro na detecção:', err);
        showAlert('Erro na detecção facial. Tente novamente.');
        resetLogin();
      }
    }, 3000); // Reduzido para 3s para melhor UX
  }

  function resetLogin() {
    clearTimeout(detectionTimeout);
    detectionTimeout = null;
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      stream = null;
    }
    elements.video.srcObject = null;
    elements.cameraContainer.classList.add('hidden');
    updateLoginBtn('Entrar', false);
  }

  function updateLoginBtn(text, disabled = false) {
    if (!elements.loginBtn) return;
    elements.loginBtn.innerHTML = disabled ? '<i class="fas fa-spinner fa-spin mr-2"></i>' + text : '<i class="fas fa-sign-in-alt mr-2"></i>' + text;
    elements.loginBtn.disabled = disabled;
  }

  function showAlert(message) {
    alert(message);
  }

  // Cleanup
  window.addEventListener('beforeunload', resetLogin);
});