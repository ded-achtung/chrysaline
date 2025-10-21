#!/usr/bin/env python3
"""
Простой калькулятор на Python
Поддерживает основные арифметические операции: +, -, *, /
"""

def add(a, b):
    """Сложение двух чисел"""
    return a + b

def subtract(a, b):
    """Вычитание двух чисел"""
    return a - b

def multiply(a, b):
    """Умножение двух чисел"""
    return a * b

def divide(a, b):
    """Деление двух чисел"""
    if b == 0:
        return "Ошибка: Деление на ноль невозможно!"
    return a / b

def calculator():
    """Главная функция калькулятора"""
    print("=" * 40)
    print("Добро пожаловать в Калькулятор!")
    print("=" * 40)

    while True:
        print("\nВыберите операцию:")
        print("1. Сложение (+)")
        print("2. Вычитание (-)")
        print("3. Умножение (*)")
        print("4. Деление (/)")
        print("5. Выход")

        choice = input("\nВведите номер операции (1-5): ")

        if choice == '5':
            print("Спасибо за использование калькулятора!")
            break

        if choice not in ['1', '2', '3', '4']:
            print("Неверный выбор! Пожалуйста, выберите операцию от 1 до 5.")
            continue

        try:
            num1 = float(input("Введите первое число: "))
            num2 = float(input("Введите второе число: "))

            if choice == '1':
                result = add(num1, num2)
                print(f"\n{num1} + {num2} = {result}")
            elif choice == '2':
                result = subtract(num1, num2)
                print(f"\n{num1} - {num2} = {result}")
            elif choice == '3':
                result = multiply(num1, num2)
                print(f"\n{num1} * {num2} = {result}")
            elif choice == '4':
                result = divide(num1, num2)
                print(f"\n{num1} / {num2} = {result}")

        except ValueError:
            print("Ошибка: Пожалуйста, введите корректное число!")
        except Exception as e:
            print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    calculator()
