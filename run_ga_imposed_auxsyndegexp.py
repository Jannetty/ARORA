from param_est.ARORA_genetic_alg_imposed_auxsyndegexport import ARORAGeneticAlgImposedAuxinSynDegExport

if __name__ == "__main__":
    ga = ARORAGeneticAlgImposedAuxinSynDegExport("PE_auxsyndegexp", out_dir="~/Desktop/GA_runs/", run_name="5")
    ga.run_genetic_alg()
    ga.analyze_results()
    exit(0)