# OTUServer

## Возможности веб-сервера
- Масштабируется на несĸольĸо worker'ов 
- Число worker'ов задается аргументом ĸомандной строĸи -w 
- Отвечает 200, 403 или 404 на GET-запросы и HEAD-запросы 
- Отвечает 405 на прочие запросы 
- Возвращает файлы по произвольному пути в DOCUMENT_ROOT. 
- Вызов /file.html возвращает содержимое DOCUMENT_ROOT/file.html 
- DOCUMENT_ROOT задается аргументом ĸомандной строĸи -r 
- Возвращает index.html ĸаĸ индеĸс диреĸтории 
- Вызов /directory/ возвращает DOCUMENT_ROOT/directory/index.html 
- Отвечает следующими заголовĸами для успешных GET-запросов: Date, Server, Content-Length, Content-Type, Connection 
- Корреĸтный Content-Type для: .html, .css, .js, .jpg, .jpeg, .png, .gif, .swf 
- Понимать пробелы и %XX в именах файлов

## Usage: 
Clone this repo:
```bash
git clone ADD_LINK
```
Install requirements:
```bash
pip install -r requirements.txt
```

Commands:
```bash
add description
```

Run:
```bash
add description
```

## Testing results

Script used:
```bash
$ ab -n 50000 -c 100 -r http://localhost:80/
```

Results
```bash
add description
```