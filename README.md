Sistema de Saneamento - APS
Este é um projeto desenvolvido para a disciplina APS, com o objetivo de criar um sistema web para monitoramento e gestão de saneamento municipal. O sistema inclui uma página de login com autenticação fictícia e reconhecimento facial, além de um dashboard interativo com indicadores ambientais, estatísticas e alertas críticos. O projeto é construído com Flask, utiliza Tailwind CSS para estilização, Font Awesome para ícones, Chart.js para gráficos e face-api.js para detecção facial.
Funcionalidades

Autenticação:
Página de login acessível em /login com credenciais fictícias: admin@gmail.com / admin123.
Reconhecimento facial via webcam (usando face-api.js) para validação adicional.
Opções de "Esqueci a Senha" (modal) e "Criar Conta" (link fictício).
Logout disponível no dashboard e na sidebar.


Dashboard:
Exibe estatísticas como usuários ativos, eficiência geral, impacto ambiental e alertas críticos.
Gráficos dinâmicos (Chart.js) para indicadores ambientais (qualidade do ar, água, etc.).
Alertas interativos com botões para "Resolver" (com modal de confirmação).
Sidebar responsiva com navegação para futuras funcionalidades (Ponto Eletrônico, Tarefas, etc.).
Suporte a modo claro/escuro com toggle no header.


Responsividade: Layout adaptável para dispositivos móveis e desktop.
UX/UI: Design moderno, com animações suaves, cores claras e acessibilidade (WCAG).

Estrutura do Projeto
APS/
├── my-flask-app/
│   ├── app/
│   │   ├── controllers/
│   │   │   └── controller.py
│   │   ├── models/
│   │   │   └── models.py
│   │   ├── routes/
│   │   │   └── routes.py
│   │   ├── static/
│   │   │   ├── css/
│   │   │   │   └── dashboard.css
│   │   │   ├── images/
│   │   │   │   └── folha.png
│   │   │   ├── js/
│   │   │   │   ├── index.js
│   │   │   │   └── login.js
│   │   │   └── models/
│   │   │       └── [pesos do face-api.js]
│   │   ├── templates/
│   │   │   ├── base.html
│   │   │   ├── index.html
│   │   │   └── login.html
│   │   └── utils/
│   │       └── utils.py
│   ├── database/
│   │   ├── db_connection.py
│   │   └── __init__.py
│   ├── doc/
│   │   ├── estrutura.md
│   │   ├── ferramentas.txt
│   │   └── Requisitos.pdf
│   ├── frontend/
│   │   ├── components/
│   │   │   └── react.tsx
│   │   ├── public/
│   │   │   └── index.html
│   │   ├── src/
│   │   │   └── index.html
│   │   └── package.json
│   ├── .env
│   ├── config.py
│   ├── Main.py
│   ├── requirements.txt
│   └── README.md


Main.py: Arquivo principal que inicia o servidor Flask.
routes.py: Define rotas para login (/login), dashboard (/dashboard), logout (/logout) e redirecionamento inicial (/).
login.html: Página de login com autenticação fictícia e reconhecimento facial.
index.html: Dashboard principal com estatísticas e gráficos.
base.html: Template base com sidebar, header e toggle de tema.
dashboard.css: Estilos para login e dashboard.
login.js: Lógica para validação do form e reconhecimento facial.
models/: Contém pesos do face-api.js (ssd_mobilenetv1) para detecção facial.

Pré-requisitos

Python 3.13+
Dependências Python (listadas em requirements.txt):
Flask
python-dotenv


Navegador moderno (Chrome, Firefox, etc.) com suporte a webcam para reconhecimento facial.
Pesos do face-api.js: Baixe de face-api.js weights e coloque em my-flask-app/app/static/models/.

Instalação

Clone o repositório (se aplicável) ou navegue até o diretório do projeto:
cd C:\Users\erick\OneDrive\Desktop\projects\Estudos\APS\my-flask-app


Crie e ative um ambiente virtual:
python -m venv venv
.\venv\Scripts\activate  # Windows


Instale as dependências:
pip install -r requirements.txt


Configure os pesos do face-api.js:

Baixe os arquivos de pesos (ssd_mobilenetv1_model-weights_manifest.json e shards) de face-api.js weights.
Crie a pasta my-flask-app/app/static/models/ e coloque os arquivos lá.


Configure variáveis de ambiente:

Edite ou crie o arquivo .env:FLASK_APP=Main.py
FLASK_ENV=development
SECRET_KEY=sua-chave-secreta-aqui


A SECRET_KEY é necessária para sessões e mensagens flash.



Como Executar

Navegue até o diretório do projeto:
cd C:\Users\erick\OneDrive\Desktop\projects\Estudos\APS\my-flask-app


Inicie o servidor Flask:
python Main.py


Acesse no navegador:

Abra http://127.0.0.1:5000.
Você será redirecionado para a página de login (/login).


Teste o login:

Use as credenciais fictícias: Email: admin@gmail.com | Senha: admin123.
Clique em "Entrar", permita acesso à webcam, posicione seu rosto por 5 segundos.
Se o rosto for detectado, você será redirecionado para o dashboard (/dashboard).



Como Testar

Página de Login:

Acesse http://127.0.0.1:5000/login.
As credenciais fictícias (admin@gmail.com / admin123) são exibidas na tela.
Insira credenciais erradas para ver a mensagem de erro.
Clique em "Esqueci a Senha" para abrir o modal (fictício).
Clique em "Criar Conta" (link fictício; adicione rota /register se necessário).


Dashboard:

Após login, acesse http://127.0.0.1:5000/dashboard.
Verifique estatísticas, gráficos, alertas e toggle de tema (claro/escuro).
Clique em "Sair" no header ou sidebar para voltar ao login.


Reconhecimento Facial:

Certifique-se de que a webcam está ativa e os pesos do face-api.js estão em static/models/.
Se a câmera não funcionar, verifique permissões no navegador.



Estrutura das Rotas



Rota
Método
Descrição



/
GET
Redireciona para /login ou /dashboard


/login
GET/POST
Página de login com autenticação fictícia


/dashboard
GET
Dashboard principal (protegido)


/logout
GET
Faz logout e redireciona para /login


Possíveis Melhorias Futuras

Autenticação Real: Integre com db_connection.py para verificar credenciais no banco de dados (ex.: usando Flask-Login e bcrypt).
Página de Registro: Crie uma rota /register e template para cadastro de usuários.
Reconhecimento Facial Avançado: Armazene descriptors faciais no backend para comparação real (ex.: com PostgreSQL).
Mais Páginas: Implemente rotas e templates para os links da sidebar (Ponto Eletrônico, Tarefas, etc.).
API REST: Adicione endpoints para integração com frontend React (se quiser usar frontend/).

Problemas Comuns e Soluções

Erro TemplateNotFound:

Verifique se login.html, index.html e base.html estão em app/templates/.
Confirme que template_folder='app/templates' está em Main.py.


Erro de face-api.js:

Certifique-se de que os pesos estão em app/static/models/.
Teste acessando http://127.0.0.1:5000/static/models/ssd_mobilenetv1_model-weights_manifest.json.


Erro de Sessão:

Adicione app.secret_key em Main.py ou SECRET_KEY no .env.


Erro de Redirecionamento:

Verifique se routes.py usa main.index no url_for.



Contribuição

Faça um fork do repositório (se aplicável).
Crie uma branch para sua feature: git checkout -b minha-feature.
Commit suas mudanças: git commit -m "Adiciona minha feature".
Envie para o repositório: git push origin minha-feature.

Licença
Este projeto é para fins educacionais e não possui licença formal. Desenvolvido para a disciplina APS.
Contato
Para dúvidas ou sugestões, contate o desenvolvedor via email ou abra uma issue (se for um repositório público).

Desenvolvido por [Seu Nome] com suporte de Grok (xAI). Última atualização: 31 de Agosto de 2025.