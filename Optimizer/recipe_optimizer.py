from scipy.optimize import minimize
import numpy as np

class RecipeOptimizer:
    def __init__(self, data):
        self.produzioni_ricette = data['produzioni_ricette']
        self.consumi = data['consumi']
        self.perc_famiglie_per_ricette = data['perc_famiglie_per_ricette']
        self.famiglia_per_perc_materiale = data['famiglia_per_perc_materiale']
        self.range_ricette_per_materiali = data['range_ricette_per_materiali']
        
        self.N_FAMIGLIE, self.N_RICETTE = self.perc_famiglie_per_ricette.shape
        self.N_MATERIALI = self.famiglia_per_perc_materiale.shape[1]
        
        self.tot_consumi = np.sum(self.consumi)
        self.tot_produzioni = np.sum(self.produzioni_ricette)
        self.resa_globale = self.tot_consumi / self.tot_produzioni
        
        self.count_iterations = 0
        self.consumi_famiglie_per_ricette = self.get_consumi_famiglie_per_ricette()
        self.perc_materiali_per_ricette = self.get_perc_materiali_per_ricette()
    
    def refresh_perc_famiglie_per_ricette(self):
        self.perc_famiglie_per_ricette = self.consumi_famiglie_per_ricette / np.sum(self.consumi_famiglie_per_ricette, axis=0)

    def get_consumi_famiglie_per_ricette(self):
        return self.perc_famiglie_per_ricette * self.produzioni_ricette
    
    def get_perc_materiali_per_ricette(self):
        perc_materiali_per_ricette = np.zeros((self.N_MATERIALI, self.N_RICETTE))
        for index_materiale in range(self.N_MATERIALI):
            perc_materiale = self.famiglia_per_perc_materiale[:, index_materiale]
            for index_ricetta in range(self.N_RICETTE):
                perc_ricetta = self.perc_famiglie_per_ricette[:, index_ricetta]
                perc_materiale_ricetta = np.sum(perc_ricetta * perc_materiale)
                perc_materiali_per_ricette[index_materiale][index_ricetta] = perc_materiale_ricetta
        return perc_materiali_per_ricette
    
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
        compos = self.famiglia_per_perc_materiale.reshape(len(self.consumi), -1)
        cons_ricetta0 = np.vstack(cons_fam[:, id_ric])
        cons_materiali_ricetta0 = cons_ricetta0 * compos
        tot_cons_ricetta0 = np.sum(cons_materiali_ricetta0, axis=0)
        tot_perc_ricetta0 = tot_cons_ricetta0 / np.sum(tot_cons_ricetta0) if np.sum(tot_cons_ricetta0) != 0 else np.zeros((len(tot_cons_ricetta0), 1))
        return tot_perc_ricetta0
    
    def err_perc_mat(self, ricetta, id_ric, id_mat, expected_val, expected_error):
        return expected_error - np.abs(self.perc_mat(ricetta, id_ric=id_ric)[id_mat] - expected_val)
    
    def callback(self, x, y=None):
        print(f'{self.count_iterations} - {self.calc_err_totali(x)}')
        self.count_iterations += 1
    
    def optimize(self):
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
            options={'disp': True, 'maxiter': 100}
        )
        
        for i in range(len(res.x)):
            self.perc_famiglie_per_ricette[i // self.N_RICETTE][i % self.N_RICETTE] = res.x[i]
        
        self.consumi_famiglie_per_ricette = self.get_consumi_famiglie_per_ricette()
        self.perc_materiali_per_ricette = self.get_perc_materiali_per_ricette()
        return res
