# Entendendo o Prazo

1. Comece por `expiry_status`: uma data vira uma quantidade de dias. `if` escolhe uma das três situações.
2. Leia `validate_item`: strings recebidas do formulário são convertidas, verificadas e retornadas como uma tupla. Valores inválidos geram `ValueError`.
3. Em `index`, cada linha do banco vira um dicionário. Uma repetição acrescenta o status, e uma compreensão de lista aplica os filtros.
4. `add_item` grava apenas valores já validados. Os `?` no SQL separam valores do comando, evitando montar consultas por concatenação.
5. `change_state` mantém o registro e permite voltar ao estoque. Estados inconsistentes são recusados.
6. `export` usa `csv`, uma biblioteca padrão, para gerar uma planilha sem depender de Excel instalado.
7. O HTML recebe os dicionários no servidor. JavaScript abre e fecha o formulário; as regras ficam no Python.

## Exercícios para evoluir

- Trocar o limite de alerta de três para cinco dias e atualizar o teste dos limites.
- Adicionar um filtro por unidade, combinável com os filtros existentes.
- Implementar edição de alimento com as mesmas validações do cadastro.
- Criar um resumo mensal de consumo e descarte por quantidade e unidade. Não some kg, litros e unidades como se fossem a mesma medida.

## Como apresentar

“O Prazo é um projeto de estudo com Python, Flask e SQLite para organizar alimentos pela validade. O foco foi transformar os fundamentos de Python em um fluxo web, com validação, persistência e testes. Usei apoio de IA durante o desenvolvimento.”

Antes de uma entrevista, execute o projeto, altere uma regra e rode os testes. Isso ajuda a explicar suas decisões com exemplos reais.
