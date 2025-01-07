[![HACS Default][hacs_shield]][hacs]

[hacs_shield]: https://img.shields.io/static/v1.svg?label=HACS&message=Default&style=popout&color=green&labelColor=41bdf5&logo=HomeAssistantCommunityStore&logoColor=white
[hacs]: https://hacs.xyz/docs/default_repositories



##Energetyczny Kompas PSE – integracja Home Assistant dla świadomego zarządzania energią
Energetyczny Kompas PSE to integracja z platformą Home Assistant, umożliwiająca uzyskanie danych o zalecanych działaniach dotyczących zużycia energii elektrycznej, opartych na informacjach dostarczanych przez Polskie Sieci Energetyczne. Dodatek ten odzwierciedla dane prezentowane w aplikacji Energetyczny Kompas PSE i jest szczególnie przydatny dla użytkowników taryfy G14Dynamic oferowanej przez Tauron. Na podstawie tych informacji Tauron przelicza ceny energii, dostosowując je do aktualnych warunków i zaleceń.

Więcej informacji: Energetyczny Kompas PSE  https://www.energetycznykompas.pl/

## Możliwe stany
- ZALECANE UŻYTKOWANIE
- NORMALNE UŻYTKOWANIE
- ZALECANE OSZCZĘDZANIE
- WYMAGANE OGRANICZANIE

## Instalacja
1. Dodaj to repozytorium jako niestandardowe w HACS.
2. Zainstaluj integrację i zrestartuj Home Assistant.
3. Sensor pojawi się automatycznie.

## Dodatkowe dane
Dzięki atrybutom jakie zwraca encja użytkownicy mają możliwość:

- tworzenia zaawansowanych scenariuszy oszczędzania energii,
- dostosowywania urządzeń do aktualnych zaleceń energetycznych,
- monitorowania i optymalizacji kosztów w taryfie G14Dynamic oferowanej przez Tauron.

## Licencja
MIT
