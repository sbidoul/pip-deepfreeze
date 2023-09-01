Work around pip limitation that cause repeated metadata recomputation for VCS URLs. When
a constraint is provided with a VCS URL with a mutable reference, pip installs it but
does not cache the wheel. During subsequent `pip-df sync` the metadata is therefore
recomputed (because it is not cached), but the wheel is not built because pip rightly
considers it is already installed. So it is never cached and this causes performance
issues. As a workaround we fixup direct_url.json with a fake commit to force
reinstallation (and therefore caching of the wheel) during subsequent sync with the
commit id.
