%% COMPRESSION D'IMAGES PAR SVD - VERSION MATLAB
% Comparaison avec l'implémentation C + MKL
%
% Auteurs: KPOKOUTA Abel, OUSSOUKPEVI Richenel, ANAHAHOUNDE A. Fredy
% UNSTIM - ENSGMM | Année 2025-2026

function svd_compress_matlab()

    fprintf('\n');
    fprintf('╔══════════════════════════════════════════════════════════════════╗\n');
    fprintf('║                                                                  ║\n');
    fprintf('║        COMPRESSION D''IMAGES PAR DÉCOMPOSITION SVD (MATLAB)      ║\n');
    fprintf('║                                                                  ║\n');
    fprintf('╚══════════════════════════════════════════════════════════════════╝\n\n');

    %% 1. Générer ou charger l'image
    fprintf('ÉTAPE 1/4: CHARGEMENT DE L''IMAGE\n');
    fprintf('═══════════════════════════════════\n\n');

    % Générer image de test (même que C)
    width = 256;
    height = 256;
    img = generate_test_image(width, height);

    fprintf('   ✓ Image générée: %d×%d pixels\n\n', height, width);

    %% 2. Calculer la SVD
    fprintf('ÉTAPE 2/4: DÉCOMPOSITION SVD\n');
    fprintf('═══════════════════════════════════\n\n');

    fprintf('   Calcul de la SVD...\n');
    tic;
    [U, S, V] = svd(img);
    elapsed_svd = toc;

    % Extraire les valeurs singulières
    singular_values = diag(S);

    fprintf('   ✓ SVD calculée en %.4f secondes\n', elapsed_svd);
    fprintf('   ✓ σ₁ = %.2f (plus grande)\n', singular_values(1));
    fprintf('   ✓ σ₁₀ = %.2f\n', singular_values(10));
    fprintf('   ✓ σ₅₀ = %.2f\n\n', singular_values(50));

    %% 3. Compression avec différentes valeurs de k
    fprintf('ÉTAPE 3/4: COMPRESSION AVEC DIFFÉRENTES VALEURS DE k\n');
    fprintf('═══════════════════════════════════════════════════════\n\n');

    k_values = [5, 10, 25, 50, 75, 100, 150, 200];

    fprintf('┌─────┬──────────┬───────────────┬──────────────┬──────────────┐\n');
    fprintf('│  k  │   PSNR   │  Compression  │   Énergie    │   Qualité    │\n');
    fprintf('│     │   (dB)   │     Ratio     │   Conservée  │              │\n');
    fprintf('├─────┼──────────┼───────────────┼──────────────┼──────────────┤\n');

    results = [];

    for i = 1:length(k_values)
        k = k_values(i);

        % Compression
        tic;
        img_compressed = compress_svd(U, S, V, k);
        time_compress = toc;

        % Métriques
        psnr_val = compute_psnr(img, img_compressed);
        ratio = compression_ratio(height, width, k);
        energy = energy_retained(singular_values, k);

        % Qualité
        if psnr_val < 25
            quality = 'Faible';
        elseif psnr_val < 30
            quality = 'Acceptable';
        elseif psnr_val < 35
            quality = 'Bonne';
        elseif psnr_val < 40
            quality = 'Très bonne';
        else
            quality = 'Excellente';
        end

        fprintf('│%4d │ %7.2f  │    %5.1f:1    │   %6.2f%%   │ %-12s │\n', ...
                k, psnr_val, ratio, energy, quality);

        % Stocker résultats
        results = [results; k, psnr_val, ratio, energy, time_compress];

        % Sauvegarder image
        filename = sprintf('C:/Users/Hp Elitebook/Desktop/mkl_exploration/matlab_compressed_k%03d.png', k);
        imwrite(uint8(img_compressed), filename);
    end

    fprintf('└─────┴──────────┴───────────────┴──────────────┴──────────────┘\n\n');

    %% 4. Analyse des valeurs singulières
    fprintf('ÉTAPE 4/4: ANALYSE DES VALEURS SINGULIÈRES\n');
    fprintf('═══════════════════════════════════════════════\n\n');

    fprintf('   Nombre total: %d\n\n', length(singular_values));
    fprintf('   Valeurs principales:\n');
    fprintf('   • σ₁   = %.2f\n', singular_values(1));
    fprintf('   • σ₅   = %.2f\n', singular_values(5));
    fprintf('   • σ₁₀  = %.2f\n', singular_values(10));
    fprintf('   • σ₂₅  = %.2f\n', singular_values(25));
    fprintf('   • σ₅₀  = %.2f\n', singular_values(50));
    fprintf('   • σ₁₀₀ = %.2f\n\n', singular_values(100));

    %% 5. Visualisation
    fprintf('ÉTAPE 5: GÉNÉRATION DES GRAPHIQUES\n');
    fprintf('═══════════════════════════════════\n\n');

    % Figure 1: Images comparatives
    figure('Position', [100, 100, 1400, 800]);

    subplot(2, 4, 1);
    imshow(uint8(img));
    title('Original', 'FontSize', 12, 'FontWeight', 'bold');

    for i = 1:7
        k = k_values(i);
        img_comp = compress_svd(U, S, V, k);
        psnr_val = compute_psnr(img, img_comp);

        subplot(2, 4, i+1);
        imshow(uint8(img_comp));
        title(sprintf('k=%d (PSNR=%.1f dB)', k, psnr_val), ...
              'FontSize', 10);
    end

    sgtitle('Compression SVD avec différentes valeurs de k', ...
            'FontSize', 14, 'FontWeight', 'bold');

    % Figure 2: Valeurs singulières
    figure('Position', [150, 150, 1200, 500]);

    subplot(1, 2, 1);
    semilogy(1:length(singular_values), singular_values, 'b-', 'LineWidth', 2);
    grid on;
    xlabel('Index i', 'FontSize', 12);
    ylabel('Valeur singulière σᵢ', 'FontSize', 12);
    title('Décroissance des valeurs singulières', 'FontSize', 14, 'FontWeight', 'bold');

    subplot(1, 2, 2);
    cumulative = cumsum(singular_values.^2) / sum(singular_values.^2) * 100;
    plot(1:length(cumulative), cumulative, 'r-', 'LineWidth', 2);
    hold on;
    yline(50, '--k', '50%');
    yline(90, '--k', '90%');
    yline(95, '--k', '95%');
    yline(99, '--k', '99%');
    grid on;
    xlabel('Nombre de valeurs k', 'FontSize', 12);
    ylabel('Énergie conservée (%)', 'FontSize', 12);
    title('Énergie cumulée', 'FontSize', 14, 'FontWeight', 'bold');
    ylim([0 105]);

    % Figure 3: PSNR vs Compression ratio
    figure('Position', [200, 200, 800, 600]);

    scatter(results(:, 3), results(:, 2), 100, 'filled', 'MarkerFaceColor', [0.2 0.4 0.8]);
    hold on;
    for i = 1:size(results, 1)
        text(results(i, 3) + 0.5, results(i, 2) + 1, ...
             sprintf('k=%d', results(i, 1)), 'FontSize', 10);
    end
    grid on;
    xlabel('Taux de compression', 'FontSize', 12);
    ylabel('PSNR (dB)', 'FontSize', 12);
    title('Qualité vs Compression', 'FontSize', 14, 'FontWeight', 'bold');

    fprintf('   ✓ Graphiques générés\n\n');

    %% 6. Sauvegarder les résultats
    csvwrite('../results/data/matlab_results.csv', results);
    fprintf('   ✓ Résultats exportés\n\n');

    fprintf('╔══════════════════════════════════════════════════════════════════╗\n');
    fprintf('║                    TRAITEMENT TERMINÉ!                           ║\n');
    fprintf('╚══════════════════════════════════════════════════════════════════╝\n\n');

    fprintf('Temps total SVD: %.4f secondes\n', elapsed_svd);
    fprintf('Images sauvegardées dans: ../images/output/\n\n');
end

%% Fonction: Générer image de test
function img = generate_test_image(width, height)
    img = zeros(height, width);
    cx = width / 2;
    cy = height / 2;
    max_dist = sqrt(cx^2 + cy^2);

    for y = 1:height
        for x = 1:width
            dx = x - cx;
            dy = y - cy;
            dist = sqrt(dx^2 + dy^2);

            % Motif: cercles + dégradé
            value = 128 + 127 * sin(dist / max_dist * 10 * pi);
            value = value + (x / width) * 50;

            img(y, x) = value;
        end
    end

    % Normaliser
    img = (img - min(img(:))) / (max(img(:)) - min(img(:))) * 255;
end

%% Fonction: Compresser avec k valeurs singulières
function img_compressed = compress_svd(U, S, V, k)
    % Garder seulement k premières valeurs
    S_k = S;
    S_k(k+1:end, k+1:end) = 0;

    % Reconstruction
    img_compressed = U * S_k * V';

    % Normaliser
    img_compressed = max(0, min(255, img_compressed));
end

%% Fonction: Calculer PSNR
function psnr_val = compute_psnr(original, compressed)
    mse = mean((original(:) - compressed(:)).^2);
    if mse < 1e-10
        psnr_val = 100;
    else
        psnr_val = 10 * log10((255^2) / mse);
    end
end

%% Fonction: Taux de compression
function ratio = compression_ratio(m, n, k)
    original_size = m * n;
    compressed_size = k * (m + n + 1);
    ratio = original_size / compressed_size;
end

%% Fonction: Énergie conservée
function energy_pct = energy_retained(singular_values, k)
    total_energy = sum(singular_values.^2);
    retained_energy = sum(singular_values(1:k).^2);
    energy_pct = (retained_energy / total_energy) * 100;
end
