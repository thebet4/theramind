# 🧠 TheraMind — Projeto SaaS de Gestão Inteligente para Terapeutas

## 📋 Visão Geral

**TheraMind** é uma plataforma SaaS voltada para **terapeutas independentes**, com o objetivo de simplificar a **gestão de pacientes** e **automatizar resumos de consultas** usando IA.

A aplicação permite que o terapeuta grave ou envie uma sessão de áudio, e receba automaticamente um **resumo estruturado**, destacando:
- Pontos principais discutidos  
- Emoções e comportamentos observados  
- Ações ou tarefas de acompanhamento  

A plataforma prioriza **privacidade**, **baixo custo operacional** e **usabilidade**, focando em valor imediato para o profissional.

---

## 🏗️ Arquitetura Geral do MVP

### 🔹 Fluxo Resumido (Arquitetura Assíncrona)

1. O terapeuta **seleciona o paciente** e faz upload do áudio (até 50 minutos) via interface web.  
2. O **frontend** faz upload direto para **S3** (presigned URL) e notifica o backend.  
3. O **backend API** cria um job e enfileira na **AWS SQS** (ou Redis Queue).  
4. Um **worker dedicado** (Lambda ou container) processa o job:
   - Baixa o áudio do S3
   - **Transcreve o áudio completo** com Whisper
   - **Gera resumo estruturado** usando GPT-4o-mini com contexto completo
   - Salva o resumo no banco de dados
   - **Deleta permanentemente** o áudio e transcrição do S3
5. O terapeuta recebe **notificação em tempo real** (WebSocket/polling) quando o processamento termina.  
6. O resumo é exibido no painel do terapeuta.  

> **Política de Zero-Storage:** Nenhum áudio ou transcrição completa é armazenado permanentemente — apenas o resumo final estruturado.

### 🔹 Diagrama de Arquitetura

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
│  (Storage)  │          Deleta após             │  Whisper +  │
└─────────────┘          processamento           │   GPT-4o    │
                                                  └─────────────┘
```

---

## ⚙️ Stack Técnica (Definitiva)

| Camada | Tecnologia | Motivo |
|---------|-------------|--------|
| **Frontend** | Next.js 15 (App Router) + TailwindCSS + shadcn/ui | Rápido, moderno, SSR, deploy grátis na Vercel |
| **Backend (API)** | FastAPI + Uvicorn | Tipado, async, ideal para integrações com IA |
| **Infraestrutura API** | Railway (container always-on) | Evita cold starts, $5/mês, ideal para MVP |
| **Worker de Processamento** | AWS Lambda (Python 3.11) | Serverless, pago por uso, suporta até 15 min/execução |
| **Fila de Jobs** | AWS SQS (Standard Queue) | Confiável, serverless, integração nativa com Lambda |
| **Banco de Dados** | PostgreSQL (Supabase Free Tier) | Relacional, ACID, queries complexas, 500MB grátis |
| **Armazenamento** | AWS S3 (bucket privado) | Storage barato, presigned URLs, lifecycle policies |
| **IA - Transcrição** | OpenAI Whisper API | Melhor custo-benefício ($0.006/min) |
| **IA - Resumo** | OpenAI GPT-4o-mini | Barato ($0.15/1M tokens input) e eficiente |
| **Autenticação** | Supabase Auth | JWT, MFA, OAuth, grátis até 50k MAU |
| **Monitoramento** | Sentry (erros) + CloudWatch (logs) | Sentry Free Tier + CloudWatch incluído na AWS |
| **Rate Limiting** | Upstash Redis (Free Tier) | Serverless, 10k requests/dia grátis |
| **Notificações Real-time** | Supabase Realtime (WebSocket) | Incluído no Supabase, notifica quando job termina |

---

## 🧾 Decisões de Design

### ⚖️ **Design Decision #01 — Política Zero-Storage de Dados Sensíveis**
**Decisão:** Nenhum áudio ou transcrição completa é armazenado permanentemente.

**Implementação:**
- Áudios são mantidos no S3 **apenas durante o processamento** (máx. 1 hora)
- Lifecycle policy automática deleta arquivos após 2 horas
- Transcrições nunca tocam disco — processadas em memória
- Apenas **resumos estruturados e anonimizados** são persistidos
- Logs de processamento não contêm dados sensíveis (apenas metadados)

**Benefícios:**
- ✅ Conformidade GDPR/LGPD simplificada
- ✅ Redução de custos de storage (99% de economia)
- ✅ Menor superfície de ataque em caso de breach
- ✅ Não requer criptografia complexa de dados em repouso

---

### ⚙️ **Design Decision #02 — Arquitetura Assíncrona desde o MVP**
**Decisão:** Processamento de áudio é **assíncrono** desde o início, usando fila + worker.

**Motivo:**
- Sessões de 50 minutos levam ~3-5 minutos para processar
- API síncrona causaria timeouts e má UX
- Permite escalabilidade horizontal (múltiplos workers)
- Worker pode ter retry logic robusto

**Implementação:**
- API REST cria job e retorna imediatamente com `job_id`
- SQS enfileira job (visibilidade timeout de 15 min)
- Lambda processa de forma independente
- Frontend recebe notificação via Supabase Realtime quando completo

---

### 🧠 **Design Decision #03 — Contexto Completo para Resumo**
**Decisão:** Transcrever **todo o áudio primeiro**, depois gerar resumo com contexto completo.

**Alternativa rejeitada:** Resumir blocos pequenos e depois combinar.

**Motivo:**
- Whisper transcribe 50 min em ~2 minutos
- GPT-4o-mini suporta até 128k tokens (suficiente para 2h de transcrição)
- Resumo com contexto completo é **mais coerente e preciso**
- Evita perda de nuances entre "blocos"

---

### 🔐 **Design Decision #04 — Anonimização Automática de Resumos**
**Decisão:** Resumos gerados pela IA **removem PII (Personally Identifiable Information)**.

**Implementação:**
- Prompt do GPT instrui explicitamente: "substitua nomes reais por 'Paciente', remova endereços, CPF, telefones"
- Backend valida output com regex patterns (detecta padrões de PII)
- Se PII detectado, reprocessa com prompt mais restritivo
- Terapeuta pode editar resumo manualmente se necessário

**Exemplo:**
```
❌ "João da Silva, CPF 123.456.789-00, mora na Rua X, 123"
✅ "Paciente relatou dificuldades no ambiente doméstico"
```  

---

## 💰 Estimativa de Custos Mensais (MVP Realista)

### 📊 Premissas de Cálculo
- **10 terapeutas ativos** no MVP
- **20 sessões/terapeuta/mês** = 200 sessões totais
- **40 minutos médios** por sessão
- **~5000 palavras** por transcrição (250 palavras/min falado)

---

### 💵 Custos Detalhados

| Serviço | Cálculo | Custo/mês | Observações |
|---------|---------|-----------|-------------|
| **Frontend (Vercel)** | Free Tier | **$0** | Até 100GB bandwidth/mês |
| **Backend API (Railway)** | Starter Plan | **$5** | 512MB RAM, always-on |
| **PostgreSQL (Supabase)** | Free Tier | **$0** | 500MB storage, 2GB bandwidth |
| **OpenAI Whisper** | 200 × 40min × $0.006 | **$48** | Transcrição de áudio |
| **OpenAI GPT-4o-mini** | 200 × 6k tokens × $0.15/1M | **$0.18** | Geração de resumos |
| **AWS S3** | 8GB storage × $0.023 | **$0.20** | Storage temporário (lifecycle 2h) |
| **AWS SQS** | 200 jobs × $0.0000004 | **$0** | Praticamente grátis (1M requests = $0.40) |
| **AWS Lambda** | 200 × 5min × 1GB RAM | **$1.50** | Worker de processamento |
| **CloudWatch Logs** | 1GB logs | **$0.50** | Monitoramento |
| **Upstash Redis** | Free Tier | **$0** | Rate limiting (10k requests/dia) |
| **Sentry** | Free Tier | **$0** | Até 5k errors/mês |
| | | | |
| **TOTAL MENSAL** | | **💰 $55.38** | Custo real com 200 sessões |
| **Custo por sessão** | | **$0.28** | Pode cobrar $5-10 para lucrar |
| **Break-even** | | **~11 sessões** | Cobrando $5/sessão |

---

### 📈 Projeção de Escalabilidade

| Cenário | Sessões/mês | Custo OpenAI | Custo Infra | Total/mês | Receita¹ | Margem |
|---------|-------------|--------------|-------------|-----------|---------|--------|
| **MVP** | 200 | $48 | $7 | **$55** | $1,000 | 95% |
| **Crescimento** | 1,000 | $240 | $15 | **$255** | $5,000 | 95% |
| **Escala** | 5,000 | $1,200 | $50 | **$1,250** | $25,000 | 95% |

¹ Considerando preço de $5/sessão para o terapeuta

---

### 🎯 Estratégias de Otimização de Custos

1. **Whisper Self-Hosted (futuro):** Economiza 80% se rodar Whisper localmente
2. **Batch Processing:** Agrupar jobs reduz cold starts do Lambda
3. **Caching de Resumos:** Se reprocessado, usar cache (Redis)
4. **Modelo Fine-Tuned:** GPT-4o-mini fine-tuned pode reduzir tokens necessários

---

## 🧭 Roadmap de Desenvolvimento (MVP Realista)

| Fase | Duração | Entregas | Critérios de Aceite |
|------|---------|----------|---------------------|
| **Fase 1: Fundação** | 2 semanas | | |
| Sprint 1 | Semana 1 | Setup de repositório, CI/CD, infraestrutura AWS | Pipeline funcionando, ambientes dev/staging/prod |
| Sprint 2 | Semana 2 | Backend FastAPI + PostgreSQL + autenticação | Login/logout funcional, API health check |
| | | | |
| **Fase 2: Core Features** | 3 semanas | | |
| Sprint 3 | Semana 3 | Upload de áudio + S3 presigned URLs | Upload de 50MB funcional, lifecycle policy ativa |
| Sprint 4 | Semana 4 | Worker Lambda + SQS + integração Whisper | Transcrição de áudio end-to-end |
| Sprint 5 | Semana 5 | Integração GPT-4o-mini + anonimização | Resumo estruturado gerado corretamente |
| | | | |
| **Fase 3: Interface** | 2 semanas | | |
| Sprint 6 | Semana 6 | Frontend Next.js + dashboard de pacientes | CRUD de pacientes funcional |
| Sprint 7 | Semana 7 | Tela de upload + histórico de sessões | UX completa, notificações real-time |
| | | | |
| **Fase 4: Segurança & Conformidade** | 1.5 semanas | | |
| Sprint 8 | Semana 8 | Rate limiting, validação de inputs, HTTPS | Testes de penetração básicos passando |
| Sprint 8.5 | Meio da semana | Auditoria GDPR, política de privacidade | Checklist de conformidade 100% |
| | | | |
| **Fase 5: Testes & Beta** | 2 semanas | | |
| Sprint 9 | Semana 9 | Testes E2E, load testing, bug fixes | <5 bugs críticos, <20 bugs menores |
| Sprint 10 | Semana 10 | Beta fechado com 3-5 terapeutas reais | Feedback coletado, ajustes de UX |
| | | | |
| **Fase 6: Launch** | 0.5 semanas | | |
| Sprint 11 | Semana 11 | Deploy prod, monitoramento, documentação | Sistema estável por 48h sem incidentes |

**Total:** 11 semanas (~2.5 meses) até MVP público

---

### 🎯 Marcos Críticos (Gates)

Cada marco deve ser aprovado antes de prosseguir:

✅ **Gate 1 (fim Semana 2):** Autenticação funcionando + testes unitários básicos  
✅ **Gate 2 (fim Semana 5):** Processamento completo áudio → resumo end-to-end  
✅ **Gate 3 (fim Semana 8):** Auditoria de segurança aprovada  
✅ **Gate 4 (fim Semana 10):** Feedback beta positivo (NPS > 7/10)

---

## 🔒 Segurança e Privacidade

### 🛡️ Camadas de Segurança

#### 1. **Segurança em Trânsito**
- ✅ **TLS 1.3** obrigatório em todas as conexões (frontend ↔ backend, backend ↔ AWS)
- ✅ **HSTS** habilitado (força HTTPS)
- ✅ **Certificate pinning** no frontend (previne MITM)
- ✅ Presigned URLs do S3 com **expiração de 15 minutos**

#### 2. **Segurança em Repouso**
- ✅ PostgreSQL: **encryption at rest** habilitado no Supabase
- ✅ S3: **AES-256 server-side encryption** (SSE-S3) automático
- ✅ Backups do banco: **criptografados e retidos por 7 dias**

#### 3. **Controle de Acesso**
- ✅ **RBAC (Role-Based Access Control):** 
  - `therapist` - acesso apenas aos próprios pacientes/sessões
  - `admin` - acesso a logs e métricas (sem dados de sessões)
- ✅ **RLS (Row-Level Security)** no PostgreSQL: terapeutas só veem seus dados
- ✅ **JWT tokens** com expiração de 1 hora (refresh token de 30 dias)
- ✅ **MFA opcional** via Supabase Auth (TOTP)

#### 4. **Proteção de Infraestrutura**
- ✅ **Rate limiting:** 100 requests/minuto por IP (Upstash Redis)
- ✅ **DDoS protection:** Cloudflare Free Tier na frente da Vercel
- ✅ **Input validation:** Pydantic models no FastAPI (previne injection)
- ✅ **CORS restrito:** Apenas domínio oficial permitido
- ✅ **Secrets management:** AWS Secrets Manager (rotação automática)

#### 5. **Auditoria e Monitoramento**
- ✅ **Audit logs:** Todas as ações sensíveis registradas (quem acessou o quê, quando)
- ✅ **Anomaly detection:** Alerta se >10 sessões processadas em 1h por um terapeuta
- ✅ **Security alerts:** Sentry notifica sobre erros de autenticação suspeitos

---

### ⚖️ Conformidade GDPR/LGPD

#### 📋 Checklist de Conformidade

| Requisito | Status | Implementação |
|-----------|--------|---------------|
| **Art. 6 - Lawful basis** | ✅ | Consentimento explícito do paciente (checkbox + timestamp) |
| **Art. 7 - Consent** | ✅ | Paciente consente antes da primeira sessão gravada |
| **Art. 13 - Information** | ✅ | Política de privacidade acessível, linguagem clara |
| **Art. 15 - Right of access** | ✅ | Endpoint `/me/data-export` retorna todos os dados do terapeuta |
| **Art. 16 - Right to rectification** | ✅ | Terapeuta pode editar resumos manualmente |
| **Art. 17 - Right to erasure** | ✅ | Endpoint `/patients/{id}/forget` deleta tudo (soft + hard delete) |
| **Art. 25 - Data protection by design** | ✅ | Zero-storage de áudio, anonimização automática |
| **Art. 30 - Records of processing** | ✅ | Audit logs completos (retidos por 2 anos) |
| **Art. 32 - Security** | ✅ | Criptografia, pseudonimização, testes de penetração |
| **Art. 33 - Breach notification** | ✅ | Processo de 72h para notificar autoridades + usuários |
| **Art. 35 - DPIA** | ⏳ | Data Protection Impact Assessment antes do launch |

#### 🌍 Localização de Dados
- **Região primária:** AWS `us-east-1` (N. Virginia)
- **GDPR compliance:** Dados podem ficar nos EUA com **Standard Contractual Clauses (SCCs)**
- **Alternativa futura:** Migrar para `eu-west-1` (Ireland) se exigido

#### 🧑‍⚖️ Responsável pela Proteção de Dados
- **DPO (Data Protection Officer):** [Nome do fundador/CTO]
- **Contato:** privacy@theramind.com
- **Responsabilidades:** 
  - Monitorar conformidade
  - Responder a data subject requests (DSR) em até 30 dias
  - Coordenar breach response

---

### 📜 Políticas e Documentos Legais

#### Documentos obrigatórios (antes do launch):
1. ✅ **Terms of Service** - Termos de uso para terapeutas
2. ✅ **Privacy Policy** - Como dados são coletados/processados
3. ✅ **Data Processing Agreement (DPA)** - Contrato GDPR com terapeutas
4. ✅ **Patient Consent Form** - Template para terapeutas coletarem consentimento
5. ⏳ **Incident Response Plan** - Protocolo em caso de data breach
6. ⏳ **Data Retention Policy** - Quanto tempo dados ficam armazenados

#### Retenção de Dados
| Tipo de Dado | Período de Retenção | Motivo |
|--------------|---------------------|--------|
| Resumos de sessões | Indefinido (até exclusão manual) | Core do produto |
| Audit logs | 2 anos | Conformidade legal |
| Dados de autenticação | Até exclusão da conta | Segurança |
| Áudio temporário | Máx. 2 horas | Processamento apenas |
| Logs de erro (sem PII) | 30 dias | Debugging |  

---

## 🧩 Estrutura de Dados Completa (PostgreSQL)

### Tabela: `therapists`
```sql
CREATE TABLE therapists (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  full_name VARCHAR(255) NOT NULL,
  professional_license VARCHAR(100), -- CRP, CRM, etc
  role VARCHAR(20) DEFAULT 'therapist', -- therapist | admin
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  last_login_at TIMESTAMP,
  is_active BOOLEAN DEFAULT TRUE
);
```

### Tabela: `patients`
```sql
CREATE TABLE patients (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  therapist_id UUID NOT NULL REFERENCES therapists(id) ON DELETE CASCADE,
  
  -- Dados básicos (mínimo necessário)
  identifier VARCHAR(100) NOT NULL, -- Iniciais ou pseudônimo (não nome completo)
  date_of_birth DATE, -- Para cálculo de idade, opcional
  
  -- Consentimento
  consent_given BOOLEAN DEFAULT FALSE,
  consent_timestamp TIMESTAMP,
  consent_ip VARCHAR(45), -- IPv6 suportado
  
  -- Metadata
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  is_deleted BOOLEAN DEFAULT FALSE, -- Soft delete
  deleted_at TIMESTAMP,
  
  CONSTRAINT unique_patient_per_therapist UNIQUE(therapist_id, identifier)
);

-- RLS Policy: Terapeutas só veem seus próprios pacientes
CREATE POLICY therapist_patients ON patients
  FOR ALL USING (therapist_id = auth.uid());
```

### Tabela: `sessions`
```sql
CREATE TABLE sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  therapist_id UUID NOT NULL REFERENCES therapists(id),
  patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
  
  -- Dados da sessão
  session_date DATE NOT NULL, -- Data real da sessão
  session_duration_minutes INT, -- Duração real (ex: 45)
  
  -- Processamento
  processing_status VARCHAR(20) DEFAULT 'pending', -- pending | processing | completed | failed
  job_id VARCHAR(100), -- ID do job no SQS
  
  -- Metadata do áudio (não armazenado)
  audio_metadata JSONB, -- {format: "mp3", size_mb: 12.5, sample_rate: 44100}
  
  -- Resumo gerado
  summary JSONB, -- Estrutura abaixo
  
  -- Auditoria
  created_at TIMESTAMP DEFAULT NOW(), -- Quando foi criado o registro
  processing_started_at TIMESTAMP,
  processing_completed_at TIMESTAMP,
  updated_at TIMESTAMP DEFAULT NOW(),
  
  -- Soft delete
  is_deleted BOOLEAN DEFAULT FALSE,
  deleted_at TIMESTAMP,
  
  -- Versionamento (se reprocessado)
  version INT DEFAULT 1,
  
  CONSTRAINT valid_status CHECK (
    processing_status IN ('pending', 'processing', 'completed', 'failed', 'cancelled')
  )
);

-- RLS Policy
CREATE POLICY therapist_sessions ON sessions
  FOR ALL USING (therapist_id = auth.uid());

-- Índices para performance
CREATE INDEX idx_sessions_therapist ON sessions(therapist_id);
CREATE INDEX idx_sessions_patient ON sessions(patient_id);
CREATE INDEX idx_sessions_date ON sessions(session_date DESC);
CREATE INDEX idx_sessions_status ON sessions(processing_status) WHERE processing_status != 'completed';
```

### Estrutura do campo `summary` (JSONB)
```json
{
  "main_points": [
    "Paciente relatou aumento de ansiedade relacionada ao trabalho",
    "Discussão sobre estratégias de enfrentamento",
    "Exploração de gatilhos específicos em ambiente profissional"
  ],
  "emotions_observed": [
    {
      "emotion": "ansiedade",
      "intensity": "alta",
      "context": "Ao falar sobre prazos no trabalho"
    },
    {
      "emotion": "alívio",
      "intensity": "moderada",
      "context": "Após discussão de técnicas de respiração"
    }
  ],
  "behavioral_patterns": [
    "Tendência a evitar confrontos",
    "Dificuldade em estabelecer limites"
  ],
  "action_items": [
    {
      "task": "Praticar técnica de respiração 4-7-8 diariamente",
      "frequency": "2x/dia",
      "deadline": "Próxima sessão"
    },
    {
      "task": "Manter diário de gatilhos de ansiedade",
      "frequency": "Sempre que ocorrer",
      "deadline": "Próxima sessão"
    }
  ],
  "risk_assessment": {
    "level": "baixo", // baixo | moderado | alto | crítico
    "notes": "Sem ideação suicida ou risco imediato"
  },
  "next_session_focus": [
    "Revisar diário de gatilhos",
    "Aprofundar técnicas de assertividade"
  ],
  "therapist_notes": "Paciente demonstrou abertura para intervenções cognitivo-comportamentais. Progresso notável desde última sessão.",
  "ai_confidence_score": 0.92, // 0-1, confiança do GPT na qualidade do resumo
  "tokens_used": {
    "input": 5823,
    "output": 421
  }
}
```

### Tabela: `audit_logs`
```sql
CREATE TABLE audit_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Quem fez a ação
  user_id UUID REFERENCES therapists(id),
  user_email VARCHAR(255),
  
  -- O que foi feito
  action VARCHAR(100) NOT NULL, -- login | logout | create_session | delete_patient | export_data
  resource_type VARCHAR(50), -- session | patient | therapist
  resource_id UUID,
  
  -- Detalhes
  details JSONB, -- Informações adicionais context-specific
  
  -- Contexto técnico
  ip_address VARCHAR(45),
  user_agent TEXT,
  request_id VARCHAR(100), -- Para correlação com logs de aplicação
  
  -- Timestamp
  created_at TIMESTAMP DEFAULT NOW(),
  
  -- Índices
  INDEX idx_audit_user (user_id, created_at DESC),
  INDEX idx_audit_action (action, created_at DESC)
);

-- Audit logs NUNCA são deletados (conformidade legal)
-- Retention: 2 anos, depois arquivados em S3 Glacier
```

### Tabela: `processing_errors`
```sql
CREATE TABLE processing_errors (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id UUID REFERENCES sessions(id),
  job_id VARCHAR(100),
  
  -- Erro
  error_type VARCHAR(50), -- whisper_api_error | gpt_timeout | s3_access_denied
  error_message TEXT,
  error_stack TEXT, -- Stack trace (sem PII)
  
  -- Retry
  retry_count INT DEFAULT 0,
  max_retries INT DEFAULT 3,
  next_retry_at TIMESTAMP,
  
  -- Context
  created_at TIMESTAMP DEFAULT NOW(),
  resolved_at TIMESTAMP,
  is_resolved BOOLEAN DEFAULT FALSE
);
```

---

## 🔄 Fluxo de Dados Completo (End-to-End)

### 1️⃣ Upload de Áudio
```mermaid
Frontend → Backend API → S3
  1. Terapeuta seleciona paciente e arquivo de áudio
  2. Frontend valida: formato (mp3/wav/m4a), tamanho (<100MB), duração (<60min)
  3. Frontend chama POST /api/sessions/upload-url
  4. Backend gera presigned URL do S3 (expira em 15min)
  5. Frontend faz upload DIRETO para S3 (sem passar pelo backend)
  6. Frontend chama POST /api/sessions com S3 key + metadata
  7. Backend cria registro na tabela sessions (status=pending)
  8. Backend enfileira job no SQS
  9. Backend retorna {session_id, job_id} para o frontend
```

### 2️⃣ Processamento (Worker Lambda)
```python
# Pseudocódigo simplificado
def lambda_handler(event, context):
    job = parse_sqs_message(event)
    session = db.get_session(job.session_id)
    
    try:
        # Update status
        session.update(status='processing', processing_started_at=now())
        
        # 1. Download áudio do S3 (streaming, não salva em disco)
        audio_stream = s3.get_object(job.s3_key)
        
        # 2. Transcrição com Whisper
        transcript = openai.Audio.transcribe(
            model="whisper-1",
            file=audio_stream,
            language="pt"  # Português
        )
        
        # 3. Validação de qualidade da transcrição
        if len(transcript.text) < 100:
            raise Exception("Transcrição muito curta - possível áudio corrompido")
        
        # 4. Gerar resumo com GPT-4o-mini
        summary = generate_summary(transcript.text)
        
        # 5. Anonimização (detectar e remover PII)
        summary_clean = anonymize_pii(summary)
        
        # 6. Salvar no banco
        session.update(
            status='completed',
            summary=summary_clean,
            processing_completed_at=now()
        )
        
        # 7. Notificar frontend via Supabase Realtime
        realtime.publish(f"session:{session.id}", {"status": "completed"})
        
        # 8. DELETAR áudio do S3 permanentemente
        s3.delete_object(job.s3_key)
        
        # 9. Audit log
        audit_log.create(action="session_processed", resource_id=session.id)
        
    except Exception as e:
        # Retry logic
        if job.retry_count < 3:
            sqs.change_visibility_timeout(job, delay=60 * (2 ** job.retry_count))
            job.retry_count += 1
        else:
            session.update(status='failed')
            error_log.create(session_id=session.id, error=str(e))
            # Notificar terapeuta sobre falha
```

### 3️⃣ Notificação Real-time (Frontend)
```typescript
// Frontend subscribe ao Realtime
const channel = supabase.channel(`session:${sessionId}`)
  .on('broadcast', { event: 'status_update' }, (payload) => {
    if (payload.status === 'completed') {
      // Recarregar página ou exibir resumo
      router.refresh()
      toast.success('Resumo gerado com sucesso!')
    } else if (payload.status === 'failed') {
      toast.error('Erro ao processar áudio. Tente novamente.')
    }
  })
  .subscribe()
```

---

## 🎨 UX - Experiência do Usuário

### Dashboard Principal
```
┌──────────────────────────────────────────────────────┐
│  TheraMind                           [👤 Dr. Silva]  │
├──────────────────────────────────────────────────────┤
│  📊 Visão Geral                                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │
│  │ 45          │ │ 12          │ │ 3           │    │
│  │ Pacientes   │ │ Sessões/mês │ │ Pendentes   │    │
│  └─────────────┘ └─────────────┘ └─────────────┘    │
│                                                       │
│  🎙️ Nova Sessão                                      │
│  [Selecionar Paciente ▼] [📎 Escolher Áudio]        │
│                                                       │
│  📋 Sessões Recentes                                 │
│  ┌─────────────────────────────────────────────┐    │
│  │ 13/11 - Paciente A.S. ✅ Concluído           │    │
│  │ 12/11 - Paciente M.J. ⏳ Processando (2min)  │    │
│  │ 11/11 - Paciente R.T. ✅ Concluído           │    │
│  └─────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────┘
```

### Tela de Upload
1. **Seleção de Paciente** (dropdown com busca)
2. **Data da Sessão** (default: hoje)
3. **Upload de Áudio** (drag & drop ou clique)
4. **Barra de Progresso** do upload
5. **Estimativa de tempo** de processamento (ex: "~3 minutos")

### Visualização do Resumo
```markdown
# Sessão de 13/11/2024 - Paciente A.S.
Duração: 45 minutos

## 🎯 Pontos Principais
- Discussão sobre ansiedade no trabalho
- Técnicas de respiração
- Estabelecimento de limites

## 😊 Emoções Observadas
- Ansiedade (alta) ao falar de trabalho
- Alívio (moderado) após técnicas

## ✅ Tarefas para Casa
- [ ] Respiração 4-7-8 (2x/dia)
- [ ] Diário de gatilhos

## 📝 Notas do Terapeuta
[Campo editável]

[Botão: Editar Resumo] [Botão: Exportar PDF] [Botão: Excluir]
```

---

## 🚨 Tratamento de Erros e Resiliência

### Cenários de Erro

| Erro | Causa | Tratamento | UX |
|------|-------|------------|-----|
| **Upload falha** | Conexão interrompida | Retry automático (3x) | "Reconectando..." → "Falha. Tente novamente" |
| **Áudio corrompido** | Arquivo inválido | Validação no frontend | "Arquivo inválido. Use MP3/WAV" |
| **Whisper API timeout** | Sobrecarga OpenAI | Retry com backoff exponencial | "Processando... pode levar mais tempo" |
| **GPT API rate limit** | Muitas requisições | Queue de espera | "Na fila de processamento (posição #3)" |
| **S3 indisponível** | Outage AWS | Fallback para Supabase Storage | Transparente para usuário |
| **Worker crash** | Exception não tratada | SQS reenviar job após timeout | Retry automático invisível |

### SLO (Service Level Objectives)
- **Uptime:** 99.5% (permitido ~3.6h downtime/mês)
- **Tempo de processamento:** 95% das sessões em <5 minutos
- **Taxa de erro:** <1% das sessões falham permanentemente

---

## 📊 Monitoramento e Alertas

### Métricas Críticas (CloudWatch)
1. **Lambda Duration** - média deve ser <200s
2. **SQS Queue Depth** - alerta se >10 jobs aguardando
3. **Error Rate** - alerta se >2% em 5 minutos
4. **API Latency** - P95 deve ser <500ms
5. **Cost per Session** - rastrear para detectar anomalias

### Alertas (PagerDuty ou email)
- 🔴 **P0 (Crítico):** Sistema totalmente inoperante - notificar imediatamente
- 🟡 **P1 (Alto):** Taxa de erro >5% - notificar em 15 min
- 🟢 **P2 (Baixo):** Custo/sessão aumentou 50% - notificar em 24h

---

## ✅ Definição de Pronto (MVP)

### Checklist de Launch

#### Funcionalidades
- [ ] Login/logout com email + senha
- [ ] MFA opcional (TOTP)
- [ ] CRUD completo de pacientes
- [ ] Upload de áudio (mp3/wav/m4a, até 100MB)
- [ ] Processamento assíncrono end-to-end
- [ ] Visualização de resumos estruturados
- [ ] Edição manual de resumos
- [ ] Exclusão de sessões (soft delete)
- [ ] Exportação de dados (JSON/PDF)
- [ ] "Direito ao esquecimento" (deletar paciente + sessões)

#### Segurança
- [ ] HTTPS em todas as conexões
- [ ] RLS habilitado no PostgreSQL
- [ ] Rate limiting ativo (100 req/min)
- [ ] Input validation em todos os endpoints
- [ ] Secrets em AWS Secrets Manager
- [ ] Logs de auditoria funcionando
- [ ] Teste de penetração básico realizado

#### Conformidade
- [ ] Política de privacidade publicada
- [ ] Termos de serviço publicados
- [ ] Template de consentimento do paciente disponível
- [ ] DPA (Data Processing Agreement) assinado
- [ ] DPIA (Data Protection Impact Assessment) completo

#### Operação
- [ ] Monitoramento Sentry + CloudWatch ativo
- [ ] Alertas configurados
- [ ] Runbook de incidentes documentado
- [ ] Backup automático diário testado
- [ ] Processo de rollback testado

#### Testes
- [ ] Cobertura de testes >70% no backend
- [ ] Testes E2E das flows principais (Playwright)
- [ ] Load testing com 100 sessões simultâneas
- [ ] Testes de falha (chaos engineering básico)

#### UX
- [ ] Mobile-responsive (funciona em celular)
- [ ] Tempos de carregamento <2s
- [ ] Mensagens de erro claras e acionáveis
- [ ] Onboarding de novos usuários (tour guiado)
- [ ] Documentação/FAQ publicada

---

## 🚀 Próximos Passos Imediatos

### 1. Setup Inicial (Dia 1-2)
```bash
# Repositório
- Criar repositório GitHub privado
- Configurar branch protection (main + staging)
- Setup CI/CD com GitHub Actions

# Infraestrutura
- Criar conta AWS (ou usar existente)
- Criar bucket S3 privado com lifecycle policy
- Configurar Supabase projeto (free tier)
- Criar conta OpenAI e obter API key

# Ambiente de Desenvolvimento
- Setup Next.js 15 + TypeScript
- Setup FastAPI + Poetry/UV para deps
- Configurar variáveis de ambiente (.env.example)
```

### 2. Priorização de Features (MoSCoW)

#### ✅ Must Have (Essencial para MVP)
- Autenticação (email/senha)
- CRUD de pacientes
- Upload + processamento de áudio
- Visualização de resumos
- Soft delete

#### 🟡 Should Have (Importante, mas não bloqueante)
- MFA (autenticação de dois fatores)
- Exportação de dados (PDF/JSON)
- Edição de resumos
- Busca/filtros avançados
- Notificações real-time

#### 🟢 Could Have (Desejável)
- Gráficos de progresso do paciente
- Tags/categorização de sessões
- Integração com calendário
- Modo escuro
- App mobile nativo

#### ⚪ Won't Have (Futuro, fora do MVP)
- Múltiplos idiomas (i18n)
- Integração com EHR (prontuários eletrônicos)
- API pública para terceiros
- White-label para clínicas

### 3. Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| **OpenAI aumenta preços** | Média | Alto | Plano B: Whisper self-hosted + modelo open-source |
| **GDPR não-conformidade** | Baixa | Crítico | Auditoria legal antes do launch (€2k investimento) |
| **Baixa adoção inicial** | Alta | Médio | Marketing em grupos de psicólogos, freemium inicial |
| **Custos excedem receita** | Média | Alto | Monitoramento em tempo real + alertas de budget |
| **Qualidade dos resumos** | Baixa | Alto | Validação com terapeutas reais durante beta |
| **Breach de dados** | Baixa | Crítico | Penetration testing + bug bounty após launch |

### 4. Modelo de Negócio (Pricing)

#### Opção 1: Por Sessão
- **Free Tier:** 5 sessões/mês
- **Professional:** $5/10 sessões ou $20/mês ilimitado
- **Clinic:** $100/mês para até 5 terapeutas

#### Opção 2: SaaS Tradicional
- **Free:** 3 sessões/mês
- **Starter:** $15/mês - 20 sessões
- **Pro:** $35/mês - 100 sessões
- **Enterprise:** Custom - volume alto

**Recomendação:** Começar com Opção 2 (mais previsível para cash flow)

### 5. Métricas de Sucesso (KPIs)

**Mês 1-3 (Beta):**
- ✅ 10-20 terapeutas ativos
- ✅ 200+ sessões processadas
- ✅ NPS (Net Promoter Score) > 7/10
- ✅ Uptime > 99%
- ✅ <1% taxa de erro

**Mês 4-6 (Early Adopters):**
- ✅ 50+ terapeutas pagantes
- ✅ $1,000 MRR (Monthly Recurring Revenue)
- ✅ Churn rate < 10%
- ✅ 1000+ sessões/mês

**Mês 7-12 (Growth):**
- ✅ 200+ terapeutas
- ✅ $5,000 MRR
- ✅ LTV/CAC > 3:1
- ✅ Payback period < 6 meses

---

## 📝 Resumo das Correções Realizadas

### 🔴 Falhas Críticas Corrigidas

| # | Problema Original | Correção Implementada |
|---|------------------|----------------------|
| 1 | **Divisão de áudio no frontend** | Movido para processamento no backend via worker Lambda |
| 2 | **Falta de segurança detalhada** | Adicionada seção completa com TLS, RLS, RBAC, criptografia, audit logs |
| 3 | **Conformidade GDPR vaga** | Checklist completo GDPR/LGPD, DPA, consentimento, direito ao esquecimento |
| 4 | **Custos subestimados** | Recalculado: $55/mês (não $10-15), com breakdown detalhado por serviço |
| 5 | **Stack indecisa** | Definida stack completa: PostgreSQL (não MongoDB), S3 (não Supabase Storage), Railway para API |

### 🟡 Falhas Moderadas Corrigidas

| # | Problema Original | Correção Implementada |
|---|------------------|----------------------|
| 6 | **Estrutura de dados incompleta** | Expandida com 4 tabelas completas + campos de auditoria, soft delete, versionamento |
| 7 | **Roadmap otimista** | Estendido de 5 para 11 semanas, com fases de segurança, beta e gates de qualidade |
| 8 | **Falta detalhes operacionais** | Adicionado monitoramento, alertas, SLOs, tratamento de erros, retry logic |
| 9 | **UX vaga** | Mockups de telas, fluxos completos, notificações real-time |
| 10 | **Arquitetura sem worker** | Arquitetura assíncrona com SQS + Lambda desde o MVP |

### ✅ Novas Seções Adicionadas

1. **🏗️ Diagrama de Arquitetura** - Visual completo do fluxo de dados
2. **🔒 Segurança e Privacidade** - 5 camadas de segurança detalhadas
3. **⚖️ Conformidade GDPR/LGPD** - Checklist artigo por artigo
4. **📜 Políticas e Documentos Legais** - Lista de documentos obrigatórios
5. **🔄 Fluxo de Dados End-to-End** - Pseudocódigo do worker
6. **🎨 UX - Experiência do Usuário** - Mockups de telas
7. **🚨 Tratamento de Erros** - Cenários de falha + SLOs
8. **📊 Monitoramento e Alertas** - Métricas críticas + alertas
9. **✅ Definição de Pronto** - Checklist completo de launch
10. **🚀 Próximos Passos** - Ações imediatas + riscos + pricing

---

## 🎯 Principais Melhorias

### Antes → Depois

| Aspecto | Antes | Depois |
|---------|-------|--------|
| **Custos mensais** | $10-15 | **$55** (realista) |
| **Tempo até MVP** | 5 semanas | **11 semanas** (com segurança + beta) |
| **Arquitetura** | API síncrona | **Assíncrona** (SQS + Lambda) |
| **Banco de dados** | "DynamoDB ou MongoDB" | **PostgreSQL** (definido) |
| **Segurança** | 4 linhas genéricas | **50+ itens** específicos |
| **GDPR** | Menção superficial | **Checklist completo** artigo por artigo |
| **Estrutura de dados** | 5 campos | **30+ campos** + 4 tabelas |
| **Processamento** | Frontend divide áudio | **Backend processa** com contexto completo |
| **UX** | Não documentada | **Mockups + flows** completos |
| **Operação** | Não mencionada | **Monitoramento, alertas, SLOs** |

---

## ✨ Conclusão

Este documento agora fornece uma **base sólida e realista** para o desenvolvimento do TheraMind MVP. 

### Próximas Ações Recomendadas:
1. ✅ **Revisão com stakeholders** (validar requisitos)
2. ✅ **Consulta legal** para GDPR/LGPD (~€2k, crítico)
3. ✅ **Setup de infraestrutura** (Semana 1)
4. ✅ **Iniciar desenvolvimento** seguindo roadmap de 11 semanas
5. ✅ **Contratar beta testers** (3-5 terapeutas reais)

**Diferencial do TheraMind:** Único SaaS que combina **zero-storage de dados sensíveis** + **IA de alta qualidade** + **conformidade GDPR by design** a um custo acessível para terapeutas independentes.

---

**Versão do Documento:** 2.0 (Revisado e Corrigido)  
**Última Atualização:** 13 de Novembro de 2024  
**Autor:** [Seu Nome]  
**Status:** ✅ Pronto para Implementação
