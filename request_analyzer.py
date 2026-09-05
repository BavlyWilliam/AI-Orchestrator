def is_request_clear(user_request):
    unclear_requests = [
        "help",
        "help me",
        "nothing",
        "idk",
        "i don't know",
        "something",
    ]

    cleaned_request = user_request.lower().strip()

    if cleaned_request in unclear_requests:
        return False

    if len(cleaned_request.split()) < 3:
        return False

    return True
