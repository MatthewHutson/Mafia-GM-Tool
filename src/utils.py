# -- Imports -- #
from typing import get_type_hints, get_origin, get_args, Callable, TypeAlias, Any, Protocol, Union, Literal, Type, Set
from types import UnionType, FunctionType

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

def union_handler(hint: type | TypeAlias) -> list[type]:
    hint_origin: type = origin(hint)
    
    if hint_origin is Union:
        return list(get_args(hint))
    elif hint_origin is UnionType:
        return list(get_args(hint))
    else:
        return [hint]

def literal_test(value: Any, hint: type) -> bool:
    return value in list(get_args(hint))

def is_instance(value: Any, hint: type | TypeAlias) -> bool:
    # -- Placing Type Cleaning Into Instance Check -- #
    if type(hint) is Literal:
        return literal_test(value, hint)
    elif type(hint) is TypeAlias:
        return type(value) is TypeAlias
    elif type(hint) is type: 
        return isinstance(value, hint)
    return False
    
def ignored_exceptions(value: Any, hint: type | TypeAlias) -> bool:
    if hint == Any: return True

    for subclass in Protocol.__subclasses__():
        if hint == subclass:
            return True
        
    if hint == Literal: return literal_test(value, hint)
    
    return False
    
def any_instance(value: Any, hint: type | TypeAlias) -> bool:
    result: bool = True
    
    for subhint in get_args(hint):
        if not ignored_exceptions(value, subhint):
            result = result and any_instance(value, get_origin(subhint))

    hints: list[type] = union_handler(hint)
    intermediate_result: bool = False

    for subhint in hints:
        intermediate_result = intermediate_result or (is_instance(value, hint) or ignored_exceptions(value, hint))

    result = result or intermediate_result

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
                assert any_instance(value, hint), f"Argument {key} for {func.__name__} must be of type {hint} but value = {value} of type {type(value)} provided"

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
def all_subclasses(cls: Type) -> Set[Type]:
    subclasses: Set[Type] = set(cls.__subclasses__())

    for subclass in subclasses:
        subsubclasses = all_subclasses(subclass)
        subclasses = subclasses.union(subsubclasses)

    return subclasses