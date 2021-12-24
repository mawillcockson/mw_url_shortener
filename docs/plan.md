## Plan

- complete local client
  - client configuration should be able to be specified through a config file, or on the command line
  - the cli should be the same, whether working on a local database, or with a remote API
  - the client should create confirm before creating a database, if the file doesn't exist  
    if the file does exist, and it's not a readable database, an error should be displayed
- add a server implementing an API
- either automatically (e.g. apistar) or manually add a remote interface to
  mimic the database interface
- add remote interface to client
- separate server into a pip extra
- add features


### Extras
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
- add cli `write-configuration` command that reads from the `--config-path` option if it exists, overrides the configuration with options from cli, and writes the configuration back to the `--config-path` option, in json-style (pretty printing would be nice)
