## Plan

- complete database interface
- complete local client
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
  control (dependency injection) with type safety for Typer
