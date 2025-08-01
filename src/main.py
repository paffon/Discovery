
from src.manager import Manager

def main() -> None:
    manager = Manager()
    manager.set_up()
    manager.run()
    manager.wrap_up()

if __name__ == "__main__":
    main()