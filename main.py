import time
from ai_manager import AIManager, GeminiClient, SampleResponseClient
from data_manager import DataManager, ShelterFileReader, FileStorage, SQLiteStorage, UserManager, Authentication, User
from io_manager import IOManager
from logic_manager import LogicManager
ADMIN_SECRET_CODE = "STAFF2026"

# Maintained by Ming Xuan (2604426)
def get_suitable_storage(filename: str) -> FileStorage | SQLiteStorage:
    if filename.endswith('.json') or filename.endswith('.csv'):
        return FileStorage(filename)
    elif filename.endswith('.db'):
        return SQLiteStorage(filename)
    else:
        raise ValueError("Unsupported file format. Please provide a .json, .csv, or .db file.")

# Maintained by Ming Xuan (2604426)
def get_recommendation(clients_file_path: str, client: dict, shelters: list[dict], tries = 0) -> bool | None:
    IOManager.print_update(f"Getting recommendations for client {client['client_id']}...")
    ai_manager = AIManager(GeminiClient(), SampleResponseClient())
    recommendation = ai_manager.get_shelter_recommendation(client, shelters)
    if recommendation is None:
        IOManager.print_error("AI recommendation failed.")
        return False
    # IOManager.print_update(f"AI Recommendation for client {client['client_id']}", f"\n{json.dumps(recommendation, indent=2)}")
    IOManager.print_update("Finding the best shelter based on AI recommendation and additional criteria...")
    logic_manager = LogicManager()
    best_shelter = logic_manager.calculate_suitability_score(shelters, client, recommendation)
    if best_shelter is None:
        IOManager.print_error("No suitable shelter found based on the recommendation.")
        return False
    # IOManager.print_update(f"Best shelter for client {client['client_id']}", f"\n{json.dumps(best_shelter, indent=2)}")
    outcome = IOManager.present_best_shelter(client, best_shelter)
    storage = get_suitable_storage(clients_file_path)
    data_manager = DataManager(storage)
    if outcome is True:
        data_manager.update_record(client['client_id'], outcome=True, accepted_shelter=best_shelter)
        IOManager.print_update(f"Client {client['client_id']} record updated with outcome: Accepted and accepted shelter: {best_shelter['shelter_name']}")
        return True
    elif outcome is False:
        if tries < 1:  # If the outcome is False, try again
            return get_recommendation(clients_file_path, client, shelters, tries + 1)
        data_manager.update_record(client['client_id'], outcome=False)
        IOManager.print_update(f"Client {client['client_id']} record updated with outcome: Rejected")
        return True
    return None


def find_client_record(data_manager, nric):
    client_list, error = data_manager.load_records()
    if error is not None:
        return None, error

    target_nric = nric.strip().upper()
    matched_client = next(
        (c for c in client_list if str(c.get("client_id", "")).strip().upper() == target_nric),
        None
    )
    return matched_client, None

# Maintained by Mahima (2604701) & Ming Xuan (2604426)
def authenticate_user() -> User | None:
    """
    Handle user authentication (login or registration).
    Returns authenticated User object or None if user exits.
    """
    user_manager = UserManager("clients.db")
    auth = Authentication(user_manager)

    while True:
        choice = IOManager.display_auth_menu()

        # Register
        if choice == 1:
            clients_file_path = "clients.json"  # Default path for client records
            storage = get_suitable_storage(clients_file_path)
            data_manager = DataManager(storage)
            client_list, error = data_manager.load_records()
            if error is not None:
                IOManager.print_error("There is an error in the registration process", error)
                continue
            else:
                #client id in JSON is actually the NRIC.
                client_nric_ages = {
                    client.get("client_id"): client.get("age") for client in client_list
                }
                print(client_nric_ages, "isudfhhohofsdf")  
                registration_data = IOManager.collect_registration_input(
                    nric_age_dict=client_nric_ages,
                    password_validator=auth.check_password_strength
                )
                if not registration_data:
                    IOManager.print_error("Registration failed due to security verification failure.")
                    time.sleep(1)
                    continue

            # Register user (password already validated during input collection)
            success, errors = auth.register_user(
                registration_data["name"],
                registration_data["nric"],
                registration_data["username"],
                registration_data["password"]
            )

            if success:
                IOManager.print_update("Registration successful! Please login to continue.")
            else:
                # This should only fail for database issues now, not password issues
                IOManager.print_error("Registration failed", "\n".join(errors))

        # Login
        elif choice == 2:
            login_data = IOManager.collect_login_input()
            success, message = auth.login(
                login_data["username"],
                login_data["password"]
            )

            if success:
                user = auth.get_current_user()
                IOManager.display_login_status(True, user.name)
                return user
            else:
                IOManager.print_error("Login failed", message)
                time.sleep(2)
                
                
        elif choice == 3:
            admin_invite_code = input("Admin invite code (please go back if client): ").strip()
            if admin_invite_code == ADMIN_SECRET_CODE:
                is_admin = 1
                registration_data = IOManager.collect_registration_input(
                    password_validator=auth.check_password_strength, is_admin = is_admin
                )
                # Register user (password already validated during input collection)
                success, errors = auth.register_user(
                    registration_data["name"],
                    registration_data["nric"], #this will be None for admin registration
                    registration_data["username"],
                    registration_data["password"],
                    is_admin
                )

                if success:
                    IOManager.print_update("Admin registration successful! Please login to continue.")
                else:
                    # This should only fail for database issues now, not password issues
                    IOManager.print_error("Admin registration failed", "\n".join(errors))
            else:
                IOManager.print_error("Invalid admin invite code.")
                time.sleep(1)
            
        # Exit
        elif choice == 4:
            IOManager.print_update("Thank you for using Social Service AI. Goodbye!")
            return None

# Maintained by Ming Xuan (2604426)
def main() -> None:
    while True:
        # Authenticate user first
        user = authenticate_user()
        print(user, "99999999del")
        if user is None:
            return  # User chose to exit from auth menu

        IOManager.print_update(f"\nWelcome to Social Service AI, {user.name}!")
        if user.is_admin == 1:
            IOManager.print_update("You are logged in as an admin. You have access to all functionalities.")
            while True:
                choice = IOManager.display_menu()
                # new client intake
                if choice == 1:
                    client = IOManager.collect_intake_input()
                    clients_file_path = IOManager.get_client_records_filename(['json', 'csv', 'db'], True)
                    storage = get_suitable_storage(clients_file_path)
                    data_manager = DataManager(storage)
                    data_manager.add_record(client)
                    time.sleep(1)
                # view all shelters
                elif choice == 2:
                    shelter_file_path = IOManager.get_shelter_filename()
                    shelter_reader = ShelterFileReader(shelter_file_path)
                    shelters = shelter_reader.load_shelters()
                    if shelters[1] is not None:
                        IOManager.print_error("Could not load shelters", shelters[1])
                        continue
                    IOManager.print_shelter_list(shelters[0])
                    time.sleep(1)
                # get shelter recommendations for clients
                elif choice == 3:
                    shelter_file_path = IOManager.get_shelter_filename()
                    clients_file_path = IOManager.get_client_records_filename(['csv', 'json', 'db'])
                    storage = get_suitable_storage(clients_file_path)
                    data_manager = DataManager(storage)
                    clients = data_manager.load_records()
                    if clients[1] is not None:
                        IOManager.print_error("Could not load clients", clients[1])
                        continue
                    shelter_reader = ShelterFileReader(shelter_file_path)
                    shelters = shelter_reader.load_shelters()
                    if shelters[1] is not None:
                        IOManager.print_error("Could not load shelters", shelters[1])
                        continue
                    for client in clients[0]:
                        if client.get("outcome") is True:
                            continue
                        result = get_recommendation(clients_file_path, client, shelters[0])
                        if result is not None:
                            continue
                        rerun = IOManager.get_rerun_decision()
                        if rerun:
                            # only rerun once more, do not ask for rerun decision again
                            get_recommendation(clients_file_path, client, shelters[0])
                    time.sleep(1)
                # search for a client record by client_id
                elif choice == 4:
                    clients_file_path = IOManager.get_client_records_filename(['csv', 'json', 'db'])
                    client_id = IOManager.ask_for_client_id()
                    storage = get_suitable_storage(clients_file_path)
                    data_manager = DataManager(storage)
                    record = data_manager.get_clientid(client_id)
                    if record[1] is not None:
                        IOManager.print_error("Could not find the requested client record.", record[1])
                        continue
                    IOManager.print_client_record(record[0])
                    time.sleep(1)
                # filter cases by outcome
                elif choice == 5:
                    clients_file_path = IOManager.get_client_records_filename(['csv', 'json', 'db'])
                    storage = get_suitable_storage(clients_file_path)
                    data_manager = DataManager(storage)
                    clients = data_manager.load_records()
                    if clients[1] is not None:
                        IOManager.print_error("Could not load clients", clients[1])
                        continue
                    outcome = IOManager.ask_for_outcome_filter()
                    filtered_cases = data_manager.filter_records_by_outcome(clients[0], outcome)
                    IOManager.print_filtered_cases(filtered_cases, outcome)
                    time.sleep(1)
                # log out
                elif choice == 6:
                    IOManager.print_update("Logging out. Returning to authentication menu...")
                    break  # Break inner loop, return to authentication
        else:
            storage = get_suitable_storage("clients.json")
            data_manager = DataManager(storage)
            while True:
                # Only fetch client data if the user selects an option that needs it (1, 2, or 3)
                matched_client, error = find_client_record(data_manager, user.nric)
                if error is not None:
                    IOManager.print_error("There is an error in finding your application record", error)
                    continue
                menu_editor = 0
                if matched_client is not None and matched_client.get("outcome") is True:
                    menu_editor = 1
                choice = IOManager.display_client_menu(menu_editor)


                if choice == 1:
                    if matched_client is not None:
                        print("You have an active application.")
                    else:
                        client = IOManager.collect_intake_input(user.nric)
                        data_manager.add_record(client)
                    time.sleep(1)

                elif choice == 2:
                    if matched_client is None:
                        print("No application record found for your NRIC. Please submit an application first.")
                    else:
                        outcome = matched_client.get("outcome")
                        if outcome is None:
                            print("Your application is still under review. Please check back later.")
                        elif outcome is True:
                            print("Congratulations! Your application has been accepted. Please view your shelter with option 3.")
                        elif outcome is False:
                            print("We regret to inform you that your application has been rejected, we are resolving the matter.")
                    time.sleep(1)

                elif choice == 3:
                    if not matched_client or matched_client.get("outcome") is not True:
                        print("You have no assigned shelter. If you have an active application, please wait for the outcome to be updated.")
                    else:
                        best_shelter = matched_client.get("accepted_shelter")
                        print("------------------------------------------------------")
                        print(IOManager.format_shelter(best_shelter))
                        time.sleep(1)
                        input("\nPress Enter to continue...")
                    time.sleep(1)
                elif choice == 4:
                    IOManager.print_update("Logging out. Returning to authentication menu...")
                    time.sleep(1)
                    break   # Break inner loop, return to authentication
            

if __name__ == "__main__":
    main()