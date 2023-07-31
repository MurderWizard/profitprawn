from deap import base, creator, tools, algorithms
import random
import numpy
import backtest2

class GeneticOptimizer:
    def __init__(self, individual_size, fitness_function, population_size, num_generations):
        self.individual_size = individual_size
        self.fitness_function = fitness_function
        self.population_size = population_size
        self.num_generations = num_generations

        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMax)

        self.toolbox = base.Toolbox()
        self.toolbox.register("attr_float", random.random)
        self.toolbox.register("individual", tools.initRepeat, creator.Individual, self.toolbox.attr_float, n=self.individual_size)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        self.toolbox.register("evaluate", self.fitness_function)
        self.toolbox.register("mate", tools.cxSimulatedBinaryBounded, eta=20.0, low=0.0, up=1.0)
        self.toolbox.register("mutate", tools.mutPolynomialBounded, eta=20.0, low=0.0, up=1.0, indpb=1.0/self.individual_size)
        self.toolbox.register("select", tools.selTournament, tournsize=3)

    def optimize(self):
        # Continue with the genetic algorithm optimization
        pop = self.toolbox.population(n=self.population_size)
        hof = tools.HallOfFame(1)
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", numpy.mean)
        stats.register("std", numpy.std)
        stats.register("min", numpy.min)
        stats.register("max", numpy.max)

        pop, logbook = algorithms.eaSimple(pop, self.toolbox, cxpb=0.5, mutpb=0.2, ngen=self.num_generations, stats=stats, halloffame=hof, verbose=True)

        return pop, logbook, hof

    def fitness_function(self, params):
        # Unpack the parameters
        (
            ema_short_period, ema_long_period,
            macd_short_period, macd_long_period,
            macd_signal_smoothing, rsi_period,
            rsi_upper, rsi_lower, support_columns,
            resistance_columns, margin, risk_per_trade,
            risk_reward_ratio, threshold
        ) = params

        # Initialize the Backtest with these parameters
        backtest = Backtest(
            ema_short_period=ema_short_period,
            ema_long_period=ema_long_period,
            macd_short_period=macd_short_period,
            macd_long_period=macd_long_period,
            macd_signal_smoothing=macd_signal_smoothing,
            rsi_period=rsi_period,
            rsi_upper=rsi_upper,
            rsi_lower=rsi_lower,
            support_columns=support_columns,
            resistance_columns=resistance_columns,
            margin=margin,
            risk_per_trade=risk_per_trade,
            risk_reward_ratio=risk_reward_ratio,
            threshold=threshold
        )

        # Run the backtest
        data = backtest.run()

        # Calculate the strategy's performance
        total_return, sortino_ratio, max_drawdown, win_rate, profit_factor = backtest.calculate_performance(data)

        # Return the performance as the fitness
        # We want to maximize total return and win rate, and minimize max drawdown
        fitness = total_return + win_rate - max_drawdown

        return fitness,

