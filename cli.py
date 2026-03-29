#!/usr/bin/env python3
"""Точка входа для запуска экспериментов Chrysaline."""

import sys


EXPERIMENTS = {
    "exercises": ("experiments.exercises", "8 упражнений по правилам русского языка"),
    "raw_text": ("experiments.raw_text", "Тест на сыром тексте учебника"),
    "five_experiments": ("experiments.five_experiments", "Поглощение, масштаб, конфликт, deep visiting, связь правил"),
    "gen_ask": ("experiments.gen_ask", "Генерация предложений и ответы на вопросы"),
    "proof": ("experiments.proof_of_generality", "Доказательство универсальности парадигмы (новый предмет)"),
    "stress": ("experiments.stress_test", "Стресс-тест: границы парадигмы (отрицание, омонимия, объяснения, масштаб)"),
    "math": ("experiments.math_test", "Математический тест: арифметика, задачи, вычисления"),
}


def run_experiment(name):
    if name not in EXPERIMENTS:
        print(f"Неизвестный эксперимент: {name}")
        print(f"Доступные: {', '.join(EXPERIMENTS)}")
        sys.exit(1)

    module_path, description = EXPERIMENTS[name]
    print(f"\n{'='*60}")
    print(f"  Запуск: {name} — {description}")
    print(f"{'='*60}\n")

    import importlib
    module = importlib.import_module(module_path)
    module.main()


def main():
    if len(sys.argv) < 2:
        print("Chrysaline — биологически-инспирированная система обучения\n")
        print("Использование: python cli.py <эксперимент>\n")
        print("Доступные эксперименты:")
        for name, (_, desc) in EXPERIMENTS.items():
            print(f"  {name:20s} — {desc}")
        print(f"  {'all':20s} — запустить все")
        sys.exit(0)

    target = sys.argv[1]

    if target == "all":
        for name in EXPERIMENTS:
            run_experiment(name)
    else:
        run_experiment(target)


if __name__ == "__main__":
    main()
