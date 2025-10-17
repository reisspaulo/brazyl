# Scripts Utilitários - Brazyl

## Scripts Disponíveis

### `populate_politicians.py`
Popular banco de dados com políticos das APIs públicas (Câmara e Senado).

**Uso:**
```bash
# Executar normalmente
python scripts/populate_politicians.py

# Modo dry-run (simular sem salvar)
python scripts/populate_politicians.py --dry-run

# Atualizar políticos existentes
python scripts/populate_politicians.py --update

# Logs mais detalhados
python scripts/populate_politicians.py --verbose

# Apenas deputados
python scripts/populate_politicians.py --only-deputados

# Apenas senadores
python scripts/populate_politicians.py --only-senadores
```

### `test_avisa_api.py`
Testa integração com a API Avisa (WhatsApp).

**Uso:**
```bash
python scripts/test_avisa_api.py +5511999999999 "Mensagem de teste"
```

### `test_supabase.py`
Testa conexão e operações básicas com Supabase.

**Uso:**
```bash
python scripts/test_supabase.py
```

## Pré-requisitos

1. Instalar dependências:
```bash
cd api
pip install -r requirements.txt
pip install tqdm  # Para barra de progresso
```

2. Configurar variáveis de ambiente:
```bash
cp api/.env.example api/.env
# Editar api/.env com suas credenciais
```

## Notas

- Scripts devem ser executados da raiz do projeto
- Conexão com internet é necessária para APIs públicas
- Processo de população pode levar alguns minutos
- Recomenda-se usar `--dry-run` primeiro para testar

