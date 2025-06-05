# noSpam

Spam or no spam - that is a question ~ Shakespear probably, idk...

## Spis treści

1. [Opis projektu](#opis-projektu)
2. [Trenowanie modelu](#trenowanie-modelu)
    - [1. Eksperymenty i wyszukiwanie hiperparametrów](#1-eksperymenty-i-wyszukiwanie-hiperparametrów)
    - [2. Wybór najlepszej konfiguracji](#2-wybór-najlepszej-konfiguracji)
    - [3. Trenowanie finalnego modelu](#3-trenowanie-finalnego-modelu)
3. [Backend (API)](#backend-api)
    - [Endpointy](#endpointy)
4. [Frontend (Angular)](#frontend-angular)

## <a id="opis-projektu"></a> Opis projektu

Projekt polega na klasyfikacji wiadomości e-mail jako **spam** lub **nie spam**, przy użyciu ręcznie wytrenowanego
modelu ML.
Projekt składa się z trzech części:

* Model ML: trenowany lokalnie z użyciem `PyTorch`, `SentenceTransformer` i `Sacred` (do zarządzania eksperymentami).
* Backend: REST API stworzone z użyciem `FastAPI`, które wykorzystuje wytrenowany model do predykcji.
  *Frontend: Aplikacja `Angular`, która umożliwia wprowadzenie tekstu wiadomości e-mail i wyświetla wynik predykcji.

## <a id="trenowanie-modelu"></a> Trenowanie modelu

### <a id="1-eksperymenty-i-wyszukiwanie-hiperparametrów"></a> 1. Eksperymenty i wyszukiwanie hiperparametrów

Skrypt model_training.py przeprowadza eksperymenty z różnymi kombinacjami hiperparametrów:

* `epochs`: [10, 25, 50]
* `batch_size`: [16, 32, 64]
* `learning_rate`: [0.01, 0.001, 0.0001]

Do zarządzania eksperymentami używany jest Sacred.
Rezultaty zapisywane są lokalnie w katalogu SACRED_OBSERVER_DIRECTORY, który zawiera konfiguracje i metryki.

```bash
    python model_training.py
```

### <a id="2-wybór-najlepszej-konfiguracji"></a> 2. Wybór najlepszej konfiguracji

Po zakończeniu wszystkich eksperymentów get_best_hyperparameters.py przeszukuje zapisane wyniki i wybiera konfigurację z
najwyższym wynikiem F1.

```bash
    python get_best_hyperparameters.py
```

Tworzy on plik best_config.json, zawierający najlepsze parametry.

### <a id="3-trenowanie-finalnego-modelu"></a> 3. Trenowanie finalnego modelu

Na podstawie najlepszego zestawu hiperparametrów, uruchamiany jest skrypt train_best_model.py, który trenuje końcowy
model i zapisuje go w lokalnym katalogu (MODEL_SAVE_PATH).

```bash
    python train_best_model.py
```

Model wykorzystuje SentenceTransformer do wektoryzacji tekstu e-maila oraz prostą sieć neuronową jako klasyfikator.

## <a id="backend-api"></a> Backend (API)

Backend to aplikacja FastAPI, która udostępnia dwa endpointy:

### <a id="endpointy"></a> Endpointy

`GET /hello`

Testowy endpoint do sprawdzenia działania API.

Zwraca odpowiedź:

```json
{
    "message": "Api works"
}
```

`POST /predict`

Przyjmuje treść wiadomości e-mail i zwraca predykcję, czy jest to spam.

Request body:

```json
{
    "text": "Congratulations! You've won a free iPhone!"
}
```

Response:

```json
{
    "spam": true,
    "confidence": 0.9765
}
```

Predykcja opiera się na progu `0.5`. Wynik to wartość logiczna oraz "pewność" modelu (output sigmoid).

## <a id="frontend-angular"></a> Frontend (Angular)

Frontend to prosta aplikacja napisana w Angular. Jej zadania:

* Wyświetlenie pola tekstowego do wklejenia treści wiadomości.
* Przycisk `Sprawdź`, który wysyła `POST` do `/predict`.
* Wyświetlenie informacji o tym, czy wiadomość to spam, oraz poziomu pewności.

Funkcjonalność:

* Używa `HttpClient` do wysyłania żądań.
* Obsługuje proste komunikaty błędów i ładowania.
* Stylizacja minimalistyczna i responsywna (np. `Angular Material` lub własny `CSS`).