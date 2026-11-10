import random
import time

class GeneticNQueens:
    def __init__(self, n=8, pop_size=100, max_iter=10000, crossover_rate=0.8, mutation_rate=0.2):
        self.n = n
        self.pop_size = pop_size
        self.max_iter = max_iter
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.population = []

    def fitness(self, individual):
        conflicts = 0
        for i in range(self.n):
            for j in range(i + 1, self.n):
                if individual[i] == individual[j]:
                    conflicts += 1
                elif abs(individual[i] - individual[j]) == abs(i - j):
                    conflicts += 1
        return conflicts

    def initialize_population(self):
        self.population = [[random.randint(0, self.n - 1) for _ in range(self.n)] for _ in range(self.pop_size)]

    def crossover(self, parent1, parent2):
        point = random.randint(1, self.n - 1)
        child1 = parent1[:point] + parent2[point:]
        child2 = parent2[:point] + parent1[point:]
        return child1, child2

    def mutate(self, individual):
        mutated = list(individual)
        col_to_change = random.randint(0, self.n - 1)
        new_val = random.randint(0, self.n - 1)
        mutated[col_to_change] = new_val
        return mutated

    def solve(self):
        self.initialize_population()
        
        for iteration in range(1, self.max_iter + 1):
            self.population.sort(key=self.fitness)
            best_fitness = self.fitness(self.population[0])

            if best_fitness == 0:
                return self.population[0], iteration

            new_offspring = []

            num_crossovers = int((self.pop_size * self.crossover_rate) // 2)
            for _ in range(num_crossovers):
                p1, p2 = random.sample(self.population, 2)
                c1, c2 = self.crossover(p1, p2)
                new_offspring.extend([c1, c2])

            num_mutations = int(self.pop_size * self.mutation_rate)
            for _ in range(num_mutations):
                ind = random.choice(self.population)
                mutated_ind = self.mutate(ind)
                new_offspring.append(mutated_ind)

            combined_population = self.population + new_offspring
            combined_population.sort(key=self.fitness)
            self.population = combined_population[:self.pop_size]

        return self.population[0], self.max_iter

    def print_board(self, individual):
        print(f"\nReprezentacja wektorowa: {individual}")
        print("Plansza:")
        for r in range(self.n):
            row_str = ""
            for c in range(self.n):
                row_str += " X " if individual[r] == c else " . "
            print(f"{r+1:2d} {row_str}")

if __name__ == "__main__":
    test_sizes = [4, 8, 16]
    
    for n in test_sizes:
        print(f"\n================ Uruchomienie dla N = {n} ================")
        ga = GeneticNQueens(n=n, pop_size=150, max_iter=20000, crossover_rate=0.8, mutation_rate=0.3)
        
        start_time = time.time()
        best_solution, iterations = ga.solve()
        execution_time = time.time() - start_time
        
        errors = ga.fitness(best_solution)
        
        print(f"Liczba iteracji: {iterations}")
        print(f"Czas wykonania: {execution_time:.4f} s")
        print(f"Liczba błędów (konfliktów): {errors}")
        
        if errors == 0:
            print("SUKCES: Znaleziono bezkonfliktowe rozwiązanie!")
            if n <= 16:
                ga.print_board(best_solution)
        else:
            print("PORAŻKA: Osiągnięto limit iteracji bez znalezienia idealnego rozwiązania.")
