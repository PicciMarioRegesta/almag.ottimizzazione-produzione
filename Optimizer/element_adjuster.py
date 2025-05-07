import numpy as np

class ElementAdjuster:
    def __init__(self, optimizer):
        self.optimizer = optimizer
    
    def get_index_max_dist(self):
        max_dist, index_elemento, index_ricetta = 0, 0, 0
        for m in range(self.optimizer.N_elementi):
            for r in range(self.optimizer.N_RICETTE):
                dist = self.optimizer.get_dist_from_range(m, r)
                if dist > max_dist:
                    max_dist = dist
                    index_elemento = m
                    index_ricetta = r
        return (index_elemento, index_ricetta) if max_dist > 0 else (None, None)
    
    def get_index_max_dist_without_visited(self, visited_values):
        max_dist, index_elemento, index_ricetta = 0, 0, 0
        for m in range(self.optimizer.N_elementi):
            for r in range(self.optimizer.N_RICETTE):
                if (m, r) not in visited_values:
                    dist = self.optimizer.get_dist_from_range(m, r)
                    if dist > max_dist:
                        max_dist = dist
                        index_elemento = m
                        index_ricetta = r
        return (index_elemento, index_ricetta) if max_dist > 0 else (None, None)
    
    def get_q_elemento(self, perc_attesa_elemento, index_ricetta, index_elemento):
        consumi_minori, consumi_neutrali, consumi_maggiori = 0, 0, 0
        q_elemento_minori, q_elemento_maggiori = 0, 0
        for index_famiglia in range(self.optimizer.N_FAMIGLIE):
            perc_elemento = self.optimizer.famiglia_per_perc_elemento[index_famiglia][index_elemento]
            q_elemento = self.optimizer.consumi_famiglie_per_ricette[index_famiglia][index_ricetta]
            if perc_elemento == 0:
                consumi_neutrali += q_elemento
            elif perc_elemento < perc_attesa_elemento:
                consumi_minori += q_elemento
                q_elemento_minori += perc_elemento * q_elemento
            elif perc_elemento >= perc_attesa_elemento:
                consumi_maggiori += q_elemento
                q_elemento_maggiori += perc_elemento * q_elemento
        return (consumi_minori, consumi_neutrali, consumi_maggiori, q_elemento_minori, q_elemento_maggiori)
    
    def get_coefficiente_maggiori(self, consumi_maggiori, consumi_neutrali, consumi_minori, q_elemento_minori, q_elemento_maggiori, q_elemento_obiettivo, tot_consumo_ricetta):
        if consumi_minori + consumi_neutrali == 0:
            return -1
        numeratore = q_elemento_obiettivo - q_elemento_minori * tot_consumo_ricetta / (consumi_minori + consumi_neutrali)
        denominatore = q_elemento_maggiori - consumi_maggiori * q_elemento_minori / (consumi_minori + consumi_neutrali)
        return numeratore / denominatore if denominatore != 0 else -1
    
    def get_coefficiente_minori(self, consumi_minori, consumi_neutrali, consumi_maggiori, coefficiente_maggiori, tot_consumo_ricetta):
        if consumi_minori + consumi_neutrali == 0:
            return -1
        coefficiente_minori = (tot_consumo_ricetta - consumi_maggiori * coefficiente_maggiori) / (consumi_minori + consumi_neutrali)
        return coefficiente_minori
    
    def adjust_elements(self, iterations=3):
        visited_values = set()
        for i in range(iterations):
            # index_elemento, index_ricetta = self.get_index_max_dist_without_visited(visited_values)
            index_elemento, index_ricetta = self.get_index_max_dist()
            if index_elemento is None:
                print(f"Tutte le ricette sono entro i range dopo {i} iterazioni")
                break
            else:
                visited_values.add((index_elemento, index_ricetta))               
                
            perc_elemento = self.optimizer.perc_elementi_per_ricette[index_elemento][index_ricetta]
            range_elemento = self.optimizer.range_ricette_per_elementi[index_ricetta][index_elemento]
            perc_attesa_elemento = range_elemento[1]

            print(f'Iterazione {i+1}')
            print(f'Indice elemento: {index_elemento}')
            print(f'Indice ricetta: {index_ricetta}')
            print(f'Range elemento: {range_elemento}')
            # print(f'Percentuale attesa elemento: {perc_attesa_elemento}')
            print(f'Percentuale elemento: {perc_elemento}')

            tot_consumo_ricetta = np.sum(self.optimizer.consumi_famiglie_per_ricette[:, index_ricetta])
            q_elemento_obiettivo = perc_attesa_elemento * tot_consumo_ricetta
            consumi_minori, consumi_neutrali, consumi_maggiori, q_elementi_minori, q_elementi_maggiori = \
                self.get_q_elemento(perc_attesa_elemento, index_ricetta, index_elemento)
            coefficiente_maggiori = self.get_coefficiente_maggiori(
                consumi_maggiori, consumi_neutrali, consumi_minori, 
                q_elementi_minori, q_elementi_maggiori, 
                q_elemento_obiettivo, tot_consumo_ricetta
            )
            coefficiente_minori = self.get_coefficiente_minori(
                consumi_minori, consumi_neutrali, consumi_maggiori, 
                coefficiente_maggiori, tot_consumo_ricetta
            )
            for index_famiglia in range(self.optimizer.N_FAMIGLIE):
                perc_elemento = self.optimizer.famiglia_per_perc_elemento[index_famiglia][index_elemento]
                consumo_precedente = self.optimizer.consumi_famiglie_per_ricette[index_famiglia][index_ricetta]
                if perc_elemento < perc_attesa_elemento:
                    self.optimizer.consumi_famiglie_per_ricette[index_famiglia][index_ricetta] = consumo_precedente * coefficiente_minori
                elif perc_elemento >= perc_attesa_elemento:
                    self.optimizer.consumi_famiglie_per_ricette[index_famiglia][index_ricetta] = consumo_precedente * coefficiente_maggiori
            
            self.optimizer.refresh_perc_famiglie_per_ricette()
            # print(f'Perc famiglie per ricette: {self.optimizer.perc_famiglie_per_ricette}')
            # print(f'Consumi famiglie per ricette: {self.optimizer.consumi_famiglie_per_ricette}')
            self.optimizer.perc_elementi_per_ricette = self.optimizer.get_perc_elementi_per_ricette()
            # print(f'Totale consumi ricetta: {tot_consumo_ricetta}')
            # print(f'Q elemento obiettivo: {q_elemento_obiettivo}')
            # print(f'Q consumi minori: {consumi_minori}')
            # print(f'Q consumi neutrali: {consumi_neutrali}')
            # print(f'Q consumi maggiori: {consumi_maggiori}')
            # print(f'Q elemento minori: {q_elementi_minori}')
            # print(f'Q elemento maggiori: {q_elementi_maggiori}')
            # print(f'K maggiori: {coefficiente_maggiori}')
            # print(f'K minori: {coefficiente_minori}')
            # print(f'Resa attuale: {self.optimizer.calc_tot_resa(self.optimizer.consumi_famiglie_per_ricette)}')
            # print('-' * 50)
