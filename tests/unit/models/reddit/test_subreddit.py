import aiohttp
import pytest
from asynctest import mock, CoroutineMock, MagicMock

from asyncpraw.exceptions import MediaPostFailed
from asyncpraw.models import Subreddit, WikiPage
from asyncpraw.models.reddit.subreddit import SubredditFlairTemplates

from ... import UnitTest


class TestSubreddit(UnitTest):
    def test_equality(self):
        subreddit1 = Subreddit(self.reddit, _data={"display_name": "dummy1", "n": 1})
        subreddit2 = Subreddit(self.reddit, _data={"display_name": "Dummy1", "n": 2})
        subreddit3 = Subreddit(self.reddit, _data={"display_name": "dummy3", "n": 2})
        assert subreddit1 == subreddit1
        assert subreddit2 == subreddit2
        assert subreddit3 == subreddit3
        assert subreddit1 == subreddit2
        assert subreddit2 != subreddit3
        assert subreddit1 != subreddit3
        assert "dummy1" == subreddit1
        assert subreddit2 == "dummy1"

    def test_construct_failure(self):
        message = "Either `display_name` or `_data` must be provided."
        with pytest.raises(TypeError) as excinfo:
            Subreddit(self.reddit)
        assert str(excinfo.value) == message

        with pytest.raises(TypeError) as excinfo:
            Subreddit(self.reddit, "dummy", {"id": "dummy"})
        assert str(excinfo.value) == message

    def test_fullname(self):
        subreddit = Subreddit(
            self.reddit, _data={"display_name": "name", "id": "dummy"}
        )
        assert subreddit.fullname == "t5_dummy"

    def test_hash(self):
        subreddit1 = Subreddit(self.reddit, _data={"display_name": "dummy1", "n": 1})
        subreddit2 = Subreddit(self.reddit, _data={"display_name": "Dummy1", "n": 2})
        subreddit3 = Subreddit(self.reddit, _data={"display_name": "dummy3", "n": 2})
        assert hash(subreddit1) == hash(subreddit1)
        assert hash(subreddit2) == hash(subreddit2)
        assert hash(subreddit3) == hash(subreddit3)
        assert hash(subreddit1) == hash(subreddit2)
        assert hash(subreddit2) != hash(subreddit3)
        assert hash(subreddit1) != hash(subreddit3)

    @mock.patch(
        "asyncpraw.Reddit.post",
        return_value={"json": {"data": {"websocket_url": ""}}},
    )
    @mock.patch("asyncpraw.models.Subreddit._upload_media", return_value="")
    @mock.patch("aiohttp.client.ClientSession.ws_connect")
    async def test_invalid_media(self, connection_mock, _mock_upload_media, _mock_post):
        self.reddit._core._requestor._http = aiohttp.ClientSession()
        recv_mock = MagicMock()
        recv_mock.receive_json = CoroutineMock(
            return_value={"payload": {}, "type": "failed"}
        )
        context_manager = MagicMock()
        context_manager.__aenter__.return_value = recv_mock
        connection_mock.return_value = context_manager

        # websockets_mock().__aenter__.recv =
        with pytest.raises(MediaPostFailed):
            await Subreddit(self.reddit, display_name="test").submit_image(
                "Test", "dummy path"
            )
        await self.reddit._core._requestor._http.close()

    def test_repr(self):
        subreddit = Subreddit(self.reddit, display_name="name")
        assert repr(subreddit) == "Subreddit(display_name='name')"

    async def test_search__params_not_modified(self):
        params = {"dummy": "value"}
        subreddit = Subreddit(self.reddit, display_name="name")
        generator = subreddit.search(None, params=params)
        assert generator.params["dummy"] == "value"
        assert params == {"dummy": "value"}

    def test_str(self):
        subreddit = Subreddit(
            self.reddit, _data={"display_name": "name", "id": "dummy"}
        )
        assert str(subreddit) == "name"

    async def test_submit_failure(self):
        message = "Either `selftext` or `url` must be provided."
        subreddit = Subreddit(self.reddit, display_name="name")

        with pytest.raises(TypeError) as excinfo:
            await subreddit.submit("Cool title")
        assert str(excinfo.value) == message

        with pytest.raises(TypeError) as excinfo:
            await subreddit.submit("Cool title", selftext="a", url="b")
        assert str(excinfo.value) == message

        with pytest.raises(TypeError) as excinfo:
            await subreddit.submit("Cool title", selftext="", url="b")
        assert str(excinfo.value) == message

    async def test_upload_banner_additional_image(self):
        subreddit = Subreddit(self.reddit, display_name="name")
        with pytest.raises(ValueError):
            await subreddit.stylesheet.upload_banner_additional_image(
                "dummy_path", align="asdf"
            )

    async def test_submit_gallery__missing_path(self):
        message = "'image_path' is required."
        subreddit = Subreddit(self.reddit, display_name="name")

        with pytest.raises(TypeError) as excinfo:
            await subreddit.submit_gallery(
                "Cool title", images=[{"caption": "caption"}, {"caption": "caption2"}]
            )
        assert str(excinfo.value) == message

    async def test_submit_gallery__invalid_path(self):
        message = "'invalid_image_path' is not a valid image path."
        subreddit = Subreddit(self.reddit, display_name="name")

        with pytest.raises(TypeError) as excinfo:
            await subreddit.submit_gallery(
                "Cool title", images=[{"image_path": "invalid_image_path"}]
            )
        assert str(excinfo.value) == message

    async def test_submit_gallery__too_long_caption(self):
        message = "Caption must be 180 characters or less."
        subreddit = Subreddit(self.reddit, display_name="name")
        caption = "wayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy too long caption"
        with pytest.raises(TypeError) as excinfo:
            await subreddit.submit_gallery(
                "Cool title", images=[{"image_path": __file__, "caption": caption}]
            )
        assert str(excinfo.value) == message


class TestSubredditFlair(UnitTest):
    async def test_set(self):
        subreddit = Subreddit(self.reddit, pytest.placeholders.test_subreddit)
        with pytest.raises(TypeError):
            await subreddit.flair.set(
                "a_redditor", css_class="myCSS", flair_template_id="gibberish"
            )


class TestSubredditFlairTemplates(UnitTest):
    async def test_not_implemented(self):
        with pytest.raises(NotImplementedError):
            await SubredditFlairTemplates(
                Subreddit(self.reddit, pytest.placeholders.test_subreddit)
            ).__aiter__()


class TestSubredditWiki(UnitTest):
    async def test__getitem(self):
        subreddit = Subreddit(self.reddit, display_name="name")
        wikipage = await subreddit.wiki.get_page("Foo", lazy=True)
        assert isinstance(wikipage, WikiPage)
        assert "foo" == wikipage.name


class TestSubredditModmailConversationsStream(UnitTest):
    async def test_conversation_stream_init(self):
        submodstream = Subreddit(self.reddit, display_name="mod").mod.stream
        submodstream.modmail_conversations()
        assert submodstream.subreddit == "all"

    async def test_conversation_stream_capilization(self):
        submodstream = Subreddit(self.reddit, display_name="Mod").mod.stream
        submodstream.modmail_conversations()
        assert submodstream.subreddit == "all"
