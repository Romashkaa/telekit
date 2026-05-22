class Debug:
    timeout_warnings: bool = False
    deletion_warnings: bool = False
    callback_query_tracing: bool = False

    @classmethod
    def set_all(cls, value: bool) -> None:
        for key in cls.__annotations__:
            setattr(cls, key, value)