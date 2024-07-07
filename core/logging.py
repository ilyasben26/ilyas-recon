from termcolor import colored  # type: ignore




def print_error(message: str) -> None:
    print(colored(f"[ERR] {message}", "red"))

def print_info(message: str) -> None:
    print(colored(f"[INF] ", "blue") + message)