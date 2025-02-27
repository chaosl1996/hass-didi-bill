import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

DOMAIN = "didi_bill"

class DidiBillConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """DiDi Bill 配置 UI"""

    async def async_step_user(self, user_input=None):
        """用户输入 URL 进行配置"""
        if user_input is not None:
            return self.async_create_entry(title="DiDi Bill", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("api_url"): str
            })
        )

    @staticmethod
    @callback
    def async_get_options_flow(entry):
        return DidiBillOptionsFlowHandler(entry)

class DidiBillOptionsFlowHandler(config_entries.OptionsFlow):
    """DiDi Bill 配置选项"""
    def __init__(self, entry):
        self.entry = entry

    async def async_step_init(self, user_input=None):
        """允许修改 URL"""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("api_url", default=self.entry.options.get("api_url", "")): str
            })
        )
