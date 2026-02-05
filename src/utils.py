# -- Imports -- #
from typing import get_type_hints, get_origin, Callable, TypeAlias, Any, Protocol

# -- Decerators -- #
def add_attributes(**attributes) -> Callable:
    # -- Adds an Attribute to A Function -- #
    def decerator(function: Callable) -> Callable:
        for key, value in attributes.items():
            setattr(function, key, value)
        return function
    return decerator

def paramaterized_generals(hint: type) -> type:
    # -- Dealing With Parameterized Generals #
    origin: type = get_origin(hint)
    if origin != None:
        origin = str(origin)[8:][:-2]
        data_type: type = eval(origin)
    else:
        data_type: type = hint

    return data_type

def is_instance(value: Any, hint: type | TypeAlias) -> bool:
    # -- Placing Type Cleaning Into Instance Check -- #
    hint = paramaterized_generals(hint)
    if type(hint) is type:
        return isinstance(value, hint)
    else: 
        return type(value) is TypeAlias

def enforce_types(func: Callable) -> Callable:
     # -- Creates Checking Function -- #
    @add_attributes(__name__ = func.__name__)
    def wrapper(*args, **kwargs): # -- Gets Parameter Types and Type Hints -- #
        args_offset: int = 0 if len(func.__qualname__.split(".")) == 1 else 1 # -- Checks If A Method (1) or Class Or Standalone Subroutine (0) -- #
        type_hints = get_type_hints(func) # -- Gets Type Hints or None if Not Given -- #
        return_hint = type_hints.pop('return', None)

        for i, (key, hint) in enumerate(type_hints.items()):
            try:
                value = args[i + args_offset] if kwargs.get(key) is None else kwargs.get(key)  # -- Checks Args then Kwargs For Entered Data Type -- #
                if type(value) == int and hint == float: value = float(value) # -- Removes Half-Correct floats as int -- #

                # -- Protocols Are Meant To Take Many Forms -- #
                for subclass in Protocol.__subclasses__():
                    if hint == subclass or hint == Any:
                        break
                else:
                    assert is_instance(value, hint), f"Argument {key} must be of type {hint} but {value=} of type={type(value)} provided"

            except IndexError: pass  # -- Ignores The No Given Hint Case -- #

        result = func(*args, **kwargs) # -- Performs The Function Normally -- #
        assert is_instance(result, return_hint), f"Return Value must be of type {return_hint} but {result=} of type={type(result)} provided" # -- Checks For Correct Output Type -- #
        return result
    
    return wrapper # -- Sends The Checking Function -- #

# -- Subroutines -- #
@enforce_types
def valid_input_list(input_text: str, failure_text: str, valid_inputs: list[str]) -> str:
    # -- Makes an input that requires a match in the lsit -- #
    valid_inputs: list = [string.lower() for string in valid_inputs]

    while (True):
        try:
          input_string: str = inputLine(input_text)
          assert input_string.lower() in valid_inputs
          return input_string
        except AssertionError:
            printLine(failure_text)
        except:
            printLine("No input detected!")

@enforce_types
def printLine(input_string: str) -> None: print("\n" + input_string)

@enforce_types
def inputLine(input_string: str) -> str: return input("\n" + input_string + ": ")

@enforce_types
def capitalise_words(input_string: str) -> str:
    words: list[str] = input_string.split(" ")
    output: str = ""

    for word in words:
        word = word.lower().capitalize()
        output += word + " "

    output = output[0:-1]
    return output