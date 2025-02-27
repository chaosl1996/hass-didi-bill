from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN

async def async_setup(hass: HomeAssistant, config: ConfigType):
    """加载 Home Assistant 配置（不再使用 `configuration.yaml`）"""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """从配置入口（config flow）加载组件"""
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """卸载实体"""
    return await hass.config_entries.async_forward_entry_unload(entry, "sensor")
