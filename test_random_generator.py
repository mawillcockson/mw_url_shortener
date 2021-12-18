from mw_url_shortener.utils import unsafe_random_string

length = 100_000
try:
    while True:
        string = unsafe_random_string(length)
        assert len(string) == length
        assert string.encode("utf-8").decode("utf-8")
        print(".", end="", flush=True)
except (UnicodeEncodeError, UnicodeDecodeError) as err:
    print("")
    print(err)
    breakpoint()
except KeyboardInterrupt:
    print("")
    pass
