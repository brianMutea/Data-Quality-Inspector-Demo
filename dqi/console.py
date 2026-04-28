"""Rich console utilities for DataQualityInspector.

This module provides shared Rich console instance and helper functions
for creating progress bars, styled output, and visual enhancements.
"""

from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn,
)
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

# Shared console instance
console = Console()


def get_progress() -> Progress:
    """Create a Rich Progress instance with custom columns.

    Returns:
        Progress: Configured progress bar with spinner, text, bar, and timing columns.
    """
    return Progress(
        SpinnerColumn(style="cyan", spinner_name="dots"),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(complete_style="green", finished_style="bright_green"),
        TaskProgressColumn(),
        "•",
        TimeRemainingColumn(),
        console=console,
    )


def get_spinner_progress(description: str = "Loading...") -> Progress:
    """Create a simple spinner progress for indeterminate tasks.

    Args:
        description: Text to display next to the spinner.

    Returns:
        Progress: Configured spinner progress bar.
    """
    return Progress(
        SpinnerColumn(style="yellow", spinner_name="dots"),
        TextColumn(f"[yellow]{description}"),
        console=console,
    )


def print_header(title: str, subtitle: str | None = None) -> None:
    """Print a styled header panel.

    Args:
        title: Main title text.
        subtitle: Optional subtitle text.
    """
    text = Text()
    text.append(title, style="bold cyan")
    if subtitle:
        text.append("\n")
        text.append(subtitle, style="dim")
    console.print(Panel(text, border_style="cyan", box=box.ROUNDED))


def print_success(message: str) -> None:
    """Print a success message with a green checkmark.

    Args:
        message: Success message to display.
    """
    console.print(f"[bold green]✓[/bold green] {message}")


def print_warning(message: str) -> None:
    """Print a warning message with a yellow warning symbol.

    Args:
        message: Warning message to display.
    """
    console.print(f"[bold yellow]⚠[/bold yellow] {message}")


def print_error(message: str) -> None:
    """Print an error message with a red X.

    Args:
        message: Error message to display.
    """
    console.print(f"[bold red]✗[/bold red] {message}")


def print_info(message: str) -> None:
    """Print an informational message with a blue info symbol.

    Args:
        message: Info message to display.
    """
    console.print(f"[bold blue]ℹ[/bold blue] {message}")


def create_summary_table() -> Table:
    """Create a styled table for summary results.

    Returns:
        Table: Configured Rich table for displaying check summaries.
    """
    table = Table(
        title="[bold cyan]Data Quality Summary[/bold cyan]",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Check", style="cyan", no_wrap=True)
    table.add_column("Status", style="bold", justify="center")
    table.add_column("Detail", style="dim")
    return table


def get_status_style(status: str) -> str:
    """Get Rich style string for a given status.

    Args:
        status: Status string (pass, warn, fail, ok, critical, warning).

    Returns:
        str: Rich style string for the status.
    """
    status_map = {
        "pass": "[bold green]OK[/bold green]",
        "ok": "[bold green]OK[/bold green]",
        "warn": "[bold yellow]WARN[/bold yellow]",
        "warning": "[bold yellow]WARN[/bold yellow]",
        "fail": "[bold red]FAIL[/bold red]",
        "critical": "[bold red]CRITICAL[/bold red]",
        "analysed": "[bold blue]ANALYZED[/bold blue]",
        "skipped": "[bold dim]SKIPPED[/bold dim]",
    }
    return status_map.get(status, f"[bold]{status.upper()}[/bold]")


def print_check_start(check_name: str) -> None:
    """Print the start of a check with styling.

    Args:
        check_name: Name of the check being started.
    """
    console.print(f"\n[bold cyan]▶ {check_name}...[/bold cyan]")


def print_check_complete(check_name: str, duration: float) -> None:
    """Print the completion of a check with timing.

    Args:
        check_name: Name of the completed check.
        duration: Duration in seconds.
    """
    console.print(f"[bold green]✓ {check_name} completed[/bold green] [dim]({duration:.2f}s)[/dim]")
