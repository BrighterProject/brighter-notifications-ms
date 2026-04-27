import re
import subprocess
from pathlib import Path
from typing import Any

from loguru import logger

TEMPLATES_DIR = Path(__file__).parent / "templates" / "emails"

# Use the local binary directly — avoids the ~1-2s npx package-resolution overhead per call
_MJML_BIN = Path(__file__).parent.parent / "node_modules" / ".bin" / "mjml"
_MJML_CMD = str(_MJML_BIN) if _MJML_BIN.exists() else "mjml"


def _apply_conditionals(content: str, data: dict[str, Any]) -> str:
    """Evaluate {{#if variable}}...{{/if}} blocks before MJML compilation."""

    def replace_block(m: re.Match) -> str:
        var_name = m.group(1)
        block_content = m.group(2)
        value = data.get(var_name)
        if value is not None and str(value).strip():
            return block_content
        return ""

    return re.sub(
        r"\{\{#if\s+(\w+)\}\}(.*?)\{\{/if\}\}",
        replace_block,
        content,
        flags=re.DOTALL,
    )


def compile_mjml(mjml_path: str) -> str:
    """
    Compile MJML file to HTML using the mjml CLI.
    Raises RuntimeError if compilation fails.
    """
    try:
        result = subprocess.run(
            [
                _MJML_CMD,
                mjml_path,
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
            "MJML compilation failed: stderr={} stdout={}",
            e.stderr,
            e.stdout,
        )
        raise RuntimeError(f"Failed to compile MJML: {e.stderr}") from e
    except FileNotFoundError as e:
        logger.error("mjml CLI not found. Is it installed? {}", e)
        raise RuntimeError(
            "mjml CLI not found. Install with: npm install -D mjml"
        ) from e


def render_mjml_template(
    template_name: str, data: dict[str, Any]
) -> tuple[str, str]:
    """
    Render an MJML template with the given data.
    Returns (subject, html) tuple.

    Handlebars syntax is used for dynamic content:
      {{variable_name}} → rendered value
      {{#if condition}}...{{/if}} → conditional blocks

    All template variables must be in the data dict. Missing variables
    cause Handlebars errors during rendering.
    """
    mjml_path = TEMPLATES_DIR / f"{template_name}.mjml"

    if not mjml_path.exists():
        raise FileNotFoundError(f"Template not found: {mjml_path}")

    # Read the MJML template
    mjml_content = mjml_path.read_text()

    # Evaluate {{#if variable}}...{{/if}} blocks first
    mjml_content = _apply_conditionals(mjml_content, data)

    # Simple Handlebars rendering: {{key}} → value
    for key, value in data.items():
        if value is not None:
            # Convert non-strings to strings
            str_value = str(value)
            # Replace Handlebars placeholder
            mjml_content = mjml_content.replace(f"{{{{{key}}}}}", str_value)

    # Create a temporary file with the rendered MJML
    temp_mjml = f"/tmp/{template_name}_rendered_{id(mjml_content)}.mjml"
    Path(temp_mjml).write_text(mjml_content)

    try:
        # Compile the MJML to HTML
        html = compile_mjml(temp_mjml)

        # Extract subject from mj-title (basic extraction)
        # The subject is set in mj-title tag
        subject = _extract_subject_from_html(html, template_name)

        return subject, html

    finally:
        # Clean up temp file
        try:
            Path(temp_mjml).unlink()
        except Exception as e:
            logger.warning("Failed to clean up temp file {}: {}", temp_mjml, e)


def _extract_subject_from_html(html: str, template_name: str) -> str:
    """
    Extract the email subject from compiled HTML.
    The subject is embedded in <title> tag by MJML from mj-title.
    """
    import re

    # Look for <title>...</title>
    match = re.search(r"<title[^>]*>([^<]+)</title>", html, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Fallback: derive from template name
    return f"Notification from Brighter ({template_name})"
