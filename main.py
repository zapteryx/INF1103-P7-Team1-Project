import json
import time

import ai_manager
import data_manager
import io_manager
import logic_manager

# Maintained by Ming Xuan (2604426)
def get_recommendation(clients_file_path: str, client: dict, shelters: list[dict]) -> bool | None:
    io_manager.print_update(f"Getting recommendations for client {client['client_id']}...")
    recommendation = ai_manager.get_shelter_recommendation(client, shelters[0])
    if recommendation is None:
        io_manager.print_error(f"AI recommendation failed for client {client['client_id']}.")
        return False
    # io_manager.print_update(f"AI Recommendation for client {client['client_id']}", f"\n{json.dumps(recommendation, indent=2)}")
    io_manager.print_update("Finding the best shelter based on AI recommendation and additional criteria...")
    best_shelter = logic_manager.calculate_suitability_score(client, recommendation)
    if best_shelter is None:
        io_manager.print_error(f"No suitable shelter found for client {client['client_id']} based on AI recommendation and additional criteria.")
        return False
    # io_manager.print_update(f"Best shelter for client {client['client_id']}", f"\n{json.dumps(best_shelter, indent=2)}")
    outcome = io_manager.present_best_shelter(client, best_shelter)
    if outcome:
        data_manager.update_record(clients_file_path, client['client_id'], outcome=outcome, accepted_shelter=best_shelter)
        io_manager.print_update(f"Client {client['client_id']} record updated with outcome: {outcome} and accepted shelter: {best_shelter['shelter_name']}")
        return True
    return None

# Maintained by Ming Xuan (2604426)
def main() -> None:
    while True:
        choice = io_manager.display_menu()
        # new client intake
        if choice == 1:
            client = io_manager.collect_intake_input()
            clients_file_path = io_manager.get_client_records_filename(['json'], True)
            data_manager.add_record(clients_file_path, client)
            time.sleep(1)
        # view all shelters
        elif choice == 2:
            shelter_file_path = io_manager.get_shelter_filename()
            shelters = data_manager.load_shelters(shelter_file_path)
            if shelters[1] is not None:
                print(f"Error loading shelters: {shelters[1]}")
                continue
            io_manager.print_shelter_list(shelters[0])
            time.sleep(1)
        # get shelter recommendations for clients
        elif choice == 3:
            shelter_file_path = io_manager.get_shelter_filename()
            clients_file_path = io_manager.get_client_records_filename(['csv', 'json'])
            clients = data_manager.load_records(clients_file_path)
            if clients[1] is not None:
                io_manager.print_error("Could not load clients", clients[1])
                continue
            shelters = data_manager.load_shelters(shelter_file_path)
            if shelters[1] is not None:
                io_manager.print_error("Could not load shelters", shelters[1])
                continue
            for client in clients[0]:
                result = get_recommendation(clients_file_path, client, shelters)
                if result is not None:
                    continue
                rerun = io_manager.get_rerun_decision()
                if rerun:
                    # only rerun once more, do not ask for rerun decision again
                    get_recommendation(clients_file_path, client, shelters)
            time.sleep(1)
        # search for a client record by client_id
        elif choice == 4:
            clients_file_path = io_manager.get_client_records_filename(['csv', 'json'])
            client_id = io_manager.ask_for_client_id()
            record = data_manager.get_clientid(clients_file_path, client_id)
            if record[1] is not None:
                io_manager.print_error(f"Could not find client record for client_id {client_id}", record[1])
                continue
            io_manager.print_client_record(record[0])
            time.sleep(1)
        # exit
        elif choice == 5:
            io_manager.print_update("Thank you for using Social Service AI. Goodbye!")
            break

if __name__ == "__main__":
    main()