import numpy as np
import pandas as pd

class DataLoader:
    def __init__(self, filepath):
        self.filepath = filepath
        
    def load_data(self):
        prod_df_raw = pd.read_excel(self.filepath, sheet_name="Produzioni")
        prod_df = prod_df_raw[['Cartellino', 'Quantita']].groupby('Cartellino').sum().sort_values(['Cartellino'])
        nomi_ricette = [ int(ricetta) for ricetta in prod_df.index ]
        produzioni_ricette = np.array(prod_df['Quantita'])
        
        cons_df_raw = pd.read_excel(self.filepath, sheet_name="Consumi")
        cons_df = cons_df_raw[['Famiglia', 'Quantità']].groupby('Famiglia').sum().sort_values(['Quantità']).sort_values(['Famiglia'])
        cons_df['Quantità'] = cons_df['Quantità'] * -1
        nomi_famiglie = [ int(famiglia) for famiglia in cons_df.index ]
        consumi = np.array(cons_df['Quantità'])
        
        cart_df_raw = pd.read_excel(self.filepath, sheet_name="Cartellino STANDARD Partenza")
        cart_df_raw = cart_df_raw[cart_df_raw['Cartellino'].isin(prod_df.index)]
        cart_df_raw = cart_df_raw[cart_df_raw['Famiglia'].isin(cons_df.index)]
        cart_df = cart_df_raw[['Cartellino', 'Famiglia', 'Percentuale']].reset_index().pivot_table(
            index=['Famiglia'],
            columns=['Cartellino'],
            values='Percentuale'
        ).fillna(0)
        perc_famiglie_per_ricette = np.array(cart_df) / 100
        
        comp_raw = pd.read_excel(self.filepath, sheet_name="Analisi IN FAM", header=2)
        comp_raw = comp_raw.drop(columns=["Media di Totale"])
        comp_raw = comp_raw[comp_raw['Etichette di riga'].isin(cons_df.index)]
        comp_raw = comp_raw.set_index('Etichette di riga')
        composizioni_famiglia = np.array(comp_raw)
        famiglia_per_perc_elemento = composizioni_famiglia / 100
        
        min_raw = pd.read_excel(self.filepath, sheet_name="Toll Fonderia Medio", header=1, usecols='A,C:O')
        min_raw = min_raw.loc[min_raw['lega'].isin(prod_df.index)]
        min_raw = min_raw.set_index('lega')
        
        max_raw = pd.read_excel(self.filepath, sheet_name="Toll Fonderia Medio", header=1, usecols='A,P:AB')
        max_raw = max_raw.loc[max_raw['lega'].isin(prod_df.index)]
        max_raw = max_raw.set_index('lega')

        att_raw = pd.read_excel(self.filepath, sheet_name="Toll Fonderia Medio", header=1, usecols='A,AC:AO')
        att_raw = att_raw.loc[att_raw['lega'].isin(prod_df.index)]
        att_raw = att_raw.set_index('lega')

        all_indices = pd.Index(sorted(set(prod_df.index)))
        min_raw = min_raw.reindex(all_indices).fillna(0)
        max_raw = max_raw.reindex(all_indices).fillna(0)
        att_raw = att_raw.reindex(all_indices).fillna(0)
        val_min = np.array(min_raw)
        val_max = np.array(max_raw)
        val_att = np.array(att_raw)
        range_ricette_per_elementi = np.full((val_att.shape[0], val_att.shape[1]), None)
        for iy, ix in np.ndindex(val_att.shape):
            if val_att[iy, ix] == 0:
                range_ricette_per_elementi[iy, ix] = (None, None, None)
            else:
                min_val = val_min[iy, ix]/100
                att_val = val_att[iy, ix]/100
                max_val = val_max[iy, ix]/100
                range_ricette_per_elementi[iy, ix] = (min(min_val, max_val), att_val, max(min_val, max_val))
        nomi_elementi = [ elemento for elemento in min_raw.columns ]

        return {
            'produzioni_ricette': produzioni_ricette,
            'consumi': consumi,
            'perc_famiglie_per_ricette': perc_famiglie_per_ricette,
            'famiglia_per_perc_elemento': famiglia_per_perc_elemento,
            'range_ricette_per_elementi': range_ricette_per_elementi,
            'nomi_ricette': nomi_ricette,
            'nomi_famiglie': nomi_famiglie,
            'nomi_elementi': nomi_elementi
        }