document.addEventListener('DOMContentLoaded', async () => {
  // Carregar modelos do face-api.js
  await faceapi.nets.ssdMobilenetv1.loadFromUri('/static/models');

  const form = document.getElementById('loginForm');
  const cameraContainer = document.getElementById('camera-container');
  const video = document.getElementById('video');
  const loginBtn = document.getElementById('login-btn');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    if (!email || !password) {
      alert('Preencha email e senha');
      return;
    }

    // Simular verificação de credenciais no client-side (opcional, já que backend faz isso)
    if (email !== 'admin@gmail.com' || password !== 'admin123') {
      alert('Credenciais inválidas. Use: admin@gmail.com / admin123');
      return;
    }

    // Mostrar câmera
    loginBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Verificando...';
    loginBtn.disabled = true;
    cameraContainer.classList.remove('hidden');
    navigator.mediaDevices.getUserMedia({ video: true })
      .then(stream => {
        video.srcObject = stream;
      })
      .catch(err => {
        console.error('Erro ao acessar câmera:', err);
        alert('Permita acesso à câmera para verificação facial');
        loginBtn.innerHTML = '<i class="fas fa-sign-in-alt mr-2"></i> Entrar';
        loginBtn.disabled = false;
        cameraContainer.classList.add('hidden');
      });

    // Detectar rosto
    setTimeout(async () => {
      const detection = await faceapi.detectSingleFace(video);
      if (detection) {
        alert('Rosto detectado! Logando...');
        form.submit(); // Submete para backend
      } else {
        alert('Nenhum rosto detectado. Tente novamente.');
        loginBtn.innerHTML = '<i class="fas fa-sign-in-alt mr-2"></i> Entrar';
        loginBtn.disabled = false;
        cameraContainer.classList.add('hidden');
      }
    }, 5000);
  });

  // Modal Esqueci Senha
  document.getElementById('forgot-password').addEventListener('click', (e) => {
    e.preventDefault();
    document.getElementById('forgot-modal').classList.remove('hidden');
  });
  document.getElementById('close-modal').addEventListener('click', () => {
    document.getElementById('forgot-modal').classList.add('hidden');
  });
});