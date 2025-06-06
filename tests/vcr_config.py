import vcr

vcr = vcr.VCR(
    record_mode="new_episodes",
    match_on=["method", "scheme", "host", "port", "path", "query"],
    filter_headers=["authorization", "session-header", "cookie"],
)