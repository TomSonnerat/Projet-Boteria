import requests
import json

class PlantTrackingTestClient:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()

    def test_get_plant_list(self):
        print("\n--- Testing Get Plant List ---")
        response = self.session.get(f"{self.base_url}/GetPlantList")
        self._print_response(response, "Plant List")

    def test_get_plant_infos(self, plant_id=1):
        print(f"\n--- Testing Get Plant Infos for Plant ID {plant_id} ---")
        response = self.session.get(f"{self.base_url}/GetPlantInfos", params={"id": plant_id})
        self._print_response(response, "Plant Infos")

    def test_get_plant_besoins(self, plant_id=1):
        print(f"\n--- Testing Get Plant Besoins for Plant ID {plant_id} ---")
        response = self.session.get(f"{self.base_url}/GetPlantBesoins", params={"id": plant_id})
        self._print_response(response, "Plant Besoins")

    def test_get_plant_interventions(self, plant_id=1):
        print(f"\n--- Testing Get Plant Interventions for Plant ID {plant_id} ---")
        response = self.session.get(f"{self.base_url}/GetPlantInterventions", params={"id_plante": plant_id})
        self._print_response(response, "Plant Interventions")

    def test_get_intervention_infos(self, intervention_id=1):
        print(f"\n--- Testing Get Intervention Infos for Intervention ID {intervention_id} ---")
        response = self.session.get(f"{self.base_url}/GetInterventionInfos", params={"id_intervention": intervention_id})
        self._print_response(response, "Intervention Infos")

    def test_get_latest_intervention(self, plant_id=1):
        print(f"\n--- Testing Get Latest Intervention for Plant ID {plant_id} ---")
        response = self.session.get(f"{self.base_url}/GetLatestIntervention", params={"id_plante": plant_id})
        self._print_response(response, "Latest Intervention")

    def test_get_all_rapports(self, plant_id=1):
        print(f"\n--- Testing Get All Rapports for Plant ID {plant_id} ---")
        response = self.session.get(f"{self.base_url}/GetAllRapports", params={"id_plante": plant_id})
        self._print_response(response, "All Rapports")

    def test_get_rapport(self, rapport_id='2024-01'):
        print(f"\n--- Testing Get Rapport for Rapport ID {rapport_id} ---")
        response = self.session.get(f"{self.base_url}/GetRapport", params={"id_rapport": rapport_id})
        self._print_response(response, "Rapport")

    def test_get_latest_rapport(self, plant_id=1):
        print(f"\n--- Testing Get Latest Rapport for Plant ID {plant_id} ---")
        response = self.session.get(f"{self.base_url}/GetLatestRapport", params={"id_plante": plant_id})
        self._print_response(response, "Latest Rapport")

    def test_get_liste_membre(self):
        print("\n--- Testing Get Liste Membre ---")
        response = self.session.get(f"{self.base_url}/GetListeMembre")
        self._print_response(response, "Liste Membre")

    def test_get_membre_infos(self, membre_id=1):
        print(f"\n--- Testing Get Membre Infos for Membre ID {membre_id} ---")
        response = self.session.get(f"{self.base_url}/GetMembreInfos", params={"id_membre": membre_id})
        self._print_response(response, "Membre Infos")

    def test_get_hierarchie(self):
        print("\n--- Testing Get Hierarchie ---")
        response = self.session.get(f"{self.base_url}/GetHierarchie")
        self._print_response(response, "Hierarchie")

    def test_get_agenda_classe(self, classe='DE'):
        print(f"\n--- Testing Get Agenda Classe for {classe} ---")
        response = self.session.get(f"{self.base_url}/GetAgendaClasse", params={"classe": classe})
        self._print_response(response, "Agenda Classe")

    def _print_response(self, response, endpoint_name):
        print(f"Endpoint: {endpoint_name}")
        print(f"Status Code: {response.status_code}")
        try:
            json_data = response.json()
            print("Response JSON:")
            print(json.dumps(json_data, indent=2))
        except json.JSONDecodeError:
            print("Response is not a valid JSON")
            print(response.text)
        except Exception as e:
            print(f"Error processing response: {e}")
        print("-" * 50)

def run_all_tests():
    client = PlantTrackingTestClient()
    
    client.test_get_plant_list()
    client.test_get_plant_infos()
    client.test_get_plant_besoins()
    client.test_get_plant_interventions()
    client.test_get_intervention_infos()
    client.test_get_latest_intervention()
    client.test_get_all_rapports()
    client.test_get_rapport()
    client.test_get_latest_rapport()
    client.test_get_liste_membre()
    client.test_get_membre_infos()
    client.test_get_hierarchie()
    client.test_get_agenda_classe()

def main():
    server_address = input("Enter the server IP address (default localhost): ") or "localhost"
    port = input("Enter the server port (default 5000): ") or "5000"
    
    client = PlantTrackingTestClient(f"http://{server_address}:{port}")
    
    while True:
        print("\nPlant Tracking Server Test Client")
        print("1. Run All Tests")
        print("2. Test Specific Endpoint")
        print("3. Exit")
        
        choice = input("Enter your choice (1-3): ")
        
        if choice == '1':
            run_all_tests()
        elif choice == '2':
            endpoints = {
                '1': ('Get Plant List', client.test_get_plant_list),
                '2': ('Get Plant Infos', lambda: client.test_get_plant_infos(input("Enter Plant ID: "))),
                '3': ('Get Plant Besoins', lambda: client.test_get_plant_besoins(input("Enter Plant ID: "))),
                '4': ('Get Plant Interventions', lambda: client.test_get_plant_interventions(input("Enter Plant ID: "))),
                '5': ('Get Intervention Infos', lambda: client.test_get_intervention_infos(input("Enter Intervention ID: "))),
                '6': ('Get Latest Intervention', lambda: client.test_get_latest_intervention(input("Enter Plant ID: "))),
                '7': ('Get All Rapports', lambda: client.test_get_all_rapports(input("Enter Plant ID: "))),
                '8': ('Get Rapport', lambda: client.test_get_rapport(input("Enter Rapport ID: "))),
                '9': ('Get Latest Rapport', lambda: client.test_get_latest_rapport(input("Enter Plant ID: "))),
                '10': ('Get Liste Membre', client.test_get_liste_membre),
                '11': ('Get Membre Infos', lambda: client.test_get_membre_infos(input("Enter Membre ID: "))),
                '12': ('Get Hierarchie', client.test_get_hierarchie),
                '13': ('Get Agenda Classe', lambda: client.test_get_agenda_classe(input("Enter Classe: ")))
            }
            
            print("\nAvailable Endpoints:")
            for key, (name, _) in endpoints.items():
                print(f"{key}. {name}")
            
            endpoint_choice = input("Enter endpoint number to test: ")
            if endpoint_choice in endpoints:
                endpoints[endpoint_choice][1]()
            else:
                print("Invalid endpoint selection.")
        
        elif choice == '3':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()