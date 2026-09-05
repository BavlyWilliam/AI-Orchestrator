def get_user_request():
    while True:
        user_request = input("What would you like help with?\n> ").strip()

        if user_request:
            return user_request

        print("\nPlease enter a request.\n")


def main():
    user_request = get_user_request()

    print("\nYou asked:")
    print(user_request)


if __name__ == "__main__":
    main()
