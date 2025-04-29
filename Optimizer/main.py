import numpy as np
from data_loader import DataLoader
from recipe_optimizer import RecipeOptimizer
from material_adjuster import MaterialAdjuster

def main():
    input_filepath = 'Dati.xlsx'
    
    # Carica i dati
    print("Caricamento dei dati...")
    data_loader = DataLoader(input_filepath)
    data = data_loader.load_data()

    produzioni_ricette = np.array([3000, 6300, 1200])
    consumi = np.array([1500, 5700, 3400, 300])
    perc_famiglie_per_ricette = np.array([
        [0.25, 0.20, 0.32],
        [0.43, 0.50, 0.33],
        [0.30, 0.27, 0.35],
        [0.02, 0.03, 0]
    ])
    famiglia_per_perc_materiale = np.array([
        [0.58, 0.42, 0],
        [1.00, 0, 0],
        [0, 1.00, 0],
        [0, 0, 1.00]
    ])
    range_ricette_per_materiali = np.array([
        [(0.56, 0.58, 0.59), (0.39, 0.396, 0.398), (0.022, 0.024, 0.025)],
        [(0.62, 0.625, 0.63), (None, None, None), (None, None, None)],
        [(0.61, 0.62, 0.63), (None, None, None), (None, None, None)]])
    
    # data = {
    #         'produzioni_ricette': produzioni_ricette,
    #         'consumi': consumi,
    #         'perc_famiglie_per_ricette': perc_famiglie_per_ricette,
    #         'famiglia_per_perc_materiale': famiglia_per_perc_materiale,
    #         'range_ricette_per_materiali': range_ricette_per_materiali
    #     }
        
    
    # Ottimizza le ricette
    print("\nOttimizzazione delle ricette...")
    optimizer = RecipeOptimizer(data)
    optimizer.optimize()
    
    # Aggiusta i materiali per rispettare i vincoli
    print("\nAggiustamento dei materiali per rispettare i vincoli...")
    adjuster = MaterialAdjuster(optimizer)
    adjuster.adjust_materials(iterations=1000)
    
    differenze = np.zeros((optimizer.N_MATERIALI, optimizer.N_RICETTE))
    for index_materiale in range(optimizer.N_MATERIALI):
        for index_ricetta in range(optimizer.N_RICETTE):
            differenze[index_materiale][index_ricetta] = adjuster.get_dist_from_range(index_materiale, index_ricetta)

    # Risultati finali
    with open('output.txt', 'w') as f:
        f.write("RISULTATI FINALI:\n")
        f.write("\nRange ricette per materiali:\n")
        f.write(str(optimizer.range_ricette_per_materiali))
        f.write("\nPercentuali famiglie per ricette:\n")
        f.write(str(optimizer.perc_famiglie_per_ricette))
        f.write("\nConsumi famiglie per ricette:\n")
        f.write(str(optimizer.consumi_famiglie_per_ricette))
        f.write("\nPercentuali materiali per ricette:\n")
        f.write(str(optimizer.perc_materiali_per_ricette))
        f.write("\nDifferenze:\n")
        f.write(str(differenze))



if __name__ == "__main__":
    main()
