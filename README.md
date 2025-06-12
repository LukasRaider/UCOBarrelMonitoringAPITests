# Automatizovaná testovací sada Barrel API 🧪

## 🔧 Požadavky
- Python 3.8+
- Instalace balíčků
- `pip install -r requirements.txt`
- Vytvoř soubor `.env` s údajem :
  BASE_URL=https://to-barrel-monitor.azurewebsites.net

## ▶️ Spuštění testů
```bash
pytest
```

# Testovací scénáře

## Testy barelů
- test_vytvoreni_noveho_barelu - Vytvoření barelu a kontrola stavového kodu 201,200
- test_ziskani_seznamu_barelu - Zobrazení všech barelů v systému, ukázáni seznamu
- test_ziskani_detailu_barelu - Získáni informaci o barelu a správný klič jako při jeho vytvoření
- test_smazani_barelu - Smazání barelu a kontrola statusu 200

## Testy měření
- test_pridani_mereni_necistot - Vytvoření meření barelu nečistot id a kodu  201
- test_ziskani_vsech_mereni - Ziskání listu o všech barelech v systému

## Testy krajních případů
- test_vytvoreni_barelu_bez_udaju - Vytvoření barelu bez údajů s prázdným json
- test_barel_spatne_typy - Vytvoření barelu se špatným tyepm ID
- test_vytvoreni_mereni_se_spatnymi_udaji - Vytvoření mereni barelu se špatnými údaji nejsou validni hodnoty a neexistuje ID
- test_mereni_chybi_vaha - Test ověřuje, že bez weight není možné vytvořit měření
- test_volani_neexistujiciho_barelu - Volání neexistujícího barelu
- test_smazani_neexistujiciho_barelu - Smazání neexistujicího barelu