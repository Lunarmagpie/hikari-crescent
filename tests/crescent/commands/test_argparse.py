from __future__ import annotations

from inspect import _empty, _ParameterKind
from typing import Union

from hikari import (
    ChannelType,
    CommandChoice,
    CommandOption,
    DMChannel,
    GroupDMChannel,
    GuildCategory,
    GuildChannel,
    GuildNewsChannel,
    GuildStageChannel,
    GuildTextChannel,
    GuildVoiceChannel,
    OptionType,
    PartialChannel,
    PrivateChannel,
    TextableChannel,
    TextableGuildChannel,
)
from sigparse import Parameter, global_PEP604
from typing_extensions import Annotated

from crescent import ChannelTypes, Choices, Description, MaxValue, MinValue, Name
from crescent.commands.args import MaxLength, MinLength
from crescent.commands.signature import gen_command_option
from tests.utils import Locale, arrays_contain_same_elements

global_PEP604()

POSITIONAL_OR_KEYWORD = _ParameterKind.POSITIONAL_OR_KEYWORD


def test_gen_command_option():
    assert (
        gen_command_option(
            Parameter(name="self", annotation=_empty, default=None, kind=POSITIONAL_OR_KEYWORD)
        )
        is None
    )

    assert gen_command_option(
        Parameter(name="1234", annotation=str, default=_empty, kind=POSITIONAL_OR_KEYWORD)
    ) == CommandOption(
        name="1234", type=OptionType.STRING, description="No Description", is_required=True
    )

    assert gen_command_option(
        Parameter(name="1234", annotation=str, default=12345, kind=POSITIONAL_OR_KEYWORD)
    ) == CommandOption(
        name="1234", type=OptionType.STRING, description="No Description", is_required=False
    )


def test_annotations():
    annotations = (
        (Annotated[str, "1234"], {"type": OptionType.STRING, "description": "1234"}),
        (Annotated[str, Description("1234")], {"type": OptionType.STRING, "description": "1234"}),
        (
            Annotated[str, Name("different_name")],
            {"type": OptionType.STRING, "name": "different_name"},
        ),
        (
            Annotated[
                str,
                Name(Locale("name", en_US="en-localization")),
                Description(Locale("description", en_US="en-localization")),
            ],
            {
                "type": OptionType.STRING,
                "name": "name",
                "name_localizations": {"en-US": "en-localization"},
                "description": "description",
                "description_localizations": {"en-US": "en-localization"},
            },
        ),
        (
            Annotated[int, MinValue(10), MaxValue(15)],
            {"type": OptionType.INTEGER, "min_value": 10, "max_value": 15},
        ),
        (
            Annotated[str, MinLength(10), MaxLength(15)],
            {"type": OptionType.STRING, "min_length": 10, "max_length": 15},
        ),
        (
            Annotated[PartialChannel, ChannelTypes(ChannelType.GUILD_NEWS)],
            {"type": OptionType.CHANNEL, "channel_types": [ChannelType.GUILD_NEWS]},
        ),
        (
            Annotated[
                str,
                Choices(
                    CommandChoice(name="option1", value=15),
                    CommandChoice(name="option2", value=30),
                ),
            ],
            {
                "type": OptionType.STRING,
                "choices": (
                    CommandChoice(name="option1", value=15),
                    CommandChoice(name="option2", value=30),
                ),
            },
        ),
    )

    for annotation, params in annotations:
        kwargs = {"name": "1234", "description": "No Description"}
        kwargs.update(params)

        assert gen_command_option(
            Parameter(name="1234", annotation=annotation, default=None, kind=POSITIONAL_OR_KEYWORD)
        ) == CommandOption(**kwargs)


def test_310_annotation_syntax():
    assert gen_command_option(
        Parameter(name="1234", annotation=int | None, default=None, kind=POSITIONAL_OR_KEYWORD)
    ) == CommandOption(name="1234", type=OptionType.INTEGER, description="No Description")

    assert gen_command_option(
        Parameter(name="1234", annotation=None | int, default=None, kind=POSITIONAL_OR_KEYWORD)
    ) == CommandOption(name="1234", type=OptionType.INTEGER, description="No Description")


def test_gen_channel_options():
    channels = (
        # Test single channels
        (PrivateChannel, [ChannelType.DM, ChannelType.GROUP_DM]),
        (DMChannel, [ChannelType.DM]),
        (GroupDMChannel, [ChannelType.GROUP_DM]),
        (
            TextableChannel,
            [
                ChannelType.GUILD_TEXT,
                ChannelType.DM,
                ChannelType.GUILD_NEWS,
                ChannelType.GUILD_VOICE,
                ChannelType.GUILD_NEWS_THREAD,
                ChannelType.GUILD_PRIVATE_THREAD,
                ChannelType.GUILD_PUBLIC_THREAD,
            ],
        ),
        (GuildCategory, [ChannelType.GUILD_CATEGORY]),
        (
            TextableGuildChannel,
            [
                ChannelType.GUILD_TEXT,
                ChannelType.GUILD_NEWS,
                ChannelType.GUILD_VOICE,
                ChannelType.GUILD_NEWS_THREAD,
                ChannelType.GUILD_PRIVATE_THREAD,
                ChannelType.GUILD_PUBLIC_THREAD,
            ],
        ),
        (GuildTextChannel, [ChannelType.GUILD_TEXT]),
        (GuildNewsChannel, [ChannelType.GUILD_NEWS]),
        (GuildVoiceChannel, [ChannelType.GUILD_VOICE]),
        (GuildStageChannel, [ChannelType.GUILD_STAGE]),
        (
            GuildChannel,
            [
                ChannelType.GUILD_TEXT,
                ChannelType.GUILD_VOICE,
                ChannelType.GUILD_CATEGORY,
                ChannelType.GUILD_NEWS,
                ChannelType.GUILD_STAGE,
                ChannelType.GUILD_NEWS_THREAD,
                ChannelType.GUILD_PRIVATE_THREAD,
                ChannelType.GUILD_PUBLIC_THREAD,
                ChannelType.GUILD_FORUM,
            ],
        ),
        # Test channel combonation
        (
            Union[GuildTextChannel, GuildVoiceChannel],
            [ChannelType.GUILD_TEXT, ChannelType.GUILD_VOICE],
        ),
        (
            Union[TextableChannel, TextableGuildChannel],
            [
                ChannelType.GUILD_TEXT,
                ChannelType.DM,
                ChannelType.GUILD_NEWS,
                ChannelType.GUILD_VOICE,
                ChannelType.GUILD_NEWS_THREAD,
                ChannelType.GUILD_PRIVATE_THREAD,
                ChannelType.GUILD_PUBLIC_THREAD,
            ],
        ),
        (
            Union[GuildChannel, TextableChannel],
            [
                ChannelType.GUILD_TEXT,
                ChannelType.GUILD_VOICE,
                ChannelType.GUILD_CATEGORY,
                ChannelType.GUILD_NEWS,
                ChannelType.GUILD_STAGE,
                ChannelType.DM,
                ChannelType.GUILD_NEWS_THREAD,
                ChannelType.GUILD_PRIVATE_THREAD,
                ChannelType.GUILD_PUBLIC_THREAD,
                ChannelType.GUILD_FORUM,
            ],
        ),
    )

    for channel_in, channel_types in channels:
        assert arrays_contain_same_elements(
            gen_command_option(
                Parameter(
                    name="1234", annotation=channel_in, default=12345, kind=POSITIONAL_OR_KEYWORD
                )
            ).channel_types,
            channel_types,
        )


def test_partial_channel_has_no_type():
    assert gen_command_option(
        Parameter(
            name="1234", annotation=PartialChannel, default=12345, kind=POSITIONAL_OR_KEYWORD
        )
    ) == CommandOption(
        name="1234",
        type=OptionType.CHANNEL,
        description="No Description",
        is_required=False,
        channel_types=None,
    )
