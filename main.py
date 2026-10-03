import io_manager

def get_file_path(file_path):
    if file_path == "":
        file_path = io_manager.get_shelter_filename()
    return file_path

# Maintained by Ming Xuan (2604426)
def main() -> None:
    file_path = ""
    while True:
        choice = io_manager.display_menu()
        # new client intake
        if choice == 1:
            client = io_manager.collect_intake_input()
            # TODO: pass client data to AI manager
        # view all shelters
        elif choice == 2:
            # TODO: move this function (load_shelters_from_csv) from IO manager to Data Manager
            shelters = io_manager.load_shelters_from_csv(get_file_path(file_path))
            io_manager.print_shelter_list(shelters)
        elif choice == 3:
            # Direct update instead of using cache function
            file_path = io_manager.get_shelter_filename()
        elif choice == 4:
            file_path = get_file_path()
        elif choice == 5:
            print("Thank you for using Social Service AI. Goodbye!")
            break
        else:
            print("You have entered an invalid choice. Please try again.")

if __name__ == "__main__":
    main()