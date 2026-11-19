// Painel web do help desk. As regras vêm de regras.js; aqui só há tela e interação.
(function () {
  "use strict";
  const R = window.Regras;
  const $ = (s) => document.querySelector(s);
  const $$ = (s) => Array.from(document.querySelectorAll(s));
  const reduzido = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const temAnime = () => Boolean(window.anime) && !reduzido;

  // anime.js é só acabamento: sem ele (offline) ou com movimento reduzido, tudo aparece pronto.
  function animar(opcoes) {
    if (temAnime()) return window.anime(opcoes);
    if (opcoes.update) opcoes.update();
    if (opcoes.complete) opcoes.complete();
    return null;
  }
  const escalonar = (ms) => (temAnime() ? window.anime.stagger(ms) : 0);
  const entrar = (alvos, extra) => animar(Object.assign({ targets: alvos, opacity: [0, 1], translateY: [8, 0],
    delay: escalonar(30), duration: 380, easing: "easeOutCubic" }, extra || {}));

  const esc = (t) => String(t).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
  const rot = (v) => R.ROTULOS[v] || v;
  const pilula = (s) => `<span class="status s-${s}">${rot(s)}</span>`;
  const etiqueta = (p) => `<span class="etiqueta e-${p}">${rot(p)}</span>`;
  const COR = { aberto: "var(--aberto)", em_atendimento: "var(--em_atendimento)",
    aguardando_terceiro: "var(--aguardando_terceiro)", resolvido: "var(--resolvido)" };
  const VERBOS = {
    "aberto>em_atendimento": "Iniciar atendimento",
    "em_atendimento>aguardando_terceiro": "Aguardar terceiro",
    "em_atendimento>resolvido": "Marcar como resolvido",
    "aguardando_terceiro>em_atendimento": "Retomar atendimento",
  };

  // ---- Estado: as mesmas estruturas do Python ----
  const carga = R.carregar(window.DADOS_CHAMADOS);
  const chamados = carga.chamados;                                    // lista
  const numeros = carga.numeros;                                      // protocolos reservados
  const porProtocolo = {};                                            // dicionário
  chamados.forEach((c) => { porProtocolo[c.protocolo] = c; });
  const fila = R.montarFila(chamados);                                // fila (FIFO)
  const historico = window.DADOS_HISTORICO.map((e) => Object.assign({}, e)); // pilha
  const filtro = { bloco: "", status: "", categoria: "", blocoLista: "", busca: "" };
  let aberto = null; // chamado exibido na gaveta

  const referencia = () => R.diaReferencia(chamados, historico);
  const base = () => (filtro.bloco ? chamados.filter((c) => R.nomeBloco(c) === filtro.bloco) : chamados);

  function aviso(texto, erro) {
    const el = $("#aviso");
    el.textContent = texto;
    el.className = erro ? "erro" : "";
    if (temAnime()) {
      window.anime.remove(el);
      window.anime.timeline({ targets: el })
        .add({ opacity: [0, 1], translateY: [16, 0], translateX: ["-50%", "-50%"], duration: 300, easing: "easeOutCubic" })
        .add({ opacity: 0, delay: 3000, duration: 400, easing: "linear" });
    } else {
      el.style.opacity = 1;
      clearTimeout(aviso.t);
      aviso.t = setTimeout(() => { el.style.opacity = 0; }, 3400);
    }
  }

  function contar(el, valor, formato) {
    const proxy = { v: Number(el.dataset.v || 0) };
    el.dataset.v = valor;
    animar({ targets: proxy, v: valor, duration: 800, easing: "easeOutExpo",
      update: () => { el.textContent = formato(temAnime() ? proxy.v : valor); } });
  }

  // ---- Cabeçalho, faixa e KPIs ----
  function desenharFaixa() {
    const ind = R.calcularIndicadores(chamados, historico);
    $("#sol").textContent = `Sol ${ind.referencia}`;
    const proximo = fila[0];
    $("#faixa").innerHTML = `
      <div class="item"><b style="color:var(--aberto)">${ind.atrasados.length}</b><span>fora do prazo</span></div><div class="sep"></div>
      <div class="item"><b style="color:#ff9a8f">${ind.urgentesPendentes}</b><span>urgentes sem solução</span></div><div class="sep"></div>
      <div class="item"><b>${fila.length}</b><span>aguardando triagem</span></div>
      ${carga.avisos.length ? `<div class="sep"></div><div class="item suave" title="${esc(carga.avisos.join(" | "))}">
        ${carga.avisos.length} registro rejeitado na carga (${esc(carga.avisos.map((a) => a.split(" ")[0]).join(", "))})</div>` : ""}
      <div class="espaco"></div>
      <button class="botao" type="button" id="faixa-atender" ${proximo ? "" : "disabled"}>
        ${proximo ? `Atender próximo · ${esc(proximo.protocolo)}` : "Fila vazia"}</button>`;
    $("#faixa-atender").addEventListener("click", atenderProximo);
  }

  function desenharChips() {
    const blocos = R.blocosDisponiveis(chamados);
    $("#chips-bloco").innerHTML = ["", ...blocos].map((b) =>
      `<button class="chip" type="button" data-bloco="${esc(b)}" aria-pressed="${filtro.bloco === b}">${b ? esc(b) : "Condomínio inteiro"}</button>`).join("");
  }

  function desenharKpis() {
    const lista = base();
    const ind = R.calcularIndicadores(lista, historico, referencia());
    const kpis = [
      ["chamados", "Chamados", ind.total, (v) => Math.round(v), "válidos na visão atual"],
      ["pendentes", "Pendentes", ind.pendentes, (v) => Math.round(v), `${ind.atrasados.length} fora do prazo`],
      ["tempo", "Tempo médio de resolução", ind.tempoMedio || 0, (v) => (ind.tempoMedio === null ? "—" : R.formatar(v) + " sol"),
        `${ind.somaResolucao} ÷ ${ind.resolvidos} resolvidos`],
      ["prazo", "Resolvidos no prazo", ind.resolvidosNoPrazo, (v) => `${Math.round(v)}/${ind.resolvidos}`, "resolução ≤ prazo"],
    ];
    const caixa = $("#kpis");
    if (!caixa.children.length) {
      caixa.innerHTML = kpis.map(([id]) => `<div class="kpi"><div class="rotulo" id="kr-${id}"></div><div class="valor" id="kv-${id}">0</div><div class="formula" id="kf-${id}"></div></div>`).join("");
      entrar("#kpis .kpi", { delay: escalonar(60) });
    }
    kpis.forEach(([id, rotulo, valor, formato, formula]) => {
      $("#kr-" + id).textContent = rotulo;
      $("#kf-" + id).textContent = formula;
      contar($("#kv-" + id), valor, formato);
    });
  }

  // ---- Rosca por status ----
  function desenharRosca() {
    const lista = base();
    const contagem = R.contarPor(lista, "status", R.STATUS);
    const total = lista.length;
    const raio = 62;
    const volta = 2 * Math.PI * raio;
    let acumulado = 0;
    const fatias = R.STATUS.map((s) => {
      const tamanho = total ? contagem[s] / total * volta : 0;
      const fatia = { s, tamanho, inicio: acumulado };
      acumulado += tamanho;
      return fatia;
    });
    const svg = $("#rosca-svg");
    svg.innerHTML = `<circle cx="80" cy="80" r="${raio}" fill="none" stroke="var(--painel-3)" stroke-width="20"/>` +
      fatias.map((f) => `<circle data-s="${f.s}" cx="80" cy="80" r="${raio}" fill="none" stroke="${COR[f.s]}" stroke-width="20"
        stroke-dasharray="0 ${volta}" stroke-dashoffset="${-f.inicio}" style="cursor:pointer"><title>${rot(f.s)}: ${contagem[f.s]}</title></circle>`).join("");
    const circulos = Array.from(svg.querySelectorAll("circle[data-s]"));
    const proxy = { t: 0 };
    animar({ targets: proxy, t: 1, duration: 900, easing: "easeOutCubic", update: () => {
      const t = temAnime() ? proxy.t : 1;
      circulos.forEach((c, i) => {
        const f = fatias[i];
        const visivel = Math.max(0, f.tamanho * t - (f.tamanho > 2 ? 1.5 : 0));
        c.setAttribute("stroke-dasharray", `${visivel} ${volta}`);
        c.setAttribute("stroke-dashoffset", String(-f.inicio * t));
      });
    } });
    circulos.forEach((c) => c.addEventListener("click", () => alternar("status", c.dataset.s)));
    contar($("#rosca-centro"), R.percentual(contagem.resolvido, total), (v) => R.formatar(v) + "%");
    $("#legenda").innerHTML = R.STATUS.map((s) => `<li><button type="button" data-status="${s}" aria-pressed="${filtro.status === s}">
      <span class="bolinha" style="background:${COR[s]}"></span>${rot(s)}<span class="n">${contagem[s]} · ${R.formatar(R.percentual(contagem[s], total))}%</span></button></li>`).join("");
  }

  // ---- Barras por categoria (empilhadas por status) ----
  function desenharBarras() {
    const lista = base();
    const contagem = R.contarPor(lista, "categoria", R.CATEGORIAS);
    const m = R.matriz(lista, R.CATEGORIAS, (c) => c.categoria);
    const maior = Math.max(1, ...Object.values(contagem));
    $("#barras").innerHTML = R.CATEGORIAS.map((cat, i) => `
      <button class="barra" type="button" data-categoria="${cat}" aria-pressed="${filtro.categoria === cat}">
        <span>${rot(cat)}</span>
        <span class="trilho" style="width:${contagem[cat] / maior * 100}%">${R.STATUS.map((s, j) => m[i][j]
          ? `<span title="${rot(s)}: ${m[i][j]}" data-largura="${m[i][j] / contagem[cat] * 100}" style="width:0;background:${COR[s]}"></span>` : "").join("")}</span>
        <span class="n">${contagem[cat]} · ${R.formatar(R.percentual(contagem[cat], lista.length))}%</span>
      </button>`).join("");
    const partes = $$("#barras .trilho span");
    animar({ targets: partes, width: (el) => el.dataset.largura + "%", delay: escalonar(25), duration: 700, easing: "easeOutCubic" });
    if (!temAnime()) partes.forEach((el) => { el.style.width = el.dataset.largura + "%"; });
  }

  // ---- Mapa de calor bloco × status ----
  function desenharMatriz() {
    const blocos = filtro.bloco ? [filtro.bloco] : R.blocosDisponiveis(chamados);
    const m = R.matriz(chamados, blocos, R.nomeBloco);
    const maior = Math.max(1, ...m.flat());
    const celula = (bloco, s, v) => {
      const intensidade = v ? 0.18 + 0.62 * v / maior : 0;
      const ativo = filtro.blocoLista === bloco && filtro.status === s;
      return `<td><button type="button" data-bloco="${esc(bloco)}" data-status="${s}" aria-pressed="${ativo}"
        aria-label="${esc(bloco)}, ${rot(s)}: ${v}" style="background:color-mix(in srgb, ${COR[s]} ${Math.round(intensidade * 100)}%, var(--painel-2))">${v}</button></td>`;
    };
    $("#matriz").innerHTML = `<table class="matriz"><thead><tr><th>Bloco</th>${R.STATUS.map((s) => `<th>${rot(s)}</th>`).join("")}<th>Total</th></tr></thead>
      <tbody>${blocos.map((b, i) => `<tr><th>${esc(b)}</th>${R.STATUS.map((s, j) => celula(b, s, m[i][j])).join("")}
        <td class="total">${m[i].reduce((a, v) => a + v, 0)}</td></tr>`).join("")}</tbody></table>`;
    entrar("#matriz td button", { delay: escalonar(18), translateY: [4, 0] });
  }

  // ---- Fila e pilha ----
  function desenharFila() {
    $("#fila").innerHTML = fila.length ? fila.slice(0, 6).map((c, i) => `<li><span class="pos">${i + 1}º</span>
        <span style="flex:1;min-width:0"><b class="mono">${esc(c.protocolo)}</b> ${esc(c.descricao)}<br><span class="suave">${esc(c.bloco)} · ${esc(c.area)}</span></span>
        ${etiqueta(c.prioridade)}</li>`).join("") + (fila.length > 6 ? `<li class="suave">+ ${fila.length - 6} na fila</li>` : "")
      : '<li class="suave">Nenhum chamado aguardando triagem.</li>';
    $("#btn-atender").disabled = !fila.length;
    $("#btn-atender").textContent = fila.length ? `Atender ${fila[0].protocolo}` : "Fila vazia";
  }

  function linhaEvento(e, topo) {
    return `<li><span class="quando">sol ${esc(e.dia_evento)} · ${esc(e.protocolo)}</span>${topo ? '<span class="selo">topo</span>' : ""}<br>
      ${pilula(e.status_anterior)} → ${pilula(e.status_novo)}<br><span class="suave">${esc(e.observacao)}</span></li>`;
  }

  function desenharPilha() {
    $("#pilha").innerHTML = R.ultimosEventos(historico, 5).map((e, i) => linhaEvento(e, i === 0)).join("");
  }

  // ---- Indicadores e conclusão ----
  function desenharIndicadores() {
    const lista = base();
    const ind = R.calcularIndicadores(lista, historico, referencia());
    const media = (v) => (v === null ? "—" : R.formatar(v));
    const itens = [
      ["Taxa de resolução", `${R.formatar(ind.taxaResolucao)}%`, `${ind.resolvidos} ÷ ${ind.total} × 100`],
      ["Espera média das pendências", `${media(ind.esperaMedia)} sol`, `soma(sol ${ind.referencia} − abertura) ÷ pendentes = ${ind.somaEspera} ÷ ${ind.pendentes}`],
      ["Pendências fora do prazo", `${ind.atrasados.length}/${ind.pendentes}`, `espera > prazo · ${ind.criticosAtrasados} urgentes ou altas`],
      ["Urgentes sem solução", String(ind.urgentesPendentes), "prioridade urgente e não resolvido"],
    ];
    $("#indicadores").innerHTML = itens.map(([nome, valor, formula]) =>
      `<div class="indicador"><span>${nome}</span><b>${valor}</b><small>${esc(formula)}</small></div>`).join("");
    $("#conclusao").innerHTML = R.gerarConclusao(lista, ind).map((f) => `<li>${esc(f)}</li>`).join("");
  }

  // ---- Lista lateral ----
  function atrasadosSet() {
    return new Set(R.calcularIndicadores(chamados, historico).atrasados.map((c) => c.protocolo));
  }

  function desenharLista() {
    const busca = filtro.busca.toLowerCase();
    const atrasados = atrasadosSet();
    const lista = base().filter((c) =>
      (!filtro.status || c.status === filtro.status) && (!filtro.categoria || c.categoria === filtro.categoria) &&
      (!filtro.blocoLista || R.nomeBloco(c) === filtro.blocoLista) &&
      (!busca || [c.protocolo, c.descricao, c.area, c.bloco].join(" ").toLowerCase().includes(busca)));
    // Pendentes primeiro (mais urgentes no topo), resolvidos por último.
    const peso = { urgente: 0, alta: 1, normal: 2 };
    lista.sort((a, b) => (a.status === "resolvido") - (b.status === "resolvido") || peso[a.prioridade] - peso[b.prioridade] ||
      parseInt(a.dia_abertura, 10) - parseInt(b.dia_abertura, 10));
    $("#contagem-lista").textContent = `${lista.length} de ${chamados.length}`;
    const ativos = [];
    if (filtro.status) ativos.push(["status", rot(filtro.status)]);
    if (filtro.categoria) ativos.push(["categoria", rot(filtro.categoria)]);
    if (filtro.blocoLista) ativos.push(["blocoLista", filtro.blocoLista]);
    $("#filtros-ativos").innerHTML = ativos.map(([k, nome]) => `<button type="button" data-limpar="${k}" aria-label="Remover filtro ${esc(nome)}">${esc(nome)} ×</button>`).join("") +
      (ativos.length > 1 ? '<button type="button" data-limpar="tudo">Limpar tudo</button>' : "");
    $("#itens").innerHTML = lista.length ? lista.map((c) => `
      <button class="item-chamado" type="button" data-protocolo="${esc(c.protocolo)}" style="--cor:${COR[c.status]}">
        <span class="l1"><span class="mono">${esc(c.protocolo)}</span>${etiqueta(c.prioridade)}${atrasados.has(c.protocolo) ? '<span class="etiqueta e-atraso">fora do prazo</span>' : ""}
          <span style="margin-left:auto">${pilula(c.status)}</span></span>
        <span class="desc">${esc(c.descricao)}</span>
        <span class="l3"><span>${esc(c.bloco)} · ${esc(c.area)}</span><span>${rot(c.categoria)}</span><span>aberto no sol ${esc(c.dia_abertura)}</span></span>
      </button>`).join("") : '<div class="vazio">Nenhum chamado com esses filtros.</div>';
    entrar("#itens .item-chamado", { delay: escalonar(20), duration: 300 });
  }

  // ---- Gaveta de detalhe ----
  function abrirCamada(el) {
    $("#veu").hidden = false;
    el.hidden = false;
    animar({ targets: "#veu", opacity: [0, 1], duration: 200, easing: "linear" });
    if (!temAnime()) $("#veu").style.opacity = 1;
  }

  function fecharCamadas() {
    const fim = () => { $("#veu").hidden = true; $("#gaveta").hidden = true; $("#modal").hidden = true; aberto = null; };
    if (temAnime()) {
      window.anime({ targets: "#veu", opacity: 0, duration: 180, easing: "linear" });
      if (!$("#gaveta").hidden) window.anime({ targets: "#gaveta", translateX: ["0%", "100%"], duration: 220, easing: "easeInCubic", complete: fim });
      else window.anime({ targets: "#modal", opacity: 0, scale: [1, 0.97], translateX: ["-50%", "-50%"], translateY: ["-50%", "-50%"], duration: 180, easing: "easeInCubic", complete: fim });
    } else fim();
  }

  function abrirGaveta(c) {
    const jaAberta = !$("#gaveta").hidden;
    aberto = c;
    desenharGaveta();
    if (!jaAberta) {
      abrirCamada($("#gaveta"));
      animar({ targets: "#gaveta", translateX: ["100%", "0%"], duration: 320, easing: "easeOutCubic" });
      if (!temAnime()) $("#gaveta").style.transform = "translateX(0)";
      $("#gaveta .fechar").focus();
    }
  }

  function desenharGaveta() {
    const c = aberto;
    if (!c) return;
    const eventos = historico.filter((e) => e.protocolo === c.protocolo).slice().reverse();
    const minimo = R.ultimoDia(c, historico);
    const sugerido = Math.max(minimo, referencia());
    const permitidos = R.TRANSICOES[c.status];
    const espera = referencia() - parseInt(c.dia_abertura, 10);
    const prazo = R.PRAZOS[c.prioridade];
    const situacaoPrazo = c.status === "resolvido"
      ? `resolvido em ${parseInt(c.dia_fechamento, 10) - parseInt(c.dia_abertura, 10)} sol(s), prazo de ${prazo}`
      : `aberto há ${espera} sol(s), prazo de ${prazo}${espera > prazo ? " · fora do prazo" : ""}`;
    $("#gaveta").innerHTML = `
      <button class="fechar" type="button" data-fechar aria-label="Fechar">×</button>
      <span class="mono suave">${esc(c.protocolo)}</span>
      <h2 id="gaveta-titulo">${esc(c.descricao)}</h2>
      <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">${pilula(c.status)} ${etiqueta(c.prioridade)}</div>
      <dl class="campos">
        <dt>Local</dt><dd>${esc(c.bloco)} · ${esc(c.area)}</dd>
        <dt>Categoria</dt><dd>${rot(c.categoria)}</dd>
        <dt>Abertura</dt><dd class="mono">sol ${esc(c.dia_abertura)}</dd>
        <dt>Fechamento</dt><dd class="mono">${c.dia_fechamento ? "sol " + esc(c.dia_fechamento) : "—"}</dd>
        <dt>Prazo</dt><dd>${situacaoPrazo}</dd>
      </dl>
      <div class="secao"><h3>Próximo passo</h3>
        ${permitidos.length ? `
          <div class="duas">
            <label class="campo">Dia (sol ≥ ${minimo})<input id="g-dia" inputmode="numeric" value="${sugerido}"></label>
            <label class="campo">Observação<input id="g-obs" placeholder="opcional"></label>
          </div>
          <div class="acoes">${permitidos.map((s, i) => `<button class="botao${i ? " fantasma" : ""}" type="button" data-para="${s}">${VERBOS[c.status + ">" + s]}</button>`).join("")}</div>
          <ul class="erros" id="g-erros"></ul>`
        : '<p class="suave" style="margin:0">Chamado resolvido: o fluxo foi encerrado.</p>'}
      </div>
      <div class="secao"><h3>Histórico do chamado</h3>
        ${eventos.length ? `<ul class="linha-tempo">${eventos.map((e) => linhaEvento(e, false)).join("")}</ul>`
          : '<p class="suave" style="margin:0">Sem atualizações: aguardando triagem.</p>'}
        <p class="nota">Aberto no sol ${esc(c.dia_abertura)}.</p>
      </div>`;
    $$("#gaveta [data-para]").forEach((b) => b.addEventListener("click", () => mudarStatus(c, b.dataset.para)));
  }

  function mudarStatus(c, novo) {
    const dia = R.diaSimulado($("#g-dia").value);
    const erro = R.checarTransicao(c, novo, dia, historico);
    if (erro) {
      $("#g-erros").innerHTML = `<li>${esc(erro)}</li>`;
      animar({ targets: "#g-erros li", translateX: [-6, 6, 0], duration: 300, easing: "easeOutQuad" });
      return;
    }
    const anterior = c.status;
    R.registrar(c, novo, dia, $("#g-obs").value.trim() || "Status atualizado.", historico, fila);
    aviso(`${c.protocolo}: ${rot(anterior)} → ${rot(novo)} no sol ${dia}.`);
    atualizar();
    desenharGaveta();
    entrar("#gaveta .secao", { delay: escalonar(60) });
  }

  function atenderProximo() {
    if (!fila.length) return;
    const c = fila[0];
    const dia = Math.max(R.ultimoDia(c, historico), referencia());
    R.registrar(c, "em_atendimento", dia, "Chamado assumido na triagem.", historico, fila);
    aviso(`${c.protocolo} em atendimento no sol ${dia}. Restam ${fila.length} na fila.`);
    atualizar();
  }

  // ---- Modal de novo chamado ----
  const novo = { categoria: "", prioridade: "" };
  function prepararModal() {
    $("#op-categoria").innerHTML = R.CATEGORIAS.map((c) => `<button type="button" data-valor="${c}" aria-pressed="false">${rot(c)}</button>`).join("");
    $("#op-prioridade").innerHTML = R.PRIORIDADES.map((p) => `<button type="button" data-valor="${p}" aria-pressed="false">${rot(p)}<small>prazo ${R.PRAZOS[p]} sol</small></button>`).join("");
    [["#op-categoria", "categoria"], ["#op-prioridade", "prioridade"]].forEach(([sel, campo]) => {
      $(sel).addEventListener("click", (ev) => {
        const b = ev.target.closest("button[data-valor]");
        if (!b) return;
        novo[campo] = b.dataset.valor;
        $$(sel + " button").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
      });
    });
    $("#form-novo").addEventListener("submit", (ev) => {
      ev.preventDefault();
      const f = ev.target;
      const registro = {
        protocolo: R.proximoProtocolo(numeros), categoria: novo.categoria, prioridade: novo.prioridade,
        descricao: f.descricao.value.trim(), bloco: f.bloco.value.trim(), area: f.area.value.trim(),
        dia_abertura: f.dia_abertura.value.trim(), status: "aberto", dia_fechamento: "",
      };
      const erros = R.validar(registro);
      if (erros.length) {
        const nomes = { descricao: "descrição", area: "área comum", dia_abertura: "dia de abertura" };
        $("#erros-novo").innerHTML = erros.map((e) => `<li>${esc(e.replace(/\b(descricao|area|dia_abertura)\b/g, (m) => nomes[m]))}</li>`).join("");
        animar({ targets: "#modal", translateX: ["-50%", "-51%", "-49%", "-50%"], translateY: ["-50%", "-50%"], duration: 320, easing: "easeOutQuad" });
        return;
      }
      chamados.push(registro);
      numeros.add(parseInt(registro.protocolo.slice(3), 10));
      porProtocolo[registro.protocolo] = registro;
      fila.push(registro);
      fecharCamadas();
      aviso(`Chamado ${registro.protocolo} registrado · ${fila.length}º na fila de triagem.`);
      atualizar();
    });
  }

  function abrirModal() {
    const f = $("#form-novo");
    f.reset();
    novo.categoria = ""; novo.prioridade = "";
    $$("#modal .opcoes button").forEach((b) => b.setAttribute("aria-pressed", "false"));
    $("#erros-novo").innerHTML = "";
    $("#sel-bloco").innerHTML = R.blocosDisponiveis(chamados).map((b) => `<option>${esc(b)}</option>`).join("");
    if (filtro.bloco) $("#sel-bloco").value = filtro.bloco;
    f.dia_abertura.value = referencia();
    $("#btn-registrar").textContent = `Registrar ${R.proximoProtocolo(numeros)}`;
    abrirCamada($("#modal"));
    animar({ targets: "#modal", opacity: [0, 1], scale: [0.96, 1], translateX: ["-50%", "-50%"], translateY: ["-50%", "-50%"], duration: 260, easing: "easeOutCubic" });
    if (!temAnime()) $("#modal").style.opacity = 1;
    $("#op-categoria button").focus();
  }

  // ---- Filtros e eventos ----
  function alternar(campo, valor) {
    filtro[campo] = filtro[campo] === valor ? "" : valor;
    desenharTudo(false);
  }

  function desenharTudo(completo) {
    desenharChips();
    if (completo !== false) desenharFaixa();
    desenharKpis();
    desenharRosca();
    desenharBarras();
    desenharMatriz();
    desenharFila();
    desenharPilha();
    desenharIndicadores();
    desenharLista();
  }
  const atualizar = () => desenharTudo(true);

  document.addEventListener("click", (ev) => {
    const alvo = ev.target.closest("button, #veu");
    if (!alvo) return;
    if (alvo.id === "veu" || alvo.hasAttribute("data-fechar")) return fecharCamadas();
    if (alvo.closest("#chips-bloco")) { filtro.bloco = alvo.dataset.bloco; filtro.blocoLista = ""; return desenharTudo(false); }
    if (alvo.closest("#legenda")) return alternar("status", alvo.dataset.status);
    if (alvo.closest("#barras")) return alternar("categoria", alvo.dataset.categoria);
    if (alvo.closest("#matriz")) {
      const mesmo = filtro.blocoLista === alvo.dataset.bloco && filtro.status === alvo.dataset.status;
      filtro.blocoLista = mesmo ? "" : alvo.dataset.bloco;
      filtro.status = mesmo ? "" : alvo.dataset.status;
      return desenharTudo(false);
    }
    if (alvo.dataset.limpar) {
      if (alvo.dataset.limpar === "tudo") { filtro.status = ""; filtro.categoria = ""; filtro.blocoLista = ""; } else filtro[alvo.dataset.limpar] = "";
      return desenharTudo(false);
    }
    if (alvo.dataset.protocolo) return abrirGaveta(porProtocolo[alvo.dataset.protocolo]);
  });
  document.addEventListener("keydown", (ev) => { if (ev.key === "Escape" && !$("#veu").hidden) fecharCamadas(); });
  $("#busca").addEventListener("input", (ev) => { filtro.busca = ev.target.value.trim(); desenharLista(); });
  $("#btn-novo").addEventListener("click", abrirModal);
  $("#btn-atender").addEventListener("click", atenderProximo);

  prepararModal();
  atualizar();
  entrar(".topo > *, .faixa, .cartao", { delay: escalonar(40), duration: 450 });
})();
