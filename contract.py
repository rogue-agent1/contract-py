#!/usr/bin/env python3
"""Design by contract — preconditions, postconditions, invariants."""
import functools, sys

def requires(*conditions):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args,**kwargs):
            for cond in conditions:
                if not cond(*args,**kwargs):
                    raise AssertionError(f"Precondition failed for {fn.__name__}")
            return fn(*args,**kwargs)
        return wrapper
    return decorator

def ensures(check):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args,**kwargs):
            result=fn(*args,**kwargs)
            if not check(result,*args,**kwargs):
                raise AssertionError(f"Postcondition failed for {fn.__name__}")
            return result
        return wrapper
    return decorator

def invariant(check):
    def decorator(cls):
        orig_init=cls.__init__
        def new_init(self,*args,**kwargs):
            orig_init(self,*args,**kwargs)
            if not check(self): raise AssertionError(f"Invariant violated after __init__")
        cls.__init__=new_init
        for name in list(vars(cls)):
            method=getattr(cls,name)
            if callable(method) and not name.startswith('_'):
                def make_wrapper(m):
                    @functools.wraps(m)
                    def wrapper(self,*args,**kwargs):
                        result=m(self,*args,**kwargs)
                        if not check(self): raise AssertionError(f"Invariant violated after {m.__name__}")
                        return result
                    return wrapper
                setattr(cls,name,make_wrapper(method))
        return cls
    return decorator

@invariant(lambda self: self.balance>=0)
class BankAccount:
    def __init__(self,balance=0): self.balance=balance
    @requires(lambda self,amount: amount>0)
    @ensures(lambda result,self,amount: self.balance>=amount)
    def deposit(self,amount): self.balance+=amount; return self.balance
    @requires(lambda self,amount: amount>0 and amount<=self.balance)
    def withdraw(self,amount): self.balance-=amount; return self.balance

if __name__ == "__main__":
    acc=BankAccount(100)
    print(f"  Deposit: {acc.deposit(50)}")
    print(f"  Withdraw: {acc.withdraw(30)}")
    try: acc.withdraw(200); print("  Should not reach here")
    except AssertionError as e: print(f"  Contract violation: {e}")
    try: BankAccount(-10)
    except AssertionError as e: print(f"  Invariant violation: {e}")
