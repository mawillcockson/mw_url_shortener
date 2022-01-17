# The async architecture used in the `run_test_command` fixture

This test fixture returns a function that can be used to run the cli
application, against mostly accurately-mocked resources: the network will
never fail, and the web application will never balk at messages that are too
large, but it should traverse the same code paths as it would in a proper
server-client, or standalone database-manipulation app.

Because the fixture is parameterized, it WILL run both the local and remote
versions of the commands. The `add_default_parameters` argument could be used
to circumvent that by setting the cli app to only access the database both
times, but that wouldn't really be the point.

The fixture started out as running the cli app for local database access to
begin with; running it against a remote api was added later.

When run normally, the cli app commands interact with an async api, but Typer
doesn't support async commands.

One way of solving this would be to write a wrapper for commands and
callbacks. It would run an asyncio loop for each async function, and return
the result.

However, the database interface is also used by the server, and since I
wanted it to be async and didn't want to write a separate interface for the
cli app, the cli app has to use the interface.

The cli app is designed so that configuration is added incrementally as
execution proceeds through subcommands to the final command:
- the main callback collects the global options
- the remote and local callbacks collect the options pertaining to their
domains (e.g. database location, base api url, etc)
- (there is no user or redirect callback as I write this)
- finally the command being run

It's also designed so that the actual command being run does not care what
the transport is: the data could be going to a local database; or over a
network, through an api, and into a database. The interfaces were intended to
be used the same from the start.

This implies that the initialization of those transports and connections,
either to a remote api, or to a local database, probably shouldn't happen in
the final commands.

I decided to put them in the local/remote callbacks, where enough
configuration is known that they can be created.

This means that, for instance, the database connection must be created
asynchronously in the remote callback, the return value must be saved, and
then that returned value must be made available to the interface called by
the final command.

Actually, it doesn't have to be done this way: when called without the
`await` keyword, asynchronous functions return an awaitable. This awaitable
could be passed to the final commands, which are then run in an async context
and can `await` that coroutine that had it's state initialized in an earlier
callback, and which does the work now.

For example, the database connection creation coroutine could be called in the
`local` callback, passing into the coroutine the state (including the database
location). The resulting awaitable could be saved and passed to the final
command using the same mechanism that passes around `settings`, and then the
final command (e.g. `user create`) could retrieve that awaitable and start an
async event loop, letting it `await` the awaitable, and finally pass the value
to the interface.

I hadn't thought of that until now, and it sounds easier than the current way.

Some downsides would be that modifying the interface to internally retrieve the
connection resource it needs using the same dependency injection framework as
the rest of the app would mean that, in the server, the database connection
creation coroutine's return value would have to be initially awaited, and then
cached somewhere to be made available to any other interface method. Each
method would have to be able to check if the resource it needs is cached, and
if not, retrieve the awaitable, await it, and then somehow cache the result
somewhere.

It's minor, but it also means any errors (e.g. a database that's corrupted)
would not surface until the database connection creation routine is `await`ed.
For the cli app, there wouldn't be a meaningful difference, but for the server,
the error wouldn't show up until the first endpoint method is called, and then
the app would somehow have to be gracefully shut down in response to that.

As long as the value isn't needed at the moment, the above framework could work.

One situation that may come up that may need to make use of the value early
would be a utility that loads some of the configuration from the database,
instead of a configuration file. Because the configuration is passed around in
a `settings` object which is passed around by dependency injection, the utility
function would best be called in the `local` or `remote` callback, the
configuration merged, and the resulting `settings` made available through
dependency injection before execution is passed to the final command.

It wouldn't be too hard to do the "bundling of awaitables for the async
context" here, too, though: because the cli performs one unit of work per run
(i.e. the final command run), the partially configured settings could be passed
to the final command, along with an awaitable that opens the database, and an
awaitable that uses that connection to merge the configuration in the database
with the `settings` retrieved through dependency injection.

That would be easier than the current approach. I am fairly heavily invested in
this one, but there's a large appeal in the reduced complexity of that
approach.

The server isn't started in an async context, currently, so using that
`settings`-merging utility would take some work to have it run at app creation
or startup, but I'm sure I could manage it.

Anyways, the current architecture takes the async coroutine that sets up the
database connection, and runs it in the `local` callback, then stashes the
database connection object in dependency injection, to be retrieved by the
final command. That final command runs the async interface functions
synchronously.

It could be possible to use `loop.run_until_complete()` on all the coroutines,
with the coroutines themselves performing the work of stashing values in
dependency injection, but I didn't think of that until now, and instead saw
that there weren't many ways to "call an async function and receive that
functions return value".

There is one function:
[`asyncio.run_coroutine_threadsafe()`](https://docs.python.org/3/library/asyncio-task.html#asyncio.run_coroutine_threadsafe).
It returns a `Future` that has a `result()` method that can immediately be
called. This method blocks until the coroutine finishes, and its return value
is available, at which point the coroutine's return value is returned as the
return value of the `result()` method.

But that requires an already running event loop. It's designed to be called
from a second thread, scheduling the coroutine to run in the event loop that's
running in the first thread, and returning the result.

Why another thread? The function expects the event loop to already be running,
and won't start a new loop if there isn't one running. The asyncio event loop
runs in a single thread, and handles execution in that thread. Until the event
loop stops, synchronous execution cannot continue.

When Python runs, it starts a single thread. That thread runs the python code,
up until the point at which the event loop is started with a call like
`loop.run_until_complete()` or `asyncio.run()`. The event loop now handles
scheduling the execution of code in that thread. It's as if the synchronous
execution is busy running the event loop and coroutines. There is no way to get
the thread to resume synchronous execution, unless the loop could somehow be
paused, the synchronous code run, then the loop resume. This would be achieved
by `loop.run_until_complete()` calls interspersed with synchronous execution.

All this means that the app's synchronous code needs to be run in a different
thread from the event loop.

Either the event loop can be started in a seperate thread, with a call like
`loop.run_forever()`, and the cli app can continue execution in the initial
thread Python creates. Or the event loop could be started in the first thread,
and
[`loop.run_in_executor()`](https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.loop.run_in_executor)
could be called to run the cli app in the second thread.

With the first option, the running event loop would have to be stopped when the
cli app ends. This could be done by holding onto the `loop` object and calling
`loop.stop()` at the end of the app's execution, or the loop could be started
with `loop.run_until_complete()` and an coroutine that `await`s an
`asyncio.Event` that indicates the shutdown. Either way, that would be much
more convenient than the second option, since the cli app's code would be more
easily debuggable, since it's in the main thread.

I went with the second option: the `mw_url_shortener.cli.entry_point.main()`
function starts an event loop and runs the cli app in a second thread, and from
the second thread, the cli app calls back to the event loop running in the main
to schedule coroutines. Then, once the cli app is done, the asyncio event loop
stops.

This means that the cli app expects to be running in that context (i.e. in a
second thread, with the first thread running an event loop).

This means the tests have to emulate that, even when using the cli framework's
test client that makes it easy to call the cli app in a way that simulates
running it on the commandline.

So the test fixture returns a coroutine that takes that cli app, wraps it in
the cli framework's app runner for testing, and wraps that in a coroutine that
runs that test client with the commandline parameters in a thread.

This works because the test functions are async and rely on being run by
[`anyio`'s `pytest`
plugin](https://anyio.readthedocs.io/en/stable/testing.html).

This conveniently provides an already a running event loop in the main thread.

However, there's a few catches: the cli app needs to have access to an object
that represents the running event loop, so that it can schedule coroutines to
run in it. In normal execution, this is done by
`mw_url_shortener.dependency_injection.main.initialize_dependency_injection()`,
which expects to be run in an async context so that it can store the running
event loop in dependency injection.

Then, the cli app calls
`mw_url_shortener.dependency_injection.main.reconfigure_dependency_injection()`
with the final state that the final command will use when it's run.

In `local` mode, that's fine: the only important state is the path to the
database file (since that's the only I/O the app does in `local` mode), and
since that state can be passed through commandline options, which can be passed
in through the cli test client runner, the state will be stored in the
`settings` object in just the same way as when the app is run on the
commandline.

However for the `remote` mode, the app does networking I/O, and expects to be
able to talk to a web server. Fortunately, both the web server framework
(starlette) and the network client framework (httpx) provide a way to call the
server app without having to start it up normally to send and receive network
traffic with the cli app.

The web server framework provides a replacement client, or stand-in client,
that replicates the `requests` library, and is thus synchronous. However, I
decided the asynchronous interface would use the asynchronous part of the
`httpx` library, so that client can't be used. Normally, the ASGI server app is
passed when instantiating the client, making it into a test client.

Inside the `remote` callback, the `httpx.AsyncClient` is created and then
stored in through dependency injection. This is then used later in the cli
app's execution.

During both modes, the fixture monkeypatches both the `local` and `remote`
subcommand callback's namespaces. It patches out the
`mw_url_shortener.dependency_injection.main.reconfigure_dependency_injection()`
function in both, and the `mw_url_shortener.remote.start.make_async_client()`
function in the `remote` subcommand's namespace.

The patched functions run the regular functions as normal, but in the case of
`reconfigure_dependency_injection()`, modify the state passed in to include the
server app's state.

The server app is made as normal
(`mw_url_shortener.server.app.make_fastapi_app()`), and the server relies on
dependency injection to make its `server_settings` available to each endpoint
that needs it.

Fortunately, the fixtures for testing the server's API already run this
function, and make the server app available, so those are depended upon by the
`run_test_command` fixture.

Their output used to access the `server_settings` object, which is the patchers
pass into `reconfigure_dependency_injection()` to include it in the final
dependency injection state.

The `make_async_client()` function's output is modified. Fortunately,
`httpx.AsyncClient` only uses a different transport for calling into the ASGI
server app directly, so the client's transport is swapped out, and the client
is returned and can be used as normal by the cli app. Also thankfully, it
appears the connection pool isn't opened until an `async with`, so no
connections need to be closed when swapping things out.

One downside is that a server app is made for both the `local` mode that
doesn't use it, and the `remote` mode that does.

It's also pretty complicated.
