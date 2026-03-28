# Changelog

This changelog will include all significant changes to the Syntactical programming language.

## [Unreleased]

- Add \_\_main\_\_.py so it can be run with `python3 -m syntactical` (or `python -m syntactical`).

## 4.0.1

- **HOTFIX**: Fix the bug that stopped you from importing other Syntactical files into your script.

## 4.0.0

- **REMOVED**: The `--python` switch will stop working on this release. You should start using `--output` (or `-o`) instead.
- Add the new `--output` (`-o`) option to specify a file to save the compiled Python code to instead of running it (replacement for removed `--python` switch).
- **REMOVED**: Removed the old `toPython()` function. It can no longer be used. The new `compile()` works just like `toPython()` used to.
- Make it so that outputted code only has needed imports.
- Change what the CLI calls itself (switch from 'Syntactical Language Runner' to 'Syntactical \<version\>').

## 3.4.0

- Lots of improvements to code comments and stucture.
- Some new/improved documentation.
- Add `match` statement.

## 3.3.3

- Rename function `toPython()` to `compile()`
- **DEPRECATED**: `toPython()` still works (for now), but will be removed soon; stop using it.
- GitHub Releases had some issues, so I guess I'm stopping using it *again*. All releases will only be on PyPI now.

## 3.3.2

- Fix bug where circular imports were present due to how the version variable was defined.

## 3.3.1

- Fix a bug where you can't import the externally importable functions.

## 3.3.0

- Fix the bug where the minus incrementer wouldn't work no matter what.
- Add feature so that `import` can be used to import other Python or Syntactical files into your code.
- Some documentation changes.

## 3.2.1

- Some minor tweaks to documentation.
- Refactors in code.
- This is mostly a test release.
- Starting using GitHub releases (again).

## 3.2.0

- Add `sleep()` function.
- Add externally importable functions for compiling and running Syntactical from your own Python or Syntactical programs (under developement).

## 3.1.0

- Make it so functions called "initialization" act as the init method for a class.

## 3.0.1

- Immprove an error message.
- Use less dependancies.

## 3.0.0

- Make `--version` more robust and stop using hardcoding for versions.
- Minor README changes.
- **BREAKING**: Change lambda syntax (for the last time)

## 2.2.2

- Fix some code styling.
- Add some more code comments.
- **VITAL**: Fix bug where pathlib and/or pillow not being installed stopped Syntactical from running.

## 2.2.1

- Fix issue [#7](https://github.com/thecoolguy62aws/syntactical/issues/7)

## 2.2.0

- Improve comments.
- Add iterable for loops.
- Add `break`, `continue`, and `pass` statements.
- Add `global` statement.

## 2.1.0

- Start using semantic commit messages.
- Change names of json functions and add some new ones.

## 2.0.0

- Improve annonymous function syntax and move away from `lambda` keyword.

## 1.6.2

- Fix issue [#5](https://github.com/thecoolguy62aws/syntactical/issues/5)

## 1.6.1

- Fix issue [#2](https://github.com/thecoolguy62aws/syntactical/issues/2)

## 1.6.0

- Add else if statements

## 1.5.3

- Fix bug where **literly** no code would work, regardless of the syntax.

## 1.5.2

- Fix bug where you had to enter filename argument even when --version was used.

## 1.5.1

- Add `--version` option.
- Add `exit()` and `stop()` as aliases of Python `exit()`.

## 1.5.0

- Add modulo operator `%`. Now we can make FizzBuzz!

## 1.4.1

- Add error message easter egg. Only one way to find out what this is!

## 1.4.0

**NOTE**: This release _should_ have been called 2.0.0 because it's not backwards compatible. But, no one uses this language yet so it doesn't really matter (and I don't want to go to version 2 this early)

- Change `use` keyword to `import` as it's more accurate about what it does.

## 1.3.3

- Make dependancies more robust

## 1.3.2

- Add egg info to gitignore
- Add publish script to gitignore
- Add PyPi description
- Add changelog

## 1.3.1

- Start switching from a Windows EXE file to a PIP install.

## 1.1.1

I am adding this _long_ after the real version, and my git logs are **BAD**. I don't really understand these so I'll just dump them here (you'll see what I mean):

```
657e091 (tag: v1.1.1) remove keyboard module
bce116f ignore venv
96fbfc6 GUESS I CANT IGNORE IT STUPID GIT
143b4b0 ignore this
11ecfd7 fix build
716a15f remove scrapy
f4ed8f8 change compile
a63689c change comile
a2f40b2 new compile
bd725c0 actually, i want that there
e7f2296 change build system
5f4509a that shouldn't be there
4984f0b hi scrapy
0282dd9 bye scrapy
57355d0 fix pygame
d794630 Add build script
a4b7fba Add pynput and pick support
dc0b5ea dumb comment
```

## 1.1.0

- Change the format of JSON Functions.
- I added, then removed `.env` support (according to my git logs). I'm not sure why.
- Add `--python` and `-p` options.
- Change lambda syntax.
- Change lambda syntax (again).
- Fix modules.
- I also had a git commit with this message:

  ```
  3609aa7 never mind! it doesn't work like that
  ```

  I'm not entirely sure what this means.

## 1.0.0 alpha

- **🎉 FIRST COMMIT!**
- Start making docs.
- Add basics of interpreter.
