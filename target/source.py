import json
import datetime
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Generator

# ====== CUSTOM EXCEPTIONS ======


class InsufficientFundsError(Exception):
    pass


class FraudDetectionError(Exception):
    pass


class AccountClosedError(Exception):
    pass

# ====== DECORATORS ======


def validate_transaction(func):
    """Decorator to validate transaction amounts."""
    def wrapper(account, amount, *args, **kwargs):
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if account.is_closed:
            raise AccountClosedError("Account is closed")
        return func(account, amount, *args, **kwargs)
    return wrapper

# ====== BASE CLASSES ======


class Account(ABC):
    def __init__(self, account_id: str, owner: str, balance: float = 0.0):
        self.account_id = account_id
        self.owner = owner
        self._balance = balance
        self.is_closed = False
        self._transaction_history: List[Dict] = []
        self._open_date = datetime.date.today()

    @property
    def balance(self) -> float:
        return self._balance

    @validate_transaction
    def deposit(self, amount: float) -> None:
        """Deposit money into the account."""
        self._balance += amount
        self._log_transaction("DEPOSIT", amount)

    @validate_transaction
    def withdraw(self, amount: float) -> None:
        """Withdraw money from the account."""
        if self._balance < amount:
            raise InsufficientFundsError("Insufficient funds")
        self._balance -= amount
        self._log_transaction("WITHDRAW", -amount)

    def _log_transaction(self, tx_type: str, amount: float) -> None:
        """Log a transaction to history."""
        tx = {
            "type": tx_type,
            "amount": amount,
            "balance_after": self._balance,
            "date": datetime.datetime.now().isoformat()
        }
        self._transaction_history.append(tx)

    def get_transactions(self, filter_type: Optional[str] = None) -> Generator[Dict, None, None]:
        """Generator to yield transactions (optionally filtered)."""
        for tx in self._transaction_history:
            if filter_type is None or tx["type"] == filter_type.upper():
                yield tx

    @abstractmethod
    def calculate_interest(self) -> float:
        """Calculate interest (implemented by subclasses)."""
        pass

    def close(self) -> None:
        """Close the account."""
        self.is_closed = True

    def to_dict(self) -> Dict:
        """Serialize account to dictionary."""
        return {
            "account_id": self.account_id,
            "owner": self.owner,
            "balance": self._balance,
            "is_closed": self.is_closed,
            "open_date": self._open_date.isoformat(),
            "type": self.__class__.__name__
        }

# ====== ACCOUNT SUBCLASSES ======


class SavingsAccount(Account):
    INTEREST_RATE = 0.05  # 5% annual interest

    def calculate_interest(self) -> float:
        """Daily compounding interest."""
        days_open = (datetime.date.today() - self._open_date).days
        return self._balance * (1 + self.INTEREST_RATE / 365) ** days_open - self._balance


class CheckingAccount(Account):
    def __init__(self, account_id: str, owner: str, balance: float = 0.0, overdraft_limit: float = 100.0):
        super().__init__(account_id, owner, balance)
        self.overdraft_limit = overdraft_limit

    @validate_transaction
    def withdraw(self, amount: float) -> None:
        """Allow overdraft up to a limit."""
        if self._balance + self.overdraft_limit < amount:
            raise InsufficientFundsError("Exceeds overdraft limit")
        self._balance -= amount
        self._log_transaction("WITHDRAW", -amount)

    def calculate_interest(self) -> float:
        """No interest for checking accounts."""
        return 0.0

# ====== BANK SYSTEM ======


class Bank:
    def __init__(self):
        self._accounts: Dict[str, Account] = {}

    def open_account(self, account: Account) -> None:
        """Register a new account."""
        if account.account_id in self._accounts:
            raise ValueError("Account ID already exists")
        self._accounts[account.account_id] = account

    def transfer(self, from_id: str, to_id: str, amount: float) -> None:
        """Transfer money between accounts."""
        if from_id not in self._accounts or to_id not in self._accounts:
            raise ValueError("One or more accounts do not exist")

        from_account = self._accounts[from_id]
        to_account = self._accounts[to_id]

        # Check for potential fraud (large transfer)
        if amount > 10_000 and from_account.balance < 50_000:
            raise FraudDetectionError("Suspicious large transfer")

        from_account.withdraw(amount)
        to_account.deposit(amount)

    def apply_interest(self) -> None:
        """Apply interest to all savings accounts."""
        for account in self._accounts.values():
            if isinstance(account, SavingsAccount):
                interest = account.calculate_interest()
                if interest > 0:
                    account.deposit(interest)

    def save_to_file(self, filename: str) -> None:
        """Save all accounts to a JSON file."""
        data = {
            "accounts": [acc.to_dict() for acc in self._accounts.values()],
            "timestamp": datetime.datetime.now().isoformat()
        }
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load_from_file(cls, filename: str) -> 'Bank':
        """Load accounts from a JSON file."""
        bank = cls()
        with open(filename, "r") as f:
            data = json.load(f)

        for acc_data in data["accounts"]:
            account_type = acc_data.pop("type")
            if account_type == "SavingsAccount":
                account = SavingsAccount(**acc_data)
            else:
                account = CheckingAccount(**acc_data)
            bank.open_account(account)
        return bank


# ====== DEMO ======
if __name__ == "__main__":
    bank = Bank()

    # Create accounts
    alice_savings = SavingsAccount("SA001", "Alice", 1000.0)
    bob_checking = CheckingAccount(
        "CA001", "Bob", 500.0, overdraft_limit=200.0)

    bank.open_account(alice_savings)
    bank.open_account(bob_checking)

    # Perform transactions
    alice_savings.deposit(200.0)
    bob_checking.withdraw(600.0)  # Uses overdraft
    bank.transfer("SA001", "CA001", 300.0)

    # Apply interest
    bank.apply_interest()

    # Print balances
    print(f"Alice's savings: ${alice_savings.balance:.2f}")
    print(f"Bob's checking: ${bob_checking.balance:.2f}")

    # Save/Load demo
    bank.save_to_file("bank_data.json")
    loaded_bank = Bank.load_from_file("bank_data.json")
    print(
        f"Loaded Bob's balance: ${loaded_bank._accounts['CA001'].balance:.2f}")
