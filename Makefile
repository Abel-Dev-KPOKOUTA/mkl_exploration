# Makefile pour le projet SVD
# Auteurs: KPOKOUTA Abel, OUSSOUKPEVI Richenel, ANAHAHOUNDE A. Fredy
# UNSTIM - ENSGMM | 2025-2026

# Compilateur
CC = gcc

# Flags de compilation
CFLAGS = -O3 -Wall -Wextra
LDFLAGS = -lm

# Flags MKL (si disponible)
MKL_AVAILABLE := $(shell command -v icc 2> /dev/null)
ifdef MKL_AVAILABLE
	CFLAGS += -I$(MKLROOT)/include -march=native -fopenmp
	LDFLAGS += -L$(MKLROOT)/lib/intel64 -lmkl_rt -lpthread -ldl
	TARGET = svd_mkl
else
	TARGET = svd_demo
endif

# Fichiers sources
SOURCES = main.c image_io.c svd_compress.c
OBJECTS = $(SOURCES:.c=.o)
HEADERS = image_io.h svd_compress.h

# Répertoires
SRCDIR = src
OUTDIR = images/output
DATADIR = results/data

# Cibles
.PHONY: all clean run help demo install-mkl

all: $(TARGET)

# Compilation de l'exécutable
$(TARGET): $(OBJECTS)
	@echo "🔗 Édition des liens..."
	$(CC) $(OBJECTS) -o $(TARGET) $(LDFLAGS)
	@echo "✅ Compilation réussie: $(TARGET)"

# Compilation des fichiers objets
%.o: %.c $(HEADERS)
	@echo "🔨 Compilation de $<..."
	$(CC) $(CFLAGS) -c $< -o $@

# Exécution
run: $(TARGET)
	@echo "🚀 Exécution du programme..."
	@mkdir -p ../$(OUTDIR) ../$(DATADIR)
	./$(TARGET)

# Démonstration avec image de test
demo: $(TARGET)
	@echo "📸 Démonstration avec image de test..."
	@mkdir -p ../$(OUTDIR) ../$(DATADIR)
	./$(TARGET)
	@echo ""
	@echo "📁 Résultats dans:"
	@echo "   - ../$(OUTDIR)/"
	@echo "   - ../$(DATADIR)/"

# Nettoyage
clean:
	@echo "🧹 Nettoyage..."
	rm -f $(OBJECTS) $(TARGET) svd_demo svd_mkl
	rm -f ../$(OUTDIR)/*.pgm
	rm -f ../$(DATADIR)/*.csv
	@echo "✅ Nettoyage terminé"

# Installation de MKL (Ubuntu/Debian)
install-mkl:
	@echo "📦 Installation d'Intel MKL..."
	@echo "⚠️  Cette commande nécessite sudo"
	wget -qO- https://apt.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS.PUB | sudo gpg --dearmor -o /usr/share/keyrings/oneapi-archive-keyring.gpg
	echo "deb [signed-by=/usr/share/keyrings/oneapi-archive-keyring.gpg] https://apt.repos.intel.com/oneapi all main" | sudo tee /etc/apt/sources.list.d/oneAPI.list
	sudo apt update
	sudo apt install -y intel-oneapi-mkl intel-oneapi-mkl-devel
	@echo "✅ MKL installé dans /opt/intel/oneapi/"
	@echo "⚡ Configurez l'environnement avec:"
	@echo "   source /opt/intel/oneapi/setvars.sh"

# Test avec différentes images
test: $(TARGET)
	@echo "🧪 Tests avec différentes tailles..."
	@mkdir -p ../$(OUTDIR) ../$(DATADIR)
	./$(TARGET)
	@echo "✅ Tests terminés"

# Benchmark de performance
benchmark: $(TARGET)
	@echo "⏱️  Benchmark de performance..."
	@mkdir -p ../$(OUTDIR) ../$(DATADIR)
	@echo "Exécution 1/5..."
	@./$(TARGET) > /dev/null
	@echo "Exécution 2/5..."
	@./$(TARGET) > /dev/null
	@echo "Exécution 3/5..."
	@./$(TARGET) > /dev/null
	@echo "Exécution 4/5..."
	@./$(TARGET) > /dev/null
	@echo "Exécution 5/5..."
	@time ./$(TARGET)

# Vérification de la configuration
check:
	@echo "🔍 Vérification de la configuration..."
	@echo ""
	@echo "Compilateur:"
	@$(CC) --version | head -1
	@echo ""
	@echo "MKL disponible:"
	@if [ -d "$(MKLROOT)" ]; then \
		echo "✅ Oui ($(MKLROOT))"; \
	else \
		echo "❌ Non - Installation nécessaire"; \
	fi
	@echo ""
	@echo "Flags de compilation:"
	@echo "  CFLAGS  = $(CFLAGS)"
	@echo "  LDFLAGS = $(LDFLAGS)"
	@echo ""

# Aide
help:
	@echo "╔══════════════════════════════════════════════════════════════╗"
	@echo "║          MAKEFILE - PROJET SVD COMPRESSION                  ║"
	@echo "╚══════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "Cibles disponibles:"
	@echo ""
	@echo "  make              - Compiler le projet"
	@echo "  make run          - Compiler et exécuter"
	@echo "  make demo         - Exécuter avec image de test"
	@echo "  make clean        - Nettoyer les fichiers générés"
	@echo "  make test         - Tester avec différentes images"
	@echo "  make benchmark    - Mesurer les performances"
	@echo "  make check        - Vérifier la configuration"
	@echo "  make install-mkl  - Installer Intel MKL (Ubuntu)"
	@echo "  make help         - Afficher cette aide"
	@echo ""
	@echo "Exemples:"
	@echo ""
	@echo "  make clean && make run"
	@echo "  make demo"
	@echo "  make check"
	@echo ""
	@echo "Variables d'environnement:"
	@echo ""
	@echo "  MKLROOT           - Chemin vers Intel MKL"
	@echo "  MKL_NUM_THREADS   - Nombre de threads (défaut: auto)"
	@echo ""
