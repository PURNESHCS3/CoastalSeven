def calculate_factorial(n):
    if n < 0: 
        return "Undefined for negative numbers"
    if n == 0 or n == 1:
        return 1
    result = 1
    for i in range(1, n + 1): 
        result *= i
    return result 
test_fact = 5
print(f'The factorial of {test_fact} is {calculate_factorial(test_fact)}')
