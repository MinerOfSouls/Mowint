# Zbiór danych

Zbiorem plików jest około 500 000 e-maily prqcowników firmy ENRON uszyskanych w wyniku śledztwa
Federal Energy Regularory Commission.
(https://www.cs.cmu.edu/~enron/)

Następnie usunięte zostały informacje nagłówkowe z wyjątkiem:
tematu maila, odbiorcy i nadawcy. W związku z czestym występowaniem w zbioże danych zbitek liter
zostały pominięte słowa dłóższe niż 22 litery, zawierające wielkie litery nie na początku lub zawierające więcej niż
4 powtóżenia tej samej litery. Usunięty zostały też stop wordy z pliku stopwords.py. Dodatkowo usunięte zostały też słowa
które moim zdaniem mogły występować w każdym pliku.

Łącznie wszyskich unikatowych słów jest około 200 000.

Funkcje do preprocesingu danych i twożenia macieży znajdują się w pliku wordbag.py
Twożą one listę termów, plików, macierz przed normalizacją i macież znormalizowaną
oraz macież Ak z SVD gdzie k jest równe 1000.

Ostatenczny rozmiar pliku z macieżą to około 350 MB

# Wyszukiwarka

Wyszukiwanie jest zarządzane przez klasy Engine i SVDEngine w pliku engine.py
Engine obsługuje wyszukiwanie z normalizacia i bez przez zmianę parametry mode w konstruktorze.
SVDEngine to klasa która obsługuje wyszukiwanie z SVD.

Aplikacja znajduje się w pliku app.py i ten plik uruchamia aplikacje.
Pozwala ona na zmiane typu wiszukiwania oraz wybranie ilości wyszukiwanych plików.
Aby uruchomić aplikacje potrzebne jest około 2GB pamięci RAM.

# Przykładowe wyszukiwania

"weekend fishing trip" - zwraca dwa ciagi maili współpracowników planujących wypad na ryby
"cars car parts" - usunięty spam o kupnie cześci samochodowych i listę mailingową o samochodach jednego człowieka
imiona i nazwiska pracowników - maile które wysłali lub które zostały wysłane do nich
zapytania zawierające stocks i podobne wyrazy - raporty o giełdzie
jakiekolwiek zapytanie zawierające buy - najktótsze maile pana Richard Buy