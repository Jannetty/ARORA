from param_est.ARORA_genetic_alg import ARORAGeneticAlg

if __name__ == "__main__":
    init_parent_file = "param_est/test_first_gen.csv"
    ga = ARORAGeneticAlg(init_parent_file)
    print(ga.fitness_function(None, 0))
    exit(0)