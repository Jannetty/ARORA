from param_est.ARORA_genetic_alg_imposed_auxsyndegexport import ARORAGeneticAlgImposedAuxinSynDegExport

if __name__ == "__main__":
    ga = ARORAGeneticAlgImposedAuxinSynDegExport("PE_test")
    ga.run_genetic_alg()
    ga.analyze_results()
    exit(0)