import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, CONF_API_URL, CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL

class DiDiBillConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """滴滴账单的配置流程"""

    async def async_step_user(self, user_input=None):
        """UI 界面配置"""
        errors = {}
        if user_input is not None:
            return self.async_create_entry(
                title="滴滴账单", data=user_input
            )

        schema = vol.Schema({
            vol.Required(CONF_API_URL, description={"suggested_value": ""}): str,
            vol.Optional(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): int,
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
