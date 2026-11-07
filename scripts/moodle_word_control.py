"""Package the MS Word assessment as a Moodle Book; requires beautifulsoup4."""
from pathlib import Path
from bs4 import BeautifulSoup
import re,html,zipfile,base64,json
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'src';OUT=ROOT/'moodle/word_control';OUT.mkdir(parents=True,exist_ok=True)
pages={}
for i in range(1,65):
 name=f'page-{i:03}';s=BeautifulSoup((SRC/'pages'/f'{i:03}.html').read_text(),'html.parser')
 pages[name]=(s.select_one('.page-section')['data-title'],s.select_one('.page-body'))
variants={int(re.fullmatch(r'Вариант (\d+)',title)[1]):pid for pid,(title,_) in pages.items() if re.fullmatch(r'Вариант (\d+)',title)}
assert set(variants)==set(range(31))
groups=[('00_index.html','Контрольная работа по MS Word',['page-001'])]
for n in range(31):
 pid=variants[n];index=int(pid[5:]);children=[];j=index+1
 while j<=64 and not re.fullmatch(r'Вариант \d+',pages[f'page-{j:03}'][0]):children.append(f'page-{j:03}');j+=1
 groups.append((f'{n+1:02}_variant_{n:02}.html','Вариант 0 — образец оформления' if n==0 else f'Вариант {n}',[pid]+children))
chapter_for={pid:file for file,_,pids in groups for pid in pids}
assert set(chapter_for)==set(pages)
anchors={pid:file for pid,file in chapter_for.items()}
for pid,(_,body) in pages.items():
 for t in body.find_all(id=True):anchors[t['id']]=chapter_for[pid]
def clean(body,current):
 soup=BeautifulSoup(str(body),'html.parser')
 for t in soup.find_all(True):
  for key in list(t.attrs):
   if key.startswith('data-') or key in ('class','dir'):del t[key]
  if t.name in ('p','li'):t['style']='white-space:pre-line;'
  if t.name=='img':t['style']='max-width:100%;height:auto;';t['alt']=t.get('alt') or 'Иллюстрация к контрольной работе'
  if t.name=='figure':t['style']='margin:1em 0;'
  if t.name=='aside':t['style']='padding:12px;background:#f3f6fa;border-left:3px solid #3572b0;white-space:pre-line;'
 for a in soup.find_all('a',href=True):
  link=a['href']
  if link.startswith('#') and link[1:] in anchors:
   target=link[1:];file=anchors[target];a['href']=('' if file==current else file)+'#'+target
 return str(soup)
def wrap(title,body):return '<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>'+html.escape(title)+'</title></head><body><main style="font-family:Arial,sans-serif;line-height:1.6;max-width:1000px;margin:auto;"><h1>'+html.escape(title)+'</h1>'+body+'</main></body></html>'
docs={};assets=set()
for file,title,pids in groups:
 content=''
 if file=='00_index.html':content+='<p>Книга содержит исходный образец оформления (вариант 0) и варианты 1–30. Основные тексты включены в главы вариантов; научные статьи доступны по сохранённым внешним ссылкам. Сначала ознакомьтесь с образцом оформления.</p>'
 for i,pid in enumerate(pids):
  source_title,body=pages[pid]
  content+=f'<section id="{pid}">'
  if i:content+='<h2>'+html.escape(source_title)+('</h2>' if not(pid=='page-004') else ' — второй материал исходного образца</h2>')
  content+=clean(body,file)+'</section>'
 docs[file]=wrap(title,content)
 assets.update(re.findall(r'(?:src|href)="(assets/[^"]+)"',content))
with zipfile.ZipFile(OUT/'MS_Word_Control_Moodle_Book.zip','w',zipfile.ZIP_DEFLATED) as z:
 for file,doc in docs.items():z.writestr(file,doc)
 for asset in sorted(assets):z.write(SRC/asset,asset)
preview='<h1>Контрольная работа по MS Word</h1><ol>'+''.join(f'<li><a href="#chapter-{i}">{html.escape(t)}</a></li>' for i,(_,t,_) in enumerate(groups))+'</ol>'
for i,(file,title,_) in enumerate(groups):
 body=BeautifulSoup(docs[file],'html.parser').main
 body.h1.decompose()
 for a in body.find_all('a',href=True):
  if '.html#' in a['href']:a['href']='#'+a['href'].split('#',1)[1]
  if a['href'].startswith('assets/'):
   path=a['href'];a['href']='data:image/'+('svg+xml' if path.endswith('.svg') else 'png')+';base64,'+base64.b64encode((SRC/path).read_bytes()).decode()
 for img in body.find_all('img'):
  path=img['src'];img['src']='data:image/'+('svg+xml' if path.endswith('.svg') else 'png')+';base64,'+base64.b64encode((SRC/path).read_bytes()).decode()
 preview+=f'<article id="chapter-{i}"><hr><h2>{html.escape(title)}</h2>{body}</article>'
(OUT/'MS_Word_Control_preview.html').write_text(wrap('Контрольная работа по MS Word',preview))
(OUT/'Import.txt').write_text('''Контрольная работа по MS Word — книга Moodle

1. Создайте ресурс «Книга» с названием «Контрольная работа по MS Word».
2. Откройте «Импорт глав». Если Moodle требует первую главу, создайте временную и удалите её после импорта.
3. Загрузите MS_Word_Control_Moodle_Book.zip без распаковки.
4. Выберите «Каждый HTML-файл представляет одну главу». Если доступно получение названий из HTML, включите его (названия записаны в <title>).
5. После импорта проверьте порядок: вводная глава, вариант 0 — образец, варианты 1–30. Всего 32 главы.
6. Проверьте переходы по ссылкам из вводной главы и изображение образца оформления.

Включены все 64 исходные страницы раздела, сгруппированные по вариантам. Тексты материалов помещены непосредственно в главы вариантов. Два исходных текста варианта 0 сохранены оба. Задания, требования к оформлению и ссылки на научные статьи сохранены; добавлены названия глав и вводное пояснение.
Научные статьи не загружались: внешние ссылки требуют доступа в интернет. После импорта проверьте внутрикнижные переходы на вашей версии Moodle; главы доступны также через оглавление самой книги.
ZIP предназначен для импорта глав, не для восстановления курса .mbz и не для банка вопросов Moodle XML.
MS_Word_Control_preview.html — автономный предварительный просмотр (внешние статьи требуют интернета).
Импорт на сервер Moodle не выполнялся.
''')
with zipfile.ZipFile(OUT/'MS_Word_Control_Moodle_Book.zip') as z:
 assert z.testzip() is None;names=set(z.namelist());assert len([n for n in names if n.endswith('.html')])==32
 parsed={name:BeautifulSoup(doc,'html.parser') for name,doc in docs.items()}
 ids={name:{t['id'] for t in soup.find_all(id=True)} for name,soup in parsed.items()}
 for file,soup in parsed.items():
  for t in soup.find_all(['a','img']):
   link=t.get('href') if t.name=='a' else t.get('src')
   if not link or re.match(r'(?:https?:|mailto:|data:)',link):continue
   path,_,anchor=link.partition('#');assert not path or path in names,(file,link)
   if anchor:assert anchor in ids[path or file],(file,link)
print(json.dumps({'chapters':32,'variants':31,'source_pages':len(chapter_for),'assets':len(assets),'zip_bytes':(OUT/'MS_Word_Control_Moodle_Book.zip').stat().st_size}))
