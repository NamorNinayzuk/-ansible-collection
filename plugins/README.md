# Modules

## file_content

Этот модуль создает файл с доставленным содержимым или считывает содержимое из существующего файла на хосте.

### Available options:

- **path** [str] - Путь к файлу. Обязателен.
- **content** [str] - Содержимое файла. Необязательный. По умолчанию используется пустая строка.

### Returned values:

- **path** - Путь к файлу
- **content** - Содержимое файла. Может быть прочитан из файла или записан в него.
- **status** [str] - Статус работы. Может быть одним из следующих:
  - **created**: файл был создан, и содержимое было сохранено в файл
  - **modified**: файл существовал, и его содержимое перезаписано (параметр содержимого не пуст)
  - **readed**:  файл существовал, и его содержимое было прочитано (опция содержимого опущена)
  - **resisted**: файл существовал, и его содержимое равно переданному
  - **denied**: модулю не удалось получить доступ к файлу - ошибка
- **uid** - Идентификатор пользователя владельца файла
- **gid** - Идентификатор группы владельцев файлов
- **owner** - Имя владельца файла
- **group** - Имя группы владельцев файлов
- **mode** - Права доступа к файлам
- **state** -  Состояние файла: файл или каталог
- **size** - Размер файла

---

## yc_vpc

Этот модуль позволяет управлять ресурсами виртуального частного облака Яндекса через пользовательский интерфейс Yandex Cloud CLI.

Требуется установить и настроить [Yandex Cloud CLI](https://cloud.yandex.ru/docs/cli/quickstart)

### Available options:

- **net** [str] - Название сети. Обязателен.
- **subnet** [str] - Название подсети. Обязателен.
- **ip_range** [str] - Пространство IP-адресов, выделенное подсети в обозначении CIDR. Необязательный. Значение по умолчанию `10.2.0.0/16`
- **state** [str] - Состояние подсети/сети. Должно быть `exists` или `absent`. Необязательный. Значение по умолчанию - `exists`

### Returned values:

- **version** [str] - Версия Yandex.Cloud CLI. Возвращался всегда.
- **net_config** [str] - Настройка сети из Облака Яндекса. Возвращает, если сеть существует или создана
- **subnet_config** [str] -  Конфигурация подсети из сети Облака Яндекса. Возвращает, существует ли подсеть или создана

---

## yc_cmp

Этот модуль позволяет управлять облачными ресурсами Yandex Compute Cloud через пользовательский интерфейс Yandex Cloud CLI.

Требуется установить и настроить [Yandex Cloud CLI](https://cloud.yandex.ru/docs/cli/quickstart)

Требуется настроить сеть и подсети с помощью CLI Yandex Cloud или модуля yc_vpc

### Available options:

- **machine** [str] - Имя экземпляра. Обязателен.
- **config** [dict] - Конфигурация параметров экземпляра из Yandex Cloud CLI. Необязателен. Возвращает, если экземпляр существует или создан.
- **state** [str] -  Состояние экземпляра. Должно быть `exists` или `absent`. Необязательный. Значение по умолчанию - `exists`

### Returned values:

- **machine** [str] - Имя экземпляра. Обязателен.
- **config** [dict] - Конфигурация экземпляра из Yandex.Cloud CLI. Возвращает, если экземпляр существует или создан.
- **ip** [str] - Внешний IP-адрес экземпляра YC. Возвращает, если экземпляр существует или создан.