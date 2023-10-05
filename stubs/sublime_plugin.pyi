# Stubs for sublime_plugin (Python 3.5)
#
# NOTE: This dynamically typed stub was automatically generated by stubgen.
from sublime import View, Window, Edit, Buffer
from typing import Any, Optional, Dict, List
assert Optional

# api_ready = ...  # type: bool
# application_command_classes = ...  # type: Any
# window_command_classes = ...  # type: Any
# text_command_classes = ...  # type: Any
# view_event_listener_classes = ...  # type: Any
view_event_listeners = ...  # type: Dict[int, List[ViewEventListener]]
# all_command_classes = ...  # type: Any
# all_callbacks = ...  # type: Any
# profile = ...  # type: Any

# def unload_module(module): ...
# def on_api_ready(): ...
# def is_view_event_listener_applicable(cls, view): ...
# def create_view_event_listeners(classes, view): ...
# def check_view_event_listeners(view): ...
# def attach_view(view): ...

# check_all_view_event_listeners_scheduled = ...  # type: bool

# def check_all_view_event_listeners(): ...
# def detach_view(view): ...
# def event_listeners_for_view(view): ...
# def find_view_event_listener(view, cls): ...
# def on_new(view_id): ...
# def on_new_async(view_id): ...
# def on_clone(view_id): ...
# def on_clone_async(view_id): ...

# class Summary:
#     max = ...  # type: float
#     sum = ...  # type: float
#     count = ...  # type: int
#     def __init__(self) -> None: ...
#     def record(self, x): ...

# def run_callback(event, callback, expr): ...
# def run_view_listener_callback(view, name): ...
# def run_async_view_listener_callback(view, name): ...
# def on_load(view_id): ...
# def on_load_async(view_id): ...
# def on_pre_close(view_id): ...
# def on_close(view_id): ...
# def on_pre_save(view_id): ...
# def on_pre_save_async(view_id): ...
# def on_post_save(view_id): ...
# def on_post_save_async(view_id): ...
# def on_modified(view_id): ...
# def on_modified_async(view_id): ...
# def on_selection_modified(view_id): ...
# def on_selection_modified_async(view_id): ...
# def on_activated(view_id): ...
# def on_activated_async(view_id): ...
# def on_deactivated(view_id): ...
# def on_deactivated_async(view_id): ...
# def on_query_context(view_id, key, operator, operand, match_all): ...
# def normalise_completion(c): ...
# def on_query_completions(view_id, prefix, locations): ...
# def on_hover(view_id, point, hover_zone): ...
# def on_text_command(view_id, name, args): ...
# def on_window_command(window_id, name, args): ...
# def on_post_text_command(view_id, name, args): ...
# def on_post_window_command(window_id, name, args): ...


class Command:
    def name(self) -> str:
        ...

    # def is_enabled_(self, args): ...
    def is_enabled(self) -> bool:
        ...

    # def is_visible_(self, args): ...
    def is_visible(self) -> bool:
        ...

    # def is_checked_(self, args): ...
    def is_checked(self) -> bool:
        ...

    # def description_(self, args): ...
    def description(self) -> str:
        ...

    # def filter_args(self, args): ...
    def want_event(self) -> bool:
        ...


class ApplicationCommand(Command):
    ...


class WindowCommand(Command):
    window = ...  # type: Window

    def __init__(self, window: Window) -> None:
        ...

    # def run_(self, edit_token, args): ...

    # def run(self) -> None: (mypy issue #5876).
    #     ...


class TextCommand(Command):
    view = ...  # type: View

    def __init__(self, view: View) -> None:
        ...

    # def run_(self, edit_token, args): ...
    # def run(self, edit: Edit) -> None: (mypy issue #5876)
    #     ...


class EventListener:
    ...


class TextChangeListener:

    buffer = ...  # type: Buffer

    @classmethod
    def is_applicable(cls, buffer: Buffer) -> bool:
        ...

    def __init__(self) -> None:
        ...

    def attach(self, buffer: Buffer) -> None:
        ...

    def detach(self) -> None:
        ...

    def is_attached(self) -> bool:
        ...


class ViewEventListener:
    @classmethod
    def is_applicable(cls, settings: dict) -> bool:
        ...

    @classmethod
    def applies_to_primary_view_only(cls) -> bool:
        ...

    view = ...  # type: View

    def __init__(self, view: View) -> None:
        ...


class CommandInputHandler:
    ...


class TextInputHandler(CommandInputHandler):
    ...


class ListInputHandler(CommandInputHandler):
    ...
