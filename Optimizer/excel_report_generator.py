import pandas as pd

class ExcelReportGenerator:
    
    def __init__(self, optimizer, nomi_ricette, nomi_famiglie, nomi_elementi):
        self.optimizer = optimizer
        self.nomi_ricette = nomi_ricette
        self.nomi_famiglie = nomi_famiglie
        self.nomi_elementi = nomi_elementi
    
    def generate_report(self, file_path):
        with pd.ExcelWriter(file_path, engine='openpyxl') as excel_writer:
            self._add_perc_famiglie_per_ricette(excel_writer)
            self._add_famiglia_per_perc_elemento(excel_writer)
            self._add_perc_elementi_per_ricette(excel_writer)
            self._add_consumi(excel_writer)
            self._add_distanze_dai_range(excel_writer)
    
    def _add_perc_famiglie_per_ricette(self, excel_writer):
        opt = self.optimizer
        rows = []
        for famiglia in range(opt.N_FAMIGLIE):
            row = [f"Famiglia {self.nomi_famiglie[famiglia]}"]
            for ricetta in range(opt.N_RICETTE):
                row.append(round(opt.perc_famiglie_per_ricette[famiglia][ricetta], 5))
            rows.append(row)
        headers = [""] + [f"Ricetta {self.nomi_ricette[ricetta]}" for ricetta in range(opt.N_RICETTE)]
        df_famiglie = pd.DataFrame(rows, columns=headers)
        df_famiglie.to_excel(excel_writer, sheet_name='Percentuali Famiglie', index=False)

    def _add_famiglia_per_perc_elemento(self, excel_writer):
        opt = self.optimizer
        rows = []
        for famiglia in range(opt.N_FAMIGLIE):
            row = [f"Famiglia {self.nomi_famiglie[famiglia]}"]
            for elemento in range(opt.N_elementi):
                row.append(round(opt.famiglia_per_perc_elemento[famiglia][elemento], 5))
            rows.append(row)
        headers = [""] + [f"{self.nomi_elementi[elemento]}" for elemento in range(opt.N_elementi)]
        df_famiglia = pd.DataFrame(rows, columns=headers)
        df_famiglia.to_excel(excel_writer, sheet_name='Famiglia per Elemento', index=False)

    def _add_perc_elementi_per_ricette(self, excel_writer):
        opt = self.optimizer
        rows = []
        for elemento in range(opt.N_elementi):
            row = [ self.nomi_elementi[elemento] ]
            for ricetta in range(opt.N_RICETTE):
                row.append(round(opt.perc_elementi_per_ricette[elemento][ricetta], 5))
            rows.append(row)
        headers = [""] + [f"Ricetta {self.nomi_ricette[ricetta]}" for ricetta in range(opt.N_RICETTE)]
        df_elementi = pd.DataFrame(rows, columns=headers)
        df_elementi.to_excel(excel_writer, sheet_name='Percentuali elementi', index=False)
    
    def _add_consumi(self, excel_writer):
        opt = self.optimizer
        rows = []
        for famiglia in range(opt.N_FAMIGLIE):
            row = [ f"Famiglia {self.nomi_famiglie[famiglia]}" ]
            for ricetta in range(opt.N_RICETTE):
                row.append(round(opt.consumi_famiglie_per_ricette[famiglia][ricetta], 5))
            rows.append(row)
        headers = [""] + [f"Ricetta {self.nomi_ricette[ricetta]}" for ricetta in range(opt.N_RICETTE)]
        df_consumi = pd.DataFrame(rows, columns=headers)
        df_consumi.to_excel(excel_writer, sheet_name='Consumi Famiglie', index=False)
    
    def _add_distanze_dai_range(self, excel_writer):
        opt = self.optimizer
        distanze = opt.get_all_dist_from_range()
        rows = []
        for elemento in range(opt.N_elementi):
            row = [ self.nomi_elementi[elemento] ]
            for ricetta in range(opt.N_RICETTE):
                row.append(round(distanze[elemento][ricetta], 5))
            rows.append(row)
        headers = [""] + [f"Ricetta {self.nomi_ricette[ricetta]}" for ricetta in range(opt.N_RICETTE)]
        df_range = pd.DataFrame(rows, columns=headers)
        df_range.to_excel(excel_writer, sheet_name='Distanza dai Range', index=False)
