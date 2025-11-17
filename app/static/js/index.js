// index.js — versão revisada e mais robusta

// Estado da aplicação
let currentTheme = localStorage.getItem('theme') || 'light';
let isLoading = false;

// Helper para obter elemento por id ou seletor seguro
function $id(id) { return document.getElementById(id); }
function resolveForm(preferredIds = [], fallbackSelector = null) {
  for (const id of preferredIds) {
    const f = document.getElementById(id);
    if (f) return f;
  }
  if (fallbackSelector) {
    const el = document.querySelector(fallbackSelector);
    if (el) return el;
  }
  // último recurso: first form.grid
  return document.querySelector('form.grid');
}

// Elementos DOM comuns (tente usar IDs/data-attrs no HTML para facilitar)
const elements = {
  themeToggle: $id('theme-toggle'),
  pageContent: $id('page-content'),
  userModal: $id('user-modal'),
  closeUserModal: $id('close-user-modal'),
  addUserBtn: $id('add-user-btn'),
  userForm: $id('user-form'),
  usuariosTbody: $id('usuarios-tbody'),
  // resolver formulários/tables preferindo IDs
  tarefaForm: resolveForm(['tarefa-form'], 'form[data-form="tarefa"]'),
  tarefaList: document.querySelector('.var(--card-bg) ul.space-y-3'),
  pontoBtn: $id('btn-ponto'),
  pontoTableBody: $id('ponto-table-body') || document.querySelector('table[data-table="ponto"] tbody') || document.querySelector('table tbody'),
  auditoriaForm: resolveForm(['auditoria-form'], 'form[data-form="auditoria"]'),
  auditoriaTableBody: $id('auditoria-table-body') || document.querySelector('.var(--card-bg) table[data-table="auditoria"] tbody') || document.querySelector('.var(--card-bg) table tbody'),
  reportPeriod: $id('report-period')
};

// Inicialização
function init() {
  applyTheme();
  setupEventListeners();
  setupAnimations();
  checkSystemStatus();
  if (elements.usuariosTbody) carregarUsuarios();
  const usuarioId = window.currentUserId || sessionStorage.getItem('usuario_id');
  if (usuarioId) {
    if (elements.tarefaForm) carregarTarefas(usuarioId);
    if (elements.pontoBtn) carregarHistoricoPonto(usuarioId);
  }
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js').catch(() => { /* não crítico */ });
  }
}

// Aplicar tema
function applyTheme() {
  document.documentElement.setAttribute('data-theme', currentTheme);
  updateThemeIcon();
  updateMetaTheme();
}

// Atualizar ícone e classes do tema
function updateThemeIcon() {
  if (!elements.themeToggle) return;
  const icon = elements.themeToggle.querySelector('i');
  if (!icon) return;
  const isDark = currentTheme === 'dark';
  // use classList para não sobrescrever outras classes do botão
  icon.className = isDark ? 'fa fa-sun' : 'fa fa-moon';
  elements.themeToggle.classList.remove('bg-gray-700', 'var(--hover)');
  elements.themeToggle.classList.add(isDark ? 'bg-gray-700' : 'var(--hover)');
}

// Atualizar meta theme-color
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
  if (elements.themeToggle) {
    elements.themeToggle.addEventListener('click', toggleTheme);
  }

  // Modal de usuário
  if (elements.addUserBtn && elements.userModal && elements.closeUserModal) {
    elements.addUserBtn.addEventListener('click', () => {
      elements.userModal.classList.remove('hidden');
      elements.userModal.setAttribute('aria-hidden', 'false');
      // foco acessível no primeiro input se existir
      const foco = elements.userModal.querySelector('input, button, textarea, select');
      if (foco) foco.focus();
    });
    elements.closeUserModal.addEventListener('click', () => {
      elements.userModal.classList.add('hidden');
      elements.userModal.setAttribute('aria-hidden', 'true');
    });
    elements.userModal.addEventListener('click', (e) => {
      if (e.target === elements.userModal) elements.userModal.classList.add('hidden');
    });
  }

  // Formulário de usuário
  if (elements.userForm) {
    elements.userForm.addEventListener('submit', handleUserSubmit);
  }

  // Navegação suave para anchors apenas
  document.querySelectorAll('a').forEach(link => {
    const href = link.getAttribute('href');
    if (!href) return;
    // anchors internos
    if (href.startsWith('#')) {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        const target = document.querySelector(href);
        if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
      return;
    }
    // não chame loading para links com target _blank, download ou rel=external
    const isExternalTarget = link.target === '_blank' || link.hasAttribute('download') || (link.rel && link.rel.includes('external'));
    if (!isExternalTarget) {
      link.addEventListener('click', () => showLoading());
    }
  });

  // Excluir usuário
  document.addEventListener('click', async (e) => {
    const btn = e.target.closest('.excluir-usuario-btn');
    if (btn) {
      const id = btn.dataset.id;
      if (!id) return showNotification('ID de usuário não encontrado', 'error');
      if (confirm('Deseja realmente excluir este usuário?')) {
        const res = await handleApiRequest(`/usuarios/excluir/${id}`, 'POST', {}, 'Usuário excluído com sucesso!');
        if (res && res.success) carregarUsuarios();
      }
    }
  });

  // Editar usuário (placeholder)
  document.addEventListener('click', (e) => {
    if (e.target.closest('.editar-usuario-btn')) {
      showNotification('Funcionalidade de edição em desenvolvimento.', 'info');
    }
  });

  // Botões globais (mais robustos)
  const execAnalysisBtn = document.querySelector('.btn-primary i.fa-play-circle')?.closest('.btn') || document.querySelector('.btn-primary');
  if (execAnalysisBtn) {
    execAnalysisBtn.addEventListener('click', () => simulateAction('Análise executada com sucesso!', 2000));
  }
  document.querySelectorAll('.btn .fa-sliders-h').forEach(icon => {
    const btn = icon.closest('.btn');
    if (btn) btn.addEventListener('click', () => showNotification('Filtros avançados abertos!', 'info'));
  });
  document.querySelectorAll('.btn .fa-download').forEach(icon => {
    const btn = icon.closest('.btn');
    if (!btn) return;
    btn.addEventListener('click', () => {
      if (btn.classList.contains('btn-primary')) {
        handleReportExport();
      } else {
        simulateAction('Relatório exportado!', 1500);
      }
    });
  });
  document.querySelectorAll('.btn .fa-sync-alt').forEach(icon => {
    const btn = icon.closest('.btn');
    if (btn) btn.addEventListener('click', () => simulateAction('Dados atualizados!', 1200));
  });
  document.querySelectorAll('button .fa-edit').forEach(icon => {
    const btn = icon.closest('button');
    if (btn) btn.addEventListener('click', () => showNotification('Editar tarefa: formulário aberto!', 'info'));
  });

  // Formulário de tarefas
  if (elements.tarefaForm) {
    elements.tarefaForm.addEventListener('submit', handleTarefaSubmit);
  }

  // Registrar ponto
  if (elements.pontoBtn) {
    elements.pontoBtn.addEventListener('click', handlePontoRegister);
  }

  // Pesquisar auditoria
  if (elements.auditoriaForm) {
    elements.auditoriaForm.addEventListener('submit', handleAuditoriaSearch);
  }
}

// Função auxiliar para ações simuladas
function simulateAction(message, delay) {
  showLoading();
  setTimeout(() => {
    showNotification(message, 'success');
    hideLoading();
  }, delay);
}

// Função auxiliar para requests API (robusta)
async function handleApiRequest(url, method = 'GET', body = null, successMsg = null) {
  try {
    const options = { method, headers: {} };
    if (body) {
      options.headers['Content-Type'] = 'application/json';
      options.body = JSON.stringify(body);
    }
    const response = await fetch(url, options);
    if (!response.ok) {
      const text = await response.text().catch(() => '');
      throw new Error(`HTTP ${response.status} ${text}`);
    }
    const result = await response.json().catch(() => null);
    if (!result) throw new Error('Resposta inválida do servidor');
    if (result.success === false) {
      showNotification(result.message || 'Erro na operação', 'error');
      return result;
    }
    if (successMsg) showNotification(successMsg, 'success');
    return result;
  } catch (err) {
    console.error('API request error', err);
    showNotification('Erro na operação', 'error');
    return null;
  }
}

// Envio do formulário de usuário
async function handleUserSubmit(e) {
  e.preventDefault();
  if (!elements.userForm) return;
  const formData = Object.fromEntries(new FormData(elements.userForm));
  await handleApiRequest('/usuarios/cadastrar', 'POST', formData, 'Usuário cadastrado com sucesso!');
  if (elements.userModal) {
    elements.userModal.classList.add('hidden');
    elements.userModal.setAttribute('aria-hidden', 'true');
  }
  elements.userForm.reset();
  carregarUsuarios();
}

// Carregar usuários
async function carregarUsuarios() {
  try {
    const resp = await fetch('/usuarios/listar');
    if (!resp.ok) throw new Error('Erro ao buscar usuários');
    const json = await resp.json();
    const usuarios = Array.isArray(json.usuarios) ? json.usuarios : [];
    if (!elements.usuariosTbody) return;
    elements.usuariosTbody.innerHTML = usuarios.map(usuario => `
      <tr>
        <td class="py-4">
          <label class="flex items-center">
            <input type="checkbox" class="form-checkbox rounded text-blue-600" />
            <div class="ml-3">
              <div class="font-medium">${usuario.nome || ''}</div>
              <div class="text-sm var(--text)">${usuario.email || ''}</div>
            </div>
          </label>
        </td>
        <td class="py-4"><span class="px-2 py-1 var(--hover) style="color: var(--text);" rounded-full text-xs">${usuario.cargo || ''}</span></td>
        <td class="py-4">${usuario.departamento || ''}</td>
        <td class="py-4">
          <span class="px-2 py-1 ${usuario.status === 'Ativo' ? 'style="background: rgba(34, 197, 94, 0.2);" text-green-800' : 'bg-red-100 text-red-800'} rounded-full text-xs">${usuario.status || ''}</span>
        </td>
        <td class="py-4">-</td>
        <td class="py-4 text-right">
          <div class="flex justify-end space-x-2">
            <button class="text-blue-600 hover:text-blue-800 editar-usuario-btn" data-id="${usuario.id || ''}" title="Editar"><i class="fas fa-edit"></i></button>
            <button class="text-red-600 hover:text-red-800 excluir-usuario-btn" data-id="${usuario.id || ''}" title="Excluir"><i class="fas fa-trash"></i></button>
          </div>
        </td>
      </tr>
    `).join('');
  } catch (err) {
    console.error(err);
    showNotification('Erro ao carregar usuários', 'error');
  }
}

// Alternar tema
function toggleTheme() {
  currentTheme = currentTheme === 'light' ? 'dark' : 'light';
  localStorage.setItem('theme', currentTheme);
  document.documentElement.style.transition = 'all 0.3s ease';
  applyTheme();
  setTimeout(() => { document.documentElement.style.transition = ''; }, 300);
}

// Loading (overlay com id fixo)
function showLoading() {
  if (isLoading) return;
  isLoading = true;
  // se já existir, não recriar
  if (document.getElementById('app-loading-overlay')) return;
  const overlay = document.createElement('div');
  overlay.id = 'app-loading-overlay';
  overlay.setAttribute('role', 'status');
  overlay.className = 'fixed inset-0 flex items-center justify-center z-50';
  overlay.style.backgroundColor = 'rgba(0,0,0,0.5)';
  overlay.innerHTML = `
    <div class="var(--card-bg) dark:bg-gray-800 p-6 rounded-xl shadow-2xl flex items-center space-x-3">
      <div class="w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin" aria-hidden="true"></div>
      <span class="style="color: var(--text);" dark:text-white">Carregando...</span>
    </div>
  `;
  document.body.appendChild(overlay);
  // fallback hide em 10s
  setTimeout(() => { if (isLoading) hideLoading(); }, 10000);
}

function hideLoading() {
  isLoading = false;
  const overlay = document.getElementById('app-loading-overlay');
  if (overlay) overlay.remove();
}

// Status do sistema
async function checkSystemStatus() {
  try {
    const resp = await fetch('/api/health');
    if (!resp.ok) throw new Error('Health check failed');
    const json = await resp.json();
    updateSystemStatus(json.status === 'ok' ? 'online' : 'offline');
  } catch {
    updateSystemStatus('offline');
  }
}

function updateSystemStatus(status) {
  const indicator = document.querySelector('.w-3.h-3.rounded-full');
  if (!indicator) return;
  const isOnline = status === 'online';
  indicator.classList.remove('bg-green-400', 'bg-red-400');
  indicator.classList.add(isOnline ? 'bg-green-400' : 'bg-red-400');
  if (indicator.nextElementSibling) indicator.nextElementSibling.textContent = isOnline ? 'Sistema Online' : 'Sistema Offline';
}

// Notificação com aria-live
function showNotification(message, type = 'info') {
  const notification = document.createElement('div');
  notification.setAttribute('role', 'status');
  notification.setAttribute('aria-live', 'polite');
  const baseClasses = 'fixed top-4 right-4 p-4 rounded-xl shadow-lg transform transition-all duration-300';
  const colorClass = type === 'error' ? 'bg-red-500' : type === 'success' ? 'style="background: rgba(34, 197, 94, 0.1);"0' : 'style="background: rgba(59, 130, 246, 0.1);"0';
  notification.className = `${baseClasses} ${colorClass} text-white z-60`;
  notification.innerHTML = `
    <div class="flex items-center space-x-3">
      <i class="fas ${type === 'error' ? 'fa-exclamation-circle' : type === 'success' ? 'fa-check-circle' : 'fa-info-circle'}"></i>
      <div class="ml-2">${message}</div>
      <button class="ml-4 close-notif" aria-label="Fechar notificação" title="Fechar"><i class="fas fa-times"></i></button>
    </div>
  `;
  document.body.appendChild(notification);
  const closeBtn = notification.querySelector('.close-notif');
  if (closeBtn) closeBtn.addEventListener('click', () => notification.remove());
  setTimeout(() => notification.remove(), 5000);
}

// Dashboard
async function loadDashboardData() {
  showLoading();
  try {
    const resp = await fetch('/api/dashboard-data');
    if (!resp.ok) throw new Error('Erro ao carregar dashboard');
    const data = await resp.json();
    updateDashboardStats(data);
  } catch (error) {
    console.error('Erro ao carregar dados do dashboard:', error);
    showNotification('Erro ao carregar dados', 'error');
  } finally {
    hideLoading();
  }
}

function updateDashboardStats(data = {}) {
  const stats = {
    'active-users': data.activeUsers,
    'efficiency': data.efficiency,
    'environment-impact': data.environmentImpact,
    'critical-alerts': data.criticalAlerts
  };
  Object.entries(stats).forEach(([id, value]) => {
    const el = document.getElementById(id);
    if (el && value !== undefined && value !== null) animateValue(el, 0, value, 1000);
  });

  const progressData = {
    'air-quality': data.airQuality,
    'water-quality': data.waterQuality,
    'waste-management': data.wasteManagement,
    'green-coverage': data.greenCoverage
  };
  Object.entries(progressData).forEach(([id, value]) => {
    const progressBar = document.getElementById(`${id}-progress`);
    const textEl = document.getElementById(id);
    if (progressBar && (value !== undefined && value !== null)) {
      progressBar.style.width = '0%';
      setTimeout(() => { progressBar.style.width = `${value}%`; }, 100);
    }
    if (textEl && (value !== undefined && value !== null)) textEl.textContent = `${value}%`;
  });
}

function animateValue(element, start, end, duration) {
  let startTimestamp = null;
  const step = (timestamp) => {
    if (!startTimestamp) startTimestamp = timestamp;
    const progress = Math.min((timestamp - startTimestamp) / duration, 1);
    const value = Math.floor(progress * (end - start) + start);
    // se id sugerir percent ou dataset indicar, adiciona %
    const isPercent = element.dataset && element.dataset.unit === 'percent' || element.id && element.id.includes('percent') || typeof end === 'number' && end > 100 === false;
    element.textContent = isPercent ? `${value}%` : value;
    if (progress < 1) window.requestAnimationFrame(step);
  };
  window.requestAnimationFrame(step);
}

// Tarefas
async function handleTarefaSubmit(e) {
  e.preventDefault();
  const usuarioId = window.currentUserId || sessionStorage.getItem('usuario_id');
  if (!usuarioId) return showNotification('Usuário não identificado', 'error');
  if (!elements.tarefaForm) return showNotification('Formulário de tarefa não encontrado', 'error');
  const formData = Object.fromEntries(new FormData(elements.tarefaForm));
  formData.usuario_id = usuarioId;
  await handleApiRequest('/api/tarefas', 'POST', formData, 'Tarefa adicionada!');
  elements.tarefaForm.reset();
  carregarTarefas(usuarioId);
}

async function carregarTarefas(usuarioId) {
  try {
    const resp = await fetch(`/api/tarefas?usuario_id=${encodeURIComponent(usuarioId)}`);
    if (!resp.ok) throw new Error('Erro ao buscar tarefas');
    const json = await resp.json();
    const tarefas = Array.isArray(json.tarefas) ? json.tarefas : [];
    if (!elements.tarefaList) return;
    elements.tarefaList.innerHTML = tarefas.map(tarefa => {
      const statusClass = tarefa.status === 'Em Andamento' ? 'text-blue-600 style="background: rgba(59, 130, 246, 0.2);"' :
                          tarefa.status === 'Concluída' ? 'text-green-600 style="background: rgba(34, 197, 94, 0.2);"' : 'text-yellow-600 style="background: rgba(245, 158, 11, 0.2);"';
      return `
        <li class="p-4 rounded-lg border flex justify-between items-center hover:var(--hover)">
          <div>
            <p class="font-medium style="color: var(--text);"">${tarefa.titulo || ''}</p>
            <span class="text-xs ${statusClass} px-2 py-1 rounded-full">${tarefa.status || ''}</span>
          </div>
          <button class="text-blue-600 hover:text-blue-800 transition"><i class="fas fa-edit"></i></button>
        </li>
      `;
    }).join('');
  } catch (err) {
    console.error(err);
    showNotification('Erro ao carregar tarefas', 'error');
  }
}

// Ponto Eletrônico
async function handlePontoRegister() {
  const usuarioId = window.currentUserId || sessionStorage.getItem('usuario_id');
  if (!usuarioId) return showNotification('Usuário não identificado', 'error');
  const now = new Date();
  const payload = {
    usuario_id: usuarioId,
    data: now.toISOString().slice(0, 10),
    hora_entrada: now.toTimeString().slice(0, 8),
    localizacao: null
  };
  await handleApiRequest('/api/ponto/registrar', 'POST', payload, 'Ponto registrado com sucesso!');
  carregarHistoricoPonto(usuarioId);
}

async function carregarHistoricoPonto(usuarioId) {
  try {
    const resp = await fetch(`/api/ponto/historico?usuario_id=${encodeURIComponent(usuarioId)}`);
    if (!resp.ok) throw new Error('Erro ao buscar ponto');
    const json = await resp.json();
    const historico = Array.isArray(json.historico) ? json.historico : [];
    if (!elements.pontoTableBody) return;
    elements.pontoTableBody.innerHTML = historico.map(ponto => `
      <tr class="border-b hover:var(--hover)">
        <td class="px-4 py-2">${ponto.data || '-'}</td>
        <td class="px-4 py-2">${ponto.hora_entrada || '-'}</td>
        <td class="px-4 py-2">${ponto.hora_saida || '-'}</td>
        <td class="px-4 py-2">${ponto.total_horas || '-'}</td>
      </tr>
    `).join('');
  } catch (err) {
    console.error(err);
    showNotification('Erro ao carregar histórico de ponto', 'error');
  }
}

// Auditoria
async function handleAuditoriaSearch(e) {
  e.preventDefault();
  if (!elements.auditoriaForm) return showNotification('Formulário de auditoria não encontrado', 'error');
  const formData = Object.fromEntries(new FormData(elements.auditoriaForm));
  const params = new URLSearchParams();
  if (formData.usuario) params.append('usuario', formData.usuario);
  if (formData.data_inicial) params.append('data_inicial', formData.data_inicial);
  if (formData.data_final) params.append('data_final', formData.data_final);
  showLoading();
  try {
    const resp = await fetch(`/api/auditoria?${params.toString()}`);
    if (!resp.ok) throw new Error('Erro na pesquisa de auditoria');
    const json = await resp.json();
    const registros = Array.isArray(json.registros) ? json.registros : [];
    if (!elements.auditoriaTableBody || registros.length === 0) {
      showNotification('Nenhum registro encontrado.', 'info');
      return;
    }
    elements.auditoriaTableBody.innerHTML = registros.map(registro => {
      const statusClass = registro.status === 'Sucesso' ? 'style="background: rgba(34, 197, 94, 0.2);" text-green-700' :
                          registro.status === 'Falha' ? 'bg-red-100 text-red-700' : 'style="background: rgba(59, 130, 246, 0.2);" text-blue-700';
      return `
        <tr class="border-b hover:var(--hover)">
          <td class="px-4 py-2">${registro.data_hora || '-'}</td>
          <td class="px-4 py-2">${registro.usuario || '-'}</td>
          <td class="px-4 py-2">${registro.acao || '-'}</td>
          <td class="px-4 py-2">${registro.ip || '-'}</td>
          <td class="px-4 py-2"><span class="px-2 py-1 ${statusClass} rounded-lg">${registro.status || '-'}</span></td>
        </tr>
      `;
    }).join('');
    showNotification('Pesquisa realizada!', 'success');
  } catch (err) {
    console.error(err);
    showNotification('Erro ao pesquisar auditoria', 'error');
  } finally {
    hideLoading();
  }
}

// Exportar relatório
async function handleReportExport() {
  showLoading();
  try {
    const period = elements.reportPeriod?.value || 'all';
    let url = `/relatorios/exportar?period=${encodeURIComponent(period)}`;
    const response = await fetch(url);
    if (!response.ok) throw new Error('Erro ao exportar relatório');
    const blob = await response.blob();
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'relatorio.xlsx';
    document.body.appendChild(link);
    link.click();
    link.remove();
    showNotification('Relatório exportado!', 'success');
  } catch (err) {
    console.error(err);
    showNotification('Erro ao exportar relatório', 'error');
  } finally {
    hideLoading();
  }
}

// Animações
function setupAnimations() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) entry.target.classList.add('animate-in');
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });
  document.querySelectorAll('.card, .stat-card').forEach(el => observer.observe(el));
  // opcional: guardar observer se quiser desconectar depois (ex: ao trocar de SPA)
}

// Inicializar
document.addEventListener('DOMContentLoaded', init);

// Exportar para global
window.dashboard = {
  init,
  toggleTheme,
  loadDashboardData,
  showNotification,
  showLoading,
  hideLoading
};
