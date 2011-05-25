What is this?
-------------

It's an implementation of Gomoku server, built over TCP. Or,
at least, this seems to be the goal of this project.

What it can do
--------------

You can play with a very stupid AI bot through a very basic
command line app. The app also keeps track of your ELO rating,
but who cares enough about it?

How do I use it?
----------------

First of all, you'll need to install the gomoku package::

   sudo python setup.py install

After this, you need to start the server::

   gomoku-server.py

And in any other terminal window, just run the following command::

   gomoku-client-cli.py

The interface is rather uncanny, but this is something that I'm going
to fix soon.

What's planned?
---------------

In no particular order:
* Human to human games
* Improved command line interface
* Stonger AIs
* Renju rules
* m,n,k general implementation (so you could play tic-tac-toe or
  connect6 depending on your humor)
* HTTP API
* Web interface
* GTK/Qt interface
* Server implementation in Clojure/Erlang/Scala
* Alternative rating systems
* Full test coverage
* Ability to save and restore games (especially with AI)

Why are you writing this?
-------------------------

Because it seems that Gomoku isn't all that popular and writing
yet another async library in Python didn't sound like fun for me.
I also liked playing Gomoku when I was a child.
