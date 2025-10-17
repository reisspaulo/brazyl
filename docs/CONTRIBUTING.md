# Guia de Contribuição - Brazyl

Obrigado por considerar contribuir com o Brazyl! Este documento fornece diretrizes para contribuições.

## Como Contribuir

### Reportar Bugs

1. Verifique se o bug já foi reportado nas [Issues](https://github.com/seu-usuario/brazyl/issues)
2. Se não, crie uma nova issue com:
   - Título claro e descritivo
   - Passos para reproduzir o bug
   - Comportamento esperado vs. atual
   - Screenshots (se aplicável)
   - Versão do software e ambiente

### Sugerir Funcionalidades

1. Verifique se já não foi sugerido
2. Crie uma issue com tag `enhancement`
3. Descreva:
   - Problema que a funcionalidade resolve
   - Solução proposta
   - Alternativas consideradas
   - Impacto e prioridade

### Pull Requests

1. **Fork** o repositório
2. **Clone** seu fork
3. **Crie** uma branch (`git checkout -b feature/minha-funcionalidade`)
4. **Faça** suas mudanças
5. **Teste** suas mudanças
6. **Commit** (`git commit -m 'Adiciona minha funcionalidade'`)
7. **Push** (`git push origin feature/minha-funcionalidade`)
8. **Abra** um Pull Request

## Configuração do Ambiente

### Pré-requisitos
- Python 3.11+
- Docker e Docker Compose
- Git
- Conta Supabase (free tier)

### Setup

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/brazyl.git
cd brazyl

# Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Instale dependências
cd api
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Dependências de desenvolvimento

# Configure .env
cp .env.example .env
# Edite .env com suas credenciais
```

### Executar Testes

```bash
# Todos os testes
pytest

# Com cobertura
pytest --cov=app tests/

# Apenas unitários
pytest tests/unit/

# Apenas integração
pytest tests/integration/

# Com relatório HTML
pytest --cov=app --cov-report=html tests/
```

### Linting e Formatação

```bash
# Black (formatação)
black app/ tests/

# Flake8 (linting)
flake8 app/ tests/

# MyPy (type checking)
mypy app/

# Ou rodar tudo
make lint
```

## Padrões de Código

### Python

#### Estilo
- Seguir [PEP 8](https://pep8.org/)
- Usar Black para formatação
- Máximo 100 caracteres por linha
- Type hints obrigatórios

#### Exemplo
```python
from typing import Optional

async def get_politician_by_id(politician_id: str) -> Optional[dict]:
    """
    Obtém político por ID.
    
    Args:
        politician_id: ID do político
    
    Returns:
        Dados do político ou None se não encontrado
    """
    try:
        result = await supabase.get_politician_by_id(politician_id)
        return result
    except Exception as e:
        logger.error(f"Erro ao buscar político: {str(e)}")
        return None
```

#### Docstrings
- Usar formato Google Style
- Sempre em português BR
- Descrever args, returns, raises

### Commits

#### Mensagens
Usar [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: adiciona endpoint de busca de políticos
fix: corrige erro ao seguir político
docs: atualiza README com instruções
refactor: melhora estrutura do service layer
test: adiciona testes para user service
chore: atualiza dependências
```

Tipos:
- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Documentação
- `refactor`: Refatoração
- `test`: Testes
- `chore`: Tarefas gerais
- `perf`: Performance
- `ci`: CI/CD

### Branches

- `main`: Código em produção
- `develop`: Código em desenvolvimento
- `feature/nome-da-feature`: Novas funcionalidades
- `fix/nome-do-bug`: Correções de bugs
- `docs/nome-da-doc`: Documentação
- `refactor/nome`: Refatorações

### Pull Requests

#### Checklist
- [ ] Código segue padrões do projeto
- [ ] Testes adicionados/atualizados
- [ ] Documentação atualizada
- [ ] Commits seguem padrão
- [ ] PR tem descrição clara
- [ ] Testes passando
- [ ] Sem conflitos com main

#### Template
```markdown
## Descrição
Breve descrição das mudanças.

## Tipo de Mudança
- [ ] Bug fix
- [ ] Nova funcionalidade
- [ ] Breaking change
- [ ] Documentação

## Como Testar
1. ...
2. ...

## Screenshots (se aplicável)

## Checklist
- [ ] Código testado
- [ ] Documentação atualizada
- [ ] Testes passando
```

## Estrutura do Código

### Organização
```
api/
├── app/
│   ├── api/          # Rotas/Controllers
│   ├── services/     # Lógica de negócio
│   ├── models/       # Modelos de dados
│   ├── schemas/      # Validação (Pydantic)
│   ├── integrations/ # Clientes externos
│   └── utils/        # Utilitários
```

### Princípios
- **DRY**: Don't Repeat Yourself
- **KISS**: Keep It Simple, Stupid
- **SOLID**: Princípios de OOP
- **Clean Code**: Código limpo e legível

## Testes

### Estrutura
```
tests/
├── unit/           # Testes unitários
├── integration/    # Testes de integração
└── conftest.py     # Fixtures compartilhadas
```

### Cobertura
- Mínimo 80% de cobertura
- Testes para todos os services
- Testes para endpoints críticos

### Exemplo
```python
import pytest
from app.services.user_service import UserService

@pytest.mark.asyncio
async def test_create_user(mock_supabase):
    service = UserService()
    
    user_data = {
        "whatsapp_number": "+5511999999999",
        "name": "João Silva"
    }
    
    user = await service.create_user(user_data)
    
    assert user["name"] == "João Silva"
    assert user["is_active"] is True
```

## Documentação

### API
- OpenAPI/Swagger gerado automaticamente
- Docstrings em todos os endpoints
- Exemplos de request/response

### Código
- Docstrings em funções/classes
- Comentários para lógica complexa
- README atualizado

### Commits
- Mensagens claras e descritivas
- Referências a issues quando aplicável

## Code Review

### Como Revisor
- Seja construtivo e respeitoso
- Questione mas não imponha
- Aprove quando estiver satisfeito
- Peça mudanças se necessário

### Como Autor
- Responda a comentários
- Faça ajustes solicitados
- Marque como resolvido quando corrigir
- Agradeça o feedback

## Comunidade

### Código de Conduta
- Seja respeitoso e inclusivo
- Não toleramos assédio ou discriminação
- Foque no problema, não na pessoa
- Ajude novos contribuidores

### Comunicação
- GitHub Issues: Bugs e features
- GitHub Discussions: Perguntas gerais
- Discord: Chat em tempo real
- Email: contato@brazyl.com

## Dúvidas?

- Leia a documentação
- Busque em issues abertas/fechadas
- Pergunte nas Discussions
- Entre no Discord

Obrigado por contribuir! 🎉

