import logging
import requests
from datetime import timedelta
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_API_URL, CONF_UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    api_url = entry.data[CONF_API_URL]
    update_interval = timedelta(minutes=entry.data.get(CONF_UPDATE_INTERVAL, 30))

    coordinator = DiDiBillCoordinator(hass, api_url, update_interval)
    
    try:
        await coordinator.async_refresh()
    except Exception as e:
        _LOGGER.error("初始化数据失败: %s", e)
    
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    async_add_entities([DiDiBillSensor(coordinator, entry)])

class DiDiBillSensor(CoordinatorEntity, Entity):
    @property
    def state(self):
        return round(self.coordinator.data.get('cost', 0.0), 2) if self.coordinator.data else 0.0

    @property
    def extra_state_attributes(self):
        fallback = {'count': 0, 'time': 0, 'distance': 0.0, 'month': '数据未就绪'}
        return self.coordinator.data.copy() if self.coordinator.data else fallback

async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """配置条目重载处理"""
    await hass.config_entries.async_reload(entry.entry_id)



class DiDiBillCoordinator(DataUpdateCoordinator):
    """数据协调器，负责定时从API获取最新账单数据"""

    async def _async_update_data(self):
        """执行数据更新操作"""
        try:
            response = await self.hass.async_add_executor_job(requests.get, self.api_url)
            data = response.json().get("data", {})
            return {
                "cost": data.get("travel_cost", 0) / 100,
                "count": data.get("travel_count", 0),
                "time": data.get("charge_duration", 0),
                "distance": data.get("travel_distance", 0),
                "month": data.get("title", "").replace("{", "").replace("}", "")
            }
        except Exception as e:
            _LOGGER.error("获取数据失败: %s", e)
            return None

    def __init__(self, hass, api_url, update_interval):
        super().__init__(
            hass,
            _LOGGER,
            name="滴滴账单",
            update_interval=update_interval,
        )
        self.api_url = api_url
        # 初始化时立即加载数据
        hass.async_create_task(self.async_refresh())

class DiDiBillSensor(CoordinatorEntity, Entity):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._entry = entry
        self._attr_name = "滴滴账单"
        self._attr_unique_id = f"didi_bill_{entry.entry_id}"
        self._attr_unit_of_measurement = "CNY"
        self._attr_icon = "mdi:currency-cny"

    @property
    def state(self):
        return self.coordinator.data.get("cost", 0) if self.coordinator.data else 0

    @property
    def extra_state_attributes(self):
        return {
            "count": self.coordinator.data.get("count", 0) if self.coordinator.data else 0,
            "time": self.coordinator.data.get("time", 0),
            "distance": self.coordinator.data.get("distance", 0),
            "month": self.coordinator.data.get("month", "")
        } if self.coordinator.data else {}

    async def _async_update_data(self):
        """执行数据更新操作
        Returns:
            包含账单数据的字典，格式为：
            {
                'cost': 总费用（单位：元）,
                'count': 行程次数,
                'time': 行程总时长（分钟）,
                'distance': 行程总距离（公里）,
                'month': 账单月份
            }
        """
        try:
            # 调用API获取原始数据
            response = await self.hass.async_add_executor_job(requests.get, self.api_url)
            data = response.json().get("data", {})

            # 数据格式转换和处理
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
    """滴滴账单传感器实体
    继承自CoordinatorEntity实现自动更新
    """

    def __init__(self, coordinator, entry):
        """初始化传感器
        Args:
            entry: 配置项实例，用于生成唯一ID
        """
        super().__init__(coordinator)
        # 实体基础配置
        self._attr_name = "滴滴账单"
        self._attr_unique_id = f"didi_bill_{entry.entry_id}"  # 唯一ID确保可管理性
        self._attr_unit_of_measurement = "CNY"
        self._attr_icon = "mdi:currency-cny"

    @property
    def state(self):
        """主状态值（账单金额）"""
        return self.coordinator.data.get("cost")

    @property
    def extra_state_attributes(self):
        """扩展属性（其他账单详细信息）"""
        return {
            "count": self.coordinator.data.get("count"),
            "time": self.coordinator.data.get("time"),
            "distance": self.coordinator.data.get("distance"),
            "month": self.coordinator.data.get("month"),
        }
