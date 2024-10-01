import logging
import sys
from typing import Any, Dict

import click
from pydantic import ValidationError

from aeternum.core.errors import AeternumBaseError, ExitCode

logger = logging.getLogger(__name__)


class AeternumCliHandler(click.Group):
    """A wrapped around CLI invocation that handles related errors."""

    AUTHOR_DETAILS: Dict[str, str] = {
        "Author": "Chino Franco",
        "Github": "https://github.com/jgfranco17",
    }

    def invoke(self, ctx: click.Context) -> Any:
        """Invoke the CLI and catch, log and exit for any raised errors."""
        try:
            return super().invoke(ctx)
        except click.UsageError as err:
            err.show()
            sys.exit(ExitCode.RUNTIME_ERROR)

        except AeternumBaseError as err:
            if ctx.obj.get("debug_logging", True):
                logger.exception(err)
            else:
                error_str = err.message
                cause = err.__cause__
                while cause is not None:
                    error_str = f"{error_str}\n\t{cause}"
                    cause = cause.__cause__
                logger.error(error_str)
            click.secho(f"{err.help_text}", fg="yellow")
            sys.exit(err.exit_code)

    def format_help(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        """Customize help info."""
        super().format_help(ctx, formatter)
        details = "\n".join(
            [f"{key}: {value}" for key, value in self.AUTHOR_DETAILS.items()]
        )
        formatter.write(f"\n{details}")
