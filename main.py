import json
import time

import ai_manager
import data_manager
import io_manager
import logic_manager

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
            io_manager.print_shelter_list(shelters[0])
            time.sleep(1)
        # get shelter recommendations for clients
        elif choice == 3:
            shelter_file_path = io_manager.get_shelter_filename()
            clients_file_path = io_manager.get_client_records_filename(['csv', 'json'])
            clients = data_manager.load_records(clients_file_path)
            if clients[1] is not None:
                io_manager.print_error("Could not load clients", clients[1])
            shelters = data_manager.load_shelters(shelter_file_path)
            if shelters[1] is not None:
                io_manager.print_error("Could not load shelters", shelters[1])
            for client in clients[0]:
                io_manager.print_update(f"Getting recommendations for client {client['client_id']}...")
                recommendation = ai_manager.get_shelter_recommendation(client, shelters[0])
                if recommendation is not None:
                    io_manager.print_update(f"AI Recommendation for client {client['client_id']}", f"\n{json.dumps(recommendation, indent=2)}")
                    io_manager.print_update("Finding the best shelter based on AI recommendation and additional criteria...")
                    best_shelter = logic_manager.calculate_suitability_score(client, recommendation)
                    if best_shelter is not None:
                        io_manager.print_update(f"Best shelter for client {client['client_id']}", f"\n{json.dumps(best_shelter, indent=2)}")
                    else:
                        io_manager.print_error(f"No suitable shelter found for client {client['client_id']} based on AI recommendation and additional criteria.")
                else:
                    io_manager.print_error(f"No recommendations available for client {client['client_id']}.")
            time.sleep(1)
        # exit
        elif choice == 4:
            io_manager.print_update("Thank you for using Social Service AI. Goodbye!")
            break
        # oob
        else:
            io_manager.print_error("You have entered an invalid choice. Please try again.")

if __name__ == "__main__":
    main()