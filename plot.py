import csv
from collections import defaultdict

import matplotlib.pyplot as plt

# 1. читаем results.csv: для каждой пары (N, M) собираем список времён
times = defaultdict(list)
with open("results.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f, delimiter=";"):
        times[(int(row["N"]), int(row["M"]))].append(float(row["T"]))

NN = sorted({n for n, m in times})
MM = sorted({m for n, m in times})

# 2. усредняем: T — среднее время, T2 = T * N
T = {key: sum(v) / len(v) for key, v in times.items()}
T2 = {(n, m): T[(n, m)] * n for (n, m) in T}

# 3. таблица 1.1 — в консоль, чтобы перенести в отчёт
print(f"{'N':>3} {'M':>3} {'T, с':>8} {'T2, с':>8}")
for n in NN:
    for m in MM:
        print(f"{n:>3} {m:>3} {T[(n, m)]:>8.2f} {T2[(n, m)]:>8.2f}")

# 4. графики: по одной линии на каждое M
COLORS = ["#2a78d6", "#eb6834", "#1baf7a"]  # синий, оранжевый, бирюзовый
MARKERS = ["o", "o", "o"]                   # разные маркеры — чтобы различать и без цвета


def plot(data, ylabel, title, filename):
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for m, color, marker in zip(MM, COLORS, MARKERS):
        ys = [data[(n, m)] for n in NN]
        ax.plot(NN, ys, color=color, marker=marker, linewidth=2,
                markersize=5, label=f"M = {m}")
        # подпись у конца линии
        ax.annotate(f"M = {m}", (NN[-1], ys[-1]), xytext=(8, 0),
                    textcoords="offset points", va="center", color="#52514e")

    ax.set_xticks(NN)
    ax.set_xlim(NN[0] - 0.3, NN[-1] + 0.7)
    ax.set_ylim(bottom=0)
    ax.set_xlabel("Число роботов N")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(axis="y", color="#e6e5e1")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(title="Число объектов", frameon=False)
    fig.tight_layout()
    fig.savefig(filename, dpi=200)
    print("Сохранено:", filename)


plot(T, "Время выполнения T, с",
     "Зависимость времени выполнения задачи от числа роботов", "T_from_N.png")
plot(T2, "Суммарное машинное время T2, с",
     "Зависимость суммарного машинного времени от числа роботов", "T2_from_N.png")


# 5. выигрыш от добавления робота: на сколько % сократилось T при N-1 -> N
def plot_gain(filename):
    steps = NN[1:]                                  # переходы 1->2, 2->3, ...
    width = 0.8 / len(MM)                           # ширина одного столбика в группе
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for i, (m, color) in enumerate(zip(MM, COLORS)):
        gains = [(T[(n - 1, m)] - T[(n, m)]) / T[(n - 1, m)] * 100 for n in steps]
        xs = [k + (i - (len(MM) - 1) / 2) * width for k in range(len(steps))]
        bars = ax.bar(xs, gains, width=width * 0.9, color=color, label=f"M = {m}")
        ax.bar_label(bars, fmt="%.0f%%", padding=2, fontsize=8, color="#52514e")

    ax.set_xticks(range(len(steps)))
    ax.set_xticklabels([f"{n - 1} → {n}" for n in steps])
    ax.axhline(0, color="#52514e", linewidth=1)
    ax.set_xlabel("Добавление робота")
    ax.set_ylabel("Сокращение времени T, %")
    ax.set_title("Выигрыш во времени от каждого следующего робота")
    ax.grid(axis="y", color="#e6e5e1")
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(title="Число объектов", frameon=False)
    fig.tight_layout()
    fig.savefig(filename, dpi=200)
    print("Сохранено:", filename)


# 6. эффективность E = T(1) / (N * T(N)) — доля "полезного" машинного времени
E = {(n, m): T[(1, m)] / (n * T[(n, m)]) * 100 for (n, m) in T}


def plot_efficiency(filename):
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.axhline(100, color="#52514e", linewidth=1, linestyle="--")
    ax.annotate("идеал", (NN[0], 100), xytext=(0, 5), textcoords="offset points",
                color="#52514e")
    for m, color, marker in zip(MM, COLORS, MARKERS):
        ys = [E[(n, m)] for n in NN]
        ax.plot(NN, ys, color=color, marker=marker, linewidth=2,
                markersize=5, label=f"M = {m}")
        ax.annotate(f"M = {m}", (NN[-1], ys[-1]), xytext=(8, 0),
                    textcoords="offset points", va="center", color="#52514e")

    ax.set_xticks(NN)
    ax.set_xlim(NN[0] - 0.3, NN[-1] + 0.7)
    ax.set_ylim(0, 115)
    ax.set_xlabel("Число роботов N")
    ax.set_ylabel("Эффективность E, %")
    ax.set_title("Эффективность использования роботов")
    ax.grid(axis="y", color="#e6e5e1")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(title="Число объектов", frameon=False, loc="lower left")
    fig.tight_layout()
    fig.savefig(filename, dpi=200)
    print("Сохранено:", filename)


plot_gain("gain_per_robot.png")
plot_efficiency("efficiency.png")

plt.show()
