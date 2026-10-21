"""Register a built-in Task Rotation sidebar from Counter integration startup."""

from pathlib import Path

path = Path("homeassistant/components/counter/__init__.py")
if not path.exists():
    raise SystemExit("Run this script from the CORE repository root.")
content = path.read_text()
if "def _register_task_rotation_panel" in content:
    raise SystemExit(0)
import_needle = "from homeassistant.core import HomeAssistant, callback"
if import_needle not in content:
    raise SystemExit(
        "Expected homeassistant.core import not found. Stop without changing files."
    )
content = content.replace(
    import_needle,
    "from homeassistant.const import EVENT_HOMEASSISTANT_STARTED\n"
    "from homeassistant.core import Event, HomeAssistant, callback",
    1,
)
needle = """    component.async_register_entity_service(
        SERVICE_SET_VALUE,
        {vol.Required(VALUE): vol.Coerce(int)},
        "async_set_value",
    )

    return True"""
replacement = '''    component.async_register_entity_service(
        SERVICE_SET_VALUE,
        {vol.Required(VALUE): vol.Coerce(int)},
        "async_set_value",
    )

    @callback
    def _register_task_rotation_panel(_event: Event | None = None) -> None:
        """Expose the frontend Task Rotation demo after frontend setup."""
        from homeassistant.components import frontend  # noqa: PLC0415

        if "frontend" not in hass.config.components:
            return
        if "task-rotation" in hass.data.get(frontend.DATA_PANELS, {}):
            return
        frontend.async_register_built_in_panel(
            hass,
            component_name="task-rotation",
            sidebar_title="Task Rotation",
            sidebar_icon="mdi:clipboard-check",
            frontend_url_path="task-rotation",
        )

    if hass.is_running:
        _register_task_rotation_panel()
    else:
        hass.bus.async_listen_once(
            EVENT_HOMEASSISTANT_STARTED, _register_task_rotation_panel
        )

    return True'''
if needle not in content:
    raise SystemExit(
        "Expected Counter service registration block not found. Stop without changing files."
    )
path.write_text(content.replace(needle, replacement, 1))
