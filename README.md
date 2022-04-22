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
