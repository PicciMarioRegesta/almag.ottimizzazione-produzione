from scipy.optimize import minimize
import numpy as np

class RecipeOptimizer:
    def __init__(self, produzioni_ricette, consumi, perc_famiglie_per_ricette, famiglia_per_perc_elemento, range_ricette_per_elementi):
        self.produzioni_ricette = produzioni_ricette
        self.consumi = consumi
        self.perc_famiglie_per_ricette = perc_famiglie_per_ricette
        self.famiglia_per_perc_elemento = famiglia_per_perc_elemento
        self.range_ricette_per_elementi = range_ricette_per_elementi
        
        self.N_FAMIGLIE, self.N_RICETTE = self.perc_famiglie_per_ricette.shape
        self.N_elementi = self.famiglia_per_perc_elemento.shape[1]
        
        self.tot_consumi = np.sum(self.consumi)
        self.tot_produzioni = np.sum(self.produzioni_ricette)
        self.resa_globale = self.tot_consumi / self.tot_produzioni
        
        self.count_iterations = 0
        self.consumi_famiglie_per_ricette = self.get_consumi_famiglie_per_ricette()
        self.perc_elementi_per_ricette = self.get_perc_elementi_per_ricette()
    
    def refresh_perc_famiglie_per_ricette(self):
        self.perc_famiglie_per_ricette = self.consumi_famiglie_per_ricette / np.sum(self.consumi_famiglie_per_ricette, axis=0)

    def get_consumi_famiglie_per_ricette(self):
        return self.perc_famiglie_per_ricette * self.produzioni_ricette
    
    def get_perc_elementi_per_ricette(self):
        perc_elementi_per_ricette = np.zeros((self.N_elementi, self.N_RICETTE))
        for index_elemento in range(self.N_elementi):
            perc_elemento = self.famiglia_per_perc_elemento[:, index_elemento]
            for index_ricetta in range(self.N_RICETTE):
                perc_ricetta = self.perc_famiglie_per_ricette[:, index_ricetta]
                perc_elemento_ricetta = np.sum(perc_ricetta * perc_elemento)
                perc_elementi_per_ricette[index_elemento][index_ricetta] = perc_elemento_ricetta
        return perc_elementi_per_ricette
    
    def calc_mat_consumi(self, ricetta):
        return ricetta.reshape(-1, len(self.produzioni_ricette)) * self.produzioni_ricette
    
    def calc_tot_consumi(self, matrice_consumi):
        return np.sum(matrice_consumi, axis=1)
    
    def calc_err_totali(self, ricetta):
        matrice_consumi = self.calc_mat_consumi(ricetta)
        tot_consumi = self.calc_tot_consumi(matrice_consumi)
        tot_err = np.sqrt(np.sum(np.square(tot_consumi - self.consumi))) / 1000
        return tot_err
    
    def calc_tot_resa(self, matrice_consumi):
        return np.sum(matrice_consumi, axis=0) / self.produzioni_ricette
    
    def calc_error_resa(self, ricetta):
        matrice_consumi = self.calc_mat_consumi(ricetta)
        tot_resa = self.calc_tot_resa(matrice_consumi)
        return np.sum(np.square(tot_resa - self.resa_globale))
    
    def perc_mat(self, ricetta, id_ric):
        cons_fam = self.calc_mat_consumi(ricetta)
        compos = self.famiglia_per_perc_elemento.reshape(len(self.consumi), -1)
        cons_ricetta0 = np.vstack(cons_fam[:, id_ric])
        cons_elementi_ricetta0 = cons_ricetta0 * compos
        tot_cons_ricetta0 = np.sum(cons_elementi_ricetta0, axis=0)
        tot_perc_ricetta0 = tot_cons_ricetta0 / np.sum(tot_cons_ricetta0) if np.sum(tot_cons_ricetta0) != 0 else np.zeros((len(tot_cons_ricetta0), 1))
        return tot_perc_ricetta0
    
    def err_perc_mat(self, ricetta, id_ric, id_mat, expected_val, expected_error):
        return expected_error - np.abs(self.perc_mat(ricetta, id_ric=id_ric)[id_mat] - expected_val)
    
    def callback(self, x, y=None):
        print(f'{self.count_iterations} - {self.calc_err_totali(x)}')
        self.count_iterations += 1
    
    def optimize(self, max_iter=100):
        ricette = self.perc_famiglie_per_ricette.flatten()
        constraints = [
            {'type': 'eq', 'fun': self.calc_err_totali},
        ]
        bounds = list(((0, 1) for _ in range(len(ricette))))
        
        res = minimize(
            self.calc_error_resa,
            ricette,
            method='SLSQP',
            constraints=constraints,
            bounds=bounds,
            callback=self.callback,
            options={'disp': True, 'maxiter': max_iter}
        )
        
        for i in range(len(res.x)):
            self.perc_famiglie_per_ricette[i // self.N_RICETTE][i % self.N_RICETTE] = res.x[i]
        
        self.consumi_famiglie_per_ricette = self.get_consumi_famiglie_per_ricette()
        self.perc_elementi_per_ricette = self.get_perc_elementi_per_ricette()
        return res
    
    def get_dist_from_range(self, index_elemento, index_ricetta):
        perc_elemento = self.perc_elementi_per_ricette[index_elemento][index_ricetta]
        range_elemento = self.range_ricette_per_elementi[index_ricetta][index_elemento]
        if range_elemento[0] is None:
            return 0
        if perc_elemento < range_elemento[0]:
            return range_elemento[0] - perc_elemento
        if perc_elemento > range_elemento[2]:
            return perc_elemento - range_elemento[2]
        return 0

    def get_all_dist_from_range(self):
        differenze = np.zeros((self.N_elementi, self.N_RICETTE))
        for index_elemento in range(self.N_elementi):
            for index_ricetta in range(self.N_RICETTE):
                differenze[index_elemento][index_ricetta] = self.get_dist_from_range(index_elemento, index_ricetta)
        return differenze