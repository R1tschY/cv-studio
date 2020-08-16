import argparse
import importlib
import logging
import os
import runpy
import sys
from functools import lru_cache
from pathlib import Path
from threading import Condition, Lock, Thread
from types import ModuleType
from typing import Callable, Generic, List, Optional, TypeVar

from pyhotreload.xreload import xreload
from watchdog.observers import Observer
from watchdog.events import EVENT_TYPE_DELETED, FileSystemEvent, \
    FileSystemEventHandler


T = TypeVar("T")
Self = TypeVar("Self")

logger = logging.getLogger("pyhotreload")


def get_root_dirs(dirs):
    dirs = [f"{Path(d).absolute().resolve()}/" for d in dirs]
    dirs.sort(key=len)

    result = []
    for d in dirs:
        x = True
        for r in result:
            if d.startswith(r):
                x = False
                break
        if x:
            result.append(d)
    return result


class BatchedQueue(Thread, Generic[T]):
    def __init__(self, interval: float, function: Callable[[List[T]], None]):
        super().__init__(daemon=True, name="pyhotreload.BatchedQueue")
        self.interval = interval
        self.function = function

        self.items = []
        self._should_exit = False
        self.cond = Condition(Lock())

    def add_item(self, item: T) -> None:
        assert self.is_alive()
        with self.cond:
            self.items.append(item)
            self.cond.notify()

    def close(self) -> None:
        with self.cond:
            self._should_exit = True
            if not self.items:
                self.items = [None]
            self.cond.notify()

        self.join()

    def run(self) -> None:
        logger.info(f"run batched queue")
        while True:
            # wait for first item
            with self.cond:
                while not self.items and not self._should_exit:
                    self.cond.wait()

                logger.info(f"wake up {self.items}")

            if self._should_exit:
                return

            # wait timeout and reset on new item
            with self.cond:
                last_items_len = 0
                while last_items_len != len(self.items) \
                        and not self._should_exit:
                    last_items_len = len(self.items)
                    logger.info(f"wait {self.items}({self.interval})")
                    self.cond.wait(self.interval)
                self.items, items = [], self.items

            if self._should_exit:
                return

            logger.info(f"execute {items}")
            self.function(items)


@lru_cache(maxsize=64)
def file_to_module(file: str) -> Optional[str]:
    _getattr = getattr
    for name, module in sys.modules.items():
        if _getattr(module, "__file__", None) == file:
            return name
    raise ValueError()


class ReloadProcessor:
    batched: BatchedQueue[Path]

    def __init__(self):
        self.batched = BatchedQueue(1.0, self.reload_files)
        self.batched.start()

    def __enter__(self: Self) -> Self:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def close(self) -> None:
        self.batched.close()

    def dispatch(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return

        if os.path.splitext(event.src_path)[-1] != ".py":
            # TODO: what's with binary modules (*.so, *.pyd, ...)?
            return

        if event.event_type == EVENT_TYPE_DELETED:
            return  # TODO
        # TODO: moved

        logger.info(f"Detected change: {event}")
        self.batched.add_item(Path(event.src_path).absolute().resolve())

    def reload_files(self, files: List[Path]):
        try:
            for file in frozenset(files):
                try:
                    module = file_to_module(str(file))
                except ValueError:
                    logging.debug(f"No loaded module found for file {file}")
                    continue

                logger.info(f"Reloading module {module}")
                xreload(sys.modules[module])
        except:
            logger.error(f"Top level exception catched while reloading",
                         exc_info=True)


def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('-m', action="store_true", default=False, dest="mod")
    parser.add_argument('file_or_mod', default=None)
    parser.add_argument('args', nargs=argparse.REMAINDER)
    args = parser.parse_args()

    processor = ReloadProcessor()
    observer = Observer()
    for path in get_root_dirs(sys.path):
        if os.path.isdir(path):
            print(f"Observe: {path}")
            observer.schedule(
                processor, os.path.abspath(path), recursive=True)
    observer.start()

    try:
        sys.argv = [sys.argv[0]] + args.args
        if args.mod:
            runpy.run_module(args.file_or_mod, alter_sys=True)
        else:
            sys.argv[0] = args.file_or_mod
            runpy.run_path(args.file_or_mod)
    finally:
        observer.stop()
        observer.join()
        processor.close()


if __name__ == '__main__':
    main()
