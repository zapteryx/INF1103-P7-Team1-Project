from io_manager import display_menu, collect_intake_input, load_shelters_from_csv, get_shelter_filename, \
    print_shelter_list

def main() -> None:
    file_path = ""
    while True:
        choice = display_menu()
        # new client intake
        if choice == 1:
            client = collect_intake_input()
            if file_path == "":
                file_path = get_shelter_filename()
            # TODO: pass client data to AI manager
        # view all shelters
        elif choice == 2:
            if file_path == "":
                file_path = get_shelter_filename()
            shelters = load_shelters_from_csv(file_path)
            print_shelter_list(shelters)
        elif choice == 3:
            file_path = get_shelter_filename()
        elif choice == 4:
            print("Thank you for using Social Service AI. Goodbye!")
            break

if __name__ == "__main__":
    main()