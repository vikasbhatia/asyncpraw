Migrating to Async PRAW
=======================

With the conversion to async, there are few critical changes that had to be made.
This page outlines a few those changes.

Network Requests
----------------

.. _network_requests:

Since Async PRAW will be operating in an asynchronous environment using
`aiohttp <https://docs.aiohttp.org/>`_ and thus anytime it could make a network request
it needs to be awaited. The majority of all methods need to be awaited.


Lazy Loading
------------

.. _lazy_loading:

In PRAW, the majority of objects are lazily loaded and are not fetched until an
attribute is accessed. With Async PRAW, objects can be fetched on initialization and
some now do this by default. For example:

* PRAW:

  .. code-block:: python

      # network request is not made and object is lazily loaded
      submission = reddit.submission('id')

      # network request is made and object is fully fetched
      print(submission.score)

* Async PRAW:

  .. code-block:: python

      # network request made and object is fully loaded
      submission = await reddit.submission('id')

      # network request is not made as object is already fully fetched
      print(submission.score)

Now, lazy loading is not gone completely and can still be done. For example, if you
only wanted to remove a post, you don't need the object fully fetched to do that.

* PRAW:

  .. code-block:: python

      # object is not fetched and is only removed
      reddit.submission('id').mod.remove()

* Async PRAW:

  .. code-block:: python

      # network request is not made and object is lazily loaded
      submission = await reddit.submission('id', lazy=True)

      # object is not fetched and is only removed
      await submission.mod.remove()

By default, only :class:`.Subreddit`, :class:`.Redditor`, :class:`.LiveThread`,
and :class:`.Multireddit` objects are still lazily loaded. You can pass ``fetch=True``
in the initialization of the object to fully load it. Inversely, the following objects
are now fully fetched when initialized: :class:`.Submission`, :class:`.Comment`,
:class:`.WikiPage`, :class:`.RemovalReason`, :class:`.Collection`, :class:`.Emoji`,
:class:`.LiveUpdate`, :class:`.Rule`, and :class:`.Preferences`. You can pass
``lazy=True`` if you want to lazily loaded it.

In addition, there will be a ``load()`` method provided for manually fetching/refreshing
objects that subclass :class:`.RedditBase`. If you need to later on access an attribute
you need to call the ``.load()`` method first:

.. code-block:: python

    # object is lazily loaded and no requests are made
    submission = await reddit.submission('id', lazy=True)
    ...
    # network request is made and item is fully fetched
    await submission.load()

    # network request is not made as object is already fully fetched
    print(submission.score)

Getting items by Indices
------------------------

.. _objects_by_indices:

In PRAW you could get specific :class:`.WikiPage`, :class:`.RemovalReason`, :class:`.Emoji`,
:class:`.LiveUpdate`, and :class:`.Rule` objects by using string indices. This will no longer
work and has been converted to a ``.get_<item name>(item)`` method. Also, they are not lazily
loaded by default anymore.

* PRAW:

  .. code-block:: python

      # lazily creates a WikiPage instance
      page = subreddit.wiki['page']

      # network request is made and item is fully fetched
      print(page.content_md)

* Async PRAW:

  .. code-block:: python

      # network request made and object is fully loaded
      page = await subreddit.wiki.get_page('page')

      # network request is not made as WikiPage is already fully fetched``
      print(page.content_md)

      # using slices
      rule = await subreddit.mod.rules.get_rule(slice(-3, None))  # to get the last 3 rules

