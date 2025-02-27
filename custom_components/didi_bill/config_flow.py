import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from .const import DOMAIN, CONF_API_URL, CONF_UPDATE_INTERVAL

class DiDiBillConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """滴滴账单配置流"""

    async def async_step_user(self, user_input=None):
        """UI 配置界面"""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(title="滴滴账单", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_URL): str,
                    vol.Optional(CONF_UPDATE_INTERVAL, default=30): int,
                }
            ),
            errors=errors,
        )
