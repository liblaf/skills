## Google-style

Google-style docstrings.

### Syntax {#google-syntax}

Sections are written like this:

```text
section identifier: optional section title
    section contents
```

All sections identifiers are case-insensitive. All sections support multiple lines in descriptions, as well as blank lines. The first line must not be blank. Each section must be separated from contents above by a blank line.

❌ This is **invalid** and will be parsed as regular markup:

```python
Some text.
Note: # (1)!
    Some information.

    Blank lines allowed.
```

1. Missing blank line above.

❌ This is **invalid** and will be parsed as regular markup:

```python
Some text.

Note: # (1)!

    Some information.

    Blank lines allowed.
```

1. Extraneous blank line below.

✅ This is **valid** and will parsed as a text section followed by a note admonition:

```python
Some text.

Note:
    Some information.

    Blank lines allowed.
```

Find out possibly invalid section syntax by grepping for "reasons" in Griffe debug logs:

```bash
griffe dump -Ldebug -o/dev/null -fdgoogle your_package 2>&1 | grep reasons
```

Some sections support documenting multiple items (attributes, parameters, etc.). When multiple items are supported, each item description can use multiple lines, and continuation lines must be indented once more so that the parser is able to differentiate items.

```python
def foo(a, b):
    """Foo.

    Args:
        a: Here's a.
            Continuation line 1.

            Continuation line 2.
        b: Here's b.
    """
```

It's possible to start a description with a newline if you find it less confusing:

```python
def foo(a, b):
    """Foo.

    Args:
        a:
            Here's a.
            Continuation line 1.

            Continuation line 2.
        b: Here's b.
    """
```

### Admonitions {#google-admonitions}

When a section identifier does not match one of the [supported sections](#google-sections), the section is parsed as an "admonition" (or "callout").

Identifiers are case-insensitive, however singular and plural forms are distinct. For example, `Note:` is not the same as `Notes:`.

In particular, `Examples` is parsed as the [Examples section](#google-section-examples), while `Example` is parsed as an admonition whose kind is `example`.

The kind is obtained by lower-casing the identifier and replacing spaces with dashes. For example, an admonition whose identifier is `See also:` will have a kind equal to `see-also`.

Custom section titles are preserved in admonitions: `Tip: Check this out:` is parsed as a `tip` admonition with `Check this out:` as title.

It is up to any downstream documentation renderer to make use of these kinds and titles.

### Sections {#google-sections}

The following sections are supported.

#### Attributes {#google-section-attributes}

- Multiple items allowed

Attributes sections allow to document attributes of a module, class, or class instance. They should be used in modules and classes docstrings only.

```python
"""My module."""

foo: int = 0
"""Description for `foo`."""
bar: bool = True
"""Description for `bar`."""


class MyClass:
    """My class."""

    foofoo: int = 0
    """Description for `foofoo`."""
    barbar: bool = True
    """Description for `barbar`."""

    def __init__(self):
        self.barbar: bool = True
```

#### Examples {#google-section-examples}

Examples sections allow to add examples of Python code without the use of markup code blocks. They are a mix of prose and interactive console snippets. They can be used in every docstring.

```python
"""My module.

Examples:
    Some explanation of what is possible.

    >>> print("hello!")
    hello!

    Blank lines delimit prose vs. console blocks.

    >>> a = 0
    >>> a += 1
    >>> a
    1
"""
```

WARNING: **Not the same as *Example* sections.**
*Example* (singular) sections are parsed as admonitions. Console code blocks will only be understood in *Examples* (plural) sections.

#### Args {#google-section-parameters}

- Multiple items allowed

Args sections allow to document parameters of a function. They are typically used in functions docstrings, but can also be used in dataclasses docstrings.

```python
def foo(a: int, b: str):
    """Foo.

    Args:
        a: Here's a.
        b: Here's b.
    """
```

#### Keyword Args {#google-section-other-parameters}

- Multiple items allowed

Keyword Args sections allow to document secondary parameters such as variadic keyword arguments, or parameters that should be of lesser interest to the user. They are used the same way Args sections are, but can also be useful in decorators / to document returned callables.

```python
def foo(a, b, **kwargs):
    """Foo.

    Args:
        a: Here's a.
        b: Here's b.

    Keyword Args:
        c (int): Here's c.
        d (bool): Here's d.
    """
```

```python
def foo(a, b):
    """Returns a callable.

    Args:
        a: Here's a.
        b: Here's b.

    Keyword Args: Parameters of the returned callable:
        c (int): Here's c.
        d (bool): Here's d.
    """

    def inner(c, d):
        ...

    return inner
```

TIP: **Types in docstrings are resolved using the docstrings' parent scope.**
See the same tip for parameters.

#### Raises {#google-section-raises}

- Multiple items allowed

Raises sections allow to document exceptions that are raised by a function. They are usually only used in functions docstrings.

```python
def foo(a: int):
    """Foo.

    Args:
        a: A value.

    Raises:
        ValueError: When `a` is less than 0.
    """
    if a < 0:
        raise ValueError("message")
```

TIP: **Exceptions names are resolved using the function's scope.**
`ValueError` and other built-in exceptions are resolved as such. You can document custom exception, using the names available in the current scope, for example `my_exceptions.MyCustomException` or `MyCustomException` directly, depending on what you imported/defined in the current module.

#### Warns {#google-section-warns}

- Multiple items allowed

Warns sections allow to document warnings emitted by the following code. They are usually only used in functions docstrings.

```python
import warnings


def foo():
    """Foo.

    Warns:
        UserWarning: To annoy users.
    """
    warnings.warn("Just messing with you.", UserWarning)
```

TIP: **Warnings names are resolved using the function's scope.**
`UserWarning` and other built-in warnings are resolved as such. You can document custom warnings, using the names available in the current scope, for example `my_warnings.MyCustomWarning` or `MyCustomWarning` directly, depending on what you imported/defined in the current module.

TIP: **Warnings section are not Warning admonitions!**
To create a warning [admonition/callout][google-admonitions], use the singular form:

```text
Warning:
    This is a warning.
```

#### Yields {#google-section-yields}

- Multiple items allowed

Yields sections allow to document values that generator yield. They should be used only in generators docstrings. Documented items can be given a name when it makes sense.

```python
from typing import Iterator


def foo() -> Iterator[int]:
    """Foo.

    Yields:
        Integers from 0 to 9.
    """
    for i in range(10):
        yield i
```

Type annotations are fetched from the function return annotation when the annotation is `typing.Generator` or `typing.Iterator`. If your generator yields tuples, you can document each item of the tuple separately, and the type annotation will be fetched accordingly:

```python
from datetime import datetime


def foo() -> Iterator[tuple[float, float, datetime]]:
    """Foo.

    Yields:
        x: Absissa.
        y: Ordinate.
        t: Time.

    ...
    """
    ...
```

You have to indent each continuation line when documenting yielded values, even if there's only one value yielded:

```python
"""Foo.

Yields:
    partial_result: Some partial result.
        A longer description of details and other information
        for this partial result.
"""
```

Type annotations can as usual be overridden using types in parentheses in the docstring itself:

```python
"""Foo.

Yields:
    x (int): Absissa.
    y (int): Ordinate.
    t (int): Timestamp.
"""
```

If you want to specify the type without a name, you still have to wrap the type in parentheses:

```python
"""Foo.

Yields:
    (int): Absissa.
    (int): Ordinate.
    (int): Timestamp.
"""
```

TIP: **Types in docstrings are resolved using the docstrings' parent scope.**
See previous tips for types in docstrings.

#### Receives {#google-section-receives}

- Multiple items allowed

Receives sections allow to document values that can be sent to generators using their `send` method. They should be used only in generators docstrings. Documented items can be given a name when it makes sense.

```python
from typing import Generator


def foo() -> Generator[int, str, None]:
    """Foo.

    Receives:
        reverse: Reverse the generator if `"reverse"` is received.

    Yields:
        Integers from 0 to 9.

    Examples:
        >>> gen = foo()
        >>> next(gen)
        0
        >>> next(gen)
        1
        >>> next(gen)
        2
        >>> gen.send("reverse")
        2
        >>> next(gen)
        1
        >>> next(gen)
        0
        >>> next(gen)
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
        StopIteration
    """
    for i in range(10):
        received = yield i
        if received == "reverse":
            for j in range(i, -1, -1):
                yield j
            break
```

Type annotations are fetched from the function return annotation when the annotation is `typing.Generator`. If your generator is able to receive tuples, you can document each item of the tuple separately, and the type annotation will be fetched accordingly:

```python
def foo() -> Generator[int, tuple[str, bool], None]:
    """Foo.

    Receives:
        mode: Some mode.
        flag: Some flag.

    ...
    """
    ...
```

You have to indent each continuation line when documenting received values, even if there's only one value received:

```python
"""Foo.

Receives:
    data: Input data.
        A longer description of what this data actually is,
        and what it isn't.
"""
```

Type annotations can as usual be overridden using types in parentheses in the docstring itself:

```python
"""Foo.

Receives:
    mode (ModeEnum): Some mode.
    flag (int): Some flag.
"""
```

If you want to specify the type without a name, you still have to wrap the type in parentheses:

```python
"""Foo.

Receives:
    (ModeEnum): Some mode.
    (int): Some flag.
"""
```

TIP: **Types in docstrings are resolved using the docstrings' parent scope.**
See previous tips for types in docstrings.

#### Returns {#google-section-returns}

- Multiple items allowed

Returns sections allow to document values returned by functions. They should be used only in functions docstrings. Documented items can be given a name when it makes sense.

```python
import random


def foo() -> int:
    """Foo.

    Returns:
        A random integer.
    """
    return random.randint(0, 100)
```

Type annotations are fetched from the function return annotation. If your function returns tuples of values, you can document each item of the tuple separately, and the type annotation will be fetched accordingly:

```python
def foo() -> tuple[bool, float]:
    """Foo.

    Returns:
        success: Whether it succeeded.
        precision: Final precision.

    ...
    """
    ...
```

You have to indent each continuation line when documenting returned values, even if there's only one value returned:

```python
"""Foo.

Returns:
    success: Whether it succeeded.
        A longer description of what is considered success,
        and what is considered failure.
"""
```

Type annotations can as usual be overridden using types in parentheses in the docstring itself:

```python
"""Foo.

Returns:
    success (int): Whether it succeeded.
    precision (Decimal): Final precision.
"""
```

If you want to specify the type without a name, you still have to wrap the type in parentheses:

```python
"""Foo.

Returns:
    (int): Whether it succeeded.
    (Decimal): Final precision.
"""
```

TIP: **Types in docstrings are resolved using the docstrings' function scope.**
See previous tips for types in docstrings.
