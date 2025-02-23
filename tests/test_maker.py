from pathlib import Path

from mirage_tank.maker.extract import extract_it
from mirage_tank.maker.make_classic import make as make_classic
from mirage_tank.maker.make_partial import make as make_partial

THIS_DIR = Path(__file__).parent
SAMPLE_PATH = THIS_DIR / "sample"
OUTPUT_PATH = THIS_DIR / "output"
if not SAMPLE_PATH.exists():
    OUTPUT_PATH.mkdir()
    (OUTPUT_PATH / ".gitignore").write_text("*")

top_img = SAMPLE_PATH / "top.jpg"
bottom_img = SAMPLE_PATH / "bottom.jpg"


def test_make_classic():
    output_img = OUTPUT_PATH / "classic.png"
    make_classic(top_img, bottom_img, output_img)
    assert output_img.exists()
    extract_it(output_img)
    assert (OUTPUT_PATH / "classic_top.jpg").exists()
    assert (OUTPUT_PATH / "classic_bottom.jpg").exists()


def test_make_partial():
    output_img = OUTPUT_PATH / "partial.png"
    make_partial(top_img, output_img)
    assert output_img.exists()
