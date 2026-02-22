# -- Imports -- #
from typing import get_type_hints, get_origin, get_args, Callable, TypeAlias, Any, Protocol, Union
import tkinter

# -- Decerators -- #
def add_attributes(**attributes) -> Callable:
    # -- Adds an Attribute to A Function -- #
    def decerator(function: Callable) -> Callable:
        for key, value in attributes.items():
            setattr(function, key, value)
        return function
    return decerator

def add_attributes_function(function: Callable, attributes: dict) -> None:
    for key, value in attributes.items():
        setattr(function, key, value)

def origin(hint: type) -> type | TypeAlias:
    if hint != None:
        temp_hint = get_origin(hint)

        if temp_hint != None and temp_hint != Union:
            hint = temp_hint

    return hint

def get_union(hint: type | TypeAlias) -> list[type | TypeAlias]:
    hint = origin(hint)

    try: hints = hint.__args__
    except: hints = [hint]

    hints = [origin(hint) for hint in hints]

    return hints

def is_instance(value: Any, hint: type | TypeAlias) -> bool:
    # -- Placing Type Cleaning Into Instance Check -- #
    if type(hint) is type:
        return isinstance(value, hint)
    else: 
        return type(value) is TypeAlias
    
def any_instance(value: Any, hint: type | TypeAlias) -> bool:
    result: bool = False
    hints = get_union(hint)

    for hint in hints:
        if is_instance(value, int) and (hint == float) and (not result): 
            value = float(value) # -- Removes Half-Correct floats as int -- #

        result = result or is_instance(value, hint)

    return result

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

                # -- Protocols Are Meant To Take Many Forms -- #
                for subclass in Protocol.__subclasses__():
                    if hint == subclass or hint == Any:
                        break
                else:
                    assert any_instance(value, hint), f"Argument {key} must be of type {hint} but value = {value} of type {type(value)} provided"

            except IndexError: pass  # -- Ignores The No Given Hint Case -- #

        result = func(*args, **kwargs) # -- Performs The Function Normally -- #
        assert any_instance(result, return_hint), f"Return Value must be of type {return_hint} but value = {result} of type {type(result)} provided" # -- Checks For Correct Output Type -- #
        return result
    
    return wrapper # -- Sends The Checking Function -- #

@enforce_types
def capitalise_words(input_string: str, split: str = " ") -> str:
    words: list[str] = input_string.split(split)
    output: str = ""

    for word in words:
        word = word.lower().capitalize()
        output += word + " "

    output = output[0:-1]
    return output