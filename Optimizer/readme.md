# Ottimizzatore di Ricette

Questo programma ottimizza la composizione di ricette in base alla distribuzione di elementi, rispettando vincoli specifici.

## Struttura del Progetto

Il progetto è organizzato nei seguenti file:

- `main.py`: File principale che coordina l'esecuzione del programma
- `data_loader.py`: Classe per il caricamento e la preparazione dei dati
- `recipe_optimizer.py`: Classe per l'ottimizzazione delle ricette
- `element_adjuster.py`: Classe per l'aggiustamento dei elementi per rispettare i vincoli
- `requirements.txt`: Elenco delle dipendenze richieste

## Installazione

Per installare le dipendenze necessarie, esegui:

```bash
pip install -r requirements.txt
```

## Utilizzo

1. Assicurati che il file `Dati.xlsx` sia nella stessa directory del programma
2. Esegui il programma con:

```bash
python main.py
```

## Descrizione del Processo

Il programma segue i seguenti passaggi:

1. **Caricamento Dati**: Legge i dati dal file Excel, includendo produzioni, consumi, percentuali delle famiglie nelle ricette, e composizione dei elementi.

2. **Ottimizzazione**: Utilizza l'algoritmo SLSQP per minimizzare gli errori nella resa globale, rispettando i vincoli sui consumi totali.

3. **Aggiustamento elementi**: Modifica iterativamente le ricette per portare le percentuali dei elementi all'interno dei range accettabili.
