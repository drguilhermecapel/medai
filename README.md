# SPEI - Sistema de Prontuário Eletrônico Inteligente

## 🏥 Sistema EMR Completo com Inteligência Artificial

O SPEI é um sistema completo de prontuário eletrônico desenvolvido com tecnologias modernas e conformidade regulatória internacional, incluindo funcionalidades avançadas de IA para diagnósticos médicos.

## 🚀 Funcionalidades Principais

### 📋 Gestão de Prontuários
- **Gestão Completa de Pacientes**: Cadastro, histórico médico, dados demográficos
- **Prontuários Eletrônicos**: Interface intuitiva para criação e edição de registros médicos
- **Histórico Médico Completo**: Acompanhamento longitudinal do paciente

### 🤖 Inteligência Artificial
- **Diagnósticos Assistidos por IA**: Algoritmos avançados para suporte diagnóstico
- **Análise de Sintomas**: Processamento inteligente de dados clínicos
- **Scoring de Confiança**: Métricas de precisão para recomendações da IA
- **Conformidade com Guidelines**: Seguimento das diretrizes médicas mais atuais

### 🩺 Telemedicina
- **Consultas Virtuais**: Plataforma integrada para teleconsultas
- **Agendamento Online**: Sistema de marcação de consultas
- **Prontuários Remotos**: Acesso seguro aos dados do paciente

### 🔒 Segurança e Conformidade
- **Conformidade Regulatória**: ANVISA, FDA, EU MDR
- **Autenticação JWT**: Sistema seguro de login e autorização
- **Criptografia de Dados**: Proteção completa das informações médicas
- **Auditoria Completa**: Logs detalhados de todas as operações

## 🛠️ Tecnologias Utilizadas

### Backend
- **FastAPI**: Framework Python moderno e performático
- **SQLAlchemy**: ORM robusto para gestão de banco de dados
- **PostgreSQL**: Banco de dados relacional confiável
- **Redis**: Cache e sessões
- **Poetry**: Gerenciamento de dependências Python

### Frontend
- **React 18**: Biblioteca JavaScript moderna
- **TypeScript**: Tipagem estática para maior robustez
- **Tailwind CSS**: Framework CSS utilitário
- **Vite**: Build tool rápido e moderno
- **React Router**: Navegação SPA

### DevOps & CI/CD
- **Docker**: Containerização completa
- **GitHub Actions**: Pipeline de CI/CD automatizado
- **Trivy**: Scanning de segurança
- **ESLint/Prettier**: Qualidade de código

## 📦 Instalação e Configuração

### 🖥️ Instalação Windows (Recomendada para Usuários Finais)

**Instalador Portátil - Duplo Clique para Instalar**

1. **Baixe o Instalador Portátil**
   - Baixe `SPEI-Setup-v1.0.0.exe` da página de releases
   - Arquivo portátil de ~50MB que baixa componentes automaticamente
   - Não requer Docker, Python ou configurações manuais

2. **Execute o Instalador Portátil**
   ```cmd
   # Simplesmente dê duplo clique no arquivo ou execute:
   SPEI-Setup-v1.0.0.exe
   ```
   - Siga o assistente de instalação intuitivo
   - Configure senha do banco de dados e usuário administrador
   - Escolha componentes (Sistema Principal, Banco de Dados, Modelos IA, Dados de Exemplo)
   - O instalador baixa automaticamente (~295MB total):
     - Python 3.11 Embeddable (~15MB)
     - Node.js 18.20.3 (~50MB)
     - PostgreSQL 15.7 Portable (~200MB)
     - Redis for Windows (~5MB)
     - Visual C++ Redistributables (~25MB)

3. **Acesse o SPEI**
   - Interface Web: http://localhost:3000
   - Documentação API: http://localhost:8000/docs
   - O instalador cria atalhos na área de trabalho para fácil acesso

#### 🛠️ Criando o Instalador Portátil (Para Desenvolvedores)

**Processo Simplificado - Um Único Comando**

1. **Pré-requisitos**
   - Windows 10/11
   - Inno Setup 6 (baixe de: https://jrsoftware.org/isinfo.php)
   - Código fonte completo do SPEI

2. **Criar Instalador Portátil**
   ```cmd
   cd windows-installer
   
   # Opção 1: Script simplificado
   create-portable-installer.bat
   
   # Opção 2: Script completo
   build-installer.bat
   ```

3. **Resultado**
   - Arquivo: `dist/SPEI-Setup-v1.0.0.exe`
   - Tamanho: ~50MB (instalador portátil)
   - Funcionalidade: Baixa componentes automaticamente durante instalação
   - Distribuição: Pronto para compartilhar com usuários finais

### 🐳 Instalação com Docker (Para Desenvolvedores)

### Pré-requisitos
- Docker e Docker Compose
- Node.js 18+ (para desenvolvimento)
- Python 3.11+ (para desenvolvimento)
- PostgreSQL 15+
- Redis 7+

```bash
# Clone o repositório
git clone https://github.com/drguilhermecapel/medai.git
cd medai

# Configure as variáveis de ambiente
cp .env.example .env

# Inicie os serviços
docker-compose up -d

# Acesse a aplicação
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# Documentação API: http://localhost:8000/docs
```

### 📋 Instalação Manual (Usuários Avançados)

Consulte [windows-installer/BUILD-INSTRUCTIONS.md](windows-installer/BUILD-INSTRUCTIONS.md) para instruções detalhadas de instalação manual.

### Desenvolvimento Local

#### Backend
```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 🏗️ Arquitetura do Sistema

```
SPEI/
├── backend/           # API FastAPI
│   ├── app/
│   │   ├── models/    # Modelos SQLAlchemy
│   │   ├── schemas/   # Schemas Pydantic
│   │   ├── services/  # Lógica de negócio
│   │   ├── routers/   # Endpoints da API
│   │   └── ai/        # Módulos de IA
│   └── tests/         # Testes automatizados
├── frontend/          # Interface React
│   ├── src/
│   │   ├── components/ # Componentes reutilizáveis
│   │   ├── pages/     # Páginas da aplicação
│   │   ├── contexts/  # Contextos React
│   │   └── hooks/     # Hooks customizados
│   └── public/        # Arquivos estáticos
├── infrastructure/    # Configurações de infraestrutura
└── .github/          # CI/CD workflows
```

## 🔧 Configuração

### Variáveis de Ambiente

#### Backend (.env)
```env
DATABASE_URL=postgresql://user:password@localhost:5432/spei_db
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
AI_MODEL_PATH=/path/to/ai/models
ANVISA_API_KEY=your-anvisa-key
```

#### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=SPEI
```

## 🧪 Testes

```bash
# Backend
cd backend
poetry run pytest

# Frontend
cd frontend
npm run test

# Cobertura
npm run test:coverage
```

## 📊 Conformidade Regulatória

### ANVISA (Brasil)
- ✅ Resolução CFM nº 1.821/2007
- ✅ Lei Geral de Proteção de Dados (LGPD)
- ✅ Padrões de interoperabilidade

### FDA (Estados Unidos)
- ✅ 21 CFR Part 820 (Quality System Regulation)
- ✅ FDA Software as Medical Device (SaMD)
- ✅ HIPAA Compliance

### EU MDR (União Europeia)
- ✅ Medical Device Regulation (MDR) 2017/745
- ✅ GDPR Compliance
- ✅ ISO 13485 Quality Management

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 📞 Suporte

Para suporte técnico ou dúvidas sobre o sistema:
- 📧 Email: suporte@spei.med.br
- 📱 WhatsApp: +55 (11) 99999-9999
- 🌐 Website: https://spei.med.br

## 🏆 Migração

Este sistema foi migrado do repositório `cardio.ai.pro` para estabelecer o `medai` como repositório principal do SPEI. A migração preservou toda a funcionalidade, histórico de desenvolvimento e conformidade regulatória.

**Data da Migração**: Junho 2025  
**Versão**: 1.0.0  
**Status**: Produção Ready ✅
