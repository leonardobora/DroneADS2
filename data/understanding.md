Projeto Drone Unibrasil: Entendendo o Problema e a Solução
Fonte 1: Trechos de "Drone-UniBrasil-ADS2.pdf"
1. Visão Geral do Projeto e Objetivos: Esta seção apresenta um projeto hipotético de drone encarregado de mapear Curitiba usando um drone autônomo. Ela destaca o objetivo principal do drone: fotografar uma lista de códigos postais enquanto minimiza o tempo de voo e as paradas de recarga para reduzir os custos gerais.

2. Especificações do Drone e Restrições Operacionais: Esta seção detalha as características técnicas do drone, incluindo sua velocidade, vida útil da bateria, limitações operacionais e procedimentos de recarga. Ela enfatiza que o drone deve apenas pousar em coordenadas designadas para evitar perdas.

3. Fatores Ambientais e Cálculo de Custo: Esta seção apresenta variáveis ambientais, como velocidade e direção do vento, que impactam diretamente no tempo de voo e no consumo de bateria do drone. Ela também especifica o custo associado a cada pouso para recarga.

4. Requisitos de Solução e Formato de Saída: Esta seção esclarece o formato de saída requerido para o projeto. Ela manda um arquivo CSV detalhando o caminho de voo ótimo do drone, incluindo horários de partida e chegada, velocidade, coordenadas e informações de pouso para cada código postal.

5. Diretrizes de Implementação e Critérios de Avaliação: Esta seção fornece diretrizes detalhadas para implementar a solução, recomendando o uso de algoritmos de computação evolutiva, preferencialmente algoritmos genéticos. Ela também define os critérios de avaliação, abrangendo a qualidade do código, a cobertura de testes e a otimalidade da solução gerada.

6. Instruções de Submissão e Dinâmica de Equipe: Esta seção fornece instruções para submeter os entregáveis do projeto, enfatizando a importância da identificação adequada da equipe e a proibição de compartilhar arquivos entre equipes. Ela também sugere um fluxo de trabalho para dividir tarefas dentro da equipe.

Fonte 2: Trechos de "Explicação Básica Sobre Algoritmos Genéticos com Exemplo Prático"
1. Introdução a Algoritmos Genéticos e Inspiração: Esta seção apresenta algoritmos genéticos como técnicas de busca inspiradas na evolução darwiniana. Ela explica seu uso em problemas de otimização e destaca sua fundação nos princípios de seleção natural.

2. Conceitos Chave e Terminologia: Esta seção define termos cruciais como cromossomos, genes, indivíduos e populações dentro do contexto de algoritmos genéticos. Ela explica como esses elementos representam soluções e suas características.

3. O Problema do Caixeiro Viajante como uma Aplicação: Esta seção apresenta o Problema do Caixeiro Viajante como uma aplicação clássica de algoritmos genéticos. Ela destaca as limitações de abordagens de força bruta e demonstra como algoritmos genéticos oferecem soluções mais eficientes.

4. Características Centrais de Algoritmos Genéticos: Esta seção lista as características definidoras de algoritmos genéticos, incluindo sua dependência de codificação de solução, operações probabilísticas e a capacidade de operar sem conhecimento específico do problema.

5. Operação Passo a Passo de Algoritmos Genéticos: Esta seção detalha os passos sequenciais envolvidos em um algoritmo genético, abrangendo a inicialização da população, a avaliação de aptidão, a seleção, o crossover, a mutação e a natureza iterativa do processo.

6. Exemplo Ilustrativo: Resolvendo uma Equação Linear: Esta seção apresenta um exemplo prático de aplicação de um algoritmo genético para encontrar os pesos ótimos em uma equação linear. Ela fornece operadores específicos usados em cada etapa do algoritmo e ilustra o processo de solução.

7. Implementação e Resultados: Esta seção demonstra a implementação de código do problema da equação linear, destacando componentes-chave como cálculo de aptidão, seleção, crossover e mutação. Ela também apresenta a execução e os resultados, demonstrando a eficácia do algoritmo em convergir para a solução desejada.

Fonte 3: Trechos de "Introdução à IA: Algoritmos Genéticos em Python"
1. Introdução a Algoritmos Genéticos e Escopo de Aplicação: Esta seção apresenta algoritmos genéticos como uma técnica de computação evolutiva para encontrar soluções aproximadas para problemas de otimização. Ela esclarece que algoritmos genéticos são adequados para problemas onde encontrar a solução ótima em tempo polinomial é desafiador.

2. O Problema do Caixeiro Viajante como um Exemplo: Esta seção se concentra no Problema do Caixeiro Viajante como um exemplo ilustrativo para implementar algoritmos genéticos. Ela explica a definição do problema e destaca o objetivo de encontrar a rota mais curta possível.

3. Representando Indivíduos e Populações: Esta seção explica a representação de soluções dentro de um algoritmo genético. Ela define indivíduos como soluções potenciais codificadas como sequências de genes, representando cidades no contexto do Problema do Caixeiro Viajante.

4. Avaliação de Aptidão e Adaptação: Esta seção discute o conceito de aptidão, uma medida de como bem um indivíduo (uma possível solução) se sai no contexto do problema. Ela enfatiza que indivíduos com maior aptidão têm uma melhor chance de sobrevivência e reprodução.

5. Operadores Genéticos: Crossover e Mutação: Esta seção explica visualmente os processos de crossover e mutação. O crossover envolve a combinação de partes de dois indivíduos pais para criar descendentes, enquanto a mutação introduz mudanças aleatórias nos genes de um indivíduo.

6. Implementação do Algoritmo e Ajuste de Parâmetros: Esta seção apresenta a implementação do algoritmo genético usando a biblioteca DEAP. Ela discute as escolhas de parâmetros, incluindo o tamanho da população, as probabilidades de crossover e mutação, e o número de gerações.

7. Resultados e Análise: Esta seção apresenta os resultados de executar o algoritmo genético, mostrando o custo decrescente da rota ao longo das gerações. Ela discute a importância de evitar soluções inválidas e enfatiza o papel da mutação em manter a diversidade e encontrar soluções ótimas.

Fonte 4: Trechos de "coordenadas.pdf"
1. Estrutura do Conjunto de Dados: Esta fonte fornece um conjunto de dados em formato CSV. Ele compreende três colunas: "cep" (código postal), "longitude", e "latitude", representando as coordenadas geográficas associadas a cada código postal.

Esses dados servem como entrada para o Projeto Drone Unibrasil descrito em "Drone-UniBrasil-ADS2.pdf". Eles fornecem as informações de localização necessárias para cada código postal que o drone precisa fotografar.