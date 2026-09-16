"""Render only v3 PDFs and contact sheets for manual visual review.

The JSON records the exact PDF hashes rendered; images remain ignored QA files.
Rendering alone is not evidence that a person has reviewed the pages.
"""
from pathlib import Path
import hashlib,json,subprocess
from PIL import Image,ImageDraw
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'report_v2'
qa=OUT/'qa/v3'
documents=[('thesis/v3/thesis.pdf','thesis_v3'),('article/v3/article.pdf','article_v3')]
records=[]
for name,tag in documents:
    pdf=OUT/name;prefix=qa/f'review_{tag}'
    # Remove only this script's old renders, so a shorter PDF leaves no stale page.
    for old in qa.glob(prefix.name+'-*.png'):old.unlink()
    for old in qa.glob(prefix.name+'_contact_*.png'):old.unlink()
    subprocess.run(['pdftoppm','-scale-to','1600',
                    '-png',str(pdf),str(prefix)],check=True)
    pages=sorted(qa.glob(prefix.name+'-*.png'))
    assert len(pages)==len(PdfReader(pdf).pages)
    for start in range(0,len(pages),8):
        sheet=Image.new('RGB',(1640,1210),'#e5e7eb');draw=ImageDraw.Draw(sheet)
        for j,p in enumerate(pages[start:start+8]):
            im=Image.open(p).convert('RGB');im.thumbnail((395,562))
            x=10+(j%4)*410;y=10+(j//4)*600
            draw.text((x,y),p.name,fill='black');sheet.paste(im,(x,y+22))
        sheet.save(qa/f'{prefix.name}_contact_{start//8+1}.png')
    records.append(dict(pdf=str(pdf.relative_to(ROOT)),pages=len(pages),
                        sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(),
                        render_prefix=str(prefix.relative_to(ROOT))))
    print(tag,len(pages),'pages rendered')
(qa/'rendered_documents.json').write_text(json.dumps(records,indent=2)+'\n')
