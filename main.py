import json
import ai_manager
import data_manager
import io_manager
import logic_manager

# Maintained by Ming Xuan (2604426)
def get_shelter_file_path(file_path):
    if file_path == "":
        file_path = io_manager.get_shelter_filename()
    return file_path

# Maintained by Ming Xuan (2604426)
def get_clients_file_path(file_path):
    if file_path == "":
        file_path = io_manager.get_client_records_filename()
    return file_path

# Maintained by Ming Xuan (2604426)
def main() -> None:
    shelter_file_path = ""
    clients_file_path = ""
    while True:
        choice = io_manager.display_menu()
        # new client intake
        if choice == 1:
            client = io_manager.collect_intake_input()
            clients_file_path = get_clients_file_path(clients_file_path)
            while not clients_file_path.endswith('.json'):
                print("Error: New client intake can only be saved in JSON files. Please provide a valid JSON filename.")
                clients_file_path = io_manager.get_client_records_filename()
            data_manager.add_record(clients_file_path, client)
        # view all shelters
        elif choice == 2:
            shelter_file_path = get_shelter_file_path(shelter_file_path)
            shelters = data_manager.load_shelters(shelter_file_path)
            if shelters[1] is not None:
                print(f"Error loading shelters: {shelters[1]}")
            io_manager.print_shelter_list(shelters[0])
        # update csv file used
        elif choice == 3:
            # Direct update instead of using cache function
            shelter_file_path = io_manager.get_shelter_filename()
            clients_file_path = io_manager.get_client_records_filename()
        # get shelter recommendations for clients
        elif choice == 4:
            shelter_file_path = get_shelter_file_path(shelter_file_path)
            clients_file_path = get_clients_file_path(clients_file_path)
            clients = data_manager.load_records(clients_file_path) # Example: loading existing records from a JSON file
            if clients[1] is not None:
                print(f"Error loading clients: {clients[1]}")
            shelters = data_manager.load_shelters(shelter_file_path)
            if shelters[1] is not None:
                print(f"Error loading shelters: {shelters[1]}")
            for client in clients[0]:
                print(f"\nGetting recommendations for client {client['client_id']}...")
                recommendation = ai_manager.get_shelter_recommendation(client, shelters[0])
                if recommendation is not None:
                    print(f"AI Recommendation for client {client['client_id']}:")
                    print(json.dumps(recommendation, indent=2))
                    print("Finding the best shelter based on AI recommendation and additional criteria...")
                    best_shelter = logic_manager.calculate_suitability_score(client, recommendation)
                    if best_shelter is not None:
                        print(f"Best shelter for client {client['client_id']}:")
                        print(json.dumps(best_shelter, indent=2))
                    else:
                        print(f"No suitable shelter found for client {client['client_id']} based on AI recommendation and additional criteria.")
                else:
                    print(f"No recommendations available for client {client['client_id']}.")
        # exit
        elif choice == 5:
            print("Thank you for using Social Service AI. Goodbye!")
            break
        # oob
        else:
            print("You have entered an invalid choice. Please try again.")

if __name__ == "__main__":
    main()