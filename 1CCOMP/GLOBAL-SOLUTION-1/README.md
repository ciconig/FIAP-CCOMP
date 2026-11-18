# Cadastro de chamados — Global Solution

Parte inicial do help desk de condomínio: dados fictícios e programa de cadastro em terminal, sem bibliotecas externas (Python 3). Não registrar nome, apartamento ou outro dado pessoal; informe apenas o bloco e a área comum.

## Como executar

Mantenha as pastas `data` e `src` juntas. Na pasta principal, execute:

```bash
python src/sistema.py
```

Se necessário, use `python3 src/sistema.py`. Selecione **1** para listar ou **2** para cadastrar. Escolha categoria e prioridade pelos números, preencha descrição, bloco, área comum e dia simulado. O programa grava o chamado no CSV e exibe o protocolo. **0** encerra. Faça uma cópia do CSV se quiser preservar os dados originais.

## Dados

- `data/chamados.csv`: UTF-8, separado por vírgulas, com cabeçalho `protocolo,categoria,prioridade,descricao,bloco,area,dia_abertura,status,dia_fechamento`. Contém 12 registros válidos e um 13º intencionalmente inválido: `CH-013` está sem categoria. Ele permanece no arquivo, mas é identificado e ignorado na listagem; corrija sua categoria no CSV para incluí-lo.
- `data/historico.csv`: 13 eventos fictícios de mudança de status, em ordem cronológica por chamado. É uma base inicial separada: o programa de cadastro ainda não lê nem altera o histórico.
- Os dias são inteiros simulados, não datas de calendário. `dia_fechamento` fica vazio enquanto o chamado não está resolvido; quando resolvido, deve ser igual ou posterior ao dia de abertura.
- Todos os campos são obrigatórios, exceto `dia_fechamento` para chamados não resolvidos. Categorias: `iluminacao`, `acessibilidade`, `limpeza`, `conservacao`. Prioridades: `urgente`, `alta`, `normal`.
- Status: `aberto` = ainda não examinado; `em_atendimento` = assumido pela administração; `aguardando_terceiro` = depende de empresa ou peça; `resolvido` = fechado. Um novo chamado começa como `aberto`.
- O protocolo é sequencial (`CH-001`, `CH-002`...), calculado a partir do maior número já presente, inclusive nas linhas inválidas, para não reutilizar identificadores. Esta implementação supõe apenas uma pessoa cadastrando de cada vez.

## Validação

O programa verifica campos obrigatórios, valores de categoria, prioridade e status, protocolo e coerência dos dias. Por exemplo, `resposta.isdigit() and 1 <= int(resposta) <= len(opcoes)` permite escolher apenas um número dentro da lista; caso contrário, pede novamente. A condição `not chamado.get(campo, "").strip()` identifica campo obrigatório vazio. O teste `not abertura.isdigit() or int(abertura) < 1` rejeita abertura ausente, não numérica ou menor que 1. Protocolos duplicados ou malformados e cabeçalho incompatível bloqueiam a leitura até a correção, evitando gerar um ID repetido. Linhas com outros erros são avisadas e ignoradas, sem apagá-las.

## Limites desta entrega

Esta é a parte de dados e cadastro, não o sistema completo do grupo. Busca por protocolo, filtros, fila, atualização de status, leitura/empilhamento do histórico, hierarquia, matriz e indicadores ainda precisam ser implementados e integrados. O CSV de histórico é apenas uma amostra para essa integração.
