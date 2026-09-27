# Sunways Cloud pro Home Assistant

Česky | [English](README.md)

Komunitní integrace pro Home Assistant, která monitoruje fotovoltaické elektrárny Sunways prostřednictvím cloudového rozhraní Sunways Portal.

## Co umí

- připojí se ke stávajícímu účtu Sunways Portal;
- vyhledá elektrárny a měniče přiřazené k účtu;
- zpřístupní výrobu, spotřebu, tok do sítě, baterii a provozní hodnoty měniče, pokud je zařízení poskytuje;
- podporuje nastavitelný interval obnovování a opětovné přihlášení;
- kontroluje kvalitu cloudových hodnot a nenahrazuje chybějící měření falešnými nulami;
- z diagnostiky odstraňuje přihlašovací údaje, tokeny a identifikátory elektrárny.

Integrace je pouze pro čtení. Nemění pracovní režim měniče, exportní limit ani jiná nastavení zařízení.

## Instalace

### Vlastní repozitář HACS

1. V HACS otevřete **Integrace** a přidejte tento repozitář jako vlastní repozitář typu **Integration**.
2. Nainstalujte **Sunways Cloud**.
3. Restartujte Home Assistant.
4. Otevřete **Nastavení → Zařízení a služby → Přidat integraci** a vyhledejte **Sunways**.

### Ruční instalace

Zkopírujte `custom_components/sunways` do `/config/custom_components/sunways`, restartujte Home Assistant a přidejte integraci z uživatelského rozhraní.

## Nastavení a soukromí

Integrace vyžaduje přihlašovací údaje k Sunways Portal. Home Assistant je ukládá ve vlastním chráněném úložišti konfigurace. Diagnostiku ani konfigurační soubory nezveřejňujte bez předchozí kontroly.

API portálu Sunways není veřejně garantované rozhraní a může se bez upozornění změnit. Projekt není oficiálně spojen se společností Sunways Technologies ani jí podporován.

## Autoři a licence

Projekt vychází z integrace [adamus-tork/home-assistant-sunways](https://github.com/adamus-tork/home-assistant-sunways) licencované pod Apache-2.0 a obsahuje následné komunitní úpravy. Podrobnosti jsou v souboru [NOTICE](NOTICE).

Projekt je vydán pod [licencí Apache 2.0](LICENSE).

## Podpora projektu

Vývoj a údržbu můžete podpořit na [Buy Me a Coffee](https://buymeacoffee.com/kojakcio).



