from pathlib import Path
import json,unicodedata
r=Path(__file__).resolve().parents[2];out=r/'report_v2/references'
text=(r/'activity_report/references/references.bib').read_text()
def clean(s):
 return unicodedata.normalize('NFKD',s.replace('‐','-').replace('–','--')).encode('ascii','ignore').decode()
for key in ['atha2018','spencer2019','roberts2017','kapoor2023']:
 m=json.loads((out/(key+'_metadata.json')).read_text())['message']
 authors=' and '.join(clean(a['family']+', '+a.get('given','')) for a in m['author'])
 year='2018' if key=='atha2018' else str(m['published']['date-parts'][0][0])
 fields={'author':authors,'title':clean(m['title'][0]),'journal':m['container-title'][0],'year':year,'volume':m.get('volume',''),'number':m.get('issue',''),'pages':m.get('page','').replace('-','--'),'doi':m['DOI']}
 text+='\n@article{'+key+',\n'+',\n'.join('  '+k+' = {'+v+'}' for k,v in fields.items() if v)+'\n}\n'
text+=r'''
@article{cawley2010,
 author={Cawley, Gavin C. and Talbot, Nicola L. C.},
 title={On Over-fitting in Model Selection and Subsequent Selection Bias in Performance Evaluation},
 journal={Journal of Machine Learning Research}, volume={11}, pages={2079--2107}, year={2010},
 url={https://www.jmlr.org/papers/v11/cawley10a.html}
}
@inproceedings{he2016,
 author={He, Kaiming and Zhang, Xiangyu and Ren, Shaoqing and Sun, Jian},
 title={Deep Residual Learning for Image Recognition},
 booktitle={Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition},
 pages={770--778}, year={2016},
 url={https://www.cv-foundation.org/openaccess/content_cvpr_2016/html/He_Deep_Residual_Learning_CVPR_2016_paper.html}
}
'''
(out/'references.bib').write_text(text)
