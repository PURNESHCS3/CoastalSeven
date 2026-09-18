def is_palindrome(number):
    num_str = str(number)
    return num_str == num_str[::-1]
test_num = 12321
if is_palindrome(test_num):
    print(f"{test_num} is a palindrome number.")
else:
    print(f"{test_num} is not a palindrome number.")
