# Guia rápido de comandos Python — Windows / PowerShell

Este guia reúne comandos úteis para desenvolver projetos Python, especialmente com **FastAPI, Pandas e ambientes virtuais (`venv`)**, como o projeto de tratamento de planilhas do Plano Diretor.

## 1. Ambiente virtual (`venv`)

O ambiente virtual isola as bibliotecas instaladas para cada projeto. Em Java, a gestão das dependências costuma ser feita com Maven ou Gradle; o `venv` isola também o ambiente Python usado na execução.

| Ação | Comando no PowerShell |
|---|---|
| Verificar versão do Python | `python --version` |
| Criar ambiente virtual | `python -m venv .venv` |
| Ativar ambiente virtual | `.\.venv\Scripts\Activate.ps1` |
| Desativar ambiente virtual | `deactivate` |
| Verificar Python utilizado | `Get-Command python` |
| Excluir ambiente virtual | `Remove-Item -Recurse -Force .venv` |

Após a ativação, o terminal geralmente apresenta:

```powershell
(.venv) PS C:\Projetos\PlanoDiretor>
```

Se o PowerShell bloquear a ativação, execute na sessão atual:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Essa alteração de política vale somente para o processo atual do PowerShell.

## 2. Instalação de bibliotecas (`pip`)

| Ação | Comando |
|---|---|
| Atualizar pip | `python -m pip install --upgrade pip` |
| Instalar Pandas | `python -m pip install pandas` |
| Instalar FastAPI | `python -m pip install fastapi` |
| Instalar Uvicorn | `python -m pip install uvicorn` |
| Instalar suporte a upload | `python -m pip install python-multipart` |
| Instalar suporte a Excel | `python -m pip install openpyxl` |
| Instalar dependências do projeto | `python -m pip install -r requirements.txt` |
| Listar bibliotecas instaladas | `python -m pip list` |
| Ver detalhes de biblioteca | `python -m pip show pandas` |
| Desinstalar biblioteca | `python -m pip uninstall pandas` |

Para registrar as versões das dependências instaladas:

```powershell
python -m pip freeze > requirements.txt
```

> **Atenção:** `pip freeze` registra os pacotes instalados no ambiente atual. Prefira executá-lo com o `venv` ativado e confira o conteúdo gerado.

## 3. Executar projetos Python e FastAPI

| Ação | Comando |
|---|---|
| Executar script | `python arquivo.py` |
| Executar módulo | `python -m app.validators.validador` |
| Iniciar FastAPI | `python -m uvicorn app.main:app --reload` |
| Escolher porta 8001 | `python -m uvicorn app.main:app --reload --port 8001` |
| Executar testes com pytest | `python -m pytest` |
| Verificar sintaxe | `python -m py_compile app/main.py` |

No comando `app.main:app`:

- `app.main` é o módulo Python localizado em `app/main.py`.
- `:app` identifica a variável que contém a instância de `FastAPI`.
- `--reload` reinicia automaticamente o servidor após alterações no código; é indicado para desenvolvimento.

Com o servidor em execução na porta padrão:

- Aplicação: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs

Para interromper o servidor, pressione `Ctrl + C`.

> **Observação:** `python -m pytest` exige que o pacote `pytest` esteja instalado. `python -m app.validators.validador` executa o módulo, mas não necessariamente realiza uma validação: isso depende de haver código executável nele.

## 4. Navegação no PowerShell

| Ação | Comando |
|---|---|
| Listar arquivos | `dir` ou `ls` |
| Entrar em pasta | `cd app` |
| Voltar uma pasta | `cd ..` |
| Criar diretório | `mkdir services` |
| Criar arquivo | `New-Item teste.py -ItemType File` |
| Limpar terminal | `cls` |
| Ver diretório atual | `pwd` |
| Mostrar estrutura de pastas | `tree /F` |

## 5. Equivalências Python × Java

| Python | Java | Finalidade |
|---|---|---|
| `def` | Declaração de método | Definir função ou método |
| `class` | `class` | Definir classe |
| `import` | `import` | Importar dependências |
| `None` | `null` | Representar ausência de valor |
| `True` / `False` | `true` / `false` | Valores booleanos |
| `dict` | `Map` | Estrutura de chave e valor |
| `list` | `List` | Coleção ordenada |
| `set` | `Set` | Coleção sem elementos duplicados |
| `try / except` | `try / catch` | Tratar exceções |
| `raise` | `throw` | Lançar exceção |
| `pip` | Maven / Gradle (aproximação) | Gerenciar bibliotecas/dependências |
| `venv` | Sem equivalente direto | Isolar ambiente Python |

## 6. Sequência para iniciar o projeto Plano Diretor

Execute os comandos na **raiz do projeto**, onde está o diretório `app`.

### Primeira execução

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install fastapi uvicorn pandas openpyxl python-multipart
python -m pip freeze > requirements.txt
```

Se já existir `requirements.txt`, prefira instalar as dependências declaradas nele:

```powershell
python -m pip install -r requirements.txt
```

### Execução diária

```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

**Dica:** não é necessário recriar o `venv` a cada execução. Basta ativá-lo e iniciar o servidor.

## 7. Resumo de consulta rápida

| Quando precisar… | Utilize |
|---|---|
| Começar um projeto isolado | `python -m venv .venv` |
| Trabalhar no projeto existente | `.\.venv\Scripts\Activate.ps1` |
| Instalar dependências registradas | `python -m pip install -r requirements.txt` |
| Iniciar a API | `python -m uvicorn app.main:app --reload` |
| Consultar endpoints no Swagger | `http://127.0.0.1:8000/docs` |
| Salvar dependências atuais | `python -m pip freeze > requirements.txt` |
| Encerrar o ambiente virtual | `deactivate` |
