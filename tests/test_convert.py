"""Testes do conversor DWG -> PNG.

Rodam fora do Streamlit (modo "bare"): os st.* viram avisos inofensivos.
Precisam do dwg2dxf em bin/ (Linux: bin/dwg2dxf do repo; Windows: bin/dwg2dxf.exe).
"""
import struct
import sys
import zlib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import app  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures"
OUTPUT = Path(__file__).parent / "output"


def png_size(data: bytes):
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "não é PNG"
    width, height = struct.unpack(">II", data[16:24])
    return width, height


# --- inspeção do cabeçalho -------------------------------------------------

def test_header_dwg_2018():
    data = (FIXTURES / "sample_2018.dwg").read_bytes()
    assert app.inspect_header(data) == ("dwg", "2018")


def test_header_dxf_renomeado():
    data = b"  0\r\nSECTION\r\n  2\r\nHEADER\r\n  0\r\nENDSEC\r\n  0\r\nEOF\r\n"
    assert app.inspect_header(data)[0] == "dxf"


def test_header_impostores():
    assert app.inspect_header(b"%PDF-1.7 lixo")[0] == "outro"
    assert app.inspect_header(b"PK\x03\x04" + b"\x00" * 40)[0] == "outro"
    assert app.inspect_header(b"")[0] == "outro"


# --- avisos do LibreDWG ----------------------------------------------------

def test_resumo_de_avisos():
    stderr = (
        "Warning: Unstable Class object 506 MATERIAL (0x481) 67/AF\n"
        "Warning: Unhandled Object TABLESTYLE in out_dxf 101/D1\n"
        "Warning: Unknown object, skipping eed/reactors/xdic\n"
        "Warning: Unknown object, skipping eed/reactors/xdic\n"
        "Warning: Skip CELLSTYLEMAP\n"
        "Warning: Skip TABLEGEOMETRY\n"
        "Warning: Unhandled Object ACAD_TABLE in out_dxf 120/F0\n"
        "Warning: Skip HATCH common handles due to short handle stream\n"
    )
    unknown, classes = app.summarize_libredwg_warnings(stderr)
    assert unknown == 2
    # estilos/materiais não entram; "Skip HATCH common handles" não é perda
    # da hachura; tabela e geometria de tabela entram
    assert classes == ["ACAD_TABLE", "TABLEGEOMETRY"]


# --- reparo do DXF desalinhado ---------------------------------------------

def test_reparo_de_valor_com_quebra_de_linha(tmp_path):
    """Simula o defeito do LibreDWG: um valor de texto com quebra de linha
    no meio desalinha código/valor a partir dali."""
    import ezdxf
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()
    msp.add_line((0, 0), (10, 0))
    msp.add_text("FICM").dxf.insert = (0, 5)
    msp.add_circle((5, 5), 2)
    good = tmp_path / "bom.dxf"
    doc.saveas(good)
    text = good.read_text(encoding="utf-8")
    assert text.count("\nFICM\n") == 1
    broken = tmp_path / "quebrado.dxf"
    broken.write_text(text.replace("\nFICM\n", "\nFICM: Electric\nlixo\n", 1), encoding="utf-8")
    with pytest.raises(Exception):
        ezdxf.readfile(broken)
    fixed, repairs = app.read_dxf_with_repair(broken)
    assert repairs == 1
    assert len(fixed.modelspace()) == 3


# --- página virtual --------------------------------------------------------

def test_pagina_lado_maior_e_piso():
    page, dpi = app.page_for_extents(1000.0, 500.0)
    assert round(page.width_in_mm) == 254
    assert round(page.height_in_mm) == 127
    assert dpi == 400
    page, _ = app.page_for_extents(10000.0, 1.0)
    assert page.height_in_mm >= app.MIN_SIDE_PX / dpi * 25.4 - 0.1


# --- conversão de ponta a ponta -------------------------------------------

@pytest.mark.skipif(app.find_dwg2dxf() is None, reason="dwg2dxf ausente em bin/")
@pytest.mark.parametrize("name", ["sample_2018.dwg", "example_2018.dwg", "Leader_2000.dwg"])
def test_dwg_para_png(name):
    OUTPUT.mkdir(exist_ok=True)
    png, info = app.convert_dwg_to_png(str(FIXTURES / name))
    width, height = png_size(png)
    assert max(width, height) == app.LONG_SIDE_PX
    assert min(width, height) >= app.MIN_SIDE_PX
    assert info["entities"] > 0
    assert info["dwgversion"] in ("2018", "2000")
    (OUTPUT / (Path(name).stem + ".png")).write_bytes(png)


@pytest.mark.skipif(app.find_dwg2dxf() is None, reason="dwg2dxf ausente em bin/")
def test_dxf_renomeado_nao_passa_pelo_libredwg(tmp_path):
    # DXF mínimo válido com uma linha, salvo como .dwg
    import ezdxf
    doc = ezdxf.new("R2010")
    doc.modelspace().add_line((0, 0), (100, 50))
    fake = tmp_path / "renomeado.dwg"
    doc.saveas(fake)
    png, info = app.convert_dwg_to_png(str(fake))
    assert png_size(png)[0] == app.LONG_SIDE_PX
    assert info["dwgversion"] == "DXF renomeado"
    assert info["entities"] == 1


def test_arquivo_que_nao_e_dwg(tmp_path):
    fake = tmp_path / "foto.dwg"
    fake.write_bytes(b"\x89PNG\r\n\x1a\n" + zlib.compress(b"x" * 100))
    with pytest.raises(app.ConversionError):
        app.convert_dwg_to_png(str(fake))


@pytest.mark.skipif(app.find_dwg2dxf() is None, reason="dwg2dxf ausente em bin/")
def test_dwg_corrompido(tmp_path):
    data = bytearray((FIXTURES / "sample_2018.dwg").read_bytes())
    data[64:] = b"\x00" * (len(data) - 64)
    fake = tmp_path / "corrompido.dwg"
    fake.write_bytes(bytes(data))
    with pytest.raises(app.ConversionError):
        app.convert_dwg_to_png(str(fake))
