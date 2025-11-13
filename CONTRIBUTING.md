# Contribuindo para o TheraMind

Obrigado por considerar contribuir com o TheraMind! 🎉

## 📋 Código de Conduta

Este projeto adere a um código de conduta. Ao participar, você concorda em manter um ambiente respeitoso e colaborativo.

## 🚀 Como Contribuir

### Reportando Bugs

1. **Verifique** se o bug já não foi reportado nas [Issues](https://github.com/youruser/theramind/issues)
2. **Abra uma nova issue** com:
   - Título claro e descritivo
   - Passos para reproduzir
   - Comportamento esperado vs. observado
   - Screenshots (se aplicável)
   - Ambiente (OS, versões, etc.)

### Sugerindo Melhorias

1. **Verifique** se a funcionalidade já não foi sugerida
2. **Abra uma issue** com tag `enhancement` descrevendo:
   - Problema que resolve
   - Solução proposta
   - Alternativas consideradas

### Pull Requests

1. **Fork** o repositório
2. **Clone** seu fork localmente
3. **Crie uma branch** descritiva:
   ```bash
   git checkout -b feature/nome-da-feature
   git checkout -b fix/nome-do-bug
   ```

4. **Faça suas alterações** seguindo os padrões:
   - Python: PEP 8, type hints, docstrings
   - TypeScript: ESLint + Prettier
   - Commits: Conventional Commits (feat:, fix:, docs:, etc.)

5. **Adicione testes** para novas funcionalidades

6. **Execute os testes**:
   ```bash
   # Backend
   cd backend && pytest
   
   # Frontend
   cd frontend && npm test
   ```

7. **Commit suas mudanças**:
   ```bash
   git commit -m "feat: adiciona funcionalidade X"
   ```

8. **Push para seu fork**:
   ```bash
   git push origin feature/nome-da-feature
   ```

9. **Abra um Pull Request** com:
   - Descrição clara das mudanças
   - Referência a issues relacionadas
   - Screenshots/GIFs (se mudanças visuais)

## 🧪 Padrões de Código

### Python (Backend)
```python
# Type hints obrigatórios
def process_audio(file_path: str, duration: int) -> dict[str, Any]:
    """
    Processa arquivo de áudio e retorna resumo.
    
    Args:
        file_path: Caminho do arquivo no S3
        duration: Duração em minutos
        
    Returns:
        Dicionário com resumo estruturado
    """
    pass

# Usar Pydantic para validação
from pydantic import BaseModel

class SessionCreate(BaseModel):
    patient_id: str
    audio_url: str
    duration_minutes: int
```

### TypeScript (Frontend)
```typescript
// Componentes com tipos explícitos
interface SessionCardProps {
  sessionId: string;
  patientName: string;
  date: Date;
}

export const SessionCard: React.FC<SessionCardProps> = ({
  sessionId,
  patientName,
  date
}) => {
  // Implementação
}
```

## 🔒 Segurança

**NUNCA** commite:
- Credenciais ou secrets
- Arquivos `.env`
- Dados de pacientes (mesmo para testes)
- API keys

Se encontrar vulnerabilidades de segurança, **não abra issue pública**. Envie email para security@theramind.com.

## 📝 Documentação

Toda nova funcionalidade deve incluir:
- ✅ Docstrings/JSDoc
- ✅ Atualização do README (se aplicável)
- ✅ Exemplos de uso
- ✅ Testes

## ✅ Checklist antes do PR

- [ ] Código segue os padrões do projeto
- [ ] Testes adicionados e passando
- [ ] Documentação atualizada
- [ ] Sem warnings de linter
- [ ] Commits seguem Conventional Commits
- [ ] Branch atualizada com `main`

## 🎯 Áreas que Precisam de Ajuda

Procurando contribuir mas não sabe por onde começar? Veja issues com labels:
- `good first issue` - Ideal para iniciantes
- `help wanted` - Precisamos de ajuda!
- `bug` - Correções de bugs
- `enhancement` - Novas funcionalidades

## 💬 Dúvidas?

- Abra uma [Discussion](https://github.com/youruser/theramind/discussions)
- Entre no nosso [Discord](https://discord.gg/theramind)
- Email: dev@theramind.com

---

Obrigado por contribuir! 🙏

