"""steamboat.core.exceptions"""


# ruff: noqa: N818
class StepRunSkip(Exception):
    """Exception to raise when a Step is intentionally skipping completion."""


class StepRunError(Exception):
    """Exception to raise when a Step wants to bubble up an error."""
