# Справочник: базовая статистика в Python

Это сквозной пример к [справочнику по статистике](basic_statistics.md). Он показывает путь от таблицы технических чтений к выводам на уровне независимых образцов. Данные ниже **искусственные**: в условиях A и B по пять независимо синтезированных образцов, каждый измерен три раза. `size_nm` — учебный характеристический размер образца в нм; это не таблица отдельных частиц из ПЭМ-практикума и не результат реального исследования. Исполняйте блоки Python **сверху вниз** в одном notebook или `.py`-файле.

Для примера нужен Python 3.11/3.12 и пакеты из [requirements.txt](../requirements.txt). Сохраните версии библиотек вместе с результатом; повторы измерений в примере заданы явно, а не генерируются случайным seed.

## 1. Таблица и приёмка

Одна строка будущей таблицы — одно техническое чтение. `sample_id` обозначает независимый синтез, `reading_no` — повтор внутри него. Не теряйте эти идентификаторы при импорте.

```python
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

readings = {
    "A": [(69, 70, 71), (70, 71, 72), (67, 69, 71),
          (72, 73, 74), (68, 69, 70)],
    "B": [(74, 75, 76), (73, 74, 75), (76, 77, 78),
          (71, 73, 75), (75, 76, 77)],
}
rows = [
    {"group": group, "sample_id": f"{group}{j:02d}",
     "reading_no": i, "size_nm": size}
    for group, samples in readings.items()
    for j, sample_readings in enumerate(samples, start=1)
    for i, size in enumerate(sample_readings, start=1)
]
df = pd.DataFrame(rows)
assert len(df) == 30  # 10 независимых образцов × 3 технических чтения
print(df.head())
```

В реальной работе сохраняйте исходный CSV без исправлений, словарь полей и отдельный журнал очистки. Пример экспорта и обратного импорта создаёт файл в **текущей рабочей папке**; название столбца содержит единицу измерения.

```python
df.to_csv("synthetic_readings.csv", index=False)
df = pd.read_csv(
    "synthetic_readings.csv",
    dtype={"group": "string", "sample_id": "string", "reading_no": "Int64"},
)
expected = {"group", "sample_id", "reading_no", "size_nm"}
if set(df.columns) != expected:
    raise ValueError(f"Неожиданные столбцы: {list(df.columns)}")
df["size_nm"] = pd.to_numeric(df["size_nm"], errors="raise")
if df["group"].isna().any() or df["sample_id"].isna().any():
    raise ValueError("Пропущен идентификатор группы или образца")
if df["reading_no"].isna().any() or df.duplicated(["sample_id", "reading_no"]).any():
    raise ValueError("Пропущен или повторяется номер чтения внутри образца")
if not np.isfinite(df["size_nm"].to_numpy()).all() or (df["size_nm"] <= 0).any():
    raise ValueError("Размеры должны быть конечными положительными числами")
if (df.groupby("sample_id")["group"].nunique() != 1).any():
    raise ValueError("Один sample_id встречается в разных группах")
print(df.groupby("group")["sample_id"].nunique())  # по 5, а не по 15
```

`errors="raise"` замечает текст в числовом поле. `NaN` нельзя без объяснения заменить нулём, а запись ниже предела обнаружения требует отдельного поля статуса и правила обработки. Для произвольного исследования число чтений на образец может различаться; фиксация «ровно три» относится только к учебному генератору выше.

## 2. Сводка с правильным знаменателем

Сначала получаем **одну строку на синтез**. Внутриобразцовое `tech_sd_nm` показывает разброс его трёх чтений, а `sample_mean_nm` представляет образец при сравнении условий.

```python
per_sample = (
    df.groupby(["group", "sample_id"], as_index=False)
      .agg(n_readings=("size_nm", "size"),
           sample_mean_nm=("size_nm", "mean"),
           tech_sd_nm=("size_nm", "std"))
)
print(per_sample)

summary = (
    per_sample.groupby("group", as_index=False)
              .agg(n_samples=("sample_id", "size"),
                   mean_nm=("sample_mean_nm", "mean"),
                   median_nm=("sample_mean_nm", "median"),
                   sd_nm=("sample_mean_nm", "std"))
)
summary["se_nm"] = summary["sd_nm"] / np.sqrt(summary["n_samples"])
print(summary.round(2))
```

`pandas.Series.std()` использует `ddof=1` по умолчанию; NumPy `np.std(...)` — `ddof=0`, поэтому для выборочного SD пишите `np.std(x, ddof=1)`. `sd_nm` описывает **межобразцовый разброс средних образцов**; `se_nm` — модельную стандартную ошибку среднего по независимым синтезам. Это разные величины. При `n_samples=1` SD и SE не определены. Группировка не лечит систематическую ошибку отбора образцов.

Для 95% t-интервала среднего группы A на уровне независимых образцов:

```python
a = per_sample.loc[per_sample["group"] == "A", "sample_mean_nm"].to_numpy()
b = per_sample.loc[per_sample["group"] == "B", "sample_mean_nm"].to_numpy()
if len(a) < 2 or len(b) < 2:
    raise ValueError("Для оценки выборочного SD нужны хотя бы два образца на группу")
ci_a = stats.t.interval(0.95, df=len(a) - 1, loc=a.mean(), scale=stats.sem(a))
print(f"A: среднее {a.mean():.2f} нм, 95% CI [{ci_a[0]:.2f}; {ci_a[1]:.2f}] нм")
```

Предпосылки этого интервала: независимость синтезов, осмысленная цель обобщения и подходящая модель для среднего. При пяти образцах интервал чувствителен к крайним значениям; он не даёт диапазон размеров для будущего отдельного образца.

## 3. Показать значения и подписать усы

Покажем все средние независимых образцов, а рядом среднее группы ± **SD между образцами**. Это *не* доверительный интервал; используем сдвиг по оси x только для читаемости, без статистического смысла.

```python
fig, ax = plt.subplots(figsize=(6, 4), layout="constrained")
for x, (label, values) in enumerate((("A", a), ("B", b))):
    ax.scatter(np.full(len(values), x) - 0.10, values, label=f"Образцы {label}")
    ax.errorbar(x + 0.12, values.mean(), yerr=values.std(ddof=1),
                fmt="s", capsize=4, color="black")
ax.set(xticks=[0, 1], xticklabels=["A", "B"],
       xlabel="Условие", ylabel="Среднее трёх чтений образца, нм",
       title="Искусственные данные: точки и среднее ± SD")
ax.legend()
fig.savefig("synthetic_group_summary.png", dpi=150)
plt.show()
```

Для реальных данных дополните подпись к рисунку числом независимых синтезов, способом отбора и определением признака. Скопление всех технических чтений на этом графике создало бы ложное впечатление о числе независимых единиц.

## 4. Сравнить независимые группы

До запуска фиксируем направление эффекта: **B − A, нм**. Для независимых синтезов применяем t-тест Уэлча, не требующий равных дисперсий двух групп. Его интервал относится к разности средних при предпосылках теста.

```python
welch = stats.ttest_ind(b, a, equal_var=False)
ci_diff = welch.confidence_interval(confidence_level=0.95)
effect_nm = b.mean() - a.mean()
print(f"B − A = {effect_nm:.2f} нм")
print(f"95% CI разности: [{ci_diff.low:.2f}; {ci_diff.high:.2f}] нм")
print(f"t = {welch.statistic:.2f}; df = {welch.df:.2f}; p = {welch.pvalue:.4g}")
```

`stats.ttest_ind(b, a, ...)` возвращает эффект и интервал именно в порядке `b − a`. Замените порядок аргументов — изменится знак. Сначала интерпретируйте эффект, единицы, интервал и план опыта, затем `p`. При маленькой выборке проверьте чувствительность вывода к самым необычным независимым образцам и не обобщайте результат на другие режимы синтеза без основания. Эквивалентность условий из большого `p` не следует.

## 5. Если измеряли те же образцы «до» и «после»

Это **другой искусственный дизайн**, не дополнительный столбец к таблице A/B. Каждая строка — один независимо выбранный образец, измеренный дважды. Сначала сравнивайте внутри пар; перестановка строк одного столбца разрушит соответствие.

```python
paired = pd.DataFrame({
    "sample_id": [f"P{i:02d}" for i in range(1, 7)],
    "before_nm": [50, 52, 51, 54, 53, 55],
    "after_nm": [49, 50, 50, 52, 50, 54],
})
if paired["sample_id"].duplicated().any() or paired.isna().any().any():
    raise ValueError("Проверьте уникальность и полноту пар")
paired["change_nm"] = paired["after_nm"] - paired["before_nm"]
res = stats.ttest_rel(paired["after_nm"], paired["before_nm"])
ci_change = res.confidence_interval(confidence_level=0.95)
print(f"Среднее изменение: {paired['change_nm'].mean():.2f} нм")
print(f"95% CI: [{ci_change.low:.2f}; {ci_change.high:.2f}] нм; p = {res.pvalue:.4g}")
```

Единица анализа здесь — **пара**, `n=6`. Парный тест работает с разностями и требует независимости между парами; он не подходит для двух групп разных образцов. Если одно измерение пары отсутствует, заранее решите, как поступить с неполной парой, и объясните исключение в отчёте.

## 6. Короткая карта инструментов

| Задача | Команда | Проверка перед применением |
|---|---|---|
| Среднее и медиана | `np.mean(x)`, `np.median(x)` | Уровень наблюдения и пропуски |
| Выборочный SD | `np.std(x, ddof=1)` | `n > 1`, единицы и независимые значения |
| Квантили | `np.quantile(x, [0.1, 0.5, 0.9])` | Правило квантилей при малом `n` |
| По группам | `df.groupby(...).agg(...)` | Идентификатор независимой единицы |
| SE среднего | `stats.sem(x)` | Независимость, смысл `n` |
| t-интервал среднего | `stats.t.interval(...)` | Условия модели и интерпретация интервала |
| Разность двух групп | `stats.ttest_ind(b, a, equal_var=False)` | Разные независимые образцы, порядок B − A |
| Изменение в парах | `stats.ttest_rel(after, before)` | Соответствие строк одним и тем же объектам |

Параметр `nan_policy="omit"` в статистической функции не заменяет выяснение причин пропусков. Не применять автоматически один тест к тысячам частиц, точек спектра или последовательным отсчётам; вернитесь к [уровням независимости](basic_statistics.md#1-сначала-вопрос-затем-число) и [лекции 7](../experimental_design/07-random_effects_and_blocks.md). Для настоящей серии ПЭМ используйте [паспорт набора](../experimental_analysis/data/tem_magnetite/README.md) и [задание](../experimental_analysis/09-tem-homework.md): там снимки вложены в образцы, а зарегистрированный размер зависит от силуэта частицы.

**Самопроверка:** замените одно из чтений `A01` с 69 на 90 нм и сравните `tech_sd_nm`, межобразцовый `sd_nm` и эффект B − A. Затем верните исходное число и замените *весь* образец A01 тремя согласованно увеличенными чтениями. Объясните, почему оба изменения по-разному затрагивают вопрос о повторяемости и вариации синтезов. Удалять необычное наблюдение без проверки первичной записи нельзя.

## Документация библиотек

- [NumPy: `std` и `ddof`](https://numpy.org/doc/2.3/reference/generated/numpy.std.html).
- [pandas: группировка и сводные расчёты](https://pandas.pydata.org/docs/user_guide/groupby.html).
- [SciPy: `ttest_ind`](https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.stats.ttest_ind.html) и [`ttest_rel`](https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.stats.ttest_rel.html).
