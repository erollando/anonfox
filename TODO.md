# TODO

1. Define and implement a secret-class precedence matrix for overlap resolution (for example `oauth_cloud_token` > `bearer_token` > `generic_secret`).
2. Add a non-reversible secret redaction mode (secret placeholders without returning original secret mapping values).
3. Externalize vendor/prefix/token patterns to configuration files so signatures can be updated without code changes.
4. Tune and validate thresholds for heuristic secret classes (`generic_secret`, `session_token`, `private_key_inline`) with explicit regression fixtures.
