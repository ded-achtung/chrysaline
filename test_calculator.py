#!/usr/bin/env python3
"""
Тестирование калькулятора
"""

import sys
sys.path.insert(0, 'src')

from calculator import add, subtract, multiply, divide

print("Тестирование калькулятора...")
print("=" * 40)

# Тест сложения
print("Тест сложения: 10 + 5 =", add(10, 5))
assert add(10, 5) == 15, "Ошибка в сложении"

# Тест вычитания
print("Тест вычитания: 10 - 5 =", subtract(10, 5))
assert subtract(10, 5) == 5, "Ошибка в вычитании"

# Тест умножения
print("Тест умножения: 10 * 5 =", multiply(10, 5))
assert multiply(10, 5) == 50, "Ошибка в умножении"

# Тест деления
print("Тест деления: 10 / 5 =", divide(10, 5))
assert divide(10, 5) == 2, "Ошибка в делении"

# Тест деления на ноль
print("Тест деления на ноль: 10 / 0 =", divide(10, 0))

print("=" * 40)
print("✓ Все тесты пройдены успешно!")
