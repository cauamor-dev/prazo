# Escolha do problema

Pesquisa realizada em 04/10/2026. As datas dos dados abaixo são as das publicações; não são estimativas para 2026.

| Área | Evidência consultada | Ideia possível | Decisão |
| --- | --- | --- | --- |
| Desperdício de alimentos | UNEP, Food Waste Index 2024: estimativa de 1,05 bilhão de toneladas em 2022, incluindo partes não comestíveis; 60% nos domicílios | Controle local de alimentos por validade | Escolhida: fluxo pequeno, dados simples e fácil demonstração |
| Digitalização de negócios | Cetic.br, TIC Empresas 2025, divulgação em junho de 2026: adoção de IA de 13% para 17% entre 2024 e 2025 | Organizador de processos com dados e automações | Boa evolução futura; o indicador não comprova demanda por um produto específico |
| Segurança digital | FBI, relatório de crimes de internet 2024: phishing/spoofing entre os três tipos com mais denúncias | Quiz educativo sobre golpes | Viável para estudo, mas distante do objetivo de praticar um fluxo completo de dados |

## Fontes

- https://www.unep.org/news-and-stories/press-release/world-squanders-over-1-billion-meals-day-un-report
- https://cetic.br/pt/noticia/uso-de-inteligencia-artificial-por-empresas-brasileiras-avanca-e-atinge-17-aponta-pesquisa-do-cetic-br/
- https://www.fbi.gov/news/press-releases/fbi-releases-annual-internet-crime-report
- https://flask.palletsprojects.com/en/stable/quickstart/

## Limites da pesquisa

O projeto é uma hipótese de solução inspirada por um problema documentado. Não houve entrevistas com usuários, validação de mercado nem medição de redução de desperdício. As regras de alerta são apenas comparações de datas: vencido antes de hoje, atenção de hoje até três dias, no prazo após isso. Não são recomendações sanitárias.

## Decisões

SQLite facilita executar sem instalar um servidor de banco. Flask conecta Python ao conhecimento prévio de HTML/CSS/JavaScript. A interface usa verde discreto, fundos claros e texto curto para transmitir organização. Não há dependências de fontes, imagens ou serviços externos na aplicação.

O histórico evita apagar registros ao consumir ou descartar. Formulários usam token de sessão; SQL usa parâmetros; Jinja escapa conteúdo; exportação neutraliza nomes que poderiam virar fórmulas em uma planilha.
