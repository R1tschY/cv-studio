"""Alternative to reload().

Original from Guido van Rossum. Licence unknown.
* https://mail.python.org/pipermail/edu-sig/2007-February/007787.html
* http://svn.python.org/projects/sandbox/trunk/xreload/

This works by executing the module in a scratch namespace, and then
patching classes, methods and functions in place.  This avoids the
need to patch instances.  New objects are copied into the target
namespace.

Some of the many limitiations include:

- Global mutable objects other than classes are simply replaced, not patched

- Code using metaclasses is not handled correctly

- Code creating global singletons is not handled correctly

- Functions and methods using decorators (other than classmethod and
  staticmethod) is not handled correctly

- Renamings are not handled correctly

- Dependent modules are not reloaded

- When a dependent module contains 'from foo import bar', and
  reloading foo deletes foo.bar, the dependent module continues to use
  the old foo.bar object rather than failing

- Frozen modules and modules loaded from zip files aren't handled
  correctly

- Classes involving __slots__ are not handled correctly
"""
import imp
import importlib
import logging
import pkgutil
import sys
from types import FunctionType, MethodType

# TODO:
#  * Enums
#  * ABC, abstractmethod
#  * __slots__
#  * __bases__
#  * Perf: set attrs only when necessary
#  * properties
#  * wrapped functions (funcutils.wraps)
#  * ClosureChanged: If the closure changed, we need to replace the entire function
#  * __weakref__, __module__


logger = logging.getLogger("pyhotreload")


def _closure_changed(oldcl, newcl):
    old = oldcl is None and -1 or len(oldcl)
    new = newcl is None and -1 or len(newcl)
    if old != new:
        return True
    if old > 0 and new > 0:
        for i in range(old):
            same = oldcl[i] == newcl[i]
            if not same:
                return True
    return False


def xreload(mod):
    """Reload a module in place, updating classes, methods and functions.

    Args:
      mod: a module object

    Returns:
      The (updated) input object itself.
    """
    # Get the module name, e.g. 'foo.bar.whatever'
    modname = mod.__name__
    # Get the module namespace (dict) early; this is part of the type check
    modns = mod.__dict__
    # Parse it into package name and module name, e.g. 'foo.bar' and 'whatever'
    i = modname.rfind(".")
    if i >= 0:
        pkgname, modname = modname[:i], modname[i+1:]
    else:
        pkgname = None

    # Compute the search path
    if pkgname:
        # We're not reloading the package, only the module in it
        path = sys.modules[pkgname].__path__  # Search inside the package
    else:
        # Search the top-level module path
        path = None  # Make find_module() uses the default search path

    # Find the module; may raise ImportError
    # TODO: port to new import logic using importlib.util.find_spec and loader
    (stream, filename, (suffix, mode, kind)) = imp.find_module(modname, path)
    # Turn it into a code object
    try:
        # Is it Python source code or byte code read from a file?
        if kind not in (imp.PY_COMPILED, imp.PY_SOURCE):
            # Fall back to built-in reload()
            return importlib.reload(mod)
        if kind == imp.PY_SOURCE:
            source = stream.read()
            code = compile(source, filename, "exec")
        else:
            code = pkgutil.read_code(stream)
    finally:
        if stream:
            stream.close()

    # Execute the code.  We copy the module dict to a temporary; then
    # clear the module dict; then execute the new code in the module
    # dict; then swap things back and around.  This trick (due to
    # Glyph Lefkowitz) ensures that the (readonly) __globals__
    # attribute of methods and functions is set to the correct dict
    # object.
    tmpns = modns.copy()
    modns.clear()
    modns["__name__"] = tmpns["__name__"]
    for attr in ("__file__", "__path__", "__spec__", "__package__"):
        if attr in tmpns:
            modns[attr] = tmpns[attr]

    exec(code, modns)

    # Now we get to the hard part
    oldnames = set(tmpns)
    newnames = set(modns)

    # Update attributes in place
    for name in oldnames & newnames:
        _update(tmpns[name], modns[name])

    return mod


def _update(oldobj, newobj):
    """Update oldobj, if possible in place, with newobj.

    If oldobj is immutable, this simply returns newobj.

    Args:
      oldobj: the object to be updated
      newobj: the object used as the source for the update

    Returns:
      either oldobj, updated in place, or newobj.
    """
    if oldobj is newobj:
        # Probably something imported
        return
    if type(oldobj) is not type(newobj):
        # Cop-out: if the type changed, give up
        return
    if hasattr(newobj, "__hotreload__"):
        # Provide a hook for updating
        newobj.__hotreload__(oldobj)
    if isinstance(newobj, type):
        _update_class(oldobj, newobj)
    if isinstance(newobj, FunctionType):
        _update_function(oldobj, newobj)
    if isinstance(newobj, MethodType):
        _update_method(oldobj, newobj)
    if isinstance(newobj, classmethod):
        _update_classmethod(oldobj, newobj)
    if isinstance(newobj, staticmethod):
        _update_staticmethod(oldobj, newobj)
    # Not something we recognize, just give up
    return


# All of the following functions have the same signature as _update()


def _update_function(oldfunc: FunctionType, newfunc: FunctionType):
    """Update a function object."""
    logger.info(f"Patch function {oldfunc.__qualname__}")
    oldfunc.__doc__ = newfunc.__doc__
    oldfunc.__dict__.update(newfunc.__dict__)
    oldfunc.__annotations__ = newfunc.__annotations__
    oldfunc.__code__ = newfunc.__code__
    oldfunc.__defaults__ = newfunc.__defaults__

    # TODO __closure__
    # old_closure = oldfunc.__closure__ or ()
    # new_closure = newfunc.__closure__ or ()
    # if len(old_closure) != len(new_closure):
    #     print(f"Skipping closure: {oldfunc} changed too much")
    #     return oldfunc
    #
    # for old_cell, new_cell in zip(old_closure, new_closure):
    #     _update(old_cell.cell_contents, new_cell.cell_contents)


def _update_method(oldmeth: MethodType, newmeth: MethodType):
    """Update a method object."""
    # XXX What if __func__ is not a function?
    _update(oldmeth.__func__, newmeth.__func__)


def _update_class(oldclass: type, newclass: type):
    """Update a class object."""
    logger.info(f"Patch class {oldclass.__qualname__}")
    olddict = oldclass.__dict__
    newdict = newclass.__dict__

    oldnames = set(olddict)
    newnames = set(newdict)

    for name in newnames - oldnames:
        setattr(oldclass, name, newdict[name])

    # for name in oldnames - newnames:
    #     delattr(oldclass, name)

    for name in oldnames & newnames - {"__dict__", "__weakref__"}:
        _update(olddict[name], newdict[name])


def _update_classmethod(oldcm: classmethod, newcm: classmethod):
    """Update a classmethod update."""
    # While we can't modify the classmethod object itself (it has no
    # mutable attributes), we *can* extract the underlying function
    # (by calling __get__(), which returns a method object) and update
    # it in-place.  We don't have the class available to pass to
    # __get__() but any object except None will do.
    _update(oldcm.__get__(0), newcm.__get__(0))


def _update_staticmethod(oldsm: staticmethod, newsm: staticmethod):
    """Update a staticmethod update."""
    # While we can't modify the staticmethod object itself (it has no
    # mutable attributes), we *can* extract the underlying function
    # (by calling __get__(), which returns it) and update it in-place.
    # We don't have the class available to pass to __get__() but any
    # object except None will do.
    _update(oldsm.__get__(0), newsm.__get__(0))
