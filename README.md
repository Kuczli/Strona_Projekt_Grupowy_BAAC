# Kasix-Photography
projekt stworzony na zaliczenie przedmiotu "Budowa i Administracja Aplikacji w Chmurze"
podgląd > https://kasix-photography.herokuapp.com/ 
Jest to wizytówka Pani Kasi, która jest fotografem.
Użytkownik ma możliwość wysłania przez formularz chęci zakupu szkolenia z fotografii. 
Automatyczny email zwrotny do klienta


## Tech/Framework/Apps

### Frontend
- [HTML] [CSS] [BOOTSTRAP]
### Backend
- [PYTHON] [FLASK] 

## Python && Monitoring && Tracing 

### Monitoring 
Monitoring z wykorzystaniem prometheus

Dostępne serwisy:
 - 8080 - aplikacja
 - 9090 - prometheus webgui
 - 9093 - alertmanager
 - 3000 - grafana

### Tracing z wykorzystaniem OpenTelemetry

Dostepne serwisy:
 - 166686 -Jaeger UI

## Uruchomienie
    
      sudo make
      sudo make start 


## Deployment na Heroku (najważniejsze pliki/komendy)

#podpięcie konta github z heroku
#zmiana pliku z app.py na main.py
main.py
pip install gunicorn
#tworzenie pliku w projekcie Procfile
Procfile
#w pliku:
web: gunicorn main:app

## Deployment na Azure (najważniejsze komendy)

#logowanie
az login

#tworzenie grupy zasobów
az group create -n Kasixphotography -l westeurope

#tworzenie plan App Service
az appservice plan create --name Kasixphotography --resource-group Kasixphotography --sku B1 --is-linux

#tworzenie nową App Service internetową
az webapp create --name Kasixphotography --runtime 'PYTHON|3.9' --plan Kasixphotography --resource-group Kasixphotography --query 'defaultHostName' --output table
```


