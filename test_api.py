import pytest
import requests
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

# Nacteni adresy pro API z env
@pytest.fixture(scope="session")
def base_url():
    url = os.getenv("BASE_URL")
    assert url, "BASE_URL není nastaven v .env souboru"
    return url

# Udrženi a připadne na začátku generování ID barelu
@pytest.fixture(scope="session")
def barrel_uuid():
    return str(uuid.uuid4())

# Vzor pro strukturu barelu
@pytest.fixture(scope="session")
def barrel_vzor(barrel_uuid):
    return {
        "id": barrel_uuid,
        "qr": "test_qr_code",
        "rfid": "test_rfid_tag",
        "nfc": "test_nfc_chip"
    }

# Vytvoření barelu a kontrola stavového kodu 201,200
def test_vytvoreni_noveho_barelu(base_url, barrel_uuid):
    try:
        response = requests.post(f"{base_url}/barrels", json={
            "id": barrel_uuid,
            "qr": "test_qr_code",
            "rfid": "test_rfid_tag",
            "nfc": "test_nfc_chip"
        })
        assert response.status_code in [200, 201], f"Unexpected status: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "Odpověď není validní JSON objekt"
        assert data.get("id") == barrel_uuid, f"UUID nesouhlasí: {data.get('id')}"
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Chyba při POST /barrels: {e}")
    except ValueError:
        pytest.fail("Odpověď není validní JSON.")
# Zobrazení všech barelů v systému, ukázáni seznamu
def test_ziskani_seznamu_barelu(base_url):
    try:
        response = requests.get(f"{base_url}/barrels")
        assert response.status_code == 200, f"Unexpected status: {response.status_code}"
        data = response.json()
        assert isinstance(data, list), f"Očekáván list, ale přišel typ: {type(data)}"
        assert len(data) > 0, "Seznam barelů je prázdný"
        assert all("id" in barrel for barrel in data), "Některé položky nemají ID"
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Chyba při GET /barrels: {e}")
    except ValueError:
        pytest.fail("Odpověď není validní JSON.")

# Vytvoření meření barelu nečistot id a kodu 201 - chyba v systému, systém nezaznamená barel
def test_pridani_mereni_necistot(base_url, barrel_uuid):
    try:
        measurement_id = str(uuid.uuid4())
        response = requests.post(f"{base_url}/measurements", json={
            "id": measurement_id,
            "barrelId": barrel_uuid,
            "dirtLevel": 0.42,
            "weight": 17.5
        })
        assert response.status_code in [200, 201], f"Unexpected status: {response.status_code}"
        data = response.json()
        assert "data" in data, "Chybí klíč 'data' ve výsledku"
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Chyba při POST /measurements: {e}")
    except ValueError:
        pytest.fail("Odpověď není validní JSON.")

# Ziskání listu o všech barelech v systému
def test_ziskani_vsech_mereni(base_url):
    try:
        response = requests.get(f"{base_url}/measurements")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "data" in data, "Neplatná struktura měření"
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Chyba při GET /measurements: {e}")
    except ValueError:
        pytest.fail("Odpověď není validní JSON.")
# Získáni informaci o barelu a správný klič jako při jeho vytvoření - neukazuje správně, posílá celý list barelu
def test_ziskani_detailu_barelu(base_url, barrel_uuid, barrel_vzor):

    try:
        response = requests.get(f"{base_url}/barrels?id={barrel_uuid}")
        assert response.status_code == 200, f"Očekáván status 200, přišel: {response.status_code}"
        data = response.json()
        if "data" in data:
            data = data["data"]
        # Kontrola, že všechna pole z původního vzoru jsou i ve vráceném JSONu
        for key in barrel_vzor:
            assert key in data, f"V odpovědi chybí klíč: {key}"

    except requests.exceptions.RequestException as e:
        pytest.fail(f"Chyba při GET požadavku: {e}")
    except ValueError:
        pytest.fail("Odpověď není validní JSON.")


# Smazání barelu a kontrola statusu 200 - nefunguje
def test_smazani_barelu(base_url, barrel_uuid):
    try:
        response = requests.delete(f"{base_url}/barrels/{barrel_uuid}")
        assert response.status_code in [200, 202, 204], f"Delete status: {response.status_code}"
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Chyba při DELETE /barrels/{barrel_uuid}: {e}")

# Edge test casy
# Vytvoření barelu bez údajů s prázdným json
def test_vytvoreni_barelu_bez_udaju(base_url):
    try:
        res = requests.post(f"{base_url}/barrels", json={})
        assert res.status_code in [400, 422]
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Request failed: {e}")

# Vytvoření barelu se špatným tyepm ID
def test_barel_spatne_typy(base_url):
    try:
        payload = {
            "id": 12345,
            "qr": True,
            "rfid": ["rfid"],
            "nfc": None
        }
        res = requests.post(f"{base_url}/barrels", json=payload)
        assert res.status_code in [400, 422], f"Očekáván chybový status, přišel: {res.status_code}"
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Chyba při POST se špatnými typy: {e}")

# Vytvoření mereni barelu se špatnými údaji nejsou validni hodnoty a neexistuje ID
def test_vytvoreni_mereni_se_spatnymi_udaji(base_url):
    try:
        payload = {
            "barrelId": str(uuid.uuid4()),
            "dirtLevel": "high",
            "weight": "heavy"
        }
        res = requests.post(f"{base_url}/measurements", json=payload)
        assert res.status_code in [400, 422]
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Request failed: {e}")

# Test ověřuje, že bez weight není možné vytvořit měření
def test_mereni_chybi_vaha(base_url, barrel_uuid):
    try:
        payload = {
            "id": str(uuid.uuid4()),
            "barrelId": barrel_uuid,
            "dirtLevel": 0.5
        }
        res = requests.post(f"{base_url}/measurements", json=payload)
        assert res.status_code in [400, 422], f"Očekáván chybový status, přišel: {res.status_code}"
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Chyba při POST /measurements bez weight: {e}")

# Volání neexistujícího barelu
def test_volani_neexistujiciho_barelu(base_url):
    try:
        fake_id = str(uuid.uuid4())
        res = requests.get(f"{base_url}/barrels/{fake_id}")
        assert res.status_code in [404, 500]
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Request failed: {e}")


# Smazání neexistujicího barelu - Nefunguje mazani špatný requerment
def test_smazani_neexistujiciho_barelu(base_url):
    try:
        fake_id = str(uuid.uuid4())
        res = requests.delete(f"{base_url}/barrels/{fake_id}")
        assert res.status_code in [404, 400, 204]
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Request failed: {e}")