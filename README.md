# better-exceptions, customized for Gentoo

Parent: https://github.com/Qix-/better-exceptions

## Jist install Gentoo and python3.7

    root> emerge -avNu python-pip
    root> emerge -avNu pygments
    pip install --user better-exceptions
    #Pip puts the stuffs under ~/.local/lib/python3.7/site-packages/better_exceptions

    #put this in your ~/.bashrc or just-in-time before the invocation of the python3 interpreter:
    export BETTER_EXCEPTIONS=1

    #I put something like this in my .bashrc, that way I can flip it on or off as needed
    alias python37_with_better_exceptions="BETTER_EXCEPTIONS=1 python3 "

## Jist install Gentoo and python2.7

    curl https://bootstrap.pypa.io/get-pip.py --output get-pip.py
    root> python2 get-pip.py
    pip2.7 install --user better-exceptions
    pip2.7 install --user pygments

    #Pip2.7 puts the stuffs under ~/.local/lib64/python2.7/site-packages/better_exceptions

    #put this in your ~/.bashrc or just-in-time before the invocation of the python3 interpreter:
    export BETTER_EXCEPTIONS=1

    #I put something like this in my .bashrc, that way I can flip it on or off as needed
    alias python27_with_better_exceptions="BETTER_EXCEPTIONS=1 python2.7 "


![Just better_exceptions](screenshot.png)

![Hybrid better_exceptions and pygments](https://i.imgur.com/au4LEJV.png)

## Demo

![demo](demogif.gif)




# License
Copyright &copy; 2017, Josh Junon. Licensed under the [MIT license](LICENSE.txt).
