/* ============================================
   MOBILE MENU CONTROLLER - Versão Corrigida
   ============================================ */
   (function() {
    'use strict';
  
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.querySelector('.sidebar-overlay');
    let isMenuOpen = false;
  
    function isMobile() {
      return window.innerWidth < 1024;
    }
  
    function updateButtonState(open) {
      if (!mobileMenuBtn) return;
      
      const icon = mobileMenuBtn.querySelector('i');
      if (!icon) return;
      
      // Atualizar ícone
      icon.classList.toggle('fa-bars', !open);
      icon.classList.toggle('fa-times', open);
      
      // Atualizar classe para estilização
      mobileMenuBtn.classList.toggle('menu-open', open);
      
      console.log('Botão atualizado:', open ? 'X (fechar)' : '☰ (abrir)');
    }
  
    function toggleBodyScroll(open) {
      document.body.style.overflow = open ? 'hidden' : '';
    }
  
    function openMobileMenu() {
      if (!sidebar || isMenuOpen || !isMobile()) return;
      
      console.log('Abrindo menu mobile');
      sidebar.classList.add('mobile-open');
      sidebarOverlay.classList.add('active');
      toggleBodyScroll(true);
      updateButtonState(true);
      isMenuOpen = true;
    }
  
    function closeMobileMenu() {
      if (!sidebar || !isMenuOpen) return;
      
      console.log('Fechando menu mobile');
      sidebar.classList.remove('mobile-open');
      sidebarOverlay.classList.remove('active');
      toggleBodyScroll(false);
      updateButtonState(false);
      isMenuOpen = false;
    }
  
    function toggleMobileMenu() {
      if (!isMobile()) return;
      
      if (isMenuOpen) {
        closeMobileMenu();
      } else {
        openMobileMenu();
      }
    }
  
    function setupLinkListeners() {
      if (!sidebar) return;
      
      const links = sidebar.querySelectorAll('a.nav-item');
      links.forEach(link => {
        link.addEventListener('click', () => {
          if (isMobile()) {
            setTimeout(closeMobileMenu, 100);
          }
        });
      });
    }
  
    function handleResize() {
      if (!isMobile() && isMenuOpen) {
        closeMobileMenu();
      }
    }
  
    // Verificar tema atual e aplicar cores
    function applyThemeColors() {
      const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
      console.log('Tema atual:', isDark ? 'escuro' : 'claro');
    }
  
    function init() {
      // Setup event listeners
      if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', toggleMobileMenu);
      }
      
      if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', closeMobileMenu);
      }
  
      window.addEventListener('resize', handleResize);
      
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && isMenuOpen) {
          closeMobileMenu();
        }
      });
  
      // Observar mudanças de tema
      const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
          if (mutation.type === 'attributes' && mutation.attributeName === 'data-theme') {
            applyThemeColors();
          }
        });
      });
      
      observer.observe(document.documentElement, { attributes: true });
  
      setupLinkListeners();
      applyThemeColors();
      
      // Garantir estado inicial correto
      if (!isMobile()) {
        sidebar.classList.remove('mobile-open');
        sidebarOverlay.classList.remove('active');
        updateButtonState(false);
      }
    }
  
    // Inicializar
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', init);
    } else {
      init();
    }
  
    window.mobileMenu = {
      open: openMobileMenu,
      close: closeMobileMenu,
      toggle: toggleMobileMenu,
      isOpen: () => isMenuOpen
    };
  
  })();