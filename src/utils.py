# -- Imports -- #
from typing import get_type_hints, Callable

# -- Subroutines -- #
def enforce_types(func: Callable) -> Callable:
     # -- Creates Checking Function -- #
    def wrapper(*args, **kwargs): # -- Gets Parameter Types and Type Hints -- #
        args_offset: int = 0 if len(func.__qualname__.split(".")) == 1 else 1 # -- Checks If A Method (1) or Class Or Standalone Subroutine (0) -- #
        type_hints = get_type_hints(func) # -- Gets Type Hints or None if Not Given -- #
        return_hint = type_hints.pop('return', None)

        for i, (key, hint) in enumerate(type_hints.items()):
            try:
                value = args[i + args_offset] if kwargs.get(key) is None else kwargs.get(key)  # -- Checks Args then Kwargs For Entered Data Type -- #
                if type(value) == int and hint == float: value = float(value) # -- Removes Half-Correct floats as int -- #
                assert isinstance(value, hint), f"Argument {key} must be of type {hint} but {value=} of type={type(value)} provided" # -- Throws Error For Wrong Type -- #
            except IndexError: pass  # -- Ignores The No Given Hint Case -- #

        result = func(*args, **kwargs) # -- Performs The Function Normally -- #
        assert isinstance(result, return_hint) # -- Checks For Correct Output Type -- #
        return result
    
    return wrapper # -- Sends The Checking Function -- #

@enforce_types
def positive_int(function: Callable) -> Callable:
    # -- Checks If A Function Output Returns A Positive Integer -- #
    def wrapper(*args, **kwargs):
        while (True):
            try:
                data: str = function(*args, **kwargs)
                output: int = int(data)
                assert(output > 0)
                return output
            except ValueError:
                printLine("Input a whole number greater than 0!")
            except AssertionError:
                printLine("This number is not greater than 0!")

    return wrapper

@enforce_types
def printLine(inputString: str) -> None: print("\n" + inputString + "\n")