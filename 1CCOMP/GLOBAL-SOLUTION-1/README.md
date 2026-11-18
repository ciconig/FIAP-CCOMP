# Cadastro e dados iniciais — Global Solution

Help desk de condomínio para registrar problemas nas áreas comuns. Esta entrega cobre cadastro, leitura e validação dos dados iniciais, conforme a divisão do plano. Usa apenas a biblioteca padrão do Python 3.

Os registros são fictícios. Informe apenas bloco e área comum: não registre nome, apartamento ou outro dado pessoal do morador.

## Como executar

Na pasta `1CCOMP/GLOBAL-SOLUTION-1`, execute:

```bash
python src/sistema.py
```

Os caminhos dos CSV são calculados a partir de `dados.py`, permitindo executar o programa de outra pasta também. Mantenha os dois arquivos em `data`, junto de `src`.

Na inicialização, o programa avisa que `CH-013` está sem categoria e mostra a quantidade de chamados válidos e eventos de histórico carregados. O menu oferece:

- **1 — Listar chamados:** exibe protocolo, categoria, prioridade, bloco, área comum e status. A prioridade `URGENTE` aparece em maiúsculas.
- **2 — Abrir chamado:** permite escolher categoria e prioridade por número e pede descrição, bloco, área comum e dia simulado. Entradas inválidas são solicitadas novamente. O chamado começa como `aberto`, é gravado no CSV e recebe um protocolo sequencial.
- **0 — Sair.**

Para testar o cadastro, uma descrição possível é “Luz apagada no hall”, local “Bloco A / Hall”, dia `18`. Na base entregue, o próximo protocolo é `CH-015`, pois `CH-014` já existe. Os cadastros persistem entre execuções; faça uma cópia dos CSV se quiser repetir a demonstração com a mesma base.

## Organização da entrega

```text
GLOBAL-SOLUTION-1/
├── data/
│   ├── chamados.csv
│   └── historico.csv
├── src/
│   ├── dados.py           # constantes, validação, leitura e gravação
│   └── sistema.py         # menu demonstrativo de cadastro e listagem
├── tests/test_dados.py    # integridade dos dados e fluxo de cadastro
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

As constantes `PRAZOS` e `TRANSICOES` ficam disponíveis em `dados.py` para a integração do grupo. Os prazos previstos são `urgente: 1`, `alta: 3` e `normal: 7` dias. A prioridade não altera a ordem de chegada da futura fila.

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

O arquivo agrupa eventos por protocolo, em ordem cronológica dentro de cada chamado. `carregar_historico` retorna a lista ordenada por dia para que o último item represente o evento mais recente na futura pilha; empates mantêm a ordem do arquivo.

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

Cada trecho permite um dos caminhos descritos acima. Se nenhum for verdadeiro, a transição é inválida. Nesta entrega, a regra é aplicada aos eventos importados; a atualização interativa cabe à integração de chamados.

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

A lista permite percorrer todos os chamados; o conjunto de números impede reutilizar protocolos. O dicionário do exemplo permite acesso por protocolo, e a lista de eventos está preparada para ser usada como pilha pelo módulo de chamados.

Busca, filtros, fila de triagem, atualização interativa e gravação de mudanças no histórico ainda cabem à parte B. Matriz, hierarquia e indicadores cabem à parte C. O menu atual demonstra cadastro e listagem; a carga do histórico já está integrada e validada.

## Verificação

Na pasta do projeto:

```bash
python -B -m unittest discover -s tests -v
```

Os oito testes cobrem os mínimos do enunciado na base entregue, campos obrigatórios, valores e datas inválidos, estrutura do CSV, reserva de protocolos, coerência do histórico, preservação dos dados na gravação e cadastro de dois chamados consecutivos pelo menu. Os testes de escrita usam arquivos temporários e não alteram a base entregue.

O registro da assistência por IA está em [docs/uso_ia.md](docs/uso_ia.md).
