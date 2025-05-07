import numpy as np
from data_loader import DataLoader
from recipe_optimizer import RecipeOptimizer
from element_adjuster import ElementAdjuster
from excel_report_generator import ExcelReportGenerator

import pandas as pd
import os


def main():
    input_filepath = 'Dati.xlsx'
    data_loader = DataLoader(input_filepath)
    data = data_loader.load_data()
    optimizer = RecipeOptimizer(
        data['produzioni_ricette'],
        data['consumi'],
        data['perc_famiglie_per_ricette'],
        data['famiglia_per_perc_elemento'],
        data['range_ricette_per_elementi']
    )
    adjuster = ElementAdjuster(optimizer)


    # OTTIMIZZAZIONE
    for num in range(30):
        optimizer.optimize(max_iter=100)
        adjuster.adjust_elements(iterations=1000)
    optimizer.optimize(max_iter=100)

    nomi_ricette = data['nomi_ricette']
    nomi_famiglie = data['nomi_famiglie']
    nomi_elementi = data['nomi_elementi']

    excel_report_generator = ExcelReportGenerator(optimizer, nomi_ricette, nomi_famiglie, nomi_elementi)
    excel_report_generator.generate_report('out/risultati_ottimizzazione.xlsx')
    print("Report generated successfully at 'out/risultati_ottimizzazione.xlsx'.")

if __name__ == "__main__":
    main()


    # Mock data
    # produzioni_ricette = np.array([3000, 6300, 1200])
    # consumi = np.array([1500, 5700, 3400, 300])
    # perc_famiglie_per_ricette = np.array([
    #     [0.25, 0.20, 0.32],
    #     [0.43, 0.50, 0.33],
    #     [0.30, 0.27, 0.35],
    #     [0.02, 0.03, 0]
    # ])
    # famiglia_per_perc_elemento = np.array([
    #     [0.58, 0.42, 0],
    #     [1.00, 0, 0],
    #     [0, 1.00, 0],
    #     [0, 0, 1.00]
    # ])
    # range_ricette_per_elementi = np.array([
    #     [(0.56, 0.58, 0.59), (0.39, 0.396, 0.398), (0.022, 0.024, 0.025)],
    #     [(0.62, 0.625, 0.63), (None, None, None), (None, None, None)],
    #     [(0.61, 0.62, 0.63), (None, None, None), (None, None, None)]])
    # data = {
    #         'produzioni_ricette': produzioni_ricette,
    #         'consumi': consumi,
    #         'perc_famiglie_per_ricette': perc_famiglie_per_ricette,
    #         'famiglia_per_perc_elemento': famiglia_per_perc_elemento,
    #         'range_ricette_per_elementi': range_ricette_per_elementi
    #     }
    