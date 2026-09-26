# Материалы и источники

Презентации сопоставлены с конспектами всех четырнадцати лекций. Конспекты расширяют материал слайдов пояснениями, вычисляемыми примерами и ограничениями применения. Порядок модулей: Python для научных данных → экспериментальные данные и воспроизводимость → планирование эксперимента и оптимизация → спектры, кривые и изображения → научное и стохастическое моделирование → машинное обучение → от лаборатории к производству → итоговый проект.

Это порядок изучения материалов; он не задаёт число аудиторных занятий или часов. В модуле планирования сначала рассматриваются планы и оптимизация, затем случайные эффекты и блочные планы. Производственный модуль включает лекции 13–14; итоговый проект объединяет методы курса в исследовательской задаче.

## Сопоставление файлов

| Порядок | Презентация | Слайдов | Конспект |
|---|---|---:|---|
| 1 | [01-python_basics.pptx](slides/01-python_basics.pptx) | 37 | [Конспект](python_basics/01-basics_and_types.md): основы языка и управление потоком |
| 2 | [02-data_structures.pptx](slides/02-data_structures.pptx) | 42 | [Конспект](python_basics/01-basics_and_types.md): структуры данных и включения |
| 3 | [03-functions.pptx](slides/03-functions.pptx) | 45 | [Конспект](python_basics/02-functions.md) |
| 4 | [04-numpy_and_visualization.pptx](slides/04-numpy_and_visualization.pptx) | 38 | [Конспект](python_basics/04-numpy_and_visualization.md) |
| 5 | [05-reproducibility.pptx](slides/05-reproducibility.pptx) | 44 | [Конспект](experimental_data/05-reproducibility.md) |
| 6 | [06-design_and_optimization.pptx](slides/06-design_and_optimization.pptx) | 30 | [Конспект](experimental_design/06-design_and_optimization.md) |
| 7 | [07-random_effects_and_blocks.pptx](slides/07-random_effects_and_blocks.pptx) | 43 | [Конспект](experimental_design/07-random_effects_and_blocks.md) |
| 8 | [08-spectra_and_curves.pptx](slides/08-spectra_and_curves.pptx) | 28 | [Конспект](experimental_analysis/08-spectra_and_curves.md) |
| 9 | [09-image_analysis.pptx](slides/09-image_analysis.pptx) | 28 | [Конспект](experimental_analysis/09-image_analysis.md) |
| 10 | [10-scientific_and_stochastic_modeling.pptx](slides/10-scientific_and_stochastic_modeling.pptx) | 38 | [Конспект](modeling/10-scientific_and_stochastic_modeling.md) |
| 11 | [11-ml_problem_and_validation.pptx](slides/11-ml_problem_and_validation.pptx) | 40 | [Конспект](machine_learning/11-ml-problem_and_validation.md) |
| 12 | [12-ml_methods_and_experiment.pptx](slides/12-ml_methods_and_experiment.pptx) | 40 | [Конспект](machine_learning/12-ml-methods_and_experiment.md) |
| 13 | [13-scaling_and_process_data.pptx](slides/13-scaling_and_process_data.pptx) | 40 | [Конспект](production/13-scaling_and_process_data.md) |
| 14 | [14-monitoring_and_digital_twin.pptx](slides/14-monitoring_and_digital_twin.pptx) | 40 | [Конспект](production/14-monitoring_and_digital_twin.md) |

## Темы конспектов и слайдов

| Лекция | Слайды источника | Разделы конспекта |
|---|---|---|
| 4 | 2–17; 18–31; 32–38 | Массивы и вычисления; Matplotlib; Seaborn и практика |
| 5 | 2–11; 12–25; 26–30; 31–38; 39–44 | Дизайн и независимость; схема и импорт; метаданные; notebook и Git; FAIR, ELN/LIMS и проект |
| 6 | 2–7; 8–15; 16–21; 22–30 | Надёжность; факторные планы; поверхности отклика; смеси, ограничения и оптимизация |
| 7 | 2–13; 14–27; 28–36; 37–43 | Мощность; случайные эффекты и EMS; вложенность; блочные планы |
| 8 | 2–5; 6–12; 13–20; 21–28 | Калибровка; предобработка; признаки; кривые, серия и QC |
| 9 | 2–6; 7–15; 16–23; 24–28 | Калибровка и выборка; сегментация; измерения; устойчивость и серия |
| 10 | 2–8; 9–11; 12–23; 24–33; 34–38 | Постановка; ОДУ; оценка параметров; случайные процессы; исследование и проверка модели |
| 11 | 2–11; 12–22; 23–29; 30–40 | Задача и единица наблюдения; тест и метрики; классификация и перенос; пример и мини-проект |
| 12 | 2–7; 8–13; 14–22; 23–28; 29–36; 37–40 | Линейные методы; спектры и PLS; дерево, лес, бустинг с числовым примером; кластеры и pH по RGB; активный опыт, сеть и аудит ноутбука log D; RL и выводы |
| 13 | 2–12; 13–24; 25–35; 36–40 | Геометрия, тепло и смешение; иерархия и временные данные; контрасты и пилот; практика и выводы |
| 14 | 2–21; 22–31; 32–37; 38–40 | Мониторинг и расследование сигнала; модель состояния и цифровой двойник; следующий допустимый опыт; практика |

## Научные источники для практикума по наночастицам (лекция 10)

- [Ermak & McCammon (1978), Brownian dynamics with hydrodynamic interactions](https://doi.org/10.1063/1.436761) — исходная работа по броуновской динамике; учебный notebook использует более простой предел независимых частиц без гидродинамических взаимодействий.
- [Zhao et al., Brownian Dynamics Simulations of Magnetic Nanoparticles Captured in Strong Magnetic Field Gradients](https://doi.org/10.1021/acs.jpcc.6b09409) — магнитный захват в неоднородном поле. Значения поля в учебном сценарии не являются измерениями из статьи.
- [ζ-Potentials of Silica in Water–Alcohol Mixtures](https://doi.org/10.1021/la00040a008) — зависимость электрокинетических свойств от состава растворителя; ζ-потенциал сам по себе не задаёт готовую количественную модель парного взаимодействия.
- [Wang & Brady, Microstructures and mechanics in the colloidal film drying process](https://authors.library.caltech.edu/records/emx3b-61457) — броуновская динамика частиц и движущаяся граница высыхающей плёнки.
- [Lesaine et al., Role of particle aggregation in the structure of dried colloidal silica layers](https://doi.org/10.1039/D0SM00723D) — опыты с высыханием SiO₂: важны полидисперсность и агрегация, порядок на поверхности не характеризует автоматически весь объём.
- [Deegan et al., Capillary flow as the cause of ring stains from dried liquid drops](https://doi.org/10.1038/39827) — радиальный перенос к закреплённой контактной линии капли.
- [Shi, Yang & Bain, Drying of Ethanol/Water Droplets Containing Silica Nanoparticles](https://doi.org/10.1021/acsami.8b21731) — водно-спиртовые капли с *пирогенным* SiO₂. Их результаты нельзя напрямую использовать как параметры монодисперсных сфер для модели опала.

Новые [конспект](modeling/10-nanoparticle-modeling.md) и [задание](modeling/10-nanoparticle-homework.md) отделяют литературные механизмы от сценарных параметров исполняемых примеров.

## Документация инструментов

Для лекций 13–14 использованы первичные материалы:

- [NIST/SEMATECH e-Handbook: Process or Product Monitoring and Control](https://www.itl.nist.gov/div898/handbook/pmc/pmc.htm).
- [NIST/SEMATECH e-Handbook: Iterative nature of experimentation](https://www.itl.nist.gov/div898/handbook/pri/section2/pri223.htm).
- [NIST: Digital Twins for Advanced Manufacturing](https://www.nist.gov/programs-projects/digital-twins-advanced-manufacturing).
- [NIST SP 1200-6: Measuring the Size of Nanoparticles in Aqueous Media Using Batch-Mode Dynamic Light Scattering](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.1200-6.pdf) — метод измерения для примера лекции 13.
- [NIST/SEMATECH e-Handbook: Selecting and Scaling Process Variables](https://www.itl.nist.gov/div898/handbook/pri/section3/pri32.htm) — выбор факторов и границ пилотного опыта.
- [Scale-up of Continuous and Semibatch Precipitation Processes](https://pubs.acs.org/doi/10.1021/ie990431u) — ограничения переноса по одному глобальному критерию смешения.

Пример процесса SiO₂ и численные значения в лекциях 13–14 искусственные.

Для уточнения API использованы официальные руководства:

- [Seaborn: lineplot](https://seaborn.pydata.org/generated/seaborn.lineplot.html) — агрегирование повторов и интервалы.
- [SciPy: peak_widths](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.peak_widths.html) — высота относительно prominence и дробные индексы пересечений.
- [statsmodels: FTestAnovaPower](https://www.statsmodels.org/stable/generated/statsmodels.stats.power.FTestAnovaPower.html) — расчёт мощности однофакторной ANOVA.
- [scikit-image: morphology](https://scikit-image.org/docs/stable/api/skimage.morphology.html) — очистка масок; примеры зафиксированы на версии 0.25.2.

В лекции о воспроизводимости также использованы понятия и библиографические ориентиры из слайдов 43–44: Lazic et al. (2018), NASEM (2019), Wickham (2014), Wilson et al. (2017), Wilkinson et al. (2016), W3C PROV (2013), руководства BIPM и Eurachem. Они не подменяют первичные протоколы конкретного исследования.
