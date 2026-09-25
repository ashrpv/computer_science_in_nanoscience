"""Учебные расчёты к лекции 14. Запуск из корня репозитория:

python production/examples/lecture14.py --out /tmp/lecture14-figures

Все данные синтетические. Границы и вероятности не являются
настроенным производственным мониторингом или разрешением режима.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import norm


DATA = Path(__file__).resolve().parents[1] / "data" / "14-pilot_batches.csv"
LOWER_SPEC, UPPER_SPEC = 108.0, 125.0  # учебный, не реальный допуск


def monitoring(data: pd.DataFrame, out: Path) -> None:
    assert data.batch_id.is_unique and len(data) == 30
    assert set(data.scale_l) == {20} and set(data.recipe_version) == {"R2"}
    baseline = data.loc[data.phase.eq("baseline"), "size_mean_nm"]
    later = data.loc[data.phase.eq("monitoring")].copy()
    assert len(baseline) == 20 and len(later) == 10

    mean = baseline.mean()
    sigma = baseline.std(ddof=1)
    lo, hi = mean - 3 * sigma, mean + 3 * sigma
    later["individual_signal"] = later.size_mean_nm.lt(lo) | later.size_mean_nm.gt(hi)

    lam = 0.25
    z = mean  # начало именно фазы мониторинга; база не расходует шаги t
    values, lower, upper = [], [], []
    for t, x in enumerate(later.size_mean_nm, start=1):
        z = lam * x + (1 - lam) * z
        spread = sigma * np.sqrt(lam / (2 - lam) * (1 - (1 - lam) ** (2 * t)))
        values.append(z)
        lower.append(mean - 3 * spread)
        upper.append(mean + 3 * spread)
    later["ewma"] = values
    later["ewma_lower"] = lower
    later["ewma_upper"] = upper
    later["ewma_signal"] = later.ewma.lt(later.ewma_lower) | later.ewma.gt(later.ewma_upper)

    print(f"База: среднее={mean:.3f} нм, s={sigma:.3f} нм; условные I-пределы [{lo:.3f}, {hi:.3f}] нм")
    for col in ("individual_signal", "ewma_signal"):
        print(col, later.loc[later[col], "batch_id"].tolist())
    print("Вне учебного допуска:", data.loc[
        data.size_mean_nm.lt(LOWER_SPEC) | data.size_mean_nm.gt(UPPER_SPEC), "batch_id"
    ].tolist())

    fig, (ax, ew) = plt.subplots(2, 1, figsize=(10, 6), sharex=True, layout="constrained")
    x = np.arange(1, len(data) + 1)
    ax.plot(x, data.size_mean_nm, "o-", markersize=4, color="#24808A", label="Средний DLS-размер партии")
    for value, color, label in [(lo, "#CB624B", "I-пределы (учебные)"),
                                (hi, "#CB624B", None),
                                (LOWER_SPEC, "#777777", "Учебный допуск"),
                                (UPPER_SPEC, "#777777", None)]:
        ax.axhline(value, color=color, linestyle="--", label=label)
    ax.axvline(20.5, color="black", linewidth=1)
    ax.axvline(21.5, color="#B88B2C", linewidth=1, linestyle=":", label="Смена сырья B122")
    ax.set(ylabel="Средний DLS-размер, нм", title="Одна независимая точка на партию")
    ax.legend(ncol=3, fontsize=8)
    ids = np.arange(21, 31)
    ew.plot(ids, later.ewma, "o-", color="#24808A", label="EWMA, λ=0,25")
    ew.plot(ids, later.ewma_lower, "--", color="#CB624B", label="Пределы EWMA (учебные)")
    ew.plot(ids, later.ewma_upper, "--", color="#CB624B")
    ew.set(xlabel="Порядковый номер партии", ylabel="EWMA, нм", xticks=[1, 5, 10, 15, 20, 21, 23, 25, 27, 30])
    ew.legend(fontsize=8)
    fig.savefig(out / "monitoring.png", dpi=170)
    plt.close(fig)


def analytic_concentration(t: np.ndarray | float, a: float = 0.25,
                           k: float = 0.08, c_in: float = 1.4,
                           c0: float = 0.2) -> np.ndarray:
    steady = a * c_in / (a + k)
    return steady + (c0 - steady) * np.exp(-(a + k) * np.asarray(t))


def euler_concentration(dt: float, end: float = 20.0) -> tuple[np.ndarray, np.ndarray]:
    t = np.arange(round(end / dt) + 1) * dt
    c = np.empty_like(t)
    c[0] = 0.2
    for i in range(1, len(t)):
        c[i] = c[i - 1] + dt * (0.25 * (1.4 - c[i - 1]) - 0.08 * c[i - 1])
    return t, c


def state_estimation(out: Path) -> None:
    t, c_euler = euler_concentration(0.2)
    _, c_fine = euler_concentration(0.1)
    c_exact = analytic_concentration(t)
    c_star = 0.25 * 1.4 / (0.25 + 0.08)
    print(f"Стационарное C*={c_star:.6f}; C(20)={c_exact[-1]:.6f}")
    print(f"Погрешность Эйлера в 20 мин: h=0.2: {abs(c_euler[-1]-c_exact[-1]):.6g}, "
          f"h=0.1: {abs(c_fine[-1]-c_exact[-1]):.6g}")

    prior, observation, sd_prior, sd_sensor = 0.80, 0.90, 0.06, 0.04
    gain = sd_prior**2 / (sd_prior**2 + sd_sensor**2)
    posterior = prior + gain * (observation - prior)
    sd_post = np.sqrt((1 - gain) * sd_prior**2)
    print(f"Обновление состояния: K={gain:.4f}, C_post={posterior:.4f}, σ_post={sd_post:.4f}")

    rng = np.random.default_rng(140)
    obs_time = np.arange(0, 21, 2)
    # Смещение появляется после 10 минут. Это пример дефекта канала датчика,
    # а не воспроизведение событий B127 в отдельном ряду партий.
    y = analytic_concentration(obs_time) + rng.normal(0, 0.025, len(obs_time))
    y[obs_time >= 10] += 0.08
    residual = y - analytic_concentration(obs_time)
    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(8, 6), sharex=True, layout="constrained")
    ax.plot(t, c_exact, label="Баланс, аналитическое решение", color="#24808A")
    ax.scatter(obs_time, y, label="Датчик с возможным смещением", color="#CB624B")
    ax.set(ylabel="C, условные единицы")
    ax.legend()
    ax2.axhline(0, color="black", linewidth=1)
    ax2.scatter(obs_time, residual, color="#CB624B")
    ax2.axvline(10, color="#B88B2C", linestyle=":")
    ax2.set(xlabel="Время, мин", ylabel="Наблюдение − прогноз")
    fig.savefig(out / "state-and-innovations.png", dpi=170)
    plt.close(fig)


def next_experiment() -> None:
    candidates = pd.DataFrame({
        "regime": ["A", "B", "C"],
        "predicted_mean_nm": [117.0, 113.0, 110.0],
        "predictive_sd_nm": [2.0, 4.0, 2.0],
        "equipment_ok": [True, True, False],
        "research_value": ["low", "high", "high"],
    })
    candidates["p_within_spec"] = (
        norm.cdf((UPPER_SPEC - candidates.predicted_mean_nm) / candidates.predictive_sd_nm)
        - norm.cdf((LOWER_SPEC - candidates.predicted_mean_nm) / candidates.predictive_sd_nm)
    )
    print("\nУчебное сравнение режимов (нормальная прогностическая модель):")
    print(candidates.round(3).to_string(index=False))
    print("К рассмотрению при учебном пороге 0.85:",
          candidates.loc[candidates.equipment_ok & candidates.p_within_spec.ge(0.85), "regime"].tolist())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("/tmp/lecture14-figures"))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    monitoring(pd.read_csv(DATA), args.out)
    state_estimation(args.out)
    next_experiment()
    print("Учебные рисунки:", args.out)


if __name__ == "__main__":
    main()
