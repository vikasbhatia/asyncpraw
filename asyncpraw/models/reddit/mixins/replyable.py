"""Provide the ReplyableMixin class."""
from ....const import API_PATH


class ReplyableMixin:
    """Interface for RedditBase classes that can be replied to."""

    async def reply(self, body: str):
        """Reply to the object.

        :param body: The Markdown formatted content for a comment.
        :returns: A :class:`~.Comment` object for the newly created
            comment or ``None`` if Reddit doesn't provide one.

        A ``None`` value can be returned if the target is a comment or
        submission in a quarantined subreddit and the authenticated user
        has not opt-ed in to viewing the content. When this happens the
        comment will be sucessfully created on Reddit and can be retried
        by drawing the comment from the user's comment history.

        .. note:: Some items, such as locked submissions/comments or
            non-replyable messages will throw
            ``asyncprawcore.exceptions.Forbidden`` when attempting to reply
            to them.

        Example usage:

        .. code-block:: python

            submission = await reddit.submission(id="5or86n", lazy=True)
            await submission.reply("reply")

            comment = await reddit.comment(id="dxolpyc", lazy=True)
            await comment.reply("reply")

        """
        data = {"text": body, "thing_id": self.fullname}
        comments = await self._reddit.post(API_PATH["comment"], data=data)
        try:
            return comments[0]
        except IndexError:  # pragma: no cover; I haven't been able to make this happen again
            return None
