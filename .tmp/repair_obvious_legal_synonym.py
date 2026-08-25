from pathlib import Path

root = Path(__file__).resolve().parents[1]
entry = root / "entries/o/obvious.md"
text = entry.read_text(encoding="utf-8")
marker = "\n【反意語】\n\n・nonobvious  \n"
if "・lack an inventive step  \n" not in text:
    block = """
【類義語】

・lack an inventive step  
定義: EPC・英国法を中心に、発明・クレームが必要な inventive step（進歩性）を備えないことを表す。  
頻度: 〈3/10〉  
違い: obvious は、先行技術に照らして当業者にとって容易に想到できるという判断を直接述べる。lack an inventive step は、その判断の法的帰結として「進歩性を欠く」と述べる表現で、文法上の完全な置換語ではない。EPC・英国では同じ判断軸で密接に対応する。  
例: The claim was found to lack an inventive step because the modification was obvious to a person skilled in the art.  
訳: その変更は当業者にとって容易に想到できたため、そのクレームは進歩性を欠くと判断された。  

"""
    if marker not in text:
        raise SystemExit("sense-4 antonym marker not found")
    text = text.replace(marker, "\n" + block + marker.lstrip("\n"), 1)
    entry.write_text(text, encoding="utf-8")
