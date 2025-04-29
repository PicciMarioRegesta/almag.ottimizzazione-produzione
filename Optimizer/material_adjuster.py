import numpy as np

class MaterialAdjuster:
    def __init__(self, optimizer):
        self.optimizer = optimizer
        
    def get_dist_from_range(self, index_materiale, index_ricetta):
        perc_materiale = self.optimizer.perc_materiali_per_ricette[index_materiale][index_ricetta]
        range_materiale = self.optimizer.range_ricette_per_materiali[index_ricetta][index_materiale]
        if range_materiale[0] is None:
            return 0
        if perc_materiale < range_materiale[0]:
            return range_materiale[0] - perc_materiale
        if perc_materiale > range_materiale[2]:
            return perc_materiale - range_materiale[2]
        return 0
    
    def get_index_max_dist(self):
        max_dist, index_materiale, index_ricetta = 0, 0, 0
        for m in range(self.optimizer.N_MATERIALI):
            for r in range(self.optimizer.N_RICETTE):
                dist = self.get_dist_from_range(m, r)
                if dist > max_dist:
                    max_dist = dist
                    index_materiale = m
                    index_ricetta = r
        return (index_materiale, index_ricetta) if max_dist > 0 else (None, None)
    
    def get_index_max_dist_without_visited(self, visited_values):
        max_dist, index_materiale, index_ricetta = 0, 0, 0
        for m in range(self.optimizer.N_MATERIALI):
            for r in range(self.optimizer.N_RICETTE):
                if (m, r) not in visited_values:
                    dist = self.get_dist_from_range(m, r)
                    if dist > max_dist:
                        max_dist = dist
                        index_materiale = m
                        index_ricetta = r
        return (index_materiale, index_ricetta) if max_dist > 0 else (None, None)
    
    def get_q_materiale(self, perc_attesa_materiale, index_ricetta, index_materiale):
        consumi_minori, consumi_neutrali, consumi_maggiori = 0, 0, 0
        q_materiale_minori, q_materiale_maggiori = 0, 0
        for index_famiglia in range(self.optimizer.N_FAMIGLIE):
            perc_materiale = self.optimizer.famiglia_per_perc_materiale[index_famiglia][index_materiale]
            q_materiale = self.optimizer.consumi_famiglie_per_ricette[index_famiglia][index_ricetta]
            if perc_materiale == 0:
                consumi_neutrali += q_materiale
            elif perc_materiale < perc_attesa_materiale:
                consumi_minori += q_materiale
                q_materiale_minori += perc_materiale * q_materiale
            elif perc_materiale >= perc_attesa_materiale:
                consumi_maggiori += q_materiale
                q_materiale_maggiori += perc_materiale * q_materiale
        return (consumi_minori, consumi_neutrali, consumi_maggiori, q_materiale_minori, q_materiale_maggiori)
    
    def get_coefficiente_maggiori(self, consumi_maggiori, consumi_neutrali, consumi_minori, q_materiale_minori, q_materiale_maggiori, q_materiale_obiettivo, tot_consumo_ricetta):
        if consumi_minori + consumi_neutrali == 0:
            return -1
        numeratore = q_materiale_obiettivo - q_materiale_minori * tot_consumo_ricetta / (consumi_minori + consumi_neutrali)
        denominatore = q_materiale_maggiori - consumi_maggiori * q_materiale_minori / (consumi_minori + consumi_neutrali)
        return numeratore / denominatore if denominatore != 0 else -1
    
    def get_coefficiente_minori(self, consumi_minori, consumi_neutrali, consumi_maggiori, coefficiente_maggiori, tot_consumo_ricetta):
        if consumi_minori + consumi_neutrali == 0:
            return -1
        coefficiente_minori = (tot_consumo_ricetta - consumi_maggiori * coefficiente_maggiori) / (consumi_minori + consumi_neutrali)
        return coefficiente_minori
    
    def adjust_materials(self, iterations=3):
        visited_values = set()
        for i in range(iterations):
            # index_materiale, index_ricetta = self.get_index_max_dist_without_visited(visited_values)
            index_materiale, index_ricetta = self.get_index_max_dist()
            if index_materiale is None:
                print(f"Tutte le ricette sono entro i range dopo {i} iterazioni")
                break
            else:
                visited_values.add((index_materiale, index_ricetta))               
                
            perc_materiale = self.optimizer.perc_materiali_per_ricette[index_materiale][index_ricetta]
            range_materiale = self.optimizer.range_ricette_per_materiali[index_ricetta][index_materiale]
            perc_attesa_materiale = range_materiale[1]

            print(f'Iterazione {i+1}')
            print(f'Indice materiale: {index_materiale}')
            print(f'Indice ricetta: {index_ricetta}')
            print(f'Range materiale: {range_materiale}')
            # print(f'Percentuale attesa materiale: {perc_attesa_materiale}')
            print(f'Percentuale materiale: {perc_materiale}')

            tot_consumo_ricetta = np.sum(self.optimizer.consumi_famiglie_per_ricette[:, index_ricetta])
            q_materiale_obiettivo = perc_attesa_materiale * tot_consumo_ricetta
            consumi_minori, consumi_neutrali, consumi_maggiori, q_materiali_minori, q_materiali_maggiori = \
                self.get_q_materiale(perc_attesa_materiale, index_ricetta, index_materiale)
            coefficiente_maggiori = self.get_coefficiente_maggiori(
                consumi_maggiori, consumi_neutrali, consumi_minori, 
                q_materiali_minori, q_materiali_maggiori, 
                q_materiale_obiettivo, tot_consumo_ricetta
            )
            coefficiente_minori = self.get_coefficiente_minori(
                consumi_minori, consumi_neutrali, consumi_maggiori, 
                coefficiente_maggiori, tot_consumo_ricetta
            )
            for index_famiglia in range(self.optimizer.N_FAMIGLIE):
                perc_materiale = self.optimizer.famiglia_per_perc_materiale[index_famiglia][index_materiale]
                consumo_precedente = self.optimizer.consumi_famiglie_per_ricette[index_famiglia][index_ricetta]
                if perc_materiale < perc_attesa_materiale:
                    self.optimizer.consumi_famiglie_per_ricette[index_famiglia][index_ricetta] = consumo_precedente * coefficiente_minori
                elif perc_materiale >= perc_attesa_materiale:
                    self.optimizer.consumi_famiglie_per_ricette[index_famiglia][index_ricetta] = consumo_precedente * coefficiente_maggiori
            
            self.optimizer.refresh_perc_famiglie_per_ricette()
            # print(f'Perc famiglie per ricette: {self.optimizer.perc_famiglie_per_ricette}')
            # print(f'Consumi famiglie per ricette: {self.optimizer.consumi_famiglie_per_ricette}')
            self.optimizer.perc_materiali_per_ricette = self.optimizer.get_perc_materiali_per_ricette()
            # print(f'Totale consumi ricetta: {tot_consumo_ricetta}')
            # print(f'Q materiale obiettivo: {q_materiale_obiettivo}')
            # print(f'Q consumi minori: {consumi_minori}')
            # print(f'Q consumi neutrali: {consumi_neutrali}')
            # print(f'Q consumi maggiori: {consumi_maggiori}')
            # print(f'Q materiale minori: {q_materiali_minori}')
            # print(f'Q materiale maggiori: {q_materiali_maggiori}')
            # print(f'K maggiori: {coefficiente_maggiori}')
            # print(f'K minori: {coefficiente_minori}')
            # print(f'Resa attuale: {self.optimizer.calc_tot_resa(self.optimizer.consumi_famiglie_per_ricette)}')
            # print('-' * 50)
