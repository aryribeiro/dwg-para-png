# 📐 Conversor de DWG para PNG

Aplicação web em Python/Streamlit que converte desenhos **DWG (AutoCAD) para PNG**, sem AutoCAD.

## 🎯 O que faz

| Entrada | Saída |
| --- | --- |
| `.dwg` (AutoCAD, R13 a 2018) | **`.png`** (fundo branco, 4000 px no lado maior, cores do desenho) |

Escopo único e fixo — este app não lida com nenhum outro formato de entrada ou saída.

- Interface de tela única (upload → converter → prévia → baixar)
- Renderiza o espaço do modelo: linhas, arcos, polilinhas, hachuras, textos, cotas e blocos
- Mostra a versão do AutoCAD, a contagem de elementos e camadas e **avisa quando a leitura foi parcial**
- Processamento em diretórios temporários — nenhum arquivo é armazenado

## ⚙️ Como converte

1. **GNU LibreDWG** (`bin/dwg2dxf`, binário Linux estático, versão 0.14) lê o DWG e grava um DXF.
2. **ezdxf** interpreta o DXF (cores por camada, blocos, hachuras, textos).
3. **PyMuPDF** rasteriza em PNG na resolução calculada.

Limites honestos do leitor livre: tabelas do AutoCAD (`ACAD_TABLE`), objetos de complementos (Architecture, Civil 3D) e sólidos 3D não são desenhados. Quando isso acontece, a interface avisa em vez de entregar um "sucesso" silencioso. Um DXF renomeado para `.dwg` é detectado e convertido sem passar pelo LibreDWG.

Resiliência incorporada (medida numa varredura de 164 DWG reais, de R13 a 2018):

- **DXF desalinhado**: em DWG com bits corrompidos o LibreDWG grava lixo com quebra de linha dentro de textos, e a saída muda a cada execução. O app conserta o desalinhamento apontado pelo erro e relê, em vez de falhar.
- **Desenho sem imagem**: linhas infinitas (XLINE/RAY), hélices e sólidos 3D não têm imagem 2D; o app explica em vez de estourar.
- **Sem fontes no servidor**: a DejaVu Sans vai no repositório como reserva, então os textos aparecem mesmo num contêiner sem fontes.
- **Concorrência e disco**: no máximo 2 conversões simultâneas e limpeza de pastas temporárias órfãs, como nos apps irmãos.
- **Desenhos pesados** (dezenas de MB de geometria em blocos dinâmicos) podem levar mais de um minuto para rasterizar a 4000 px.

## 🚀 Rodar localmente

Pré-requisitos: Python 3.10+ e o `dwg2dxf` da LibreDWG.

- **Linux/macOS**: o binário Linux já está em `bin/`. No macOS, instale a LibreDWG (`brew install libredwg`) — o app usa o `dwg2dxf` do PATH.
- **Windows**: baixe `libredwg-0.14-win64.zip` em https://github.com/LibreDWG/libredwg/releases e copie `dwg2dxf.exe` para `bin/` (o `.gitignore` já ignora).

```bash
pip install -r requirements.txt
streamlit run app.py
```

Abre em `http://localhost:8501`.

## 🧪 Testes

```bash
pip install pytest
pytest -q
```

Os testes cobrem a detecção de versão e de impostores, o resumo de avisos do LibreDWG, o reparo do DXF desalinhado, o cálculo da resolução e a conversão de ponta a ponta com DWG reais de `tests/fixtures/` (arquivos de teste do próprio projeto LibreDWG). Os PNG gerados ficam em `tests/output/`.

Para provar o ambiente de deploy (Linux sem fontes nem pacotes de sistema):

```bash
docker build -f tests/Dockerfile.smoke -t dwg-smoke . && docker run --rm dwg-smoke
```

Fontes públicas usadas na validação manual: os 141 DWG da suíte da [LibreDWG](https://github.com/LibreDWG/libredwg), os desenhos por versão de [nextgis/dwg_samples](https://github.com/nextgis/dwg_samples) e plantas reais de edifícios publicadas pela [Cal Poly](https://afd.calpoly.edu/facilities/campus-maps/building-floor-plans/autocad/).

## ☁️ Deploy no Streamlit Cloud

1. Faça push para o GitHub
2. Em [share.streamlit.io](https://share.streamlit.io), conecte o repositório
3. Nenhum pacote de sistema é necessário: o `bin/dwg2dxf` é estático e os demais motores vêm do `requirements.txt`
4. Deploy

## 🔁 Reconstruir o binário do LibreDWG

O `bin/dwg2dxf` foi compilado a partir do código-fonte oficial (release 0.14) com o `bin/build/Dockerfile`:

```bash
cd bin/build
docker build -t libredwg-static .
docker create --name tmp libredwg-static && docker cp tmp:/out/dwg2dxf ../dwg2dxf && docker rm tmp
```

## 📋 Estrutura

```
dwg-para-png/
├── app.py              # Aplicação principal
├── requirements.txt    # streamlit, ezdxf, pymupdf
├── bin/
│   ├── dwg2dxf         # LibreDWG 0.14, Linux x86_64 estático
│   └── build/          # Dockerfile que gera o binário + licença da LibreDWG
├── tests/              # pytest + fixtures DWG reais
├── NOTICE.md           # Licenças dos componentes
└── README.md
```

## 🛠️ Tecnologias

- **Streamlit** — interface web
- **GNU LibreDWG** — leitura do DWG
- **ezdxf** — interpretação do DXF e desenho
- **PyMuPDF** — rasterização em PNG

## 🔒 Privacidade

Os arquivos são processados em diretórios temporários e removidos após a conversão. Nada é armazenado permanentemente.

---

Desenvolvido com ❤️ usando Python e Streamlit.
