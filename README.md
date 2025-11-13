# 🧠 TheraMind

> **Plataforma SaaS de Gestão Inteligente para Terapeutas**  
> Automatize resumos de consultas usando IA, mantendo privacidade e conformidade GDPR/LGPD.

[![Status](https://img.shields.io/badge/status-in%20development-yellow)](https://github.com/youruser/theramind)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![GDPR Compliant](https://img.shields.io/badge/GDPR-compliant-green.svg)](docs/)

---

## 📋 Sobre o Projeto

**TheraMind** é uma solução inovadora que permite terapeutas independentes:
- 🎙️ **Gravar sessões** de até 50 minutos
- 🤖 **Gerar resumos automaticamente** com IA (GPT-4o-mini)
- 📊 **Gerenciar pacientes** de forma organizada
- 🔒 **Garantir privacidade total** - nenhum áudio é armazenado permanentemente

### 🎯 Diferenciais

- **Zero-Storage**: Áudios deletados após processamento (conformidade GDPR by design)
- **IA de Alta Qualidade**: OpenAI Whisper + GPT-4o-mini
- **Custo Acessível**: ~$0.28 por sessão processada
- **Anonimização Automática**: Remove PII dos resumos

---

## ✨ Principais Funcionalidades

### MVP (v1.0)
- ✅ Autenticação segura (email/senha + MFA opcional)
- ✅ CRUD completo de pacientes
- ✅ Upload de áudio (MP3, WAV, M4A até 100MB)
- ✅ Processamento assíncrono (transcrição + resumo)
- ✅ Resumos estruturados:
  - Pontos principais discutidos
  - Emoções e comportamentos observados
  - Tarefas para casa (action items)
  - Avaliação de risco
- ✅ Notificações em tempo real
- ✅ Exportação de dados (PDF/JSON)
- ✅ Direito ao esquecimento (GDPR Art. 17)

### Roadmap Futuro
- 🔜 Gráficos de progresso do paciente
- 🔜 Tags e categorização de sessões
- 🔜 Integração com calendário
- 🔜 App mobile nativo (iOS/Android)
- 🔜 White-label para clínicas

---

## 🏗️ Arquitetura

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Next.js   │────────▶│   FastAPI    │────────▶│  SQS Queue  │
│  (Frontend) │  HTTPS  │  (Backend)   │         │             │
└─────────────┘         └──────────────┘         └─────────────┘
      │                        │                         │
      │                        ▼                         ▼
      │                  ┌──────────────┐         ┌─────────────┐
      │                  │  PostgreSQL  │         │   Worker    │
      │                  │  (Supabase)  │◀────────│  (Lambda)   │
      │                  └──────────────┘         └─────────────┘
      │                                                  │
      ▼                                                  ▼
┌─────────────┐                                  ┌─────────────┐
│     S3      │◀─────────────────────────────────│   OpenAI    │
│  (Storage)  │     Deleta após processamento    │   API       │
└─────────────┘                                  └─────────────┘
```

### Fluxo de Processamento

1. **Upload** → Frontend envia áudio direto para S3 (presigned URL)
2. **Enfileiramento** → Backend cria job no SQS
3. **Processamento** → Worker Lambda:
   - Transcreve áudio (Whisper)
   - Gera resumo estruturado (GPT-4o-mini)
   - Anonimiza PII automaticamente
   - Salva no banco de dados
   - **Deleta áudio permanentemente**
4. **Notificação** → Terapeuta recebe alerta em tempo real
5. **Visualização** → Resumo disponível no dashboard

---

## ⚙️ Stack Técnica

| Camada | Tecnologia | Motivo |
|--------|------------|--------|
| **Frontend** | Next.js 15 + TailwindCSS + shadcn/ui | SSR, modern, deploy grátis |
| **Backend** | FastAPI + Uvicorn | Tipado, async, performático |
| **Infraestrutura** | Railway (API) + AWS Lambda (Worker) | Always-on + serverless |
| **Banco de Dados** | PostgreSQL (Supabase) | Relacional, RLS, grátis |
| **Storage** | AWS S3 | Lifecycle policies, presigned URLs |
| **Fila** | AWS SQS | Confiável, serverless |
| **IA** | OpenAI Whisper + GPT-4o-mini | Melhor custo-benefício |
| **Autenticação** | Supabase Auth | JWT, MFA, OAuth |
| **Monitoramento** | Sentry + CloudWatch | Erros + logs |
| **Rate Limiting** | Upstash Redis | Serverless, grátis |

---

## 🚀 Quick Start

### Pré-requisitos

```bash
- Node.js 18+ (para Next.js)
- Python 3.11+ (para FastAPI)
- Conta AWS (S3, Lambda, SQS)
- Conta OpenAI (API key)
- Conta Supabase (grátis)
```

### 1️⃣ Clone o Repositório

```bash
git clone https://github.com/youruser/theramind.git
cd theramind
```

### 2️⃣ Configurar Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas credenciais AWS, OpenAI, Supabase

# Rodar migrações do banco
alembic upgrade head

# Iniciar servidor
uvicorn app.main:app --reload
```

### 3️⃣ Configurar Frontend

```bash
cd frontend
npm install

# Configurar variáveis de ambiente
cp .env.example .env.local
# Editar .env.local com URLs do backend e Supabase

# Iniciar servidor de desenvolvimento
npm run dev
```

### 4️⃣ Configurar Worker (Lambda)

```bash
cd worker
pip install -r requirements.txt

# Empacotar para deploy
./build.sh

# Deploy para AWS Lambda
aws lambda update-function-code \
  --function-name theramind-processor \
  --zip-file fileb://function.zip
```

### 5️⃣ Acessar Aplicação

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

---

## 💰 Custos Estimados (200 sessões/mês)

| Serviço | Custo/mês | Detalhes |
|---------|-----------|----------|
| Vercel (Frontend) | **$0** | Free Tier |
| Railway (Backend) | **$5** | Starter Plan |
| Supabase (DB + Auth) | **$0** | Free Tier (500MB) |
| OpenAI Whisper | **$48** | 200 × 40min × $0.006 |
| OpenAI GPT-4o-mini | **$0.18** | 200 × 6k tokens |
| AWS S3 + SQS + Lambda | **$2** | Pay-per-use |
| **TOTAL** | **~$55/mês** | **$0.28/sessão** |

💡 **Margem de 95%** cobrando $5/sessão do terapeuta

---

## 🔒 Segurança & Conformidade

### Segurança
- ✅ TLS 1.3 obrigatório em todas as conexões
- ✅ Criptografia em repouso (PostgreSQL + S3)
- ✅ Row-Level Security (RLS) no banco
- ✅ Rate limiting (100 req/min)
- ✅ Input validation (Pydantic)
- ✅ Secrets management (AWS Secrets Manager)
- ✅ Audit logs completos

### Conformidade GDPR/LGPD
- ✅ Consentimento explícito do paciente
- ✅ Direito de acesso aos dados (Art. 15)
- ✅ Direito ao esquecimento (Art. 17)
- ✅ Anonimização automática de PII
- ✅ Data Processing Agreement (DPA)
- ✅ Breach notification (<72h)
- ✅ Data Protection Impact Assessment (DPIA)

---

## 📊 Roadmap de Desenvolvimento

| Fase | Duração | Status | Entregas |
|------|---------|--------|----------|
| **Fase 1: Fundação** | 2 semanas | 🟡 Em progresso | Setup + Infra + Auth |
| **Fase 2: Core** | 3 semanas | ⚪ Pendente | Upload + Worker + IA |
| **Fase 3: Interface** | 2 semanas | ⚪ Pendente | Dashboard + UX |
| **Fase 4: Segurança** | 1.5 semanas | ⚪ Pendente | Auditoria + GDPR |
| **Fase 5: Beta** | 2 semanas | ⚪ Pendente | Testes + Feedback |
| **Fase 6: Launch** | 0.5 semana | ⚪ Pendente | Deploy produção |

**Total:** 11 semanas (~2.5 meses) até MVP público

---

## 📈 Métricas de Sucesso

### Mês 1-3 (Beta)
- 🎯 10-20 terapeutas ativos
- 🎯 200+ sessões processadas
- 🎯 NPS > 7/10
- 🎯 Uptime > 99.5%

### Mês 4-6 (Growth)
- 🎯 50+ terapeutas pagantes
- 🎯 $1,000 MRR
- 🎯 Churn < 10%

### Mês 7-12 (Scale)
- 🎯 200+ terapeutas
- 🎯 $5,000 MRR
- 🎯 LTV/CAC > 3:1

---

## 🧪 Testes

```bash
# Backend - Testes unitários
cd backend
pytest tests/ --cov=app --cov-report=html

# Frontend - Testes E2E
cd frontend
npm run test:e2e

# Load testing
cd tests
artillery run load-test.yml
```

### Cobertura de Testes
- Backend: >70% cobertura
- Frontend: Testes E2E dos fluxos principais
- Load testing: 100 sessões simultâneas

---

## 📝 Documentação

- 📘 [Documentação Técnica Completa](docs/TheraMind_Documentacao_Projeto.md)
- 🔐 [Guia de Segurança](docs/security.md)
- ⚖️ [Conformidade GDPR/LGPD](docs/compliance.md)
- 🎨 [Design System](docs/design-system.md)
- 🚀 [Guia de Deploy](docs/deployment.md)
- 📊 [API Reference](http://localhost:8000/docs)

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Guidelines
- Código deve ter testes
- Seguir PEP 8 (Python) e ESLint (JavaScript)
- Documentar novas funcionalidades
- Não commitar secrets ou .env

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👥 Time

- **Tech Lead:** [Seu Nome]
- **DPO (Data Protection Officer):** [Nome do responsável]
- **Contato:** privacy@theramind.com

---

## 🙏 Agradecimentos

- OpenAI pela API Whisper e GPT
- Comunidade Supabase
- Todos os beta testers

---

## 📞 Suporte

- 📧 Email: support@theramind.com
- 💬 Discord: [Link do servidor]
- 🐦 Twitter: [@theramind](https://twitter.com/theramind)
- 📚 Documentação: [docs.theramind.com](https://docs.theramind.com)

---

<p align="center">
  Feito com ❤️ para terapeutas que valorizam tecnologia e privacidade
</p>

<p align="center">
  <a href="https://theramind.com">Website</a> •
  <a href="https://docs.theramind.com">Documentação</a> •
  <a href="https://twitter.com/theramind">Twitter</a>
</p>

