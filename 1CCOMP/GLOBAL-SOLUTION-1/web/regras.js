(function (raiz) {
  "use strict";

  const CAMPOS = ["protocolo", "categoria", "prioridade", "descricao", "bloco", "area",
    "dia_abertura", "status", "dia_fechamento"];
  const OBRIGATORIOS = CAMPOS.slice(0, -1);
  const CATEGORIAS = ["iluminacao", "acessibilidade", "limpeza", "conservacao"];
  const PRIORIDADES = ["urgente", "alta", "normal"];
  const STATUS = ["aberto", "em_atendimento", "aguardando_terceiro", "resolvido"];
  const PRAZOS = { urgente: 1, alta: 3, normal: 7 };
  const TRANSICOES = {
    aberto: ["em_atendimento"],
    em_atendimento: ["aguardando_terceiro", "resolvido"],
    aguardando_terceiro: ["em_atendimento"],
    resolvido: [],
  };
  const ROTULOS = {
    iluminacao: "Iluminação", acessibilidade: "Acessibilidade", limpeza: "Limpeza",
    conservacao: "Conservação", aberto: "Aberto", em_atendimento: "Em atendimento",
    aguardando_terceiro: "Aguardando terceiro", resolvido: "Resolvido",
    urgente: "Urgente", alta: "Alta", normal: "Normal",
  };

  function texto(registro, campo) {
    const valor = registro[campo];
    return typeof valor === "string" ? valor.trim() : "";
  }

  function diaSimulado(valor) {
    if (typeof valor !== "string" || !/^[0-9]+$/.test(valor.trim())) return null;
    const dia = parseInt(valor, 10);
    return dia > 0 ? dia : null;
  }

  function numeroProtocolo(protocolo) {
    if (!/^CH-[0-9]{3,}$/.test(protocolo)) return null;
    const numero = parseInt(protocolo.slice(3), 10);
    return numero > 0 ? numero : null;
  }

  function validar(chamado) {
    const dados = {};
    CAMPOS.forEach((campo) => { dados[campo] = texto(chamado, campo); });
    const erros = [];
    const ausentes = OBRIGATORIOS.filter((campo) => !dados[campo]);
    if (ausentes.length) erros.push("campos obrigatórios ausentes: " + ausentes.join(", "));
    if (numeroProtocolo(dados.protocolo) === null) erros.push("protocolo inválido");
    if (!CATEGORIAS.includes(dados.categoria)) erros.push("categoria inválida");
    if (!PRIORIDADES.includes(dados.prioridade)) erros.push("prioridade inválida");
    if (!STATUS.includes(dados.status)) erros.push("status inválido");
    const abertura = diaSimulado(dados.dia_abertura);
    const fechamento = diaSimulado(dados.dia_fechamento);
    if (abertura === null) erros.push("dia de abertura deve ser um inteiro positivo");
    if (dados.status === "resolvido") {
      if (fechamento === null || (abertura !== null && fechamento < abertura)) {
        erros.push("resolvido precisa de dia de fechamento igual ou posterior à abertura");
      }
    } else if (dados.dia_fechamento) {
      erros.push("chamado não resolvido não pode ter dia de fechamento");
    }
    return erros;
  }

  function carregar(linhas) {
    const validos = [];
    const numeros = new Set();
    const avisos = [];
    linhas.forEach((linha) => {
      numeros.add(numeroProtocolo(linha.protocolo));
      const erros = validar(linha);
      if (erros.length) avisos.push(`${linha.protocolo} ignorado: ${erros.join("; ")}`);
      else validos.push(Object.assign({}, linha));
    });
    return { chamados: validos, numeros, avisos };
  }

  function proximoProtocolo(numeros) {
    let maior = 0;
    numeros.forEach((n) => { if (n !== null && n > maior) maior = n; });
    return "CH-" + String(maior + 1).padStart(3, "0");
  }

  function montarFila(chamados) {
    return chamados.filter((c) => c.status === "aberto");
  }

  function ultimoDia(chamado, historico) {
    let dia = parseInt(chamado.dia_abertura, 10);
    historico.forEach((e) => {
      if (e.protocolo === chamado.protocolo) dia = Math.max(dia, parseInt(e.dia_evento, 10));
    });
    return dia;
  }

  function checarTransicao(chamado, novo, dia, historico) {
    if (!STATUS.includes(novo)) return "Status desconhecido.";
    if (!TRANSICOES[chamado.status].includes(novo)) {
      return `Transição bloqueada: ${chamado.status} não pode ir direto para ${novo}.`;
    }
    const minimo = ultimoDia(chamado, historico);
    if (dia === null || dia < minimo) return `Dia inválido: informe um inteiro a partir de ${minimo}.`;
    return null;
  }

  function registrar(chamado, novo, dia, observacao, historico, fila) {
    historico.push({
      protocolo: chamado.protocolo, dia_evento: String(dia),
      status_anterior: chamado.status, status_novo: novo, observacao,
    });
    chamado.status = novo;
    if (novo === "resolvido") chamado.dia_fechamento = String(dia);
    const posicao = fila.indexOf(chamado);
    if (posicao >= 0) fila.splice(posicao, 1);
  }

  function ultimosEventos(historico, quantidade) {
    const pilha = historico.slice();
    const recentes = [];
    while (pilha.length && recentes.length < quantidade) recentes.push(pilha.pop());
    return recentes;
  }

  function nomeBloco(chamado) {
    return chamado.bloco.trim().split(/\s+/).map((p) =>
      p.charAt(0).toUpperCase() + p.slice(1).toLowerCase()).join(" ");
  }

  function converterDia(valor) {
    if (valor === null || valor === undefined || valor === "") return null;
    const dia = parseInt(valor, 10);
    return Number.isNaN(dia) ? null : dia;
  }

  function percentual(parte, total) { return total === 0 ? 0 : parte * 100 / total; }

  function diaReferencia(chamados, historico) {
    let maior = 0;
    chamados.forEach((c) => {
      [converterDia(c.dia_abertura), converterDia(c.dia_fechamento)].forEach((d) => {
        if (d !== null && d > maior) maior = d;
      });
    });
    historico.forEach((e) => {
      const d = converterDia(e.dia_evento);
      if (d !== null && d > maior) maior = d;
    });
    return maior;
  }

  function blocosDisponiveis(chamados) {
    const blocos = [];
    chamados.forEach((c) => { const b = nomeBloco(c); if (!blocos.includes(b)) blocos.push(b); });
    return blocos.sort();
  }

  function contarPor(chamados, campo, valores) {
    const contagem = {};
    valores.forEach((v) => { contagem[v] = 0; });
    chamados.forEach((c) => { if (c[campo] in contagem) contagem[c[campo]] += 1; });
    return contagem;
  }

  function matriz(chamados, linhas, chaveLinha) {
    const m = linhas.map(() => STATUS.map(() => 0));
    chamados.forEach((c) => {
      const i = linhas.indexOf(chaveLinha(c));
      const j = STATUS.indexOf(c.status);
      if (i >= 0 && j >= 0) m[i][j] += 1;
    });
    return m;
  }

  function montarHierarquia(chamados) {
    const arvore = {};
    blocosDisponiveis(chamados).forEach((b) => { arvore[b] = {}; });
    chamados.forEach((c) => {
      const b = nomeBloco(c);
      if (!arvore[b][c.categoria]) arvore[b][c.categoria] = [];
      arvore[b][c.categoria].push(c);
    });
    return arvore;
  }

  function calcularIndicadores(chamados, historico, referencia) {
    if (referencia === undefined) referencia = diaReferencia(chamados, historico);
    const r = {
      referencia, total: chamados.length, resolvidos: 0, pendentes: 0, somaResolucao: 0,
      resolvidosNoPrazo: 0, somaEspera: 0, atrasados: [], urgentesPendentes: 0, criticosAtrasados: 0,
    };
    chamados.forEach((c) => {
      let abertura = converterDia(c.dia_abertura);
      let fechamento = converterDia(c.dia_fechamento);
      const prazo = PRAZOS[c.prioridade];
      if (abertura === null) abertura = referencia;
      if (c.status !== "resolvido") {
        r.pendentes += 1;
        const espera = referencia - abertura;
        r.somaEspera += espera;
        const atrasado = prazo !== undefined && espera > prazo;
        if (atrasado) r.atrasados.push(c);
        if (atrasado && (c.prioridade === "urgente" || c.prioridade === "alta")) r.criticosAtrasados += 1;
        if (c.prioridade === "urgente") r.urgentesPendentes += 1;
      } else {
        r.resolvidos += 1;
        if (fechamento === null) fechamento = abertura;
        const duracao = fechamento - abertura;
        r.somaResolucao += duracao;
        if (prazo === undefined || duracao <= prazo) r.resolvidosNoPrazo += 1;
      }
    });
    r.taxaResolucao = percentual(r.resolvidos, r.total);
    r.tempoMedio = r.resolvidos ? r.somaResolucao / r.resolvidos : null;
    r.esperaMedia = r.pendentes ? r.somaEspera / r.pendentes : null;
    r.eventos = historico.length;
    return r;
  }

  function maisFrequentes(contagem) {
    let maior = 0;
    Object.values(contagem).forEach((v) => { if (v > maior) maior = v; });
    if (maior === 0) return { chaves: [], maior: 0 };
    return { chaves: Object.keys(contagem).filter((k) => contagem[k] === maior), maior };
  }

  function formatar(numero) { return numero.toFixed(1).replace(".", ","); }

  function gerarConclusao(chamados, ind) {
    if (!chamados.length) return ["Não há chamados válidos para interpretar."];
    const frases = [];
    const cat = maisFrequentes(contarPor(chamados, "categoria", CATEGORIAS));
    const nomes = cat.chaves.map((c) => ROTULOS[c]);
    frases.push(nomes.length === 1
      ? `A categoria com mais chamados é ${nomes[0]} (${cat.maior}).`
      : `Há empate entre ${nomes.join(", ")} (${cat.maior} chamados cada).`);
    const pend = {};
    blocosDisponiveis(chamados).forEach((b) => { pend[b] = 0; });
    chamados.forEach((c) => { if (c.status !== "resolvido") pend[nomeBloco(c)] += 1; });
    const blo = maisFrequentes(pend);
    if (blo.maior === 0) frases.push("Nenhum bloco tem chamados pendentes.");
    else if (blo.chaves.length === 1) frases.push(`O bloco/torre com mais pendências é ${blo.chaves[0]} (${blo.maior}).`);
    else frases.push(`Os blocos/torres ${blo.chaves.join(", ")} empatam em pendências (${blo.maior} cada).`);
    frases.push(ind.taxaResolucao < 50
      ? `Só ${formatar(ind.taxaResolucao)}% dos chamados foram resolvidos: a maior parte segue em aberto.`
      : `${formatar(ind.taxaResolucao)}% dos chamados já foram resolvidos.`);
    const atrasados = ind.atrasados.length;
    if (atrasados > 0 && ind.urgentesPendentes > 0) {
      frases.push(`${atrasados} pendência(s) passaram do prazo, e há ${ind.urgentesPendentes} urgente(s) sem solução: vale priorizar esses casos.`);
    } else if (atrasados > 0) {
      frases.push(`${atrasados} pendência(s) passaram do prazo previsto.`);
    } else {
      frases.push("Todas as pendências estão dentro do prazo previsto.");
    }
    frases.push("Os dados são simulados; servem para treinar a análise, não para avaliar um condomínio real.");
    return frases;
  }

  const Regras = {
    CAMPOS, CATEGORIAS, PRIORIDADES, STATUS, PRAZOS, TRANSICOES, ROTULOS,
    diaSimulado, validar, carregar, proximoProtocolo, montarFila, ultimoDia,
    checarTransicao, registrar, ultimosEventos, nomeBloco, percentual, diaReferencia,
    blocosDisponiveis, contarPor, matriz, montarHierarquia, calcularIndicadores,
    gerarConclusao, formatar,
  };
  if (typeof module !== "undefined" && module.exports) module.exports = Regras;
  else raiz.Regras = Regras;
})(globalThis);
