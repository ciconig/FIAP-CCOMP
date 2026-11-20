# Nexcondo: help desk de condomínio

Global Solution 2026.2 · Ciência da Computação ON · desafio CitizenTech, case *Neighborhood Action Dashboard*.

## 1. Equipe: NexoTech

| Integrante | RM |
|---|---|
| Guilherme Augusto Ciconi Torquato | RM574912 |
| Jessica Marques Nazareth da Silva | RM575170 |
| Julio Cesar Victorio Fernandes | RM574452 |
| Nicolas Jordão Souza | RM575020 |
| Matheus Luiz Neiva Rossilho Moysés | RM574836 |

## 2. Comunidade, problema e público beneficiado

**A comunidade simulada** é um condomínio com três blocos (A, B e C) e áreas comuns como garagem, hall, corredores, rampa de acesso, elevador, jardim, piscina e salão de festas. Na apresentação, o condomínio aparece como o Habitat Marte-1 da Colônia Aurora, a narrativa do curso. O tema é só visual: os dados, as regras e os indicadores são os de um condomínio comum.

**O problema.** As reclamações sobre as áreas comuns (lâmpada queimada, corrimão solto, lixeira transbordando, portão quebrado) costumam chegar por mensagem no grupo, recado na portaria ou conversa no elevador. Nada fica registrado num lugar só. Ninguém sabe o que já foi visto, o que está parado e o que é urgente, e o morador não consegue acompanhar o pedido que fez.

**A solução.** O Nexcondo funciona como um help desk:

- o morador abre um chamado e recebe um protocolo (`CH-015`, por exemplo);
- a administração atende os chamados pela fila de triagem e muda o status até a resolução;
- cada mudança fica no histórico;
- o painel mostra o que está pendente, o que passou do prazo e onde os problemas se concentram.

**Quem se beneficia:**

- **moradores:** registram o problema e acompanham pelo protocolo;
- **síndico, zelador e administração:** veem a fila, as prioridades e os atrasos;
- **pessoas com deficiência, idosos e quem tem mobilidade reduzida:** a acessibilidade é uma categoria própria, e uma rampa ou um elevador com defeito pode ser marcado como urgente, com prazo de 1 dia.

O projeto se relaciona com o **ODS 11**, meta 11.7 (espaços coletivos seguros, inclusivos e acessíveis), e com o **ODS 10**, meta 10.2 (inclusão de pessoas com deficiência e idosos).

## 3. Estruturas de dados e justificativa

| Estrutura | Onde está | Para que serve | Por que essa estrutura |
|---|---|---|---|
| **Lista** | `chamados` (`sistema.py`) | guarda todos os chamados válidos; é percorrida para listar, filtrar e calcular indicadores | mantém a ordem de registro e permite percorrer tudo com `for` |
| **Dicionário** | `por_protocolo` (`sistema.py`) | consulta e atualiza um chamado pelo protocolo | acesso direto pela chave, sem percorrer a lista |
| **Fila** | `fila_triagem` (`chamados.py`) | chamados `aberto` ainda não examinados | o primeiro a chegar é o primeiro atendido: `append` no fim e `pop(0)` no início. A prioridade não fura a fila; ela define o prazo |
| **Pilha** | `historico` (`chamados.py`, `dashboard.py`) | cada mudança de status é empilhada; "Últimas atualizações" lê do topo | o evento mais recente é sempre o último empilhado. A leitura usa `pop()` numa cópia, para não apagar o histórico |
| **Hierarquia** | `montar_hierarquia` (`dashboard.py`) | bloco → categoria → chamados (dicionário de dicionários de listas) | segue o jeito como a administração percorre o condomínio: primeiro o bloco, depois o tipo de problema |
| **Matriz** | `matriz_categoria_status` e `matriz_bloco_status` (`dashboard.py`) | lista de listas: linha = categoria (ou bloco), coluna = status | cruza duas informações numa tabela; somar uma linha ou uma coluna dá os totais |
| **Conjunto** | `numeros` (`dados.py`) | números de protocolo já usados, inclusive o do registro rejeitado | impede repetir protocolo; a busca num conjunto é direta |

## 4. Regras lógicas

### Cadastro e validação (`dados.py`)

- **Campos obrigatórios:** protocolo, categoria, prioridade, descrição, bloco, área, dia de abertura e status. O `dia_fechamento` só é obrigatório quando o chamado está resolvido.
- **Valores padronizados:**

| Campo | Valores aceitos |
|---|---|
| Categoria | `iluminacao`, `acessibilidade`, `limpeza`, `conservacao` |
| Prioridade | `urgente` (prazo de 1 dia), `alta` (3 dias), `normal` (7 dias) |
| Status | `aberto`, `em_atendimento`, `aguardando_terceiro`, `resolvido` |

- **Significado de cada status:**

| Status | Significado |
|---|---|
| `aberto` | registrado e ainda não examinado (está na fila de triagem) |
| `em_atendimento` | a administração assumiu o chamado |
| `aguardando_terceiro` | depende de uma empresa externa ou de uma peça |
| `resolvido` | atendimento concluído, com dia de fechamento |

- **Dias:** são números inteiros positivos (dia 1, dia 2…). Um texto como `0`, `-1`, `1.5` ou `abc` é recusado.
- **Na carga do CSV:** um registro inválido gera um aviso e fica fora da lista, mas o número do protocolo dele continua reservado. É o caso do `CH-013`, que está sem categoria.

### Mudança de status (`chamados.py`)

| Status atual | Pode ir para |
|---|---|
| `aberto` | `em_atendimento` |
| `em_atendimento` | `aguardando_terceiro` ou `resolvido` |
| `aguardando_terceiro` | `em_atendimento` |
| `resolvido` | nada (o fluxo termina) |

O dia de uma atualização não pode ser anterior à abertura nem ao último evento daquele chamado.

### Condições com AND, OR e NOT, e a mensagem que cada uma produz

| Condição (como está no código) | Arquivo | Quando é verdadeira, o sistema… |
|---|---|---|
| `(categoria and categoria not in CATEGORIAS) or (status and status not in STATUS)` | `chamados.py` | mostra **"Filtro inválido"**: o usuário digitou uma categoria ou um status que não existe. Um campo vazio não conta como erro, porque significa "todos" |
| `(not categoria or chamado["categoria"] == categoria) and (not status or chamado["status"] == status)` | `chamados.py` | **inclui o chamado no resultado do filtro**: ele precisa passar nos dois critérios, e um critério vazio deixa todos passarem |
| `fechamento is None or (abertura is not None and fechamento < abertura)` | `dados.py` | recusa um chamado `resolvido` **sem dia de fechamento ou com fechamento antes da abertura** |
| `anterior != ultimos_status[protocolo] or novo not in TRANSICOES[anterior]` | `dados.py` | **bloqueia a carga do histórico** se um evento pula uma etapa ou faz uma transição proibida |
| `atrasado and (prioridade == "urgente" or prioridade == "alta")` | `dashboard.py` | conta um **atraso crítico**: o chamado passou do prazo e é urgente ou alto |
| `not chamado["status"] == "resolvido"` | `dashboard.py` | considera o chamado **pendente** |
| `numero is not None and 1 <= numero <= len(opcoes)` | `sistema.py` | aceita a escolha do menu; se for falsa, mostra **"Opção inválida"** e pergunta de novo |

**Expressão booleana documentada.** O filtro é a expressão central de consulta:

```python
filtro_invalido = (categoria and categoria not in CATEGORIAS) or (status and status not in STATUS)
```

Se o usuário digitar `jardim` como categoria, `categoria` é verdadeiro (não está vazio) **e** `categoria not in CATEGORIAS` também é. O primeiro lado do `or` fica verdadeiro, a expressão inteira fica verdadeira e o sistema mostra "Filtro inválido". Se ele deixar a categoria vazia e digitar `aberto`, os dois lados são falsos e o filtro roda normalmente.

**Outras mensagens:**

| Situação | Mensagem |
|---|---|
| protocolo que não existe | **"Chamado CH-099 não encontrado."** |
| status fora da lista | **"Status desconhecido"** |
| transição proibida (por exemplo, `aberto` → `resolvido`) | **"Transição bloqueada"** |
| chamado já resolvido | **"o fluxo foi encerrado"** |

O menu principal usa uma sequência de `if`/`elif`/`else` (`sistema.py`).

## 5. Indicadores, fórmulas e interpretação

O painel (opção 8 do menu) mostra os dados de origem, a fórmula e o resultado de cada indicador. O "hoje" simulado é o **dia de referência**: o maior dia que aparece na base, que é o dia 18 nos dados entregues.

| Indicador | Fórmula | Resultado na base entregue |
|---|---|---|
| Chamados por status | quantidade e quantidade ÷ total × 100 | aberto 5 (38,5%) · em atendimento 3 (23,1%) · aguardando terceiro 2 (15,4%) · resolvido 3 (23,1%) |
| Chamados por categoria | quantidade e quantidade ÷ total × 100 | iluminação 4 (30,8%) · acessibilidade 3 · limpeza 3 · conservação 3 (23,1% cada) |
| Taxa de resolução | resolvidos ÷ total × 100 | 3 ÷ 13 = **23,1%** |
| Tempo médio de resolução | soma(fechamento − abertura) ÷ resolvidos | (2 + 3 + 3) ÷ 3 = **2,7 dias** |
| Resolvidos no prazo | resolução ≤ prazo da prioridade | **3 de 3** |
| Espera média das pendências | soma(referência − abertura) ÷ pendentes | 104 ÷ 10 = **10,4 dias** |
| Pendências fora do prazo | pendente e espera > prazo | **9 de 10**: 2 urgentes, 4 altas e 3 normais |

**Matriz categoria × status:**

| Categoria | Aberto | Em atendimento | Aguardando terceiro | Resolvido | Total |
|---|---|---|---|---|---|
| Iluminação | 2 | 1 | 0 | 1 | 4 |
| Acessibilidade | 1 | 1 | 1 | 0 | 3 |
| Limpeza | 1 | 1 | 0 | 1 | 3 |
| Conservação | 1 | 0 | 1 | 1 | 3 |
| **Total** | 5 | 3 | 2 | 3 | 13 |

**Matriz bloco × status:**

| Bloco | Aberto | Em atendimento | Aguardando terceiro | Resolvido | Total |
|---|---|---|---|---|---|
| Bloco A | 2 | 0 | 1 | 2 | 5 |
| Bloco B | 2 | 1 | 0 | 1 | 4 |
| Bloco C | 1 | 2 | 1 | 0 | 4 |

**Interpretação.** Iluminação é o problema mais frequente, e o Bloco C é o mais crítico: nenhum dos 4 chamados dele foi resolvido. Só 23,1% dos chamados foram resolvidos, e 9 das 10 pendências passaram do prazo, 2 delas urgentes (CH-002 e CH-009). Há ainda um terceiro urgente sem solução, o CH-014, que acabou de ser aberto e está dentro do prazo. Por outro lado, os chamados resolvidos fecharam rápido (2,7 dias em média, todos no prazo). Isso indica que o gargalo está em **começar** o atendimento, não em concluí-lo. Na prática, a triagem precisa andar mais rápido. Como os dados são fictícios, a conclusão serve para mostrar o raciocínio, não para avaliar um condomínio real.

## 6. Como executar

É preciso ter **Python 3.8 ou mais recente**. O sistema usa só a biblioteca padrão. Na pasta `1CCOMP/GLOBAL-SOLUTION-1`:

```bash
python src/sistema.py
```

| Opção | O que faz |
|---|---|
| 1 | lista os chamados (protocolo, categoria, prioridade, bloco/área, abertura, status) |
| 2 | abre um chamado: valida os campos, gera o protocolo, grava no CSV e coloca o chamado no fim da fila |
| 3 | consulta um chamado pelo protocolo |
| 4 | filtra por categoria, por status ou pelos dois |
| 5 | atende o próximo da fila (vai para `em_atendimento`) |
| 6 | atualiza o status, só para os próximos status permitidos, e registra no histórico |
| 7 | mostra as 5 últimas atualizações (topo da pilha) |
| 8 | mostra o painel de indicadores completo |
| 9 | mostra o painel de um bloco |
| 10 | abre o dashboard web com os dados desta sessão (opcional, ver a seção "Extras") |
| 0 | sai |

No terminal, cada operação mostra o resultado e espera um **Enter**; depois a tela é limpa e o menu volta ao topo, com um resumo de uma linha (chamados, pendentes, fila e eventos). Quando a saída não é um terminal (testes ou redirecionamento), a tela não é limpa e não há pausa.

**Os dados ficam em `data/`:**

- `chamados.csv`: os chamados, em UTF-8 e separados por vírgula;
- `historico.csv`: as mudanças de status.

Os cadastros novos (opção 2) são gravados no CSV. As mudanças de status (opções 5 e 6) valem durante a execução. A opção 10 regrava o `web/dados.js`. Para voltar à base original depois de uma demonstração, rode `git checkout -- data web/dados.js`.

Os testes automatizados (23) ficam em `tests/`:

```bash
python -m unittest discover -s tests
```

## 7. Exemplo de uso

Trechos da saída real do sistema. As entradas digitadas aparecem depois de `→`, e algumas perguntas foram resumidas numa linha só.

**Cadastro** (opção 2):

```text
Escolha: 2  → categoria 1 (iluminacao), prioridade 1 (urgente)
Descrição: → Poste apagado na entrada da garagem
Bloco: → Bloco B        Área comum: → Garagem        Dia simulado de abertura: → 19
[OK] Chamado cadastrado! Protocolo: CH-015
```

**Consulta por protocolo** (opção 3):

```text
Informe o protocolo (ex.: CH-001): → CH-015
===== DADOS DO CHAMADO =====
protocolo: CH-015
categoria: iluminacao
prioridade: urgente
descricao: Poste apagado na entrada da garagem
bloco: Bloco B
area: Garagem
dia_abertura: 19
status: aberto
dia_fechamento: -
```

**Filtro** (opção 4), com categoria `iluminacao` e status `aberto`:

```text
PROTOCOLO | CATEGORIA | PRIORIDADE | BLOCO / ÁREA | ABERTURA | STATUS
CH-005 | iluminacao | normal | Bloco B / Corredor comum | dia 4 | aberto
CH-014 | iluminacao | URGENTE | Bloco A / Hall | dia 18 | aberto
CH-015 | iluminacao | URGENTE | Bloco B / Garagem | dia 19 | aberto
```

**Alteração de status** (opção 6). Primeiro, uma transição proibida; depois, a permitida:

```text
Informe o protocolo: → CH-015
Status atual: aberto. Próximos permitidos: em_atendimento.
Novo status: → resolvido
[!] Transição bloqueada: aberto não pode ir direto para resolvido.

Informe o protocolo: → CH-015
Status atual: aberto. Próximos permitidos: em_atendimento.
Novo status: → em_atendimento     Dia da atualização: → 19     Observação: → Zelador trocou o reator
[OK] Chamado CH-015: aberto -> em_atendimento registrado no histórico.
```

**Últimas atualizações** (opção 7, a pilha):

```text
===== ÚLTIMAS 5 ATUALIZAÇÕES (mais recente primeiro) =====
Dia 19 | CH-015 | aberto -> em_atendimento | Zelador trocou o reator
Dia 11 | CH-010 | em_atendimento -> aguardando_terceiro | Assistência especializada solicitada
Dia 10 | CH-010 | aberto -> em_atendimento | Elevador inspecionado
Dia 10 | CH-008 | em_atendimento -> resolvido | Banco reparado
Dia 9 | CH-009 | aberto -> em_atendimento | Administração iniciou a verificação
```

**Saída do painel** (opção 8, trecho dos indicadores, com a base original):

```text
Taxa de resolução: 3 resolvidos / 13 chamados x 100 = 23.1%
Tempo médio de resolução: soma(fechamento - abertura) / resolvidos = 8 / 3 = 2.7 dia(s)
Resolvidos dentro do prazo da prioridade: 3 de 3
Espera média das pendências: soma(referência - abertura) / pendentes = 104 / 10 = 10.4 dia(s)
Pendências fora do prazo (urgente 1 dia(s), alta 3 dia(s), normal 7 dia(s)): 9 de 10
  das quais com prioridade urgente ou alta: 6
```

## 8. Acessibilidade, inclusão e privacidade

- **Privacidade:** o chamado registra só o bloco e a área comum, nunca nome, apartamento ou telefone do morador. O cadastro lembra isso na tela. Todos os dados do projeto são fictícios.
- **Inclusão:** a acessibilidade é uma categoria própria, e uma rampa quebrada ou um elevador parado pode ser registrado como urgente, com prazo de 1 dia. A fila de triagem segue a ordem de chegada, mas a administração pode assumir um chamado urgente direto pela opção 6, sem esperar a vez. O painel conta os urgentes sem solução e os atrasos críticos (urgentes ou altos fora do prazo).
- **Acessibilidade da interface:**
  - o menu é numerado e as escolhas de categoria e prioridade são feitas por número, sem precisar digitar termos técnicos;
  - entradas inválidas são perguntadas de novo, com uma mensagem que diz o que está errado;
  - as cores do terminal só reforçam o texto: status, prioridade e mensagens (`[OK]`, `[!]`) estão sempre escritos por extenso;
  - as cores são desligadas quando a saída não é um terminal ou quando a variável `NO_COLOR` está definida;
  - no painel, toda barra vem acompanhada do número e da porcentagem.

## 9. Vídeo de apresentação

**[Assistir no YouTube](https://www.youtube.com/watch?v=7vBMwB1HzT4)**

## 10. Conclusões, limitações e aprendizados

**Conclusões.** Com estruturas simples (lista, dicionário, fila, pilha, matriz e uma hierarquia de dicionários) e regras com `if`/`elif`/`else` e AND/OR/NOT, foi possível transformar reclamações soltas em informação útil: quem registrou, onde, em que situação está e há quanto tempo espera. Os indicadores mostram onde agir primeiro. Na base simulada, isso significa acelerar a triagem e olhar para o Bloco C.

**Limitações:**

- os dados são simulados, e o "hoje" é um dia de referência, não a data real;
- as mudanças de status valem durante a execução e não são gravadas no CSV; só os cadastros novos são gravados;
- não há login nem perfis: qualquer pessoa usando o terminal pode mudar um status, e o sistema considera uma pessoa usando por vez;
- não há integração com a administração real, notificação ao morador nem anexos (como fotos do problema);
- os prazos por prioridade são fixos e não consideram dias úteis.

**Aprendizados:**

- **A estrutura depende da operação.** A fila resolveu "quem é o próximo"; a pilha, "o que aconteceu por último"; o dicionário, "me mostra o CH-010". Usar uma lista para tudo funcionaria, mas deixaria cada operação mais confusa.
- **Validar na entrada protege os indicadores.** Um chamado sem categoria ou com fechamento antes da abertura distorceria as médias. Por isso o `CH-013` é recusado logo na carga.
- **Separar o cálculo da exibição** (`calcular_indicadores` × `exibir_dashboard`) permitiu conferir os números com testes automatizados, sem depender do que aparece na tela.
- **Combinar as regras antes de dividir o trabalho.** As três partes do grupo só se encaixaram depois que todos passaram a usar as mesmas constantes de `dados.py` (categorias, prazos e transições).

## Extras

### Tema visual no terminal

O banner, o menu e as cores seguem a narrativa da Colônia Aurora (`src/visual.py`). É só apresentação: nenhuma regra muda.

### Dashboard web (opcional)

O `web/index.html` é um painel visual com as mesmas regras, traduzidas em `web/regras.js` (mesmas categorias, prazos, transições, validação e fórmulas):

- filtro por bloco;
- gráfico por status e barras por categoria;
- mapa bloco × status;
- fila, pilha, indicadores e conclusão;
- cadastro e mudança de status.

A **opção 10 do menu** exporta os dados da sessão para `web/dados.js` e abre a página no navegador. A ligação vai só do terminal para a web: o que é feito na página vale só naquela aba. Para gerar os dados sem abrir o menu, use `python web/gerar_dados.py`.

O dashboard usa HTML, CSS, JavaScript e [anime.js](https://animejs.com/) 3.2.2, que estão fora do conteúdo das fases 1 a 3. Por isso ele é só um complemento: **o sistema avaliado é o Python** (`python src/sistema.py`).

## Organização da entrega

```text
GLOBAL-SOLUTION-1/
├── README.md
├── data/
│   ├── chamados.csv        # 14 registros: 13 válidos + CH-013 (inválido, para a validação)
│   └── historico.csv       # 13 mudanças de status
├── src/
│   ├── sistema.py          # menu principal (ponto de entrada)
│   ├── dados.py            # constantes, leitura, validação e gravação dos CSV
│   ├── chamados.py         # consulta, filtro, fila, mudança de status e histórico
│   ├── indicadores.py      # opções 8 e 9 do menu
│   ├── dashboard.py        # painel: contagens, matrizes, hierarquia, indicadores e conclusão
│   ├── visual.py           # banner, menu e cores do tema
│   └── painel_web.py       # opção 10: exporta a sessão e abre o dashboard web
├── tests/                  # test_dados.py, test_chamados.py, test_dashboard.py
├── web/                    # dashboard web opcional
└── docs/uso_ia.md          # registro do uso de inteligência artificial
```

### Formato dos arquivos

`data/chamados.csv`:

```csv
protocolo,categoria,prioridade,descricao,bloco,area,dia_abertura,status,dia_fechamento
CH-001,iluminacao,alta,Lâmpada apagada na garagem,Bloco A,Garagem,1,resolvido,3
```

`data/historico.csv`:

```csv
protocolo,dia_evento,status_anterior,status_novo,observacao
CH-001,2,aberto,em_atendimento,Administração iniciou a verificação
```

Os dois arquivos usam UTF-8 e vírgula como separador.

**Regras do histórico:**

- cada evento precisa apontar para um chamado válido;
- os dias não podem voltar no tempo;
- a sequência de status precisa seguir a tabela de transições;
- o último status precisa bater com o do `chamados.csv`.

Se algo não fechar, a carga é interrompida com uma mensagem explicando o motivo.

**Dados entregues × mínimo do enunciado:**

| Exigência do enunciado | Dados entregues |
|---|---|
| ≥ 12 ocorrências nas 4 categorias | 13 válidas (iluminação 4, as outras 3 cada) |
| ≥ 3 situações distintas | 4 status |
| ≥ 8 eventos de acompanhamento | 13 eventos |
| ≥ 1 registro inconsistente tratado | `CH-013`, sem categoria, rejeitado com aviso |

## Uso de inteligência artificial

O registro está em [docs/uso_ia.md](docs/uso_ia.md).
