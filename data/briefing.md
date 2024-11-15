Briefing Doc: Curitiba Drone Mapping Project
This document reviews the main themes and important information extracted from the provided sources concerning a hypothetical drone mapping project for the city of Curitiba, named "UNIBRASIL Maps".

Project Goal
The goal of the project is to plan the drone's flight path to photograph a list of postal codes (CEPs) in Curitiba and return to its origin (Unibrasil Campus), minimizing the total flight time and recharge stops.

Constraints and Requirements
Drone Capabilities:Base speed: 30 km/h
Maximum speed: 60 km/h (affected by wind)
Speed adjustments are in whole numbers.
Autonomy: 30 minutes (1800 seconds)
Requires 1-minute stop (60 seconds) for takeoff, landing, and photography at each location.
Operational Constraints:Flights only during daylight hours (06:00:00 - 19:00:00)
All data collection must be completed within 5 days.
Drone can only land at specified CEP coordinates.
Landing for recharge costs 60 reais.
Data:List of CEPs with corresponding latitudes and longitudes.
5-day wind speed and direction forecast.
Implementation:Evolutionary computation algorithm (preferably genetic algorithm) for path optimization.
Programming languages: Python or C# (natively compatible with Linux).
Output file: CSV format detailing the optimal flight path.
Evaluation Criteria:Correct calculation of distances, wind-affected speeds, battery consumption, and overall cost/time.
Clarity and organization of fitness function and genetic coding.
Validity and quality of the solution (optimized schedule and visitation order).
Code clarity, efficiency, and unit test coverage.
Key Concepts from Sources
Genetic Algorithms (GAs): The selected solution approach involves using GAs, a type of evolutionary algorithm inspired by natural selection, to find near-optimal solutions. This is particularly relevant due to the complex nature of the problem with numerous variables and constraints.
Excerpts from "Explicação Básica Sobre Algoritmos Genéticos com Exemplo Prático":"Genetic algorithms are a particular class of evolutionary algorithms that use techniques inspired by evolutionary biology, such as heredity, mutation, natural selection, and crossover."
"[GAs] are based on an encoding of the set of possible solutions and not on the parameters of the utilization."
"They do not require any derived knowledge of the problem, only a way to evaluate the result, and they use probabilistic transactions rather than deterministic rules."
Excerpts from "Introdução à IA: Algoritmos Genéticos em Python":"Genetic algorithms […] are a technique of evolutionary computation that serves to search for solutions to optimization problems […where] we do not have a guarantee that the solution we found is the optimal solution."
"The three main parts [of a GA] are selection, crossover, and mutation. […] the most apt individuals will have a greater chance of reproducing […]"
Implementation Considerations:
The provided documents offer guidance on the algorithm's implementation, including representing the flight path as a chromosome, using latitude/longitude to calculate distances, factoring wind effects on flight time, and defining the fitness function to minimize total time and recharge stops.
Excerpts from "Drone-UniBrasil-ADS2.pdf":
"Your implementation must generate an output file in CSV […] with the best solution found by your algorithm: [detailed column structure]"
"The calculation of flight time between one coordinate and another MUST be calculated in seconds and rounded up in the case of a fractional second."
"The drone's speed only allows adjustments to whole numbers. Wind can make the effective speed a fractional number, but the basis for battery consumption is the whole number calculated by the algorithm before applying the wind effect."
Excerpts from "Introdução à IA: Algoritmos Genéticos em Python":
"What happens is that in each iteration we will evaluate the aptitude, based on the aptitude there will be a selection, [and] the most suitable individuals will have a greater chance of undergoing crossover with other individuals and undergoing mutation."
"We can [improve the solution] by increasing the number of generations, increasing the probability of mutation, increasing the probability of crossover, [or] making more profound changes […]"
Additional Notes
The source "coordenadas.pdf" provides the necessary list of CEPs with their respective latitude and longitude coordinates.
The specific wind forecast data is not included in the provided sources.
Next Steps
Data Acquisition: Obtain the wind speed and direction data from Climatempo for the next 5 days.
Implementation: Develop the GA using Python or C#, integrating the provided constraints and data, and generating the required CSV output.
Testing and Validation: Thoroughly test the solution with unit tests ensuring validity and optimality of the generated flight path.
Documentation: Prepare a detailed report explaining the implementation, results, and analysis of the chosen solution.
This briefing document provides a starting point for the Unibrasil Drone Mapping Project. Successful execution will rely on careful consideration of the outlined constraints, efficient algorithm design, and thorough testing to ensure a valid and optimized solution is achieved.