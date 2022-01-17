## Plan

- the cli should be the same, whether working on a local database, or with a remote API
- add a server implementing an API
- either automatically (e.g. apistar) or manually add a remote interface to
  mimic the database interface
- add remote interface to client
- log api interactions to database
  - add cli for searching logs
    - I want to be able to answer "who all has accessed this endpoint, and
      when?", especially the main redirect matching endpoint
- release mvp to PyPI
- add features/[extras](#extras)


### Extras
- separate server into a pip extra
- client configuration should be able to be specified through a config file,
  which should be overridden by individual values on the command-line
- obscure passwords (plain and hashed) with `pydantic.SecretStr` and others
  ([this commit message explains
  more](https://github.com/mawillcockson/mw_url_shortener/commit/6a492a1c090f082f399aa851537bd0a402355be5))
- check out <https://returns.readthedocs.io/en/latest/pages/context.html> and
  <https://fsharpforfunandprofit.com/rop/> for ideas on how to do inversion of
  control (dependency injection) with type safety for Typer (as well as
  <https://github.com/tiangolo/typer/issues/80#issuecomment-950349503>)
- tags on everything
- datestamps on everything
- multiple shortlinks for reach redirect
  - I don't know how to model this one in the database:
    - shortlink table and an index between redirects and shortlinks
    - json list of shortlinks for each redirect
    - each redirect row has at least one unique column, so every redirect is
      different, but it's O(1) to fetch a specific redirect, and you can be
      more and more specific to retrieve fewer and fewer rows
- link users and redirects:
  - which users created and modified redirects
    - deleted redirects
    - also track user actions on users
- user permissions
- permission scoping based on tags
- `discoverable` flag
  - sitemap generator of all `discoverable` links
- make interface errors json-encodeable, surface errors in cli with --json option as json
- add cli `write-configuration` command that reads from the `--config-path`
  option if it exists, overrides the configuration with options from cli, and
  writes the configuration back to the `--config-path` option, in json-style
  (pretty printing would be nice)
- server shoud be able to take configuration through config file, environment
  variables, and command line, with that also being the order of precedence
  from lowest to highest
- the client should have to confirm before creating a database, if the file doesn't exist
  - if the file does exist, and it's not a readable database, an error should be displayed
- wrangle logging
- tests should verify error message content
- look at `hypercorn.run.run_multiple` for better server scaling:
  <https://gitlab.com/pgjones/hypercorn/-/blob/main/src/hypercorn/run.py#L41>
- reduce code duplication between various interfaces to the database
  - can probably use `python-inject` instead of the FastAPI dependency system
    for injecting the `async_session` into the database interface calls
    themselves, eliminating the need to pass a resource to them
  - this would also allow the interface to be used directly by the api:
    `router.delete("/")(user_interface.remove)`
    - the interface would have to raise custom errors, and an interface handler
      would have to be added to convert them, but it would be worth it,
      probably
- improve error handling and messages of cli in both `json` and `text` output
  styles (`json` currently outputs not messages, in the hopes that any tools
  that use it will fail, even if they're not watching for the exit code, making
  debugging harder)
