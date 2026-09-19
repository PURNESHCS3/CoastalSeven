class BankAccount:

    def __init__(self, name, account_number, balance):
        self.name = name
        self.account_number = account_number
        self.balance = balance
    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            print("Amount deposited successfully")
        else:
            print("Invalid amount")
    def withdraw(self, amount):
        if amount <= 0:
            print("Invalid amount")
        elif amount > self.balance:
            print("Insufficient balance")
        else:
            self.balance -= amount
            print("Amount withdrawn successfully")
    def check_balance(self):
        print("Current balance:", self.balance)
    def display_details(self):
        print("Name:", self.name)
        print("Account Number:", self.account_number)
        print("Balance:", self.balance)
accounts = []
def create_account():
    name = input("Enter your name: ")
    account_number = int(input("Enter account number: "))
    balance = float(input("Enter initial balance: "))
    account = BankAccount(name, account_number, balance)
    accounts.append(account)
    print("Account created successfully")
def find_account(account_number):
    for account in accounts:
        if account.account_number == account_number:
            return account
    return None
def deposit_money():
    account_number = int(input("Enter account number: "))
    account = find_account(account_number)
    if account is not None:
        amount = float(input("Enter amount to deposit: "))
        account.deposit(amount)
    else:
        print("Account not found")
def withdraw_money():
    account_number = int(input("Enter account number: "))
    account = find_account(account_number)
    if account is not None:
        amount = float(input("Enter amount to withdraw: "))
        account.withdraw(amount)
    else:
        print("Account not found")
def check_balance():
    account_number = int(input("Enter account number: "))
    account = find_account(account_number)
    if account is not None:
        account.check_balance()
    else:
        print("Account not found")
def show_details():
    account_number = int(input("Enter account number: "))
    account = find_account(account_number)
    if account is not None:
        account.display_details()
    else:
        print("Account not found")

while True:
    print("\n===== BANKING SYSTEM =====")
    print("1. Create Account")
    print("2. Deposit Money")
    print("3. Withdraw Money")
    print("4. Check Balance")
    print("5. Account Details")
    print("6. Exit")
    choice = input("Enter your choice: ")

    if choice == "1":
        create_account()

    elif choice == "2":
        deposit_money()

    elif choice == "3":
        withdraw_money()

    elif choice == "4":
        check_balance()

    elif choice == "5":
        show_details()

    elif choice == "6":
        print("Thank you for using the banking system")
        break
    else:
        print("Invalid choice")