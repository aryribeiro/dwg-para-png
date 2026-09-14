# NOTICE

O código deste repositório (`app.py`, testes e documentação) é distribuído sob a licença MIT (ver `LICENSE`).

Este projeto redistribui e depende de componentes de terceiros com licenças próprias:

| Componente | Uso | Licença |
| --- | --- | --- |
| **GNU LibreDWG 0.14** (`bin/dwg2dxf`) | binário compilado a partir do código-fonte oficial, sem modificações, executado como processo separado | GPL-3.0-or-later — texto em `bin/build/COPYING-LibreDWG`; código-fonte em https://github.com/LibreDWG/libredwg/releases/tag/0.14; receita de compilação em `bin/build/Dockerfile` |
| **ezdxf** | leitura do DXF e desenho | MIT |
| **PyMuPDF** (MuPDF) | rasterização em PNG | AGPL-3.0 (Artifex). O uso comercial sem disponibilizar o código-fonte exige licença comercial da Artifex |
| **Streamlit** | interface web | Apache-2.0 |
| **DejaVu Sans** (`static/fonts/`) | fonte de reserva para os textos do desenho quando o servidor não tem fontes | Bitstream Vera License + domínio público — texto em `static/fonts/LICENSE_DEJAVU` |

Os arquivos DWG em `tests/fixtures/` vêm da suíte de testes do projeto LibreDWG (`test/test-data/`) e são usados apenas para verificação automatizada.

AutoCAD e DWG são marcas da Autodesk, Inc. Este projeto não é afiliado à Autodesk.
