%% BENCHMARK SVD - MATLAB vs C+MKL
function benchmark_svd_matlab()

    fprintf('=== BENCHMARK SVD MATLAB ===\n\n');

    % 1. Définir les tailles de matrices à tester
    sizes = [256, 512, 1024, 2048];  % Carrées
    % sizes = [500, 1000, 1500, 2000];  % Autres tailles

    % 2. Initialiser les résultats
    results = zeros(length(sizes), 2);  % [taille, temps_ms]

    % 3. Paramètres communs
    num_runs = 3;  % Nombre d'exécutions pour moyenne
    warmup = 1;    % Première exécution ignorée

    fprintf('┌──────────┬──────────────┬────────────┐\n');
    fprintf('│  Taille  │  Temps (ms)  │  Moyenne   │\n');
    fprintf('│  (n×n)   │  (meilleur)  │  (%d runs) │\n', num_runs);
    fprintf('├──────────┼──────────────┼────────────┤\n');

    for s_idx = 1:length(sizes)
        n = sizes(s_idx);

        % Générer une matrice aléatoire (reproductible)
        rng(42);  % Graine fixe pour reproductibilité
        A = randn(n, n);

        times = zeros(num_runs + warmup, 1);

        % Exécuter plusieurs fois
        for run = 1:(num_runs + warmup)
            tic;
            [U, S, V] = svd(A);
            elapsed = toc * 1000;  % en ms

            times(run) = elapsed;

            if run > warmup
                fprintf('│ %4d×%-4d │   %8.2f   │', n, n, elapsed);
                if run == warmup + 1
                    fprintf('            │\n');
                else
                    fprintf('    --      │\n');
                end
            end
        end

        % Calculer moyenne (sans warmup)
        avg_time = mean(times(warmup+1:end));
        results(s_idx, :) = [n, avg_time];

        % Afficher la moyenne
        fprintf('├──────────┼──────────────┼────────────┤\n');
        fprintf('│          │   MOYENNE    │  %8.2f  │\n', avg_time);
        fprintf('├──────────┼──────────────┼────────────┤\n');
    end

    fprintf('└──────────┴──────────────┴────────────┘\n\n');

    % 4. Sauvegarder les résultats
    csvwrite('matlab_benchmark.csv', results);

    % 5. Afficher le résumé
    fprintf('\n=== RÉSUMÉ DES PERFORMANCES MATLAB ===\n');
    for i = 1:size(results, 1)
        fprintf('  %4d×%-4d : %8.2f ms\n', results(i,1), results(i,1), results(i,2));
    end

    % 6. Visualisation rapide
    figure('Position', [100, 100, 600, 400]);
    bar(results(:,1), results(:,2), 'FaceColor', [0.2 0.4 0.8]);
    xlabel('Taille de la matrice (n×n)');
    ylabel('Temps (ms)');
    title('Performance SVD - MATLAB', 'FontSize', 14, 'FontWeight', 'bold');
    grid on;

    % Ajouter les valeurs sur les barres
    for i = 1:length(results(:,2))
        text(results(i,1), results(i,2)+max(results(:,2))*0.05, ...
             sprintf('%.1f ms', results(i,2)), ...
             'HorizontalAlignment', 'center', 'FontWeight', 'bold');
    end

    fprintf('\n✓ Résultats exportés: matlab_benchmark.csv\n');
end
