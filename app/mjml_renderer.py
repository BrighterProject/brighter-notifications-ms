import re
import subprocess
from pathlib import Path
from typing import Any

from loguru import logger

TEMPLATES_DIR = Path(__file__).parent / "templates" / "emails"

# Use the local binary directly — avoids ~1-2s npx package-resolution overhead per call
_MJML_BIN = Path(__file__).parent.parent / "node_modules" / ".bin" / "mjml"
_MJML_CMD = str(_MJML_BIN) if _MJML_BIN.exists() else "mjml"

# Compiled at module load: template name → (html_with_placeholders, subject)
_TEMPLATE_CACHE: dict[str, tuple[str, str]] = {}

# Matches leftover {{ key }} placeholders not supplied by the caller.
_PLACEHOLDER_RE = re.compile(r"\{\{\s*[\w.]+\s*\}\}")


def _compile_mjml_file(mjml_path: Path) -> str:
    """Compile a single MJML file to HTML via the CLI.

    Args:
        mjml_path: Absolute path to the .mjml source file.

    Returns:
        Minified HTML string.

    Raises:
        RuntimeError: If the mjml CLI fails or is not found.
    """
    try:
        result = subprocess.run(
            [
                _MJML_CMD,
                str(mjml_path),
                "-o",
                "/dev/stdout",
                "--config.minify=true",
                "--config.validationLevel=strict",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(
            "MJML compilation failed for {}: stderr={} stdout={}",
            mjml_path,
            e.stderr,
            e.stdout,
        )
        raise RuntimeError(f"Failed to compile MJML {mjml_path}: {e.stderr}") from e
    except FileNotFoundError as e:
        logger.error("mjml CLI not found. Is it installed? {}", e)
        raise RuntimeError("mjml CLI not found. Install with: npm install -D mjml") from e


def _extract_subject(html: str, template_name: str) -> str:
    """Extract email subject from the <title> tag in compiled HTML.

    Args:
        html: Compiled HTML string.
        template_name: Fallback label if no title is found.

    Returns:
        Subject string.
    """
    match = re.search(r"<title[^>]*>([^<]+)</title>", html, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return f"Notification from Brighter ({template_name})"


def _build_template_cache() -> dict[str, tuple[str, str]]:
    """Compile every MJML template and extract subjects at startup.

    Returns:
        Mapping of template stem → (compiled_html, subject).

    Raises:
        RuntimeError: If any template fails to compile.
    """
    cache: dict[str, tuple[str, str]] = {}
    for mjml_path in sorted(TEMPLATES_DIR.glob("*.mjml")):
        name = mjml_path.stem
        logger.info("Compiling MJML template: {}", name)
        html = _compile_mjml_file(mjml_path)
        subject = _extract_subject(html, name)
        cache[name] = (html, subject)
        logger.debug("Compiled MJML template: {} subject={!r}", name, subject)
    if not cache:
        logger.warning("No MJML templates found in {}", TEMPLATES_DIR)
    return cache


# Compile all templates once at module load.
# Fails fast if the mjml CLI is unavailable or a template is invalid MJML.
_TEMPLATE_CACHE = _build_template_cache()


def render_mjml_template(template_name: str, data: dict[str, Any]) -> tuple[str, str]:
    """Render a pre-compiled MJML template by substituting {{key}} placeholders.

    All substitution happens via plain str.replace on the cached HTML — no
    subprocess, no disk I/O, no regex at render time.

    Args:
        template_name: Template stem (e.g. "payment_receipt").
        data: Variable map; each key replaces its {{key}} placeholder.

    Returns:
        (subject, html) tuple with all placeholders replaced.

    Raises:
        KeyError: If template_name was not compiled at startup.
    """
    if template_name not in _TEMPLATE_CACHE:
        raise KeyError(f"Template not compiled at startup: {template_name!r}")

    html, subject = _TEMPLATE_CACHE[template_name]
    for key, value in data.items():
        if value is not None:
            html = html.replace(f"{{{{{key}}}}}", str(value))

    # Strip any placeholders the caller did not supply so raw {{key}} tokens
    # never leak into a delivered email.
    html = _PLACEHOLDER_RE.sub("", html)

    return subject, html
