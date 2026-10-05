# Prazo

Controle de alimentos por validade, feito com Python, Flask e SQLite. Um projeto de estudo para transformar os fundamentos de Python em uma aplicação web útil e simples de usar.

## O que resolve

É fácil esquecer o que está na despensa e perceber a validade só depois. O Prazo reúne os alimentos em um painel, destaca os que vencem em até três dias e mantém um histórico de consumo e descarte.

O [Food Waste Index 2024, do UNEP](https://www.unep.org/resources/publication/food-waste-index-report-2024) estima que os domicílios foram responsáveis por 60% do desperdício de alimentos medido em 2022. Esse contexto motivou a escolha do problema. O projeto não mede redução de desperdício nem avalia se um alimento está seguro para consumo.

## Funcionalidades

- Cadastro com categoria, quantidade, unidade e validade.
- Painel com alimentos ativos, próximos do vencimento e vencidos.
- Pesquisa e filtros combináveis, com ordenação pela validade.
- Registro de consumo ou descarte, com opção de desfazer.
- Exportação CSV compatível com planilhas.
- Dados fictícios de demonstração, carregados somente em uma base vazia.
- Interface responsiva, navegação por teclado e formulário em modal.

## Executar

Requisitos: Python 3.11 ou superior.

```bash
git clone https://github.com/cauamor-dev/prazo.git
cd prazo
python -m venv .venv
```

Ative o ambiente:

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

```bash
# Linux / macOS
source .venv/bin/activate
```

Depois:

```bash
python -m pip install -r requirements.txt
python app.py
```

Abra **http://127.0.0.1:5000**. Clique em **Explorar demonstração** para começar com exemplos. Para usar seus próprios dados, comece em uma instalação vazia: os dados ficam em `instance/prazo.sqlite`, fora do Git.

## Testes

```bash
python -m unittest discover -s tests -v
```

Os testes verificam limites das datas, validação, persistência, filtros, consumo, restauração, proteção de formulários, escape de HTML, exportação e carga de demonstração.

## Estrutura

- `app.py`: rotas, validação, regras de validade e persistência.
- `templates/`: páginas renderizadas no servidor com Jinja.
- `static/`: CSS responsivo e JavaScript do modal.
- `tests/`: testes com banco temporário.
- `docs/`: pesquisa, decisões e guia para entender o código.

## O que pratiquei

Funções, condições, listas, dicionários, repetição, strings e importações. Flask, SQLite, sessões e testes foram extensões práticas além do conteúdo introdutório do curso. A estrutura é intencionalmente pequena para facilitar o estudo e a manutenção.

## Escopo

Aplicação local para estudo e uso individual. Não possui autenticação, notificações automáticas, controle de lotes, edição de registros ou sincronização entre dispositivos. O servidor de desenvolvimento não é uma implantação de produção. Para corrigir um registro, marque-o no histórico e cadastre os dados corretos. Em uma evolução futura, a edição pode ser adicionada com testes próprios.

O projeto foi desenvolvido com apoio de IA e validado com testes. Não contém dados pessoais reais nos exemplos.
