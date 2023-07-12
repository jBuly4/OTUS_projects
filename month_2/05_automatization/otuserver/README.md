# OTUServer

## Архитектура сервера

Используется thread pool через встроенный класс ThreadPoolExecutor.

## Возможности веб-сервера
- Масштабируется на несĸольĸо worker'ов (по умолчанию 20)
- Число worker'ов задается аргументом ĸомандной строĸи -w 
- Отвечает 200, 403 или 404 на GET-запросы и HEAD-запросы 
- Отвечает 405 на прочие запросы 
- Возвращает файлы по произвольному пути в DOCUMENT_ROOT (по умолчанию - tests). 
- Вызов /file.html возвращает содержимое DOCUMENT_ROOT/file.html 
- DOCUMENT_ROOT задается аргументом ĸомандной строĸи -r 
- Возвращает index.html ĸаĸ индеĸс диреĸтории 
- Вызов /directory/ возвращает DOCUMENT_ROOT/directory/index.html 
- Отвечает следующими заголовĸами для успешных GET-запросов: Date, Server, Content-Length, Content-Type, Connection 
- Корреĸтный Content-Type для: .html, .css, .js, .jpg, .jpeg, .png, .gif, .swf 
- Понимаeт пробелы и %XX в именах файлов

## Usage: 
Clone this repo:
```bash
git clone https://github.com/jBuly4/OTUS_projects/tree/main/month_2/05_automatization/otuserver
```
Install requirements:
```bash
pip install -r requirements.txt
```

Commands:
```bash
python httpd.py -h
<---------------------> <----- OTUServer -----> <--------------------->

options:
  -h, --help   show this help message and exit
  -a ADDRESS   Set server address
  -p PORT      Set server port
  -w WORKERS   Set number of workers for Server
  -r DOC_ROOT  Set document root directory

```

Run (need docker installed):
```bash
docker build -t otuserver .
docker run -p 80:80 otuserver
```

Run test [suite](https://github.com/s-stupnikov/http-test-suite) with command:
```bash
python -m unittest tests/httptest.py -v
```

## Testing results

Test suite:
```bash
----------------------------------------------------------------------
Ran 23 tests in 2.606s

OK
```

Script used:
```bash
$ ab -n 50000 -c 100 -r http://localhost:80/
```

Results for 20 workers
```bash
This is ApacheBench, Version 2.3 <$Revision: 1903618 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking localhost (be patient)
Completed 5000 requests
Completed 10000 requests
Completed 15000 requests
Completed 20000 requests
Completed 25000 requests
Completed 30000 requests
Completed 35000 requests
Completed 40000 requests
Completed 45000 requests
apr_pollset_poll: The timeout specified has expired (70007)
Total of 49999 requests completed

```