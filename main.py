import io_manager

def main() -> None:
    file_path = ""
    while True:
        choice = io_manager.display_menu()
        # new client intake
        if choice == 1:
            client = io_manager.collect_intake_input()
            if file_path == "":
                file_path = io_manager.get_shelter_filename()
            # TODO: pass client data to AI manager
        # view all shelters
        elif choice == 2:
            if file_path == "":
                file_path = io_manager.get_shelter_filename()
            shelters = io_manager.load_shelters_from_csv(file_path)
            io_manager.print_shelter_list(shelters)
        elif choice == 3:
            file_path = io_manager.get_shelter_filename()
        elif choice == 4:
            print("Thank you for using Social Service AI. Goodbye!")
            break

if __name__ == "__main__":
    main()