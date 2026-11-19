# Help desk de condomínio — Global Solution

## Equipe: Maximi Tech

| Integrante | RM |
|---|---|
| Guilherme Augusto Ciconi Torquato | RM574912 |
| Jessica Marques Nazareth da Silva | RM575170 |
| Julio Cesar Victorio Fernandes | RM574452 |
| Nicolas Jordão Souza | RM575020 |
| Matheus Luiz Neiva Rossilho Moysés | RM574836 |

Help desk de condomínio para registrar, acompanhar e analisar problemas nas áreas comuns. Usa apenas a biblioteca padrão do Python 3.

Os registros são fictícios. Informe apenas bloco e área comum: não registre nome, apartamento ou outro dado pessoal do morador.

## Como executar

Na pasta `1CCOMP/GLOBAL-SOLUTION-1`, execute:

```bash
python src/sistema.py
```

Os caminhos dos CSV são calculados a partir de `dados.py`, permitindo executar o programa de outra pasta também. Mantenha os dois arquivos em `data`, junto de `src`.

Na inicialização, o programa avisa que `CH-013` está sem categoria e mostra a quantidade de chamados válidos e eventos de histórico carregados. O menu oferece:

- **1 — Listar chamados:** exibe protocolo, categoria, prioridade, bloco, área comum, dia de abertura e status. A prioridade `URGENTE` aparece em maiúsculas.
- **2 — Abrir chamado:** permite escolher categoria e prioridade por número e pede descrição, bloco, área comum e dia simulado. Entradas inválidas são solicitadas novamente. O chamado começa como `aberto`, é gravado no CSV e recebe um protocolo sequencial.
- **3 — Consultar protocolo:** mostra todos os campos de um chamado ou avisa que ele não foi encontrado.
- **4 — Filtrar:** por categoria, por status ou pelos dois; valores fora da lista são recusados.
- **5 — Atender próximo da fila:** retira o primeiro chamado `aberto` da fila de triagem (ordem de registro) e o coloca `em_atendimento`.
- **6 — Atualizar status:** mostra os próximos status permitidos, bloqueia transições proibidas e registra a mudança no histórico.
- **7 — Últimas atualizações:** os 5 eventos mais recentes, do topo da pilha para baixo.
- **8 — Painel de indicadores** e **9 — Visão por bloco:** ver a seção do dashboard.
- **0 — Sair.**

Mudanças de status (opções 5 e 6) ficam na memória durante a execução e aparecem no painel e nas últimas atualizações; só os cadastros novos são gravados no CSV.

### Interface: Colônia Aurora

O terminal usa a narrativa do curso: o condomínio é o Habitat Marte-1, uma cúpula pressurizada da Colônia Aurora, e o menu é o painel de controle da colônia. O tema é só visual; dados, regras e indicadores são os mesmos. `src/visual.py` concentra o banner, o menu e as cores:

| Elemento | Cor |
|---|---|
| Títulos, banner e bordas | laranja marciano |
| `aberto` / `URGENTE` | vermelho |
| `em_atendimento` | amarelo |
| `aguardando_terceiro` | magenta |
| `resolvido` e mensagens `[OK]` | verde |
| Mensagens de erro `[!]` | vermelho |

As cores só reforçam o texto: status, prioridade e mensagens continuam escritos por extenso, e os prefixos `[OK]` e `[!]` indicam sucesso ou erro sem depender de cor. Elas são desligadas automaticamente quando a saída não é um terminal e podem ser desativadas com a variável de ambiente `NO_COLOR`.

Para testar o cadastro, uma descrição possível é “Luz apagada no hall”, local “Bloco A / Hall”, dia `18`. Na base entregue, o próximo protocolo é `CH-015`, pois `CH-014` já existe. Os cadastros persistem entre execuções; faça uma cópia dos CSV se quiser repetir a demonstração com a mesma base.

### Interface web (extra)

`web/index.html` é um painel de controle do mesmo help desk, com o tema da Colônia Aurora: alertas (fora do prazo, urgentes, fila), filtro por bloco, gráfico de status, barras por categoria, mapa bloco × status, fila de triagem com "atender próximo", últimas atualizações (pilha), indicadores e conclusão. Clicar no gráfico, nas barras ou no mapa filtra a lista de chamados; clicar num chamado abre o detalhe com histórico e os próximos status permitidos; "+ Novo chamado" abre o cadastro com a mesma validação do Python. Animações com [anime.js](https://animejs.com/) 3.2.2; sem ele (offline) ou com "reduzir movimento" ativado no sistema, a página funciona igual, sem animação.

As regras ficam em `web/regras.js`, uma tradução direta de `dados.py`, `chamados.py` e `dashboard.py` (mesmas categorias, prazos, transições, validação e fórmulas). Os dados vêm de `web/dados.js`, gerado a partir dos CSV:

```bash
python web/gerar_dados.py        # atualiza web/dados.js depois de mudar os CSV
python -m http.server -d web     # depois abra http://localhost:8000
```

Abrir o `index.html` direto no navegador também funciona. As alterações feitas na página valem só naquela aba. **O sistema avaliado continua sendo o Python** (`python src/sistema.py`); a interface web é uma demonstração visual das mesmas regras.

## Organização da entrega

```text
GLOBAL-SOLUTION-1/
├── data/
│   ├── chamados.csv
│   └── historico.csv
├── src/
│   ├── dados.py           # constantes, validação, leitura e gravação
│   ├── chamados.py        # consulta, filtro, fila de triagem, status e histórico
│   ├── indicadores.py     # opções 8 e 9 do menu
│   ├── dashboard.py       # painel, matrizes, hierarquia e indicadores
│   ├── visual.py          # banner, menu e cores do tema Colônia Aurora
│   └── sistema.py         # menu principal (ponto de entrada)
├── web/                   # interface web (index.html, app.js, regras.js, dados.js)
├── tests/                 # test_dados.py, test_chamados.py, test_dashboard.py
└── docs/uso_ia.md
```

## Formato dos chamados

`data/chamados.csv` usa UTF-8, vírgula como separador e o cabeçalho abaixo, nessa ordem. A leitura aceita BOM e remove espaços nas extremidades dos campos. Campos com vírgulas, aspas ou quebras de linha são tratados pelo módulo `csv`.

```csv
protocolo,categoria,prioridade,descricao,bloco,area,dia_abertura,status,dia_fechamento
```

| Campo | Obrigatório | Regra |
|---|---|---|
| `protocolo` | Sim | `CH-` seguido de ao menos três dígitos de 0 a 9, com número positivo e único; gerado pelo cadastro |
| `categoria` | Sim | `iluminacao`, `acessibilidade`, `limpeza` ou `conservacao` |
| `prioridade` | Sim | `urgente`, `alta` ou `normal` |
| `descricao` | Sim | Texto breve sobre o problema, sem dados pessoais |
| `bloco` | Sim | Localidade genérica, como `Bloco A` |
| `area` | Sim | Área comum, como `Garagem` ou `Jardim` |
| `dia_abertura` | Sim | Inteiro positivo representado como texto |
| `status` | Sim | Um dos quatro valores padronizados abaixo |
| `dia_fechamento` | Quando resolvido | Inteiro positivo igual ou posterior à abertura; deve ficar vazio nos demais status |

Os dias são simulados: `1`, `2`, `3` etc., sem correspondência obrigatória com datas de calendário. O fechamento no mesmo dia da abertura é permitido. Os dicionários mantêm os valores como **strings**, inclusive os dias; para calcular intervalos, use `int(chamado["dia_abertura"])` e `int(chamado["dia_fechamento"])` após a validação.

| Status | Significado |
|---|---|
| `aberto` | Registrado e ainda não examinado |
| `em_atendimento` | Assumido pela administração |
| `aguardando_terceiro` | Depende de empresa ou peça |
| `resolvido` | Atendimento concluído e fechamento informado |

As constantes `PRAZOS` e `TRANSICOES` ficam disponíveis em `dados.py` para a integração do grupo. Os prazos previstos são `urgente: 1`, `alta: 3` e `normal: 7` dias. A prioridade não altera a ordem de chegada da fila de triagem.

## Cobertura dos dados iniciais

| Critério | Base entregue |
|---|---|
| Pelo menos 12 ocorrências válidas | 13 válidas, incluindo o cadastro existente `CH-014` |
| Quatro categorias | Todas representadas; três ou mais chamados válidos por categoria |
| Pelo menos três situações distintas | Quatro status representados |
| Pelo menos oito eventos de acompanhamento | 13 mudanças de status em `historico.csv` |
| Registro ausente ou inconsistente tratado | `CH-013`, sem categoria, rejeitado com aviso |

O CSV tem 14 registros ao todo. `CH-013` permanece no arquivo para demonstrar a validação, mas não entra na lista de chamados válidos. Seu número continua reservado. Corrigir sua categoria para `iluminacao` permite carregá-lo em uma nova execução. Mesmo que a linha de maior protocolo seja rejeitada, seu número não será reutilizado.

## Histórico inicial

`data/historico.csv` usa o mesmo formato de codificação e separador, com cabeçalho:

```csv
protocolo,dia_evento,status_anterior,status_novo,observacao
```

Todos os campos do histórico são obrigatórios. Cada evento deve apontar para um chamado válido, ter dia positivo igual ou posterior à abertura e ao evento anterior daquele chamado, além de respeitar a sequência de status. O histórico começa implicitamente em `aberto`; registrar a abertura não exige um evento separado.

As transições permitidas são:

- `aberto` → `em_atendimento`;
- `em_atendimento` → `aguardando_terceiro` ou `resolvido`;
- `aguardando_terceiro` → `em_atendimento`;
- `resolvido` encerra o fluxo.

O último status de cada histórico deve coincidir com `chamados.csv`. Para resolvidos, o dia do último evento deve ser o dia de fechamento. Chamados ainda abertos podem não ter eventos. Uma inconsistência no histórico bloqueia a carga inicial com mensagem explicativa, pois descartar um evento isolado poderia quebrar a sequência.

O arquivo agrupa eventos por protocolo, em ordem cronológica dentro de cada chamado. `carregar_historico` retorna a lista ordenada por dia para que o último item represente o evento mais recente na pilha; empates mantêm a ordem do arquivo.

## Validações e regras lógicas

`validar` devolve uma lista de motivos, incluindo os nomes dos campos obrigatórios ausentes. Categoria, prioridade e status desconhecidos são rejeitados. Dias como `0`, `-1`, `1.5`, letras ou o caractere `²` são rejeitados sem encerrar o cadastro. Um chamado não resolvido não pode ter fechamento, e um resolvido precisa de fechamento coerente mesmo quando a abertura também está inválida.

Exemplos das expressões usadas:

- `if not dados[campo]` identifica texto obrigatório vazio e permite informar qual campo falta.
- `fechamento is None or (abertura is not None and fechamento < abertura)` rejeita fechamento ausente/inválido ou anterior a uma abertura válida.
- `anterior != ultimos_status[protocolo] or novo not in TRANSICOES[anterior]` rejeita histórico que pula um elo da sequência ou aplica uma transição proibida.
- `numero is not None and 1 <= numero <= len(opcoes)` aceita apenas uma escolha numérica dentro do menu apresentado.

O dicionário `TRANSICOES` representa a expressão booleana prevista no plano:

```python
(atual == "aberto" and novo == "em_atendimento") or (
    atual == "em_atendimento"
    and (novo == "aguardando_terceiro" or novo == "resolvido")
) or (atual == "aguardando_terceiro" and novo == "em_atendimento")
```

Cada trecho permite um dos caminhos descritos acima. Se nenhum for verdadeiro, a transição é inválida. A mesma regra vale na carga do histórico e na opção 6 do menu, que lê `TRANSICOES` de `dados.py`.

Erros de dados comuns, como a categoria ausente em `CH-013`, geram aviso e exclusão apenas da lista em memória. Cabeçalho incompatível, quantidade incorreta de colunas, CSV malformado, codificação inválida e protocolos duplicados ou inválidos bloqueiam a carga. Comparar também o número do protocolo impede tratar `CH-001` e `CH-0001` como identificadores diferentes.

A gravação valida novamente o registro e verifica se o protocolo já está reservado antes de acrescentá-lo. Ela preserva as linhas rejeitadas e funciona mesmo se faltar uma quebra de linha no final do arquivo. Esta implementação pressupõe uma pessoa cadastrando por vez; alterações manuais nos CSV devem ser feitas com o programa fechado.

## Integração com as outras partes

As funções de `dados.py` podem receber caminhos alternativos para testes. Na execução normal, usam os CSV de `data`.

| Função | Retorno / comportamento |
|---|---|
| `carregar(caminho=ARQUIVO, exibir_avisos=True)` | Tupla `(chamados, numeros)`: lista de dicionários válidos e conjunto de números reservados, incluindo os das linhas rejeitadas |
| `validar(chamado)` | Lista de erros; vazia quando o registro é válido; não modifica a entrada |
| `dia_simulado(valor)` | Dia como inteiro positivo, ou `None` para texto inválido |
| `carregar_historico(chamados, caminho=ARQUIVO_HISTORICO)` | Recebe os chamados já validados e retorna eventos válidos do mais antigo ao mais recente |
| `salvar_novo_chamado(chamado, caminho=ARQUIVO)` | Valida e acrescenta um chamado `aberto`; retorna o dicionário salvo |

Problemas de integridade geram `ValueError`; falhas de acesso podem gerar `OSError`. O menu trata ambos com mensagens. Para os próximos módulos, a carga inicial pode ser feita assim:

```python
from dados import carregar, carregar_historico

chamados, numeros = carregar()
historico = carregar_historico(chamados)
por_protocolo = {chamado["protocolo"]: chamado for chamado in chamados}
```

A lista permite percorrer todos os chamados; o conjunto de números impede reutilizar protocolos. O dicionário permite acesso por protocolo, e a lista de eventos é usada como pilha.

## Chamados (parte B)

`src/chamados.py` recebe as estruturas montadas em `sistema.py`:

| Estrutura | Variável | Uso |
|---|---|---|
| Lista | `chamados` | listar e filtrar, percorrendo com `for` |
| Dicionário | `por_protocolo` | consultar e atualizar sem percorrer a lista |
| Fila | `fila_triagem` | chamados `aberto` na ordem de registro; `pop(0)` atende o primeiro e novos cadastros entram no fim com `append` |
| Pilha | `historico` | cada mudança é empilhada com `append`; as últimas atualizações desempilham uma cópia com `pop()` |

Regras aplicadas no menu:

- `(categoria and categoria not in CATEGORIAS) or (status and status not in STATUS)` recusa um filtro com valor fora da lista; campo vazio significa "todos".
- `(not categoria or chamado["categoria"] == categoria) and (not status or chamado["status"] == status)` seleciona os chamados do filtro.
- `novo not in TRANSICOES[atual]` bloqueia transições proibidas, como `aberto` direto para `resolvido`.
- O dia de uma atualização não pode ser anterior à abertura nem ao último evento do chamado.

## Dashboard (parte C)

O módulo src/dashboard.py monta o painel a partir dos chamados já validados por dados.py. Ele só lê os dados; nada é gravado nos CSV. No menu principal, a opção 8 — Painel de indicadores mostra o painel geral e a opção 9 — Visão por bloco mostra o painel de um bloco escolhido por número. As duas chamam src/indicadores.py, que repassa os dados para o dashboard.py. O painel também abre sozinho com python src/dashboard.py.

Se o menu enviar o histórico (exibir_painel_indicadores(chamados, historico)), o painel mostra as últimas atualizações; sem ele, essa seção aparece vazia. O dashboard aceita dias como texto ou inteiro e eventos nos dois formatos do grupo (dia_evento/status_anterior/status_novo ou dia/de/para).

Neste condomínio, cada bloco corresponde a uma torre. O nome do bloco é padronizado só para agrupar (bloco  a e Bloco A entram no mesmo grupo); o valor gravado não muda.

### Seções do painel geral

- Chamados por status: quantidade, proporção e barra de texto.
- Chamados por categoria: mesmo formato.
- Matriz categoria × status (lista de listas): linha = categoria, coluna = status, com totais.
- Matriz bloco/torre × status: quantos chamados cada torre tem em cada situação.
- Hierarquia bloco/torre → categoria → chamados: dicionário de dicionários de listas, exibido em árvore com protocolo, área, status e prioridade.
- Indicadores, com fórmula e dados de origem na tela.
- Últimas atualizações: o histórico é usado como pilha; uma cópia é desempilhada com pop() para mostrar os 5 eventos mais recentes sem apagar o original.
- Conclusão: frases geradas por regras simples a partir dos números.

O painel por bloco/torre repete status, categoria, chamados, indicadores e últimas atualizações filtrados para um bloco.

### Estruturas de dados

| Estrutura | Uso no dashboard | Por quê |
|---|---|---|
| Lista | chamados e historico percorridos com for | Guarda todos os registros na ordem de cadastro |
| Dicionário | contar_por devolve {valor: quantidade} | Acesso direto ao contador de cada categoria/status |
| Matriz (lista de listas) | categoria × status e bloco × status | Cruza duas informações numa tabela; somar linha ou coluna dá os totais |
| Hierarquia (dict → dict → list) | montar_hierarquia | Organiza do geral (torre) ao específico (chamado), como o condomínio é percorrido |
| Pilha | ultimos_eventos | O último evento empilhado é o mais recente; pop() lê do topo |

### Indicadores e fórmulas

O dia de referência ("hoje" simulado) é o maior dia que aparece em aberturas, fechamentos ou eventos. Na base entregue, é o dia 18 (abertura do CH-014).

| Indicador | Fórmula | Base entregue |
|---|---|---|
| Proporção por categoria/status | quantidade ÷ total × 100 | ex.: 5 abertos ÷ 13 = 38,5% |
| Taxa de resolução | resolvidos ÷ total × 100 | 3 ÷ 13 = 23,1% |
| Tempo médio de resolução | soma(fechamento − abertura) ÷ resolvidos | (2 + 3 + 3) ÷ 3 = 2,7 dias |
| Resolvidos no prazo | resolução ≤ PRAZOS[prioridade] | 3 de 3 |
| Espera média das pendências | soma(referência − abertura) ÷ pendentes | 104 ÷ 10 = 10,4 dias |
| Pendências fora do prazo | pendente e espera > PRAZOS[prioridade] | 9 de 10 (6 urgentes ou altas) |

Distribuição por torre na base entregue:

| Bloco/torre | Aberto | Em atendimento | Aguardando terceiro | Resolvido | Total |
|---|---|---|---|---|---|
| Bloco A | 2 | 0 | 1 | 2 | 5 |
| Bloco B | 2 | 1 | 0 | 1 | 4 |
| Bloco C | 1 | 2 | 1 | 0 | 4 |

As porcentagens são arredondadas para uma casa decimal, então a soma exibida pode variar em 0,1 ponto.

### Expressões booleanas do dashboard

- `espera > prazo and (prioridade == "urgente" or prioridade == "alta")`: conta um atraso crítico só quando o chamado passou do prazo e é urgente ou alto.
- `not chamado["status"] == "resolvido"`: define pendente como tudo que não está resolvido.
- `if categoria in CATEGORIAS and status in STATUS`: só soma na matriz valores padronizados, protegendo os índices.
- `if total == 0 / if not chamados`: evita divisão por zero e mostra aviso quando não há chamados.

### Interpretação da base simulada

Iluminação é a categoria mais frequente (4 chamados). O Bloco C concentra mais pendências (4 de 4 chamados sem solução). Só 23,1% dos chamados foram resolvidos, e 9 das 10 pendências passaram do prazo, incluindo 3 urgentes. Os poucos chamados resolvidos fecharam rápido (2,7 dias em média, todos no prazo), o que indica que o gargalo está em iniciar o atendimento, não em concluí-lo. Como os dados são fictícios, essas conclusões servem para demonstrar o raciocínio, não para avaliar um condomínio real.

### Acessibilidade

O painel não depende de cores: toda barra vem acompanhada do número e da porcentagem, as abreviações das matrizes têm legenda, e a escolha do bloco é feita por número. Nenhum dado pessoal é exibido, só bloco e área comum.

## Verificação

Na pasta do projeto:

```bash
python -B -m unittest discover -s tests -v
```

Os testes de `test_dados.py` cobrem os mínimos do enunciado na base entregue, campos obrigatórios, valores e datas inválidos, estrutura do CSV, reserva de protocolos, coerência do histórico, preservação dos dados na gravação e cadastro de dois chamados consecutivos pelo menu. Os testes de escrita usam arquivos temporários e não alteram a base entregue. `test_chamados.py` cobre a ordem da fila, transições válidas e bloqueadas, saída da fila, consulta, filtro e a pilha de atualizações; `test_dashboard.py` cobre o painel.

O registro da assistência por IA está em [docs/uso_ia.md](docs/uso_ia.md).
