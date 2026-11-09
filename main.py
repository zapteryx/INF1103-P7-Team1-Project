import time
from ai_manager import AIManager, GeminiClient, SampleResponseClient
from data_manager import DataManager, ShelterFileReader, FileStorage
from io_manager import IOManager
from logic_manager import LogicManager

# Maintained by Ming Xuan (2604426)
def get_recommendation(clients_file_path: str, client: dict, shelters: list[dict]) -> bool | None:
    IOManager.print_update(f"Getting recommendations for client {client['client_id']}...")
    ai_manager = AIManager(GeminiClient(), SampleResponseClient())
    recommendation = ai_manager.get_shelter_recommendation(client, shelters)
    if recommendation is None:
        IOManager.print_error(f"AI recommendation failed for client {client['client_id']}.")
        return False
    # IOManager.print_update(f"AI Recommendation for client {client['client_id']}", f"\n{json.dumps(recommendation, indent=2)}")
    IOManager.print_update("Finding the best shelter based on AI recommendation and additional criteria...")
    logic_manager = LogicManager()
    best_shelter = logic_manager.calculate_suitability_score(shelters, client, recommendation)
    if best_shelter is None:
        IOManager.print_error(f"No suitable shelter found for client {client['client_id']} based on AI recommendation and additional criteria.")
        return False
    # IOManager.print_update(f"Best shelter for client {client['client_id']}", f"\n{json.dumps(best_shelter, indent=2)}")
    outcome = IOManager.present_best_shelter(client, best_shelter)
    data_manager = DataManager(FileStorage(clients_file_path))
    if outcome is True:
        data_manager.update_record(client['client_id'], outcome=True, accepted_shelter=best_shelter)
        IOManager.print_update(f"Client {client['client_id']} record updated with outcome: Accepted and accepted shelter: {best_shelter['shelter_name']}")
        return True
    elif outcome is False:
        data_manager.update_record(client['client_id'], outcome=False)
        IOManager.print_update(f"Client {client['client_id']} record updated with outcome: Rejected")
        return True
    return None

# Maintained by Ming Xuan (2604426)
def main() -> None:
    while True:
        choice = IOManager.display_menu()
        # new client intake
        if choice == 1:
            client = IOManager.collect_intake_input()
            clients_file_path = IOManager.get_client_records_filename(['json', 'csv'], True)
            data_manager = DataManager(FileStorage(clients_file_path))
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
            clients_file_path = IOManager.get_client_records_filename(['csv', 'json'])
            data_manager = DataManager(FileStorage(clients_file_path))
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
            clients_file_path = IOManager.get_client_records_filename(['csv', 'json'])
            client_id = IOManager.ask_for_client_id()
            data_manager = DataManager(FileStorage(clients_file_path))
            record = data_manager.get_clientid(client_id)
            if record[1] is not None:
                IOManager.print_error(f"Could not find client record for client_id {client_id}", record[1])
                continue
            IOManager.print_client_record(record[0])
            time.sleep(1)
        # filter cases by outcome
        elif choice == 5:
            clients_file_path = IOManager.get_client_records_filename(['csv', 'json'])
            data_manager = DataManager(FileStorage(clients_file_path))
            clients = data_manager.load_records()
            if clients[1] is not None:
                IOManager.print_error("Could not load clients", clients[1])
                continue
            outcome = IOManager.ask_for_outcome_filter()
            filtered_cases = data_manager.filter_records_by_outcome(clients[0], outcome)
            IOManager.print_filtered_cases(filtered_cases, outcome)
            time.sleep(1)
        # exit
        elif choice == 6:
            IOManager.print_update("Thank you for using Social Service AI. Goodbye!")
            break

if __name__ == "__main__":
    main()