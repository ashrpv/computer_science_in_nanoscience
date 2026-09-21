# Функции в Python

## 1. Определение и вызов функции

```python
def имя_функции(параметр1, параметр2=значение_по_умолчанию):
    """Документация (docstring)"""
    тело_функции
    return результат
```

- Функция — именованный блок кода.
- Можно вызывать многократно.
- `def` создаёт **новую локальную область видимости**.
- Без `return` функция возвращает `None`.
- `return` без значения тоже даёт `None`.
- `return a, b` возвращает **кортеж**.
- Аннотации типов не обязательны:
  ```python
  def f(x: int) -> int:
      return x + 1
  ```
- Функция — объект первого класса:
  - её можно передать;
  - сохранить в переменной;
  - вернуть из другой функции.
- `help(f)` и `f.__doc__` показывают docstring.

```python
def min_max(seq):
    return min(seq), max(seq)

lo, hi = min_max([3, 1, 4, 1, 5])
```

---

## 2. Области видимости и правило LEGB

Поиск имени идёт по четырём уровням:

| Уровень | Название | Что содержит |
|---|---|---|
| **L** | Local | переменные текущей функции |
| **E** | Enclosing | переменные внешней функции |
| **G** | Global | переменные уровня модуля |
| **B** | Built-in | встроенные имена (`print`, `len`) |

- Поиск останавливается на первом найденном уровне.
- Если имя не найдено нигде — `NameError`.
- Новую область видимости создают только `def` и `class`.
- `if`, `for`, `while`, `with` **не создают** область видимости.
- `locals()` — словарь локальных имён.
- `globals()` — словарь глобальных имён.
- `global` нужен для изменения глобальной переменной.
- `nonlocal` нужен для изменения внешней, но не глобальной.
- `nonlocal` работает только внутри вложенной функции.
- Замыкание использует уровень `E`.

```python
x = 2
def foo(y):
    z = 5
    print(locals())          # {'y': 3, 'z': 5}
    print(globals()['x'])    # 2
    print(x, y, z)           # 2 3 5

foo(3)
```

```python
x = 2
def foo(y):
    x = 41                   # локальная x
    z = 5
    print(locals())          # {'x': 41, 'y': 3, 'z': 5}
    print(globals()['x'])    # 2
    print(x, y, z)           # 41 3 5

foo(3)
```

---

## 3. Параметры и аргументы

### 3.1 Параметры по умолчанию

```python
def ask_yn(prompt, retries=4, complaint='Enter Y/N!'):
    ...
```

- Позволяют вызывать функцию с меньшим числом аргументов.
- Значения по умолчанию вычисляются **один раз**.
- Нельзя использовать изменяемые объекты как значения по умолчанию.
- Плохо:
  ```python
  def f(x, acc=[]):
      acc.append(x)
      return acc
  ```
- Хорошо:
  ```python
  def f(x, acc=None):
      if acc is None:
          acc = []
      acc.append(x)
      return acc
  ```
- Значения по умолчанию могут быть именованными.

### 3.2 Именованные (keyword) аргументы

```python
ask_yn('Really quit?')
ask_yn('OK to overwrite?', retries=2)
ask_yn('Update status?', complaint='Just Y/N')
ask_yn('Send text?', retries=2, complaint='Y/N!')
```

- Именованные аргументы повышают читаемость.
- Порядок именованных аргументов не важен.
- Имя должно совпадать с параметром.
- Дублирование позиционного и именованного запрещено.

### 3.3 Правила вызова

```python
def parrot(voltage, state='...', action='...', type='...'):
    ...
```

Корректные вызовы:

```python
parrot(1000)
parrot(voltage=1000)
parrot(voltage=1000000, action='V00000M')
parrot(action='V00000M', voltage=1000000)
parrot('a million', 'bereft of life', 'jump')
parrot('a thousand', state='pushing up the daisies')
```

Некорректные:

```python
parrot()                         # нет обязательного аргумента
parrot(voltage=5.0, 'dead')      # позиционный после именованного
parrot(110, voltage=220)         # дублирование аргумента
parrot(actor='Александр Петров') # неизвестный именованный аргумент
```

### 3.4 `*args` — вариативные позиционные аргументы

```python
def product(*nums, scale=1):
    p = scale
    for n in nums:
        p *= n
    return p

product(2, 3, 5)            # 30
product(2, 3, 5, scale=2)   # 60
```

- `*nums` собирает лишние позиционные аргументы в **кортеж**.
- Всё после `*args` — **keyword-only** параметры.
- Можно запретить позиционную передачу:
  ```python
  def f(a, *, b):
      return a + b
  ```
- Можно запретить именованную передачу:
  ```python
  def f(a, /, b):
      return a + b
  ```
- `/` — positional-only, Python 3.8+.
- Распаковка при вызове:
  ```python
  primes = [2, 3, 5, 7, 11]
  product(*primes)
  ```

### 3.5 `**kwargs` — вариативные именованные аргументы

```python
def authorize(quote, **speaker_info):
    print(">", quote)
    print("-" * (len(quote) + 2))
    for k, v in speaker_info.items():
        print(k, v, sep=': ')

authorize(
    "If music be the food of love, play on.",
    playwright="Shakespeare",
    act=1,
    scene=1,
    speaker="Duke Orsino"
)
```

- `**speaker_info` собирает лишние именованные аргументы в **словарь**.
- Ключи словаря должны быть строками.
- Распаковка при вызове:
  ```python
  info = {'sonnet': 18, 'line': 1, 'author': "Shakespeare"}
  authorize("Shall I compare thee...", **info)
  ```

### 3.6 Общий вид функции

```python
def foo(a, b, c=1, *args, e=1, **kwargs):
    ...
```

Порядок:

1. обязательные позиционные;
2. параметры по умолчанию;
3. `*args`;
4. keyword-only;
5. `**kwargs`.

С positional-only:

```python
def foo(a, b, /, c=1, *args, e=1, **kwargs):
    ...
```

---

## 4. Полезные встроенные функции

```python
print(..., sep=' ', end='\n', file=sys.stdout, flush=False)
range(start, stop, step=1)
enumerate(iterable, start=0)
int(x, base=10)
pow(x, y, z=None)
seq.sort(*, key=None, reverse=False)
sorted(iterable, *, key=None, reverse=False)
sum(iterable, start=0)
min(iterable, default=...)
max(iterable, default=...)
abs(x)
round(x, ndigits=None)
zip(*iterables, strict=False)
reversed(seq)
divmod(a, b)
isinstance(obj, class_or_tuple)
type(obj)
id(obj)
dir(obj)
help(obj)
```

- `sorted()` возвращает новый список.
- `list.sort()` сортирует список на месте.
- `zip(strict=True)` требует одинаковой длины.
- `enumerate()` даёт пары `(индекс, элемент)`.
- `reversed()` возвращает итератор.
- `sum()` часто быстрее ручного цикла.

---

# Функциональное программирование в Python

## 1. Идея функционального программирования (ФП)

- **Первичная сущность** — функция.
- **Чистая функция:**
  - результат зависит только от аргументов;
  - нет побочных эффектов;
  - не меняет внешнее состояние.
- `print()` и `file.write()` — с побочными эффектами.
- Python поддерживает ФП, но не требует её строго.
- Haskell — пример строгого ФП-языка.
- Важны функции высшего порядка.
- Функция может принимать и возвращать функцию.

**Плюсы ФП:**

- модульность;
- комбинируемость;
- простая отладка;
- предсказуемость;
- удобство тестирования.

---

## 2. `map` и `filter`

### 2.1 Обычная схема через цикл

```python
# аналог map
output = []
for element in iterable:
    output.append(function(element))

# включением
[function(element) for element in iterable]
```

```python
# аналог filter
output = []
for element in iterable:
    if predicate(element):
        output.append(element)

# включением
[element for element in iterable if predicate(element)]
```

### 2.2 `map(fn, iterable)`

```python
map :: (a -> b) × [a] -> [b]
```

```python
languages = ["python", "perl", "java", "c"]
list(map(len, languages))      # [6, 4, 4, 1]
list(map(float, ['1.0', '3.3', '-4.2']))
# [1.0, 3.3, -4.2]
```

- Применяет функцию к каждому элементу.
- Элементы не взаимодействуют друг с другом.
- Возвращает **итератор**, а не список.
- Может принимать несколько итерируемых:
  ```python
  list(map(lambda x, y: x + y, [1, 2], [10, 20]))
  # [11, 22]
  ```
- Останавливается по самому короткому итерируемому.

### 2.3 `filter(pred, iterable)`

```python
filter :: (a -> bool) × [a] -> [a]
```

```python
list(filter(lambda x: x % 2 == 0, range(10)))
# [0, 2, 4, 6, 8]
```

- Оставляет элементы, где предикат истинен.
- Возвращает **итератор**.
- `filter(None, iterable)` удаляет ложные значения:
  ```python
  list(filter(None, [0, 1, '', 'a', [], [1]]))
  # [1, 'a', [1]]
  ```

### 2.4 Сравнение с включениями

| Критерий | Включения | `map` / `filter` |
|---|---|---|
| Память | хранят все результаты | вычисляют по запросу |
| Скорость | обычно быстрее | вызовы функций |
| Читаемость | часто понятнее | короче для простых операций |
| Ленивость | нет | да |
| Повторное использование | список можно обойти много раз | итератор исчерпывается |

- `map`/`filter` можно комбинировать.
- Для больших данных ленивость экономит память.
- Для простых случаев генераторы часто читаемее.

---

## 3. Лямбда-функции

```python
lambda параметры: выражение
```

- Создаёт **анонимную** функцию.
- Возвращает значение выражения.
- `return` не нужен.
- Только одно выражение.
- Нельзя использовать блоки и инструкции.
- Нельзя присваивать переменные.
- Может иметь значения по умолчанию:
  ```python
  lambda x=1: x + 1
  ```

```python
# квадраты чисел
list(map(lambda val: val ** 2, range(10)))

# фильтрация по второму элементу кортежа
list(filter(lambda pair: pair[1] > 0, [(4, 1), (3, -2), (8, 0)]))

# сортировка по ключу
sorted([(4, 1), (3, -2), (8, 0)], key=lambda pair: pair[1])
```

**Плохо:**

```python
triple = lambda x: x * 3   # PEP 8 не рекомендует
```

**Хорошо:**

```python
def triple(x):
    return x * 3
```

**Когда использовать лямбды:**

- одноразовые мелкие функции;
- не засорять пространство имён;
- записать функцию прямо в месте вызова;
- ключ сортировки;
- аргумент `map`/`filter`.

**Ограничения:**

- нет docstring;
- нет аннотаций;
- сложно отлаживать;
- не заменяет обычную функцию.

---

## 4. Итераторы

**Итератор** — объект, отдающий элементы по одному.

```python
it = iter([1, 2, 3])
next(it)   # 1
next(it)   # 2
next(it)   # 3
next(it)   # StopIteration
```

- `iter(data)` — получить итератор.
- `next(it)` — следующий элемент.
- `StopIteration` — конец.
- `next(it, default)` не выбрасывает исключение.
- Итератор можно пройти только один раз.
- Итерируемый объект — тот, из которого можно получить итератор.
- У итератора есть `__next__`.
- У итерируемого есть `__iter__`.
- `iter(callable, sentinel)` вызывает `callable` до `sentinel`.
- Итераторы могут быть **бесконечными**.

**Встроенные функции, возвращающие значение:**

```python
max(iterable)
min(iterable)
val in iterable
val not in iterable
all(iterable)
any(iterable)
sum(iterable)
```

**Встроенные функции, возвращающие итератор:**

```python
enumerate(iterable)
map(fn, iterable)
filter(pred, iterable)
zip(*iterables)
reversed(seq)
```

- Для получения списка: `list(iterable)`.
- С бесконечным итератором `max`/`min`/`all`/`any` могут зависнуть.
- `for` неявно использует `iter()` и `next()`.
- `dict.keys()`, `dict.values()`, `dict.items()` — представления, не итераторы.

---

## 5. Генераторы

**Генератор** — функция с `yield`, возвращающая итератор.

```python
def generate_ints(n):
    for i in range(n):
        yield i

g = generate_ints(3)   # функция ещё не запущена
next(g)                # 0
next(g)                # 1
next(g)                # 2
next(g)                # StopIteration
```

**Отличия от обычных функций:**

| Обычная функция | Генератор |
|---|---|
| возвращает одно значение | возвращает итератор |
| локальные переменные удаляются | состояние сохраняется |
| выполняется сразу | выполняется по шагам |
| `return` завершает | `yield` приостанавливает |

**Генераторное выражение:**

```python
(expensive_fn(data) for data in iterable)
```

**Разница:**

```python
needle in (expensive_fn(item) for item in haystack)
# лениво: останавливается при находке

needle in [expensive_fn(item) for item in haystack]
# считает весь список
```

**Пример бесконечного генератора:**

```python
def generate_fibs():
    a, b = 0, 1
    while True:
        a, b = b, a + b
        yield a

g = generate_fibs()
next(g)   # 1
next(g)   # 1
next(g)   # 2
next(g)   # 3
# max(g) — НИКОГДА не завершится!
```

**Ограничение сверху:**

```python
def fibs_under(n):
    for fib in generate_fibs():
        if fib > n:
            break
        print(fib)
```

**Дополнительно:**

- `yield from subiter` делегирует другому итератору.
- `g.send(value)` передаёт значение в генератор.
- `g.close()` завершает генератор.
- `g.throw(exc)` выбрасывает исключение внутри.
- `return value` в генераторе попадает в `StopIteration.value`.

**Зачем нужны итераторы и генераторы:**

- расчёт данных по запросу;
- экономия памяти;
- меньше ненужных вызовов;
- задание потоков данных;
- асинхронное программирование;
- обработка больших файлов;
- бесконечные последовательности.

---

## 6. Декораторы

**Декоратор** — функция, принимающая функцию и возвращающая новую.

### 6.1 Функции как аргументы

```python
def perform_twice(fn, *args, **kwargs):
    fn(*args, **kwargs)
    fn(*args, **kwargs)

perform_twice(print, 5, 10, sep='&', end='...')
# => 5&10...5&10...
```

### 6.2 Функции как возвращаемое значение

```python
def make_divisibility_test(n):
    def divisible_by_n(m):
        return m % n == 0
    return divisible_by_n

div_by_3 = make_divisibility_test(3)
list(filter(div_by_3, range(10)))   # [0, 3, 6, 9]
make_divisibility_test(5)(10)       # True
```

### 6.3 Простой декоратор

```python
def debug(function):
    def wrapper(*args, **kwargs):
        print("Arguments:", args, kwargs)
        return function(*args, **kwargs)
    return wrapper

@debug
def foo(a, b, c=1):
    return (a + b) * c

foo(5, 3, c=2)
# Arguments: (5, 3) {'c': 2}
# 16
```

- `@debug` — сахар для `foo = debug(foo)`.
- `wrapper` принимает `*args, **kwargs`.
- Декоратор возвращает `wrapper`.
- Исходная функция заменяется обёрткой.

**Полезно:**

- `functools.wraps` сохраняет имя и docstring:
  ```python
  from functools import wraps

  def debug(function):
      @wraps(function)
      def wrapper(*args, **kwargs):
          print("Arguments:", args, kwargs)
          return function(*args, **kwargs)
      return wrapper
  ```
- Декоратор с аргументами требует ещё один уровень:
  ```python
  def repeat(times):
      def decorator(function):
          @wraps(function)
          def wrapper(*args, **kwargs):
              for _ in range(times):
                  result = function(*args, **kwargs)
              return result
          return wrapper
      return decorator

  @repeat(3)
  def hello():
      print("Hi")
  ```
- Несколько декораторов применяются снизу вверх:
  ```python
  @a
  @b
  def f():
      ...
  # f = a(b(f))
  ```

## 7. Краткий глоссарий

| Термин | Значение |
|---|---|
| Итерируемый объект | объект, из которого можно получить итератор (`list`, `str`, `dict`) |
| Итератор | объект с `__next__`, отдающий элементы по одному |
| Генератор | функция с `yield`, возвращающая итератор |
| Генераторное выражение | ленивое включение вида `(expr for x in it)` |
| Чистая функция | без побочных эффектов, результат зависит только от входа |
| Декоратор | функция, оборачивающая другую функцию |
| Лямбда | анонимная функция из одного выражения |
| Функция высшего порядка | принимает или возвращает функцию |
| Замыкание | функция, помнящая переменные из внешней области |
| Ленивые вычисления | значение вычисляется только при необходимости |
| Побочный эффект | изменение внешнего состояния или ввод/вывод |
| `StopIteration` | исключение, сигнализирующее конец итератора |
