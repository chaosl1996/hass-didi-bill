import logging
import requests
from datetime import timedelta
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import CURRENCY_YUAN

from .const import DOMAIN, CONF_API_URL, CONF_UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """设置传感器"""
    api_url = entry.data[CONF_API_URL]
    update_interval = timedelta(minutes=entry.data.get(CONF_UPDATE_INTERVAL, 30))

    coordinator = DiDiBillCoordinator(hass, api_url, update_interval)

    # **修正错误的 `ConfigEntryState` 逻辑**
    await coordinator.async_config_entry_first_refresh()

    async_add_entities([DiDiBillSensor(coordinator)], True)

class DiDiBillCoordinator(DataUpdateCoordinator):
    """管理数据更新"""

    def __init__(self, hass, api_url, update_interval):
        """初始化"""
        super().__init__(hass, _LOGGER, name="滴滴账单", update_interval=update_interval)
        self.api_url = api_url

    async def _async_update_data(self):
        """获取最新账单数据"""
        try:
            response = await self.hass.async_add_executor_job(requests.get, self.api_url)
            data = response.json().get("data", {})
            return {
                "cost": data.get("travel_cost", 0) / 100,  # 分 -> 元
                "count": data.get("travel_count", 0),
                "time": data.get("charge_duration", 0),
                "distance": data.get("travel_distance", 0),
                "month": data.get("title", "").replace("{", "").replace("}", ""),
            }
        except Exception as e:
            _LOGGER.error("获取滴滴账单失败: %s", e)
            return {}

class DiDiBillSensor(CoordinatorEntity, Entity):
    """滴滴账单传感器"""

    def __init__(self, coordinator):
        """初始化"""
        super().__init__(coordinator)
        self._attr_name = "滴滴账单"
        self._attr_native_unit_of_measurement = CURRENCY_YUAN  # 设置单位
        self._attr_device_class = "monetary"  # 货币类别

    @property
    def native_value(self):
        """返回账单金额"""
        return self.coordinator.data.get("cost")

    @property
    def extra_state_attributes(self):
        """返回额外属性"""
        return {
            "count": self.coordinator.data.get("count"),
            "time": self.coordinator.data.get("time"),
            "distance": self.coordinator.data.get("distance"),
            "month": self.coordinator.data.get("month"),
        }
