// Interface web do help desk. Toda regra vem de regras.js; aqui só há tela.
(function () {
  "use strict";
  const R = window.Regras;
  const $ = (seletor) => document.querySelector(seletor);
  const reduzido = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // anime.js é só enfeite: sem ele (offline) ou com movimento reduzido, nada quebra.
  function animar(opcoes) {
    if (window.anime && !reduzido) return window.anime(opcoes);
    const alvos = typeof opcoes.targets === "string"
      ? document.querySelectorAll(opcoes.targets) : [].concat(opcoes.targets || []);
    alvos.forEach((el) => {
      if (!el || !el.style) return;
      if (opcoes.opacity) el.style.opacity = [].concat(opcoes.opacity).pop();
      if (opcoes.width) el.style.width = [].concat(opcoes.width).pop();
      if (opcoes.translateY !== undefined) el.style.transform = "none";
    });
    if (opcoes.update) opcoes.update({ progress: 100 });
    return null;
  }
  const escala = (n) => (window.anime && !reduzido ? window.anime.stagger(n) : 0);

  function esc(texto) {
    return String(texto).replace(/[&<>"']/g, (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
  }
  const rotulo = (v) => R.ROTULOS[v] || v;
  const pilula = (s) => `<span class="status s-${s}">${rotulo(s)}</span>`;
  const prioridade = (p) => (p === "urgente" ? '<span class="urgente">Urgente</span>' : rotulo(p));

  // ---- Estado: as mesmas estruturas do Python ----
  const carga = R.carregar(window.DADOS_CHAMADOS);
  const chamados = carga.chamados;                         // lista
  const numeros = carga.numeros;                           // protocolos reservados
  const porProtocolo = {};                                 // dicionário
  chamados.forEach((c) => { porProtocolo[c.protocolo] = c; });
  const fila = R.montarFila(chamados);                     // fila (FIFO)
  const historico = window.DADOS_HISTORICO.map((e) => Object.assign({}, e)); // pilha
  let selecionado = null;
  let historicoCompleto = false;

  function aviso(mensagem, tipo) {
    const el = $("#aviso-vivo");
    el.textContent = mensagem;
    el.className = tipo === "erro" ? "erro" : "";
    if (window.anime) window.anime.remove(el);
    animar({ targets: el, opacity: [0, 1], translateY: [12, 0], duration: 300, easing: "easeOutCubic",
      complete: () => animar({ targets: el, opacity: 0, delay: 3200, duration: 400, easing: "linear" }) });
    if (!window.anime || reduzido) setTimeout(() => { el.style.opacity = 0; }, 3600);
  }

  function opcoes(select, valores, primeiro) {
    select.innerHTML = (primeiro ? `<option value="">${primeiro}</option>` : "") +
      valores.map((v) => `<option value="${esc(v)}">${esc(rotulo(v))}</option>`).join("");
  }

  // ---- Topo ----
  function contarAte(el, valor, sufixo) {
    const alvo = { n: Number(el.dataset.valor || 0) };
    el.dataset.valor = valor;
    const decimais = Number.isInteger(valor) ? 0 : 1;
    animar({ targets: alvo, n: valor, duration: 700, easing: "easeOutExpo", round: decimais ? 10 : 1,
      update: () => { el.textContent = (decimais ? alvo.n.toFixed(1).replace(".", ",") : Math.round(alvo.n)) + (sufixo || ""); } });
    if (!window.anime || reduzido) el.textContent = (decimais ? valor.toFixed(1).replace(".", ",") : valor) + (sufixo || "");
  }

  function desenharTopo() {
    const ind = R.calcularIndicadores(chamados, historico);
    $("#sol").textContent = `Sol ${ind.referencia}`;
    const itens = [["validos", "Chamados válidos", ind.total], ["pendentes", "Pendentes", ind.pendentes],
      ["fila", "Na fila de triagem", fila.length], ["taxa", "Resolvidos", ind.taxaResolucao, "%"],
      ["atrasados", "Fora do prazo", ind.atrasados.length]];
    const kpis = $("#kpis");
    if (!kpis.children.length) {
      kpis.innerHTML = itens.map(([id, nome]) => `<div class="kpi"><b id="k-${id}">0</b><span>${nome}</span></div>`).join("");
      animar({ targets: "#kpis .kpi", opacity: [0, 1], translateY: [10, 0], delay: escala(60), duration: 500, easing: "easeOutCubic" });
    }
    itens.forEach(([id, , valor, sufixo]) => contarAte($("#k-" + id), valor, sufixo));
    $("#cont-fila").textContent = fila.length;
  }

  // ---- Chamados ----
  function desenharLista() {
    const protocolo = $("#f-protocolo").value.trim().toUpperCase();
    const categoria = $("#f-categoria").value;
    const status = $("#f-status").value;
    const filtrados = chamados.filter((c) =>
      (!protocolo || c.protocolo.includes(protocolo)) &&
      (!categoria || c.categoria === categoria) && (!status || c.status === status));
    $("#lista").innerHTML = filtrados.map((c) => `
      <tr class="clicavel" tabindex="0" data-protocolo="${esc(c.protocolo)}"${selecionado === c ? ' aria-current="true" style="background:var(--painel-2)"' : ""}>
        <td class="mono">${esc(c.protocolo)}</td><td>${rotulo(c.categoria)}</td><td>${prioridade(c.prioridade)}</td>
        <td>${esc(c.bloco)} / ${esc(c.area)}</td><td class="num">${esc(c.dia_abertura)}</td><td>${pilula(c.status)}</td>
      </tr>`).join("");
    $("#lista-vazia").hidden = filtrados.length > 0;
    animar({ targets: "#lista tr", opacity: [0, 1], delay: escala(18), duration: 300, easing: "linear" });
  }

  function desenharDetalhe() {
    const c = selecionado;
    const caixa = $("#detalhe");
    if (!c) return;
    const eventos = historico.filter((e) => e.protocolo === c.protocolo).slice().reverse();
    const permitidos = R.TRANSICOES[c.status];
    const minimo = R.ultimoDia(c, historico);
    caixa.innerHTML = `
      <h2>${esc(c.protocolo)}</h2>
      <dl class="campos">
        <dt>Status</dt><dd>${pilula(c.status)}</dd>
        <dt>Categoria</dt><dd>${rotulo(c.categoria)}</dd>
        <dt>Prioridade</dt><dd>${prioridade(c.prioridade)} · prazo de ${R.PRAZOS[c.prioridade]} sol(s)</dd>
        <dt>Local</dt><dd>${esc(c.bloco)} / ${esc(c.area)}</dd>
        <dt>Descrição</dt><dd>${esc(c.descricao)}</dd>
        <dt>Abertura</dt><dd class="mono">sol ${esc(c.dia_abertura)}</dd>
        <dt>Fechamento</dt><dd class="mono">${c.dia_fechamento ? "sol " + esc(c.dia_fechamento) : "—"}</dd>
      </dl>
      <h3>Histórico do chamado</h3>
      ${eventos.length ? `<ul class="linha-tempo">${eventos.map((e, i) => linhaEvento(e, i, false)).join("")}</ul>`
        : '<p class="dica">Ainda sem atualizações: o chamado está aguardando triagem.</p>'}
      <h3>Atualizar status</h3>
      ${permitidos.length ? `
        <form id="form-status" class="grade-form" novalidate>
          <label>Novo status<select name="novo">${permitidos.map((s) => `<option value="${s}">${rotulo(s)}</option>`).join("")}</select></label>
          <label>Dia (a partir do sol ${minimo})<input name="dia" inputmode="numeric" value="${minimo}"></label>
          <label class="largo">Observação<input name="observacao" placeholder="Status atualizado."></label>
          <p class="largo" style="margin:0"><button class="botao" type="submit">Registrar mudança</button></p>
        </form><ul class="erros" id="erros-status"></ul>`
        : '<p class="dica">Chamado resolvido: o fluxo foi encerrado.</p>'}`;
    animar({ targets: caixa.children, opacity: [0, 1], translateY: [6, 0], delay: escala(30), duration: 350, easing: "easeOutCubic" });
    const form = $("#form-status");
    if (form) form.addEventListener("submit", (ev) => {
      ev.preventDefault();
      const dados = new FormData(form);
      const novo = dados.get("novo");
      const dia = R.diaSimulado(String(dados.get("dia")));
      const erro = R.checarTransicao(c, novo, dia, historico);
      if (erro) { $("#erros-status").innerHTML = `<li>${esc(erro)}</li>`; return; }
      const anterior = c.status;
      R.registrar(c, novo, dia, String(dados.get("observacao")).trim() || "Status atualizado.", historico, fila);
      aviso(`${c.protocolo}: ${rotulo(anterior)} → ${rotulo(novo)} registrado no histórico.`);
      atualizarTudo();
    });
  }

  function linhaEvento(e, indice, topo) {
    return `<li><span class="quando">sol ${esc(e.dia_evento)} · ${esc(e.protocolo)}</span>${topo && indice === 0 ? '<span class="topo">topo</span>' : ""}<br>
      ${pilula(e.status_anterior)} → ${pilula(e.status_novo)} <span class="dica">${esc(e.observacao)}</span></li>`;
  }

  // ---- Abrir ----
  function prepararFormulario() {
    const form = $("#form-abrir");
    opcoes(form.categoria, R.CATEGORIAS, "Selecione…");
    opcoes(form.prioridade, R.PRIORIDADES, "Selecione…");
    $("#lista-blocos").innerHTML = R.blocosDisponiveis(chamados).map((b) => `<option value="${esc(b)}">`).join("");
    form.addEventListener("submit", (ev) => {
      ev.preventDefault();
      const dados = Object.fromEntries(new FormData(form));
      const novo = Object.assign({}, dados, {
        protocolo: R.proximoProtocolo(numeros), status: "aberto", dia_fechamento: "",
      });
      Object.keys(novo).forEach((k) => { novo[k] = String(novo[k]).trim(); });
      const erros = R.validar(novo);
      if (erros.length) {
        $("#erros-abrir").innerHTML = erros.map((e) => `<li>${esc(e)}</li>`).join("");
        animar({ targets: "#erros-abrir li", translateX: [-6, 0], duration: 300, easing: "easeOutElastic(1, .6)" });
        return;
      }
      $("#erros-abrir").innerHTML = "";
      chamados.push(novo);
      numeros.add(parseInt(novo.protocolo.slice(3), 10));
      porProtocolo[novo.protocolo] = novo;
      fila.push(novo);
      form.reset();
      aviso(`Chamado registrado. Protocolo ${novo.protocolo}, ${fila.length}º na fila de triagem.`);
      atualizarTudo();
    });
  }

  // ---- Fila ----
  function desenharFila() {
    $("#fila").innerHTML = fila.length ? fila.map((c, i) => `
      <li><span class="pos">${i + 1}º</span>
        <span><span class="mono">${esc(c.protocolo)}</span> · ${esc(c.descricao)}<br>
          <span class="dica">${esc(c.bloco)} / ${esc(c.area)} · aberto no sol ${esc(c.dia_abertura)}</span></span>
        <span>${prioridade(c.prioridade)}</span></li>`).join("")
      : '<li><span></span><span class="dica">Não há chamados na fila de triagem.</span><span></span></li>';
    $("#btn-atender").disabled = !fila.length;
    const campo = $("#form-fila").dia;
    if (fila.length) campo.placeholder = `a partir do sol ${R.ultimoDia(fila[0], historico)}`;
    animar({ targets: "#fila li", opacity: [0, 1], translateX: [-8, 0], delay: escala(40), duration: 300, easing: "easeOutCubic" });
  }

  $("#form-fila").addEventListener("submit", (ev) => {
    ev.preventDefault();
    if (!fila.length) return;
    const primeiro = fila[0];
    const dia = R.diaSimulado($("#form-fila").dia.value);
    const erro = R.checarTransicao(primeiro, "em_atendimento", dia, historico);
    if (erro) { $("#erros-fila").innerHTML = `<li>${esc(erro)}</li>`; return; }
    $("#erros-fila").innerHTML = "";
    R.registrar(primeiro, "em_atendimento", dia, "Chamado assumido na triagem.", historico, fila);
    $("#form-fila").reset();
    aviso(`${primeiro.protocolo} agora está em atendimento. Restam ${fila.length} na fila.`);
    atualizarTudo();
  });

  // ---- Histórico ----
  function desenharHistorico() {
    const eventos = historicoCompleto ? historico.slice().reverse() : R.ultimosEventos(historico, 5);
    $("#historico").innerHTML = eventos.map((e, i) => linhaEvento(e, i, true)).join("");
    $("#btn-historico").textContent = historicoCompleto ? "Mostrar só as 5 últimas" : `Mostrar todos (${historico.length})`;
    animar({ targets: "#historico li", opacity: [0, 1], delay: escala(35), duration: 300, easing: "linear" });
  }
  $("#btn-historico").addEventListener("click", () => { historicoCompleto = !historicoCompleto; desenharHistorico(); });

  // ---- Painel ----
  function barras(contagem, total, chaveCor) {
    const maior = Math.max(1, ...Object.values(contagem));
    return Object.keys(contagem).map((k) => `
      <div class="barra"><span>${rotulo(k)}</span>
        <div class="trilho"><div class="preenchido" data-largura="${contagem[k] * 100 / maior}"
          style="${chaveCor ? `background:var(--${k})` : ""}"></div></div>
        <span class="valor">${contagem[k]} · ${R.formatar(R.percentual(contagem[k], total))}%</span></div>`).join("");
  }

  function tabelaMatriz(linhas, m, rotuloLinha) {
    const totaisColuna = R.STATUS.map((_, j) => m.reduce((s, linha) => s + linha[j], 0));
    return `<table><thead><tr><th></th>${R.STATUS.map((s) => `<th class="num">${rotulo(s)}</th>`).join("")}<th class="num">Total</th></tr></thead>
      <tbody>${linhas.map((l, i) => `<tr><td>${rotuloLinha(l)}</td>${m[i].map((v) => `<td class="num">${v}</td>`).join("")}
        <td class="num">${m[i].reduce((a, b) => a + b, 0)}</td></tr>`).join("")}
      <tr><th>Total</th>${totaisColuna.map((v) => `<th class="num">${v}</th>`).join("")}<th class="num">${totaisColuna.reduce((a, b) => a + b, 0)}</th></tr></tbody></table>`;
  }

  function desenharPainel() {
    const bloco = $("#p-bloco").value;
    const base = bloco ? chamados.filter((c) => R.nomeBloco(c) === bloco) : chamados;
    const ref = R.diaReferencia(chamados, historico); // "hoje" é o mesmo para todos os blocos
    const ind = R.calcularIndicadores(base, historico, ref);
    $("#p-status").innerHTML = barras(R.contarPor(base, "status", R.STATUS), base.length, true);
    $("#p-categoria").innerHTML = barras(R.contarPor(base, "categoria", R.CATEGORIAS), base.length, false);
    const media = (v) => (v === null ? "—" : R.formatar(v));
    const cards = [
      ["Taxa de resolução", `${R.formatar(ind.taxaResolucao)}%`, `${ind.resolvidos} resolvidos ÷ ${ind.total} × 100`],
      ["Tempo médio de resolução", `${media(ind.tempoMedio)} sol(s)`, `soma(fechamento − abertura) ÷ resolvidos = ${ind.somaResolucao} ÷ ${ind.resolvidos}`],
      ["Resolvidos no prazo", `${ind.resolvidosNoPrazo} de ${ind.resolvidos}`, "resolução ≤ prazo da prioridade"],
      ["Espera média das pendências", `${media(ind.esperaMedia)} sol(s)`, `soma(sol ${ind.referencia} − abertura) ÷ pendentes = ${ind.somaEspera} ÷ ${ind.pendentes}`],
      ["Pendências fora do prazo", `${ind.atrasados.length} de ${ind.pendentes}`, `${ind.criticosAtrasados} urgentes ou altas · espera > prazo`],
    ];
    $("#p-indicadores").innerHTML = cards.map(([nome, valor, formula]) =>
      `<div class="indicador"><span class="dica">${nome}</span><b>${valor}</b><span class="formula">${esc(formula)}</span></div>`).join("");
    $("#p-matriz-cat").innerHTML = tabelaMatriz(R.CATEGORIAS, R.matriz(base, R.CATEGORIAS, (c) => c.categoria), rotulo);
    const blocos = R.blocosDisponiveis(chamados);
    $("#cartao-matriz-bloco").hidden = Boolean(bloco);
    $("#p-matriz-bloco").innerHTML = tabelaMatriz(blocos, R.matriz(chamados, blocos, R.nomeBloco), (b) => b);
    const arvore = R.montarHierarquia(base);
    $("#p-hierarquia").innerHTML = Object.keys(arvore).map((b) => {
      const cats = arvore[b];
      const total = Object.values(cats).reduce((s, l) => s + l.length, 0);
      return `<details class="arvore" open><summary>${esc(b)} (${total})</summary>${Object.keys(cats).map((c) =>
        `<details open><summary>${rotulo(c)} (${cats[c].length})</summary><ul>${cats[c].map((ch) =>
          `<li><span class="mono">${esc(ch.protocolo)}</span> · ${esc(ch.area)} · ${pilula(ch.status)} · ${prioridade(ch.prioridade)}</li>`).join("")}</ul></details>`).join("")}</details>`;
    }).join("") || '<p class="dica">Sem chamados.</p>';
    $("#p-conclusao").innerHTML = R.gerarConclusao(base, ind).map((f) => `<li>${esc(f)}</li>`).join("");
    animar({ targets: "#aba-painel .preenchido", width: (el) => el.dataset.largura + "%", delay: escala(40), duration: 800, easing: "easeOutCubic" });
    if (!window.anime || reduzido) document.querySelectorAll("#aba-painel .preenchido").forEach((el) => { el.style.width = el.dataset.largura + "%"; });
  }

  // ---- Navegação ----
  function mostrarAba(nome) {
    document.querySelectorAll("nav button").forEach((b) => b.setAttribute("aria-selected", String(b.dataset.aba === nome)));
    document.querySelectorAll("main > section").forEach((s) => { s.hidden = s.id !== "aba-" + nome; });
    if (nome === "painel") desenharPainel();
    if (nome === "fila") desenharFila();
    if (nome === "historico") desenharHistorico();
    animar({ targets: `#aba-${nome} .cartao`, opacity: [0, 1], translateY: [8, 0], delay: escala(50), duration: 350, easing: "easeOutCubic" });
  }
  document.querySelectorAll("nav button").forEach((b) => b.addEventListener("click", () => mostrarAba(b.dataset.aba)));

  function atualizarTudo() {
    desenharTopo();
    desenharLista();
    if (selecionado) desenharDetalhe();
    desenharFila();
    desenharHistorico();
    if (!$("#aba-painel").hidden) desenharPainel();
    $("#proximo-protocolo").textContent = `Próximo protocolo: ${R.proximoProtocolo(numeros)}`;
  }

  // ---- Início ----
  opcoes($("#f-categoria"), R.CATEGORIAS, "Todas");
  opcoes($("#f-status"), R.STATUS, "Todos");
  ["#f-protocolo", "#f-categoria", "#f-status"].forEach((s) => $(s).addEventListener("input", desenharLista));
  $("#lista").addEventListener("click", (ev) => {
    const linha = ev.target.closest("tr[data-protocolo]");
    if (!linha) return;
    selecionado = porProtocolo[linha.dataset.protocolo];
    desenharLista();
    desenharDetalhe();
  });
  $("#lista").addEventListener("keydown", (ev) => {
    if ((ev.key === "Enter" || ev.key === " ") && ev.target.matches("tr[data-protocolo]")) { ev.preventDefault(); ev.target.click(); }
  });
  const pBloco = $("#p-bloco");
  pBloco.innerHTML = '<option value="">Condomínio inteiro</option>' +
    R.blocosDisponiveis(chamados).map((b) => `<option>${esc(b)}</option>`).join("");
  pBloco.addEventListener("change", desenharPainel);
  if (carga.avisos.length) {
    $("#avisos-carga").innerHTML = carga.avisos.map((a) =>
      `<div class="alerta"><b>Validação na carga:</b> ${esc(a)}. O registro fica fora da lista, mas o protocolo continua reservado.</div>`).join("");
  }
  prepararFormulario();
  atualizarTudo();
  animar({ targets: "header .marca > *", opacity: [0, 1], translateY: [-8, 0], delay: escala(80), duration: 600, easing: "easeOutCubic" });
})();
