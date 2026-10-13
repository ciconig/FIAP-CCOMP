# MGPEB — item 3 da atividade integradora

Protótipo didático em Python 3, sem bibliotecas externas.

## Execução

```bash
python mgpeb.py
python test_mgpeb.py
```

`saida.txt` contém a saída da execução validada.

## Dados e hipóteses

Os dez módulos, prioridades, combustíveis, massas e criticidades reproduzem o cenário da equipe. Prioridade 1 é a mais alta. Os rótulos de carga resumem a função de cada módulo.

Regras propostas, ainda dependentes de alinhamento com o item 2:
- Combustível >= 50%; o cenário menciona 50% como referência de alerta, mas sua utilização como limite de autorização é uma hipótese adicional.
- Massa <= 12.000 kg; capacidade hipotética da plataforma.
- Área livre, sistemas operacionais e ausência de impedimento individual.
- Baixo combustível OU impedimento gera ALERTA; demais falhas geram ESPERA.
- Uma autorização simula um pouso sequencial concluído antes do próximo.

O cadastro permanece na ordem inicial MD01..MD10. A fila é uma cópia, reorganizada por Insertion Sort: prioridade crescente, criticidade da carga (Crítica, Alta, Média, Baixa) e combustível crescente. Empates exatos mantêm a ordem de chegada. Após reordenação, o processamento remove o início da fila (FIFO). Alertas usam pilha (LIFO) somente para demonstrar atendimento manual, sem autorização automática ou estratégia real de emergência.

## Resultado de referência

Menor combustível: MD10 (42%). Maior prioridade com desempate por criticidade e combustível: MD03 (prioridade 1; Crítica; 48%). Busca Medicina: MD03.
Fila: MD03, MD02, MD01, MD05, MD04, MD09, MD08, MD06, MD10, MD07.
Rodada nominal: 8 pousados, 2 alertas (MD03 e MD10), 0 em espera. Alerta com carga crítica: MD03.

## Limites

Não há consumo de combustível, ETA, concorrência, persistência, dependências entre módulos ou física de pouso/estabilização. Criticidade ordena a fila e destaca alertas críticos, mas não altera a regra de autorização, mantida alinhada ao item 2. Fila com pop(0) custa O(n), adequada ao exemplo de dez registros, não a um sistema real de voo. Busca linear O(n); Insertion Sort O(n²) no pior caso e O(n) na melhor situação. Os testes usam somente recursos da biblioteca padrão e asserts.
