# Nexcondo · Demonstração da interface web

[Assistir ao vídeo](Nexcondo.mp4) · [Baixar as legendas em português](Nexcondo.srt) · [Ouvir a narração isolada](composicao/public/Narracao.wav)

O filme acompanha o chamado CH-015, da abertura pelo morador ao registro do reparo na garagem do Bloco B. As telas vêm de uma sessão da interface web com os dados simulados do projeto. A composição em Remotion reúne essas capturas, as animações, as legendas abertas, a locução e uma trilha instrumental original.

A voz em português brasileiro foi sintetizada localmente com Piper e o modelo Faber. [Ficha da voz](https://huggingface.co/rhasspy/piper-voices/blob/main/pt/pt_BR/faber/medium/MODEL_CARD)

## Editar ou renderizar novamente

Na pasta `composicao`, execute `npm ci` e `npm run studio` para abrir as cenas no Remotion Studio. Para exportar o MP4, execute `npm run video`. O texto da narração está em `src/roteiro.json` e os tempos usados pelas cenas e legendas estão em `src/tempo.json`.
