%% ==========================================================================
%  Résolution de l'équation logistique par méthode de Runge-Kutta d'ordre 4
%  MATLAB Implementation
%% ==========================================================================
% 
% Équation différentielle : dy/dt = r*y*(1 - y/K)
% 
% Paramètres :
%   - y0 = 100    : Population initiale (bactéries)
%   - r  = 0.4    : Taux de croissance (h^-1)
%   - K  = 1000   : Capacité limite
%   - t  = [0,20] : Intervalle de temps (heures)
% 
% Utilisation :
%   >> logistic_rk4_matlab
%   ou
%   >> [y_final, temps] = logistic_rk4_matlab;
%
%% ==========================================================================

function [y_final, elapsed_time] = logistic_rk4_matlab()
    
    %% ======================================================================
    %  Paramètres du problème
    %% ======================================================================
    y0 = 100;           % Population initiale (bactéries)
    r = 0.4;            % Taux de croissance (h^-1)
    K = 1000;           % Capacité limite (bactéries)
    t0 = 0;             % Temps initial (heures)
    t_end = 20;         % Temps final (heures)
    n_steps = 10000;    % Nombre de pas de temps
    
    %% ======================================================================
    %  Initialisation
    %% ======================================================================
    h = t_end / n_steps;  % Pas de temps
    t = t0;               % Temps courant
    y = y0;               % Population courante
    
    %% ======================================================================
    %  Résolution numérique avec RK4
    %% ======================================================================
    fprintf('\nDémarrage de la simulation...\n');
    
    % Démarrage du chronomètre
    tic;
    
    % Boucle principale RK4
    for i = 1:n_steps
        % Calcul des 4 pentes k1, k2, k3, k4
        k1 = h * logistic_deriv(t, y, r, K);
        k2 = h * logistic_deriv(t + h/2, y + k1/2, r, K);
        k3 = h * logistic_deriv(t + h/2, y + k2/2, r, K);
        k4 = h * logistic_deriv(t + h, y + k3, r, K);
        
        % Mise à jour de y
        y = y + (k1 + 2*k2 + 2*k3 + k4) / 6;
        
        % Mise à jour du temps
        t = t + h;
    end
    
    % Arrêt du chronomètre
    elapsed_time = toc;
    
    %% ======================================================================
    %  Solution analytique
    %% ======================================================================
    y_exact = K / (1 + ((K - y0) / y0) * exp(-r * t_end));
    
    %% ======================================================================
    %  Calcul des erreurs
    %% ======================================================================
    error_abs = abs(y - y_exact);
    error_rel = error_abs / y_exact;
    
    %% ======================================================================
    %  Affichage des résultats
    %% ======================================================================
    fprintf('\n');
    fprintf('========================================================================\n');
    fprintf('    RÉSOLUTION DE L''ÉQUATION LOGISTIQUE - MÉTHODE RUNGE-KUTTA 4      \n');
    fprintf('========================================================================\n');
    fprintf('\n');
    fprintf('PARAMÈTRES DU PROBLÈME :\n');
    fprintf('  Population initiale (y0)  : %.1f bactéries\n', y0);
    fprintf('  Taux de croissance (r)    : %.2f h^-1\n', r);
    fprintf('  Capacité limite (K)       : %.1f bactéries\n', K);
    fprintf('  Intervalle de temps       : [%.1f, %.1f] heures\n', t0, t_end);
    fprintf('  Nombre de pas (n_steps)   : %d\n', n_steps);
    fprintf('  Pas de temps (h)          : %.6f heures\n', h);
    fprintf('\n');
    fprintf('------------------------------------------------------------------------\n');
    fprintf('RÉSULTATS À t = %.1f heures :\n', t_end);
    fprintf('------------------------------------------------------------------------\n');
    fprintf('  Solution numérique (RK4)  : %.10f bactéries\n', y);
    fprintf('  Solution analytique       : %.10f bactéries\n', y_exact);
    fprintf('\n');
    fprintf('------------------------------------------------------------------------\n');
    fprintf('ANALYSE DE L''ERREUR :\n');
    fprintf('------------------------------------------------------------------------\n');
    fprintf('  Erreur absolue            : %.2e\n', error_abs);
    fprintf('  Erreur relative           : %.2e (%.6f%%)\n', error_rel, error_rel * 100);
    fprintf('\n');
    fprintf('------------------------------------------------------------------------\n');
    fprintf('PERFORMANCES :\n');
    fprintf('------------------------------------------------------------------------\n');
    fprintf('  Temps d''exécution         : %.6f secondes\n', elapsed_time);
    fprintf('  Temps par itération       : %.2e secondes\n', elapsed_time / n_steps);
    fprintf('  Itérations par seconde    : %.2e\n', n_steps / elapsed_time);
    fprintf('\n');
    fprintf('========================================================================\n');
    fprintf('  Logiciel : MATLAB R%s\n', version('-release'));
    fprintf('========================================================================\n');
    fprintf('\n');
    
    %% ======================================================================
    %  Valeur de retour
    %% ======================================================================
    y_final = y;
    
end

%% ==========================================================================
%  Fonction dérivée de l'équation logistique
%% ==========================================================================
function dydt = logistic_deriv(t, y, r, K)
    % Calcul de dy/dt = r*y*(1 - y/K)
    dydt = r * y * (1 - y / K);
end

%% ==========================================================================
%  NOTES THÉORIQUES :
%% ==========================================================================
% 
% L'équation logistique de Verhulst modélise la croissance d'une population
% avec ressources limitées :
% 
%   dy/dt = r*y*(1 - y/K)
% 
% où :
%   - y(t) : population au temps t
%   - r    : taux de croissance intrinsèque
%   - K    : capacité de charge de l'environnement
% 
% Solution analytique :
% 
%   y(t) = K / (1 + ((K-y0)/y0) * exp(-r*t))
% 
% Méthode RK4 :
%   k1 = h * f(t_n, y_n)
%   k2 = h * f(t_n + h/2, y_n + k1/2)
%   k3 = h * f(t_n + h/2, y_n + k2/2)
%   k4 = h * f(t_n + h, y_n + k3)
%   y_{n+1} = y_n + (k1 + 2*k2 + 2*k3 + k4) / 6
% 
% Propriétés RK4 :
%   - Ordre 4 : erreur locale O(h^5)
%   - Erreur globale O(h^4)
%   - 4 évaluations de f par pas
% 
%% ==========================================================================
