"""
表情链接插件

功能：发送"表情链接"文字 + 引用/附带一张图片，自动回复该图片的URL链接。
"""
from astrbot.api.all import Star, Plain, Reply, logger
from astrbot.api.event import filter
from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import AiocqhttpMessageEvent


class 表情链接(Star):
    """表情链接——提取消息中的图片URL"""

    @filter.command("表情链接")
    @filter.platform_adapter_type(filter.PlatformAdapterType.AIOCQHTTP)
    async def on_group_message(self, event: AiocqhttpMessageEvent):
        """监听群消息，检测'表情链接'关键词"""
        if not isinstance(event, AiocqhttpMessageEvent):
            return

        raw = event.message_obj.raw_message

        if not isinstance(raw, dict):
            return

        result = []
        for i in raw.get("message") or []:
            if i.get("type") == "image":
                try:
                    result.append(i['data']['url'])
                except Exception as e:
                    logger.error(f"获取图片URL失败：{e}", exc_info=True)

            elif i.get("type") == "reply":
                try:
                    reply_data = await event.bot.call_action(action="get_msg", message_id=i['data']['id'])
                    if not isinstance(reply_data, dict):
                        raise TypeError(f"获取消息失败，结果非dict类型：{reply_data}")
                except Exception as e:
                    logger.error(f"获取引用消息失败：{e}", exc_info=True)
                    continue
                for j in reply_data.get("message") or []:
                    if j.get("type") == "image":
                        try:
                            result.append(j['data']['url'])
                        except Exception as e:
                            logger.error(f"获取图片URL失败：{e}", exc_info=True)

        if result:
            await self._reply_with_text(event, '\n'.join(result))
        else:
            await self._reply_with_text(event, "没有找到表情/图片链接")

    @staticmethod
    async def _reply_with_text(event: AiocqhttpMessageEvent, 文本: str) -> None:
        """以引用回复的方式发送文本"""
        await event.send(
            event.chain_result(
                [
                    Reply(id=event.message_obj.message_id),
                    Plain(text=文本)
                ]
            )
        )