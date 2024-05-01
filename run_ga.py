from param_est.ARORA_genetic_alg import ARORAGeneticAlg

if __name__ == "__main__":
    ga = ARORAGeneticAlg("param_est/param_est_4-25-24_rank_selection_top_10_parents_mate.json")
    ga.run_genetic_alg()
    ga.analyze_results()
    exit(0)
