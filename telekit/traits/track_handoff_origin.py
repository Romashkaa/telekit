from functools import partial
from typing import Callable

import telekit


class TrackHandoffOrigin(telekit.Trait):

    TRACK_HANDOFF_ORIGIN: bool = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.handoff_origin: telekit.Handler | None = None

    def _on_handoff(self, origin: telekit.Handler) -> None:
        """
        Called when this handler is reached via :meth:`handoff`.
        Override to customize handoff behaviour.
        """
        if self.TRACK_HANDOFF_ORIGIN:
            self.handoff_origin = origin

        super()._on_handoff(origin)

    @property
    def is_handed_off(self) -> bool:
        """
        Whether this handler was reached via :meth:`handoff`.

        - ``True`` if a previous handler transferred control here,
        - ``False`` if this handler was invoked directly.
        """
        return self.handoff_origin is not None

    def handoff_back(self, *args, **kwargs):
        """
        Transfer control back to the handler that handed off to this one.

        Useful for implementing "« Back" buttons without hardcoding the
        previous handler class::

            self.chain.set_inline_keyboard({
                "« Back": self.handoff_back
            })

        Any positional or keyword arguments are forwarded directly to
        ``handoff_origin.handle()``::

            self.handoff_back("some_arg", key="value")
            # equivalent to: handoff_origin.handle("some_arg", key="value")

        :raises RuntimeError: If this handler was not reached via
            :meth:`handoff` (i.e. ``handoff_origin`` is ``None``).
        """
        if self.handoff_origin is None:
            raise RuntimeError(
                f"{type(self).__name__}().handoff_back() called, but this handler "
                "was not reached via handoff() - handoff_origin is None."
            )
        self.handoff_origin.chain._set_previous_message(self.chain.get_previous_message())
        self.handoff_origin.handle(*args, **kwargs)

    def handle_handoff_back_or(
        self,
        handler: type[telekit.Handler] | str,
        *args,
        **kwargs,
    ) -> None:
        """
        Transfer control back to the origin handler, or to ``handler`` if
        this handler was invoked directly, and immediately run its ``handle()``.

        Unlike :meth:`handoff_back_or`, it takes the fallback handler as an
        argument, so it can be passed directly as a callback together with
        its arguments, without creating an extra closure::

            self.chain.add_callback(
                "« Back",
                self.handle_handoff_back_or,
                [StartHandler],
            )

        It can also be called directly. Any extra positional or keyword
        arguments are forwarded to ``handle()`` of whichever handler is
        invoked::

            self.handle_handoff_back_or(StartHandler, "some_arg", key="value")
            # if handed off:  handoff_origin.handle("some_arg", key="value")
            # if direct:      StartHandler.handle("some_arg", key="value")

        :param handler: Fallback handler class (or name) to transfer control
            to when ``handoff_origin`` is ``None``.
        :type handler: type[Handler] | str

        :raises NameError: If a string name is provided but no registered
            handler exists with that name.
        :raises TypeError: If the provided value is not a ``Handler`` subclass.

        .. seealso:: :meth:`handoff_back`, :meth:`handoff_back_or`
        """
        if self.handoff_origin is None:
            self.handoff(handler).handle(*args, **kwargs)
        else:
            self.handoff_back(*args, **kwargs)

    def handoff_back_or(self, handler: type[telekit.Handler] | str) -> Callable[..., None]:
        """
        Return a callable that transfers control back to the origin handler,
        or falls back to ``handler`` if this handler was invoked directly.

        Useful for ``« Back`` buttons in handlers that can be reached both
        via :meth:`handoff` and directly::

            self.chain.set_inline_keyboard({
                "« Back": self.handoff_back_or(StartHandler)
            })

        Any positional or keyword arguments passed to the returned callable
        are forwarded to ``handle()`` of whichever handler is invoked::

            back = self.handoff_back_or(StartHandler)
            back("some_arg", key="value")
            # if handed off:  handoff_origin.handle("some_arg", key="value")
            # if direct:      StartHandler.handle("some_arg", key="value")

        :param handler: Fallback handler class (or name) to transfer control
            to when ``handoff_origin`` is ``None``.
        :type handler: type[Handler] | str

        :return: A callable that performs the handoff; it accepts any
            arguments and forwards them to ``handle()``.
        :rtype: Callable[..., None]

        .. seealso:: :meth:`handle_handoff_back_or` — a closure-free
            alternative for use as a callback.
        """
        return partial(self.handle_handoff_back_or, handler)