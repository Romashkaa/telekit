import telekit

class TrackHandoffOrigin(telekit.Handler):

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
    def is_handoffed(self) -> bool:
        """
        Whether this handler was reached via :meth:`handoff`.

        - ``True`` if a previous handler transferred control here,
        - ``False`` if this handler was invoked directly.
        """
        return self.handoff_origin is not None
    
    def handoff_back(self):
        """
        Transfer control back to the handler that handed off to this one.

        Useful for implementing "« Back" buttons without hardcoding the
        previous handler class:

        .. code-block:: python

            self.chain.set_inline_keyboard({
                "« Back": self.handoff_back
            })

        :raises RuntimeError: If this handler was not reached via :meth:`handoff`
                            (i.e. ``handoff_origin`` is ``None``).
        """
        if self.handoff_origin is None:
            raise RuntimeError(
                f"{type(self).__name__}().handoff_back() called, but this handler "
                "was not reached via handoff() - handoff_origin is None."
            )
        
        self.handoff_origin.handle()

    def handoff_back_or(self, handler: type[telekit.Handler] | str):
        """
        Return a callable that transfers control back to the origin handler,
        or falls back to ``handler`` if this handler was invoked directly.

        Useful for ``« Back`` buttons in handlers that can be reached both
        via :meth:`handoff` and directly:

        .. code-block:: python

            self.chain.set_inline_keyboard({
                "« Back": self.handoff_back_or(StartHandler)
            })

        :param handler: Fallback handler class (or name) to transfer control to when
                        ``handoff_origin`` is ``None``.
        :type handler: ``type[Handler]`` | ``str``
        :return: A zero-argument callable that performs the handoff.
        :rtype: ``Callable[[], None]``
        """
        def handoff_invoker():
            if self.handoff_origin is None:
                self.handoff(handler).handle()
            else:
                self.handoff_back()
                    
        return handoff_invoker