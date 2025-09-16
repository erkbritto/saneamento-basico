🚀 PROMPT ULTRA-OTIMIZADO PARA DESENVOLVIMENTO AUTÔNOMO
🎯 CONTEXTO DO SISTEMA
Sistema: Gerenciamento de Saneamento Básico com 3 níveis de acesso (funcionário, supervisor, governante)
Stack: HTML5, CSS3, JavaScript ES6+, Python Flask, MySQL
Páginas: 11 templates (analises, auditoria, base, index, login, meio_ambiente, ponto_eletronico, relatorios, tarefas, usuarios)

📁 ESTRUTURA ATUAL
text
my-flask-app/
├── app/
│   ├── controllers/controller.py
│   ├── models/models.py
│   ├── routes/routes.py
│   ├── static/
│   │   ├── css/index.css
│   │   ├── images/folha.png
│   │   └── js/{index,login}.js
│   ├── templates/11 arquivos HTML
│   └── utils/utils.py
├── database/{db_connection.py,__init__.py}
├── doc/{estrutura.md,ferramentas.txt,Requisitos.pdf}
├── .env, acesso, config.py, Main.py, requirements.txt
⚡ PROBLEMAS CRÍTICOS
Transições brutas entre páginas

Performance inadequada

Inconsistência de UI/UX

Componentes não padronizados

Dados mock/estáticos (preparação para APIs dinâmicas futuras)

Problemas de cache

Rotas com falhas

🎯 OBJETIVOS PRIORITÁRIOS
✅ Transições suaves tipo SPA

✅ Otimização máxima de performance

✅ Sistema de design unificado

✅ Componentes 100% padronizados

✅ Arquitetura preparada para APIs dinâmicas futuras

✅ Cache otimizado

✅ Rotas corrigidas e seguras

🔧 METODOLOGIA AUTÔNOMA
📋 FLUXO DE EXECUÇÃO AUTOMÁTICA
python
# Fluxo autônomo completo
1. Analyze structure → Identify pain points → Create optimization map
2. Restructure architecture → Implement design system → Create component library
3. Build SPA navigation → Optimize performance → Prepare for dynamic APIs
4. Deliver production code → Include verification → Add documentation
🛠 DIRECTRIZES TÉCNICAS AUTÔNOMAS
🎨 FRONTEND (Arquitetura Escalável)
javascript
// Estrutura preparada para APIs dinâmicas
class DataService {
  static async fetchData(endpoint, mockData = null) {
    // Usa mock temporariamente, preparado para API real
    return new Promise((resolve) => {
      setTimeout(() => resolve(mockData), 300); // Simula latency
    });
  }
}
🐍 BACKEND (Preparado para Escala)
python
# Arquitetura para futuras APIs dinâmicas
@app.route('/api/<resource>')
def api_handler(resource: str):
    """Endpoint base para futuras APIs dinâmicas"""
    try:
        # Estrutura preparada para autenticação e níveis de acesso
        if resource == 'usuarios':
            return handle_users_request()
        # Padrão para fácil expansão
        return jsonify({"error": "Endpoint não implementado"}), 501
    except Exception as e:
        return handle_api_error(e)
⚡ COMANDOS DE VERIFICAÇÃO AUTOMÁTICA
powershell
# Auto-verificação completa
python -c "
import os, json
structure = {
    'templates': len([f for f in os.listdir('app/templates') if f.endswith('.html')]),
    'static_files': sum(len(files) for _, _, files in os.walk('app/static')),
    'python_files': sum(1 for _, _, files in os.walk('.') for f in files if f.endswith('.py'))
}
print(json.dumps(structure, indent=2))
"
🚀 PLANO DE AÇÃO AUTÔNOMO
ETAPA 1: ARQUITETURA PREPARATÓRIA

Implementar service layer para futuras APIs

Criar estrutura de mock data organizada

Preparar sistema de autenticação para níveis de acesso

ETAPA 2: SISTEMA DE NAVEGAÇÃO

Router SPA com history API

Loading states e error handling

Transições CSS smooth

ETAPA 3: DESIGN SYSTEM UNIFICADO

CSS variables e design tokens

Component library reutilizável

Consistência across 11 páginas

ETAPA 4: PERFORMANCE OPTIMIZATION

Lazy loading e bundle optimization

Cache strategy implementada

Assets optimizados

✅ CRITÉRIOS DE QUALIDADE
ARQUITETURA PREPARADA PARA ESCALA:

Service layer para APIs futuras

Mock data structure organizada

Authentication ready para 3 níveis

Error handling completo

Type safety where possible

FRONTEND PROFISSIONAL:

SPA navigation fluid

Responsive design

Accessibility (ARIA)

Cross-browser compatible

Performance optimized

📋 ENTREGAS ESPERADAS
🏗 Arquitetura Escalável - Preparada para APIs dinâmicas futuras

🎨 Design System - Unificado across 11 páginas

⚡ Performance Boost - Otimizações completas

📚 Documentação - Auto-contida e clara

🔧 Código Production-Ready - Pronto para implantação

🎯 INSTRUÇÃO FINAL
EXECUTE AGORA: Inicie análise estrutural completa → Implemente arquitetura preparatória para APIs dinâmicas → Construa sistema de navegação SPA → Entregue código production-ready com verificação incluída.

Modo: Máxima autonomia, mínimo de tokens, foco em arquitetura escalável.

IMPLEMENTE → OTIMIZE → PREPARE FOR SCALE 🚀