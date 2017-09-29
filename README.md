# better-exceptions

Pretty and more helpful exceptions in Python, automatically.

![Example screenshot of exceptions](screenshot.png)

## Usage Manually

Install `better_exceptions` via pip:

```console
$ pip install better_exceptions
```

And import it somewhere:

```python
import better_exceptions
```

You're done

# 

### Custom Parameters:

If you want to allow the entirety of values to be outputted instead of being truncated to a certain amount of characters:

```python
better_exceptions.MAX_LENGTH = None
```

## Python startup hook so you don't need to `import better_exceptions`

See: https://stackoverflow.com/a/46494872/445131

How to execute the python file defined in $PYTHONSTARTUP when you execute a file like `python foobar.py`
------------------------------------------------------------------------

**Run this command to find out where your OS has defined `USER_SITE`:**

    $ python -c "import site; site._script()" 

**Mine says:**

    USER_SITE: '/home/el/.local/lib64/python2.7/site-packages'

**Create a new file there called `/home/el/.local/lib64/python2.7/site-packages/usercustomize.py`, put this code in there:**

    try:
        import your_things
        import readline
        print("ROCKETMAN!")
    
    except ImportError:
        print("Can't load your things")
        print("Either exit here, or perform remedial actions")
        exit()

**Close the terminal and reopen it to clear out any shenanigans.**

**Make a new file `python foobar.py` anywhere on the filesystem, put this code in there:**

    #Note there is no your_things module imported here.
    #Print your_things version:
    print(your_things.__version__)


**Run it:** 

    python foobar.py 
    ROCKETMAN!
    '1.12.0'

**What just happened.**

You used the python sitewide specific python configuration hook and imported libraries in the `usercustomize.py` file which ran before foobar.py.

Documentation: https://docs.python.org/2/library/site.html

Where I found this trick: https://nedbatchelder.com/blog/201001/running_code_at_python_startup.html



## hold-your-hand setup.py to do the wrapper (not as good as above):

- [paradoxxxzero/better-exceptions-hook](https://github.com/paradoxxxzero/better-exceptions-hook) - removes the need to `import better_exceptions` by adding a startup hook

# License
Copyright &copy; 2017, Josh Junon. Licensed under the [MIT license](LICENSE.txt).
