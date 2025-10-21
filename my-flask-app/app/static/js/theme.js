/* ============================================
   THEME CONTROLLER - Sistema de Saneamento
   ============================================ */
   (function() {
    'use strict';
  
    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    const themeIcon = themeToggleBtn ? themeToggleBtn.querySelector('i') : null;
  
    // Verificar tema salvo ou preferência do sistema
    function getSavedTheme() {
      const savedTheme = localStorage.getItem('theme');
      if (savedTheme) {
        return savedTheme;
      }
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
  
    // Aplicar tema
    function applyTheme(theme) {
      document.documentElement.setAttribute('data-theme', theme);
      localStorage.setItem('theme', theme);
      updateThemeIcon(theme);
      updateMetaThemeColor(theme);
    }
  
    // Atualizar ícone do botão
    function updateThemeIcon(theme) {
      if (!themeIcon) return;
      
      if (theme === 'dark') {
        themeIcon.classList.remove('fa-moon');
        themeIcon.classList.add('fa-sun');
      } else {
        themeIcon.classList.remove('fa-sun');
        themeIcon.classList.add('fa-moon');
      }
    }
  
    // Atualizar meta tag theme-color para mobile
    function updateMetaThemeColor(theme) {
      const metaThemeColor = document.querySelector('meta[name="theme-color"]');
      if (metaThemeColor) {
        metaThemeColor.setAttribute('content', theme === 'dark' ? '#0f172a' : '#f8fafc');
      }
    }
  
    // Alternar tema
    function toggleTheme() {
      const currentTheme = document.documentElement.getAttribute('data-theme');
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
      applyTheme(newTheme);
    }
  
    // Inicializar tema
    function initTheme() {
      const savedTheme = getSavedTheme();
      applyTheme(savedTheme);
      
      // Adicionar evento de clique no botão
      if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', toggleTheme);
      }
  
      // Observar mudanças na preferência do sistema
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        if (!localStorage.getItem('theme')) {
          applyTheme(e.matches ? 'dark' : 'light');
        }
      });
  
      console.log('Tema inicializado:', savedTheme);
    }
  
    // Inicializar quando DOM estiver pronto
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', initTheme);
    } else {
      initTheme();
    }
  
    // Exportar funções para uso global
    window.themeController = {
      toggle: toggleTheme,
      getCurrentTheme: () => document.documentElement.getAttribute('data-theme'),
      setTheme: applyTheme
    };
  
  })();