// Estado da aplicação
let currentTheme = localStorage.getItem('theme') || 'light';
let isLoading = false;

// Elementos DOM
const themeToggle = document.getElementById('theme-toggle');
const pageContent = document.getElementById('page-content');

// Inicialização
function init() {
  applyTheme();
  setupEventListeners();
  setupAnimations();
  checkSystemStatus();
}

// Aplicar tema
function applyTheme() {
  document.body.setAttribute('data-theme', currentTheme);
  updateThemeIcon();
  updateMetaTheme();
}

// Atualizar ícone do tema
function updateThemeIcon() {
  if (themeToggle) {
    const icon = themeToggle.querySelector('i');
    if (currentTheme === 'dark') {
      icon.classList.remove('fa-moon');
      icon.classList.add('fa-sun');
      themeToggle.classList.add('bg-gray-700');
      themeToggle.classList.remove('bg-gray-100');
    } else {
      icon.classList.remove('fa-sun');
      icon.classList.add('fa-moon');
      themeToggle.classList.remove('bg-gray-700');
      themeToggle.classList.add('bg-gray-100');
    }
  }
}

// Atualizar meta theme-color para mobile
function updateMetaTheme() {
  const themeColor = currentTheme === 'dark' ? '#0f172a' : '#f8fafc';
  let metaTheme = document.querySelector('meta[name="theme-color"]');
  
  if (!metaTheme) {
    metaTheme = document.createElement('meta');
    metaTheme.name = 'theme-color';
    document.head.appendChild(metaTheme);
  }
  
  metaTheme.content = themeColor;
}

// Configurar event listeners
function setupEventListeners() {
  // Toggle de tema
  if (themeToggle) {
    themeToggle.addEventListener('click', toggleTheme);
  }
  
  // Navegação suave
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });
  
  // Loading state para links
  document.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', function() {
      if (this.getAttribute('href') && !this.getAttribute('href').startsWith('#')) {
        showLoading();
      }
    });
  });
}

// Setup de animações
function setupAnimations() {
  // Intersection Observer para animações ao scroll
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate-in');
      }
    });
  }, observerOptions);
  
  // Observar elementos para animação
  document.querySelectorAll('.card, .stat-card').forEach(el => {
    observer.observe(el);
  });
}

// Alternar tema
function toggleTheme() {
  currentTheme = currentTheme === 'light' ? 'dark' : 'light';
  document.body.setAttribute('data-theme', currentTheme);
  localStorage.setItem('theme', currentTheme);
  updateThemeIcon();
  updateMetaTheme();
  
  // Animação de transição
  document.documentElement.style.transition = 'all 0.3s ease';
  setTimeout(() => {
    document.documentElement.style.transition = '';
  }, 300);
}

// Mostrar estado de loading
function showLoading() {
  if (isLoading) return;
  
  isLoading = true;
  const overlay = document.createElement('div');
  overlay.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
  overlay.innerHTML = `
    <div class="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-2xl flex items-center space-x-3">
      <div class="w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
      <span class="text-gray-800 dark:text-white">Carregando...</span>
    </div>
  `;
  
  document.body.appendChild(overlay);
  
  // Remover após 5s (timeout de segurança)
  setTimeout(() => {
    if (isLoading) {
      hideLoading();
    }
  }, 5000);
}

// Esconder loading
function hideLoading() {
  isLoading = false;
  const overlay = document.querySelector('.fixed.inset-0.bg-black');
  if (overlay) {
    overlay.remove();
  }
}

// Verificar status do sistema
async function checkSystemStatus() {
  try {
    const response = await fetch('/api/health');
    const data = await response.json();
    
    if (data.status === 'ok') {
      updateSystemStatus('online');
    } else {
      updateSystemStatus('offline');
    }
  } catch (error) {
    updateSystemStatus('offline');
  }
}

// Atualizar indicador de status
function updateSystemStatus(status) {
  const statusIndicator = document.querySelector('.w-3.h-3.rounded-full');
  if (statusIndicator) {
    if (status === 'online') {
      statusIndicator.classList.remove('bg-red-400', 'bg-gray-400');
      statusIndicator.classList.add('bg-green-400');
      statusIndicator.nextElementSibling.textContent = 'Sistema Online';
    } else {
      statusIndicator.classList.remove('bg-green-400', 'bg-gray-400');
      statusIndicator.classList.add('bg-red-400');
      statusIndicator.nextElementSibling.textContent = 'Sistema Offline';
    }
  }
}

// Função para mostrar notificação
function showNotification(message, type = 'info') {
  const notification = document.createElement('div');
  notification.className = `fixed top-4 right-4 p-4 rounded-xl shadow-lg transform transition-all duration-300 animate-fade-in ${
    type === 'error' ? 'bg-red-500 text-white' :
    type === 'success' ? 'bg-green-500 text-white' :
    'bg-blue-500 text-white'
  }`;
  notification.innerHTML = `
    <div class="flex items-center">
      <i class="fas ${
        type === 'error' ? 'fa-exclamation-circle' :
        type === 'success' ? 'fa-check-circle' :
        'fa-info-circle'
      } mr-2"></i>
      <span>${message}</span>
      <button class="ml-4" onclick="this.parentElement.parentElement.remove()">
        <i class="fas fa-times"></i>
      </button>
    </div>
  `;
  
  document.body.appendChild(notification);
  
  // Auto-remover após 5 segundos
  setTimeout(() => {
    if (notification.parentElement) {
      notification.remove();
    }
  }, 5000);
}

// Função para carregar dados do dashboard
async function loadDashboardData() {
  try {
    showLoading();
    const response = await fetch('/api/dashboard-data');
    const data = await response.json();
    
    // Atualizar estatísticas
    updateDashboardStats(data);
    hideLoading();
    
  } catch (error) {
    console.error('Erro ao carregar dados do dashboard:', error);
    showNotification('Erro ao carregar dados', 'error');
    hideLoading();
  }
}

// Atualizar estatísticas do dashboard
function updateDashboardStats(data) {
  const stats = {
    'active-users': data.activeUsers,
    'efficiency': data.efficiency,
    'environment-impact': data.environmentImpact,
    'critical-alerts': data.criticalAlerts
  };
  
  Object.entries(stats).forEach(([id, value]) => {
    const element = document.getElementById(id);
    if (element && value !== undefined) {
      animateValue(element, 0, value, 1000);
    }
  });
  
  // Atualizar progress bars
  const progressData = {
    'air-quality': data.airQuality,
    'water-quality': data.waterQuality,
    'waste-management': data.wasteManagement,
    'green-coverage': data.greenCoverage
  };
  
  Object.entries(progressData).forEach(([id, value]) => {
    const progressBar = document.getElementById(`${id}-progress`);
    const textElement = document.getElementById(id);
    
    if (progressBar && value !== undefined) {
      progressBar.style.width = '0%';
      setTimeout(() => {
        progressBar.style.width = `${value}%`;
      }, 100);
    }
    
    if (textElement && value !== undefined) {
      textElement.textContent = `${value}%`;
    }
  });
}

// Animação de contagem
function animateValue(element, start, end, duration) {
  let startTimestamp = null;
  const step = (timestamp) => {
    if (!startTimestamp) startTimestamp = timestamp;
    const progress = Math.min((timestamp - startTimestamp) / duration, 1);
    const value = Math.floor(progress * (end - start) + start);
    element.textContent = element.id.includes('percent') ? `${value}%` : value;
    if (progress < 1) {
      window.requestAnimationFrame(step);
    }
  };
  window.requestAnimationFrame(step);
}

// Inicializar quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', init);

// Exportar funções para uso global
window.dashboard = {
  init,
  toggleTheme,
  loadDashboardData,
  showNotification,
  showLoading,
  hideLoading
};

// Funções para botões globais do sistema
document.addEventListener('DOMContentLoaded', () => {
  // Executar análise (analises.html)
  const execAnalysisBtn = document.querySelector('.btn-primary i.fa-play-circle')?.parentElement;
  if (execAnalysisBtn) {
    execAnalysisBtn.addEventListener('click', () => {
      dashboard.showLoading();
      setTimeout(() => {
        dashboard.showNotification('Análise executada com sucesso!', 'success');
        dashboard.hideLoading();
      }, 2000);
    });
  }

  // Filtros avançados (analises, meio_ambiente)
  document.querySelectorAll('.btn .fa-sliders-h').forEach(icon => {
    icon.parentElement.addEventListener('click', () => {
      dashboard.showNotification('Filtros avançados abertos!', 'info');
    });
  });

  // Exportar relatório (meio_ambiente, relatorios)
  document.querySelectorAll('.btn .fa-download').forEach(icon => {
    icon.parentElement.addEventListener('click', () => {
      dashboard.showLoading();
      setTimeout(() => {
        dashboard.showNotification('Relatório exportado!', 'success');
        dashboard.hideLoading();
      }, 1500);
    });
  });

  // Atualizar dados (relatorios)
  document.querySelectorAll('.btn .fa-sync-alt').forEach(icon => {
    icon.parentElement.addEventListener('click', () => {
      dashboard.showLoading();
      setTimeout(() => {
        dashboard.showNotification('Dados atualizados!', 'success');
        dashboard.hideLoading();
      }, 1200);
    });
  });

  // Adicionar usuário (usuarios.html)
  const addUserBtn = document.getElementById('add-user-btn');
  if (addUserBtn) {
    addUserBtn.addEventListener('click', () => {
      dashboard.showNotification('Novo usuário: formulário aberto!', 'info');
    });
  }

  // Adicionar tarefa (tarefas.html)
  document.querySelectorAll('form button .fa-plus').forEach(icon => {
    icon.parentElement.addEventListener('click', (e) => {
      e.preventDefault();
      dashboard.showLoading();
      setTimeout(() => {
        dashboard.showNotification('Tarefa adicionada!', 'success');
        dashboard.hideLoading();
      }, 1200);
    });
  });

  // Editar tarefa (tarefas.html)
  document.querySelectorAll('button .fa-edit').forEach(icon => {
    icon.parentElement.addEventListener('click', () => {
      dashboard.showNotification('Editar tarefa: formulário aberto!', 'info');
    });
  });

  // Registrar ponto (ponto_eletronico.html)
  const pontoBtn = document.getElementById('btn-ponto');
  if (pontoBtn) {
    pontoBtn.addEventListener('click', () => {
      dashboard.showLoading();
      setTimeout(() => {
        dashboard.showNotification('Ponto registrado!', 'success');
        dashboard.hideLoading();
      }, 1000);
    });
  }

  // Pesquisar auditoria (auditoria.html)
  document.querySelectorAll('form button .fa-search').forEach(icon => {
    icon.parentElement.addEventListener('click', (e) => {
      e.preventDefault();
      dashboard.showLoading();
      setTimeout(() => {
        dashboard.showNotification('Pesquisa realizada!', 'success');
        dashboard.hideLoading();
      }, 1000);
    });
  });
});

// Service Worker para PWA (opcional)
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then(() => console.log('Service Worker registrado'))
      .catch(() => console.log('Service Worker não suportado'));
  });
}