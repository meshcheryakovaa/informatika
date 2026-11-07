from pathlib import Path
import re,zipfile,html
src=Path(__file__).resolve().parents[1]/'src'
out=src.parent/'moodle/lr9';out.mkdir(parents=True,exist_ok=True)
import tempfile
_temp=tempfile.TemporaryDirectory()
work=Path(_temp.name)
s=(src/'pages/104.html').read_text()
paragraphs=re.findall(r'<p\b[^>]*>(.*?)</p>',s,re.S)
paragraphs=[p for p in paragraphs if p.strip()]
imgs=re.findall(r'<img src="([^"]+)"',s)
assert len(imgs)==20
chapters=[]
def add(filename,title,body):
 # Inline presentation survives Moodle's head/style sanitization.
 doc=f'''<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><title>{html.escape(title)}</title></head>
<body><div style="max-width:960px;margin:auto;line-height:1.6;font-family:Arial,sans-serif;">
<h1>{html.escape(title)}</h1>{body}</div></body></html>'''
 chapters.append((filename,title,body));(work/filename).write_text(doc,encoding='utf-8')
def p(t): return '<p>'+t+'</p>'
add('01_goal.html','ЛР9. Цель работы', '<h2>Оформление документов с математическими формулами</h2>'+p(paragraphs[1])+p('В книге приведены порядок работы в Microsoft Word и 31 вариант формул: 1–15 из исходных материалов, 16–31 — дополнительные учебные варианты.'))
add('02_equations.html','Создание математических формул', ''.join(p(t) for t in paragraphs[3:6])+p(paragraphs[6].replace('например ,','например, <code>x + y = z</code>,'))+p('<small>Пример x + y = z добавлен при подготовке книги: в исходном тексте после слова «например» формула отсутствовала.</small>'))
add('03_editing.html','Редактирование формул и специальные символы', ''.join(p(t) for t in paragraphs[7:]))
groups=[[0],[1],[2],[3,4],[5],[6],[7,8],[9],[10],[11,12],[13],[14,15],[16],[17,18],[19]]
for number,indices in enumerate(groups,1):
 body=p('Воспроизведите формулы своего варианта в Microsoft Word с помощью редактора формул. Изображения ниже служат образцом; вычислять значения выражений не требуется.')
 for part,i in enumerate(indices,1):
  path=imgs[i];alt=f'Вариант {number}: образец формул'+(f', часть {part}' if len(indices)>1 else '')
  body+=f'<figure style="margin:1em 0;"><img src="{path}" alt="{alt}" style="max-width:100%;height:auto;"><figcaption>{alt}</figcaption></figure>'
 body+=p('<small>Формулы приведены в исходном виде. Пояснение о воспроизведении формул добавлено при подготовке книги.</small>')
 add(f'{number+3:02}_variant_{number:02}.html',f'Вариант {number}',body)
# Additional variants are separate from the original source images.
import json
extra=json.loads((out/'variants_16_31.json').read_text(encoding='utf-8'))
def asset_path(path):
 return (out/path) if path.startswith('generated/') else (src/path)
for number,formulas in extra.items():
 path=f'generated/variant_{number}.png'
 imgs.append(path)
 body=p('Воспроизведите все три формулы в Microsoft Word с помощью редактора формул. Сохраните структуру дробей, индексы, степени, пределы интегрирования и суммирования. Вычислять значения выражений не требуется.')
 body+=f'<figure style="margin:1em 0;"><img src="{path}" alt="Вариант {number}: три формулы для воспроизведения" style="max-width:100%;height:auto;"><figcaption>Вариант {number}. Образец оформления формул.</figcaption></figure>'
 body+=p('<small>Дополнительный учебный вариант, подготовленный для ЛР9. Варианты 1–15 сохранены из исходных материалов.</small>')
 add(f'{int(number)+3:02}_variant_{int(number):02}.html',f'Вариант {number}',body)
with zipfile.ZipFile(out/'LR9_Moodle_Book.zip','w',zipfile.ZIP_DEFLATED) as z:
 for filename,_,_ in chapters:z.write(work/filename,filename)
 for path in imgs:z.write(asset_path(path),path)
with zipfile.ZipFile(out/'LR9_Variants_16-31.zip','w',zipfile.ZIP_DEFLATED) as z:
 for filename,_,_ in chapters[18:]:z.write(work/filename,filename)
 for path in imgs[20:]:z.write(asset_path(path),path)
preview='<html lang="ru"><head><meta charset="utf-8"><title>ЛР9 — книга Moodle</title></head><body style="font-family:Arial,sans-serif;max-width:960px;margin:32px auto;padding:0 18px;line-height:1.6"><h1>ЛР9. Оформление документов с математическими формулами</h1><h2>Оглавление</h2><ol>'
for i,(_,title,_) in enumerate(chapters):preview+=f'<li><a href="#chapter-{i}">{title}</a></li>'
preview+='</ol>'
import base64
for i,(_,title,body) in enumerate(chapters):
 body=re.sub(r'src="((?:assets|generated)/[^"]+)"',lambda m:'src="data:image/png;base64,'+base64.b64encode(asset_path(m[1]).read_bytes()).decode()+'"',body)
 preview+=f'<section id="chapter-{i}"><hr><h2>{title}</h2>{body}</section>'
preview+='</body></html>'
(out/'LR9_preview.html').write_text(preview,encoding='utf-8')
(out/'LR9_Import.txt').write_text('''ЛР9. Оформление документов с математическими формулами

Импорт в Moodle
1. Включите режим редактирования курса.
2. Добавьте ресурс «Книга».
3. Название: «ЛР9. Оформление документов с математическими формулами».
4. Сохраните и откройте книгу. Если Moodle требует первую главу, создайте временную главу «Временная».
5. В меню книги «Ещё» или в блоке «Управление» выберите «Импорт глав» (расположение зависит от версии и темы Moodle).
6. Загрузите LR9_Moodle_Book.zip. Тип импорта: «Каждый HTML-файл представляет одну главу».
7. Выполните импорт. При наличии настройки получения названий из HTML включите её: названия записаны в <title> каждого файла.
8. Если создавали временную главу, удалите её.
9. Проверьте порядок: цель → создание формул → редактирование → варианты 1–31. В книге должно быть 34 главы.
10. Откройте несколько вариантов и убедитесь, что изображения отображаются.

ZIP не нужно распаковывать перед загрузкой. Это архив для «Импорта глав», не резервная копия курса .mbz и не Moodle XML для банка вопросов.

Состав: 34 HTML-главы, 20 исходных изображений и 16 новых изображений (48 формул). Варианты 4, 7, 10, 12 и 14 объединяют соседние изображения одного варианта. Исходные формулы не перерисованы и не изменены.
Варианты 16–31 — дополнительные учебные варианты. Исходный код формул записан в variants_16_31.json; изображения можно пересоздать командой python scripts/render_lr9_variants.py (нужна библиотека matplotlib).

Если книга с вариантами 1–15 уже импортирована, загрузите LR9_Variants_16-31.zip через «Импорт глав»: он содержит только 16 новых глав и добавит их в конец существующей книги. Полный архив повторно импортировать не нужно.

Источник: предоставленный informatika_all_in_one.html, страница ЛР9.

При подготовке добавлены вступление, краткое пояснение к вариантам и простой пример x + y = z вместо пропущенного примера в исходнике. Сроки сдачи, оценивание и номер назначенного варианта не устанавливались.

LR9_preview.html — автономный файл для предварительного просмотра всей книги; импортировать в Moodle следует ZIP, а не этот файл.

Импорт непосредственно на вашем сервере Moodle не выполнялся: подключение к Moodle в этой сессии отсутствует.
''',encoding='utf-8')
with zipfile.ZipFile(out/'LR9_Moodle_Book.zip') as z:
 assert z.testzip() is None
 names=set(z.namelist())
 assert len([n for n in names if n.endswith('.html')])==34
 for filename,_,_ in chapters:
  text=z.read(filename).decode()
  for path in re.findall(r'src="([^"]+)"',text):assert path in names
print('Validated: 34 chapters, 36 images; ZIP relative references resolve')
print([(p.name,p.stat().st_size) for p in out.iterdir()])
