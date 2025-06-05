## Dokumentacja przepływów CI/CD w projekcie Spam Detector

Poniżej znajduje się opis czterech głównych “pipeline’ów” (przepływów pracy) zdefiniowanych w plikach YAML. Dokumentacja
jest napisana w przystępnym, studenckim języku i wyjaśnia, co robi każdy z tych przepływów oraz w jaki sposób wspierają
one praktyki MLOps.

---

### 1. `train-and-evaluate.yml`

**Nazwa:** Train Spam Model  
**Kiedy się uruchamia:**

- Gdy zostanie otwarte lub zaktualizowane Pull Request (PR) na gałęzi `main` w katalogu `backend/` lub pliku
  `.github/workflows/deploy-backend.yml`.

**Co robi ten pipeline:**

1. **Checkout kodu**
    - Pobiera cały kod projektu (sekcja `backend/`).
2. **Instalacja środowiska Pythona**
    - Ustawia Python w wersji 3.9.
3. **Cache’owanie zależności `pip`**
    - Przyspiesza kolejne uruchomienia, cache’ując folder `~/.cache/pip`.
4. **Instalacja zależności**
    - Wczytuje `requirements.txt` z katalogu `backend/` i instaluje potrzebne biblioteki (np. PyTorch, scikit-learn
      itp.).
5. **Trening modelu**
    - Uruchamia skrypt `python -m backend.model_training`, który przeprowadza wstępne eksperymenty (np. przeszukiwanie
      przestrzeni hiperparametrów, walidację itp.).
6. **Wybór najlepszych hiperparametrów**
    - Na podstawie wyników eksperymentów zapisuje najlepszą konfigurację do pliku `backend/best_config.json`.
7. **Trenowanie finalnego modelu**
    - Używa wybranych hiperparametrów (`best_config.json`) i uruchamia `python -m backend.train_best_model`, co generuje
      plik wag modelu `backend/best_model.pth`.
8. **Upload artefaktów (model + konfiguracja)**
    - Wysyła do GitHub Actions artefakty:
        - `backend/best_config.json`
        - `backend/best_model.pth`

Po zakończeniu etapu „retrain” pojawia się drugi etap:

9. **Wywołanie pipeline’a `deploy-backend.yml`**

- Używa artefaktów wyprodukowanych przez trenowanie (ścieżka do folderu `backend/`) oraz podanego tagu obrazu (
  `image_tag: ${{ github.head_ref }}`) i przekazuje je dalej do workflow, który zbuduje kontener z backendem (wraz z
  wytrenowanym modelem).

---

### 2. `deploy-backend.yml`

**Nazwa:** Build Backend Image  
**Kiedy się uruchamia:**

- Zdarza się jako “reusable workflow” (może być wywołany z innych przepływów, np. z `train-and-evaluate.yml`).
- Przyjmuje w wejściu:
- `inputs.artifact_path` (ścieżka do folderu z modelowymi artefaktami, np. `backend/`)
- `inputs.image_tag` (dowolny identyfikator/tag, np. nazwa gałęzi lub SHA)
- Sekrety: `DOCKERHUB_USER`, `DOCKERHUB_TOKEN`.

**Co robi ten pipeline:**

1. **Checkout kodu**
    - Klonuje repozytorium z gałęzi, która wywołała ten workflow.
2. **Pobranie artefaktów modelu**
    - Korzysta z `actions/download-artifact@v4`, aby pobrać pliki:
    - `best_config.json`
    - `best_model.pth`
    - Artefakty te trafiają do katalogu przekazanego w `input.artifact_path`.
3. **Setup Docker Buildx**
    - Przygotowuje środowisko do budowy multi-architekturowego obrazu (opcjonalne, ale zalecane).
4. **Sanityzacja tagu**

- Zastępuje znaki “/” w nazwie tagu, aby utworzyć poprawny `SANITIZED_TAG` (np. `feature/x` → `feature-x`).

5. **Logowanie do Docker Hub**

- Używa sekretów `DOCKERHUB_USER` i `DOCKERHUB_TOKEN` do `docker/login-action@v3`.

6. **Budowa i wypchnięcie obrazu Docker**
    - Buduje obraz na podstawie pliku `backend/Dockerfile`.
    - Oznacza obraz dwoma tagami:
    - `docker.io/${DOCKERHUB_USER}/spam-api:latest`
    - `docker.io/${DOCKERHUB_USER}/spam-api:${SANITIZED_TAG}`
    - Wysyła (push) te obrazy do Docker Hub.
7. **Potwierdzenie**
    - Wypisuje w konsoli GitHub Actions: który tag został wypchnięty.

    
---

### 3. `create-frontend-image.yml`

**Nazwa:** Build Frontend Image  
**Kiedy się uruchamia:**

- To kolejny “reusable workflow” uruchamiany przez `deploy-frontend-image.yml`.
- Przyjmuje w wejściu:
    - `inputs.image_tag` (dowolny tag, np. nazwa gałęzi lub SHA)
    - Sekrety: `DOCKERHUB_USER`, `DOCKERHUB_TOKEN`.

**Co robi ten pipeline:**

1. **Checkout kodu**
    - Klonuje całe repozytorium (potrzebne, żeby mieć dostęp do folderu `frontend/no-spam-client`).
2. **Setup Docker Buildx**
    - Przygotowuje środowisko do budowy obrazu.
3. **Sanityzacja tagu**
    - Podobnie jak w backendzie: zastępuje znaki “/” w nazwie tagu (np. `feature/x` → `feature-x`).
4. **Logowanie do Docker Hub**
    - Korzysta z `docker/login-action@v2` i sekretów:
        - `DOCKERHUB_USER`
        - `DOCKERHUB_TOKEN`
5. **Budowa i wypchnięcie obrazu Docker**
    - Buduje obraz na podstawie katalogu frontend:
        - `context: ./frontend/no-spam-client`
        - `file: ./frontend/no-spam-client/Dockerfile`
    - Oznacza obraz nazwą:

- `docker.io/${DOCKERHUB_USER}/spam-client:latest`
- `docker.io/${DOCKERHUB_USER}/spam-client:${SANITIZED_TAG}`
- Wypycha (push) oba tagi do Docker Hub.

6. **Potwierdzenie**
    - Wyświetla komunikat: “Built frontend image tag: ${SANITIZED_TAG}”

 
---

### 4. `deploy-frontend-image.yml`

**Nazwa:** Build & Deploy Spam-Client  
**Kiedy się uruchamia:**

- Gdy zostanie otwarte lub zaktualizowane Pull Request (PR) na gałęzi `main` w katalogu `frontend/no-spam-client/` lub w
  pliku `.github/workflows/create-frontend-image.yml`.

**Co robi ten pipeline:**

1. **Wywołanie pipeline’u `create-frontend-image.yml`**
    - Przekazuje parametr:
        - `image_tag: ${{ github.head_ref }}` (czyli nazwa gałęzi PR-a)
    - Przekazuje też sekrety: `DOCKERHUB_USER`, `DOCKERHUB_TOKEN`.
2. **(Dalsze kroki wykonuje `create-frontend-image.yml`)**
    - Buduje i pushuje frontendowy kontener.

**Dlaczego to pasuje do MLOps/DevOps:**

- Umożliwia automatyczny build frontendu przy każdej zmianie w kodzie frontendu.
- Oddziela logikę “kiedy budować frontend” (czyli reguły wyzwalania) od właściwego procesu budowania (określonego w
  `create-frontend-image.yml`).
- Sprawia, że front-end „spam-client” jest zawsze aktualny w Docker Hub przy każdej aktualizacji kodu.

---

## Jak te pipeline’y współgrają w kontekście MLOps

1. **Centralizacja i powtarzalność**
    - Każdy etap (trenowanie, budowanie backendu, budowanie frontendu) jest jawnie zapisany w plikach YAML.
    - Dzięki temu każdy deweloper może łatwo sprawdzić, co odbywa się po każdej zmianie w kodzie.
    - Gwarantuje się, że dla każdej wersji kodu otrzymujemy te same (powtarzalne) wyniki: wytrenowany model, kontenery.

2. **Automatyzacja pełnego cyklu od kodu do wdrożenia**
    - **Krok 1:** Kiedy coś zmieni się w kodzie backendu (np. algorytm modelu), pipeline `train-and-evaluate.yml`
      automatycznie:
        - trenuje model
        - wybiera najlepsze hiperparametry
        - trenuje finalny model
        - wrzuca artefakty (plik `.pth` + konfiguracja)
        - wywołuje `deploy-backend.yml`, który “pakuje” model razem z aplikacją REST/API i pushuje nowy kontener.
    - **Krok 2:** Separatnie, kiedy zmienia się kod frontendu, pipeline `deploy-frontend-image.yml` wywołuje
      `create-frontend-image.yml`, który buduje i wypycha nowy obraz frontendu.

3. **Zarządzanie wersjami modelu i aplikacji**
    - W tagach obrazu (`image_tag`) umieszczona jest nazwa gałęzi lub SHA komitu.
    - “Sanityzacja” (`SANITIZED_TAG`) zapewnia, że tag nie zawiera niedozwolonych znaków w Dockerze.
    - Oznaczanie obrazów frontend i backend tym samym tagiem (gdy zmiany są powiązane) pozwala na łatwiejsze śledzenie
      kompatybilnych wersji.

4. **Modularność i wielokrotne użycie (reusable workflows)**
    - Pliki `deploy-backend.yml` i `create-frontend-image.yml` można wywołać z dowolnego innego pipeline’a, co pozwala
      na:
        - łatwe utrzymanie (gdy trzeba zmienić sposób budowania obrazu, wystarczy zaktualizować tylko jeden plik)
        - spójność (wszystkie obrazy backendu są budowane według tej samej procedury)
    - Uproszczona organizacja: osobne pliki dla treningu modelu, dla budowania backendu, dla budowania frontendu.

5. **Zastosowanie dobrych praktyk MLOps/DevOps**
    - CI (Continuous Integration): automatyczny trening i testy modelu przy każdym PR-ie.
    - CD (Continuous Deployment): automatyczne budowanie i wypychanie kontenerów do Docker Hub.
    - Trwałe artefakty: model jest zawsze zapisany w GitHub Actions, a potem w obrazie kontenera.
    - Oddzielenie logiki biznesowej (kod backendu + model) od logiki infrastruktury (Docker + CI/CD).

---

## Podsumowanie

- **`train-and-evaluate.yml`** – od kodu do wytrenowanego modelu. Po zakończeniu treningu wywołuje budowę obrazu
  backendu.
- **`deploy-backend.yml`** – pobiera wytrenowany model, buduje kontener z API backendu i wypycha go do Docker Hub.
- **`create-frontend-image.yml`** – buduje i wypycha kontener z aplikacją frontendu (Spam Client).
- **`deploy-frontend-image.yml`** – uruchamia `create-frontend-image.yml` po zmianach w kodzie frontendu.

Cały przepływ gwarantuje, że:

1. Kod modelu i jego konfiguracja są zawsze świeże i zoptymalizowane (pipeline trenowania).
2. Model jest “opakowany” razem z API w kontenerze (pipeline backendu).
3. Frontend aplikacji jest osobno budowany i łatwo wdrażany (pipeline frontendu).

Dzięki temu rozwiązaniu MLOps mamy kompletny, w pełni zautomatyzowany cykl: od zmiany w kodzie aż po gotowy do
postawienia (lub wdrożenia w chmurze) kontener Docker.
