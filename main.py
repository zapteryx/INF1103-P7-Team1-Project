from io_manager import display_menu, collect_intake_input

def main() -> None:
    choice = display_menu()
    # new client intake
    if choice == 1:
        client = collect_intake_input()
    # view all shelters
    elif choice == 2:
        pass
    elif choice == 3:
        print("Thank you for using Social Service AI. Goodbye!")
        exit()

if __name__ == "__main__":
    main()