"""Fontes do desenho: sem elas o texto quebra onde não devia e embola.

O DWG referencia fontes pelo nome (aqui, Arial). Sem Arial no servidor o
ezdxf cai numa substituta mais larga, o MTEXT quebra numa linha a mais e
as linhas se atropelam — foi o que o dono viu na prancha da torre.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import app  # noqa: E402

PRIVATE = Path(__file__).parent / "fixtures" / "private"
TORRE = PRIVATE / "torre.dwg"


def test_arial_vem_no_repositorio():
    """A coleção de fontes tem de trazer a Arial: é ela que a maioria dos
    desenhos pede e que não existe no servidor."""
    assert (ROOT / "static" / "fonts" / "arial.ttf").is_file()


def test_ezdxf_resolve_arial_para_o_arquivo_do_repositorio():
    from ezdxf.fonts import fonts

    app.prepare_font_environment()
    for pedido in ("Arial", "ARIAL.TTF", "arial.ttf"):
        face = (fonts.get_font_face(pedido) if pedido.lower().endswith(".ttf")
                else fonts.resolve_font_face(pedido))
        assert face.filename.lower() == "arial.ttf", (pedido, face)


@pytest.mark.skipif(not TORRE.exists(), reason="fixture privada ausente")
@pytest.mark.skipif(app.find_dwg2dxf() is None, reason="dwg2dxf ausente em bin/")
def test_torre_linhas_do_bloco_nao_embolam():
    """Prancha real do dono (dados pessoais: fica fora do git). O bloco de
    cinco linhas no alto à esquerda tem de sair como cinco linhas de mesma
    altura. Sem a Arial, a terceira linha quebrava em duas e caía em cima da
    quarta: as duas viravam uma faixa de tinta 50% mais alta que as outras.
    Medido na imagem, que é o que o dono vê."""
    import pymupdf

    png, _info = app.convert_dwg_to_png(str(TORRE))
    pix = pymupdf.Pixmap(png)
    # bloco das cinco linhas, em fração da imagem
    x0, y0 = int(pix.width * 0.17), int(pix.height * 0.13)
    x1, y1 = int(pix.width * 0.40), int(pix.height * 0.23)
    faixas, inicio = [], None
    for y in range(y0, y1):
        tem = any(sum(pix.pixel(x, y)[:3]) < 400 for x in range(x0, x1, 2))
        if tem and inicio is None:
            inicio = y
        elif not tem and inicio is not None:
            faixas.append(y - inicio)
            inicio = None
    if inicio is not None:
        faixas.append(y1 - inicio)

    assert len(faixas) == 5, f"esperava 5 linhas no bloco, achei {len(faixas)}: {faixas}"
    assert max(faixas) <= 1.5 * min(faixas), (
        f"uma faixa bem mais alta que as outras = linhas emboladas: {faixas}")
