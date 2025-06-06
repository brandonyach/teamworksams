import vcr


def vcr_config():
    return {
        "record_mode": "new_episodes",
        "match_on": ["method", "scheme", "host", "port", "path", "query"],
        "filter_headers": ["authorization", "session-header", "cookie"],
    }
    
vcr.default_vcr = vcr.VCR(**vcr_config())