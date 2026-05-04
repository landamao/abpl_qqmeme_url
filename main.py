"""
表情链接插件

功能：发送"表情链接"文字 + 引用/附带一张图片，自动回复该图片的URL链接。
"""
from astrbot.api.all import (
    Star, Context, Plain, Reply, Image
)
from astrbot.api.event import filter
from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import AiocqhttpMessageEvent


class 表情链接(Star):
    """表情链接——提取消息中的图片URL"""

    def __init__(self, context: Context):
        super().__init__(context)

    @filter.event_message_type(filter.EventMessageType.ALL)
    @filter.platform_adapter_type(filter.PlatformAdapterType.AIOCQHTTP)
    async def on_group_message(self, event: AiocqhttpMessageEvent):
        """监听群消息，检测'表情链接'关键词"""
        消息文本 = event.get_message_str().strip()

        if 消息文本 != "表情链接":
            return

        消息链 = event.get_messages()
        if not 消息链:
            return

        # 优先检查引用消息中是否有图片
        for 组件 in 消息链:
            if isinstance(组件, Reply):
                for 组件2 in 组件.chain:
                    if isinstance(组件2, Image):
                        await self._reply_with_text(event, 组件2.url)
                        return
                return
            # 也检查直接附带在消息中的图片
            if isinstance(组件, Image):
                await self._reply_with_text(event, 组件.url)
                return

        # 没找到图片
        await self._reply_with_text(event, "没有找到表情")

    @staticmethod
    async def _reply_with_text(event: AiocqhttpMessageEvent, 文本: str) -> None:
        """以引用回复的方式发送文本"""
        await event.send(event.chain_result([
            Reply(id=event.message_obj.message_id),
            Plain(text=文本)
        ]))