import faust
from faust import App
from faust.topics import Topic, Any, ChannelT
import logging


LOGGER = logging.getLogger(__name__)


class ShortRepartitionTopic(Topic):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def derive(self, **kwargs: Any) -> ChannelT:
        current_suffix = kwargs.get("suffix")
        if 'repartition' in current_suffix:
            kwargs['suffix'] = '-'.join(['-GroupBy', current_suffix.lstrip('-').split('-')[-2]])
            kwargs['prefix'] = ''
        return self.derive_topic(**kwargs)


class InstrumentedApp(App):
    """
    Faust app with metric of number of agent exceptions
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conf.Topic = ShortRepartitionTopic

    async def _on_agent_error(self, agent: faust.agents.AgentT, exc: BaseException) -> None:
        self.wrapper.agent_exception(exc)
        await super(InstrumentedApp, self)._on_agent_error(agent, exc)
