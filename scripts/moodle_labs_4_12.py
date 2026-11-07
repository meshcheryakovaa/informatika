"""Create eight independent Moodle Book import ZIPs. Requires beautifulsoup4."""
from pathlib import Path
from bs4 import BeautifulSoup
import re,zipfile,html,base64,json
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'src';OUT=ROOT/'moodle'
CONFIG={
4:('099',[(0,'Инструменты форматирования'),(8,'Ввод текста и настройка страницы'),(12,'Форматирование шрифта'),(28,'Форматирование абзацев'),(39,'Рамка, символы и сохранение')]),
5:('100',[(0,'Виды списков'),(3,'Нумерованные списки'),(11,'Маркированные списки'),(16,'Многоуровневые списки')]),
6:('101',[(0,'Инструменты работы с таблицами'),(6,'Создание и изменение таблицы'),(21,'Оформление таблицы'),(29,'Вычисления в таблице'),(36,'Диаграммы по данным таблиц')]),
8:('103',[(0,'Слияние документов'),(5,'Подготовка источника данных'),(9,'Основной документ и подключение данных'),(16,'Поля слияния и просмотр результатов'),(21,'Объединение писем и сохранение')]),
10:('066',[(0,'Блок-схема по образцу'),(5,'Группировка и подпись рисунка'),(7,'Блок-схема квадратного уравнения'),(10,'Организационная диаграмма SmartArt')]),
11:('067',[(0,'Стили и их назначение'),(10,'Исходный документ'),(14,'Создание и применение стилей'),(33,'Оформление документа'),(36,'Сноски'),(41,'Предметный указатель'),(47,'Оглавление и титульный лист')]),
12:('069',[(0,'Задание 1. Приглашение'),(8,'Задание 2. Докладная записка'),(10,'Задание 3. Докладная записка'),(12,'Задание 4. Докладная записка'),(14,'Задание 5. Докладная записка с таблицей'),(16,'Задание 6. Докладная записка с таблицей'),(18,'Задание 7. Табуляция')])}
def source(n):
 soup=BeautifulSoup((SRC/'pages'/f'{n}.html').read_text(),'html.parser')
 return soup.select_one('.page-section')['data-title'],soup.select_one('.page-body')
def clean(content):
 soup=BeautifulSoup(content,'html.parser')
 for t in soup.find_all(True):
  for key in list(t.attrs):
   if key.startswith('data-') or key in ('class','dir'):del t[key]
  if t.name=='img':
   t['style']='max-width:100%;height:auto;';t['alt']=t.get('alt') or 'Иллюстрация к заданию'
  if t.name in ('p','li'):t['style']='white-space:pre-line;'
  if t.name=='aside':t['style']='padding:12px;border-left:3px solid #3572b0;background:#f4f7fb;white-space:pre-line;'
  if t.name=='figure':t['style']='margin:1em 0;'
  if t.name in ('table','td','th'):t['style']='border:1px solid #888;border-collapse:collapse;padding:6px;'
 for a in soup.find_all('a',href=True):
  if a['href']=='#page-068':a['href']='08_source_text.html'
  if a['href']=='assets/11aa35452f830f89a350ab46.bin':a['href']='assets/internet.doc'
 return str(soup)
def wrap(title,body):return '<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>'+html.escape(title)+'</title></head><body><div style="font-family:Arial,sans-serif;line-height:1.6;max-width:1000px;margin:auto;"><h1>'+html.escape(title)+'</h1>'+body+'</div></body></html>'
def asset_file(path):return SRC/('assets/11aa35452f830f89a350ab46.bin' if path=='assets/internet.doc' else path)
books={}
for lab,(n,splits) in CONFIG.items():
 title,body=source(n);blocks=body.find_all(recursive=False);chapters=[]
 for i,(start,name) in enumerate(splits):
  end=splits[i+1][0] if i+1<len(splits) else len(blocks)
  chapters.append((f'{i+1:02}_{lab}_{i+1}.html',name,clean(''.join(map(str,blocks[start:end])))))
 # Preserve every source block in its original order, including image-only tasks.
 assert ''.join(''.join(map(str,blocks[a:(splits[i+1][0] if i+1<len(splits) else len(blocks))])) for i,(a,_) in enumerate(splits))==''.join(map(str,blocks))
 if lab==11:
  _,backup=source('068');chapters.append(('08_source_text.html','Исходный текст: Интернет и его сервисы',clean(str(backup))))
 books[lab]=(title,chapters)
# The LR7 source page has no body. Derive an explicitly identified workbook from LR6.
_,b=source('101');blocks=b.find_all(recursive=False)
def chunk(a,z):return clean(''.join(map(str,blocks[a:z])))
books[7]=('ЛР7. Создание диаграмм',[
 ('01_intro.html','Назначение работы','<p>Освоить создание и оформление диаграмм в Microsoft Word.</p><p><strong>Примечание к источнику.</strong> Страница ЛР7 в предоставленных материалах содержит только заголовок. Эта книга составлена на основе заданий по диаграммам из ЛР6; вводные пояснения добавлены при подготовке.</p><p>Создайте новый документ. Для каждого задания воспроизведите исходную таблицу, затем постройте диаграмму по её данным. Не включайте строку «Итого» в ряд отдельных значений.</p>'),
 ('02_routes.html','Диаграмма автобусных маршрутов','<p>Используйте таблицу маршрутов как образец. Значения количества проданных билетов задайте самостоятельно, если они отсутствуют в образце.</p>'+chunk(28,29)+chunk(36,37)),
 ('03_salary.html','Гистограмма заработной платы',chunk(37,43)),
 ('04_pie.html','Круговая диаграмма',chunk(43,45)+'<p>Если в исходной таблице несколько сотрудников занимают одну должность, предварительно суммируйте их заработную плату по должностям, чтобы каждый сектор соответствовал одной должности.</p>'),
 ('05_check.html','Проверка результата','<p>Проверьте соответствие подписей и чисел исходным таблицам, наличие названий диаграмм и осей гистограммы, читаемость подписей и легенды. Сохраните документ с тремя диаграммами.</p>')])
report=[]
for lab,(title,chapters) in sorted(books.items()):
 dest=OUT/f'lr{lab}';dest.mkdir(parents=True,exist_ok=True)
 assets=set();docs={}
 for name,heading,body in chapters:
  docs[name]=wrap(heading,body)
  for path in re.findall(r'(?:src|href)="(assets/[^"]+)"',body):assets.add(path)
 with zipfile.ZipFile(dest/f'LR{lab}_Moodle_Book.zip','w',zipfile.ZIP_DEFLATED) as z:
  for name,doc in docs.items():z.writestr(name,doc)
  for path in sorted(assets):z.write(asset_file(path),path)
 preview='<h1>'+html.escape(title)+'</h1><ol>'+''.join(f'<li><a href="#c{i}">{html.escape(h)}</a></li>' for i,(_,h,_) in enumerate(chapters))+'</ol>'
 for i,(_,h,body) in enumerate(chapters):
  def embed(m):
   path=m[1];mime='application/msword' if path.endswith('.doc') else ('image/svg+xml' if path.endswith('.svg') else 'image/png')
   return '="data:'+mime+';base64,'+base64.b64encode(asset_file(path).read_bytes()).decode()+'"'
  body=re.sub(r'="(assets/[^"]+)"',embed,body)
  body=body.replace('href="08_source_text.html"','href="#c7"')
  preview+=f'<section id="c{i}"><hr><h2>{html.escape(h)}</h2>{body}</section>'
 (dest/f'LR{lab}_preview.html').write_text(wrap(title,preview))
 note=('ЛР7 создана на основе заданий по диаграммам из ЛР6: в исходной ЛР7 был только заголовок.' if lab==7 else 'Содержимое, задания и иллюстрации перенесены из предоставленного HTML; добавлены названия глав.')
 (dest/'Import.txt').write_text(f'''{title}

1. Добавьте в курс Moodle ресурс «Книга» с названием «{title}».
2. Откройте «Импорт глав» в меню книги. Если требуется, сначала создайте временную главу и удалите её после импорта.
3. Загрузите LR{lab}_Moodle_Book.zip без распаковки.
4. Тип импорта: «Каждый HTML-файл представляет одну главу».
5. Если доступна настройка названий из HTML, включите её. Названия записаны в <title>.
6. Проверьте порядок глав, отображение изображений и ссылки на вложения.

Глав: {len(chapters)}. Файлов-вложений: {len(assets)}.
{note}
В ЛР11 включены internet.doc и запасной исходный текст в отдельной главе.
Файл LR{lab}_preview.html предназначен для просмотра, а не для импорта.
Архив предназначен для импорта глав «Книги», не для восстановления курса .mbz.
Импорт на сервер Moodle не выполнялся.
''')
 with zipfile.ZipFile(dest/f'LR{lab}_Moodle_Book.zip') as z:
  assert z.testzip() is None;names=set(z.namelist())
  for name,doc in docs.items():
   for link in re.findall(r'(?:src|href)="([^"]+)"',doc):
    if not re.match(r'(?:https?:|mailto:|#|data:)',link):assert link in names,(lab,link)
 report.append({'lab':lab,'chapters':len(chapters),'assets':len(assets)})
print(json.dumps(report,ensure_ascii=False))
