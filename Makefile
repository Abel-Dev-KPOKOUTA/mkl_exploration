# Compilateur
CC = gcc

# Flags de compilation
CFLAGS = -O3 -Wall -Wextra -march=native -fopenmp
LDFLAGS = -lm -llapacke -llapack -lblas -lgfortran -fopenmp

# Cibles
TARGET = svd_compressor

# Fichiers sources
SOURCES = main.c image_io.c svd_compress.c
OBJECTS = $(SOURCES:.c=.o)
HEADERS = image_io.h svd_compress.h

# Cibles principales
.PHONY: all clean run help

all: $(TARGET)

# Compilation de l'exécutable
$(TARGET): $(OBJECTS)
	@echo "🔗 Édition des liens avec LAPACK/BLAS..."
	$(CC) $(OBJECTS) -o $(TARGET) $(LDFLAGS)
	@echo "✅ Compilation réussie: $(TARGET)"

# Compilation des fichiers objets
%.o: %.c $(HEADERS)
	@echo "🔨 Compilation de $<..."
	$(CC) $(CFLAGS) -c $< -o $@

# Vérification des bibliothèques
check-libs:
	@echo "🔍 Vérification des bibliothèques..."
	@echo -n "LAPACKE: "
	@if pkg-config --exists lapacke; then \
		echo "✅"; \
	else \
		echo "❌"; \
		echo "Installez avec: sudo apt-get install liblapacke-dev"; \
	fi
	@echo -n "BLAS: "
	@if pkg-config --exists blas; then \
		echo "✅"; \
	else \
		echo "❌"; \
		echo "Installez avec: sudo apt-get install libblas-dev"; \
	fi

# Exécution
run: $(TARGET)
	@echo "🚀 Exécution du programme..."
	@mkdir -p ../images/output ../results/data
	./$(TARGET)

# Nettoyage
clean:
	@echo "🧹 Nettoyage..."
	rm -f $(OBJECTS) $(TARGET)
	rm -f ../images/output/*.pgm
	rm -f ../results/data/*.csv
	@echo "✅ Nettoyage terminé"

# Test de performance
benchmark: $(TARGET)
	@echo "⏱️  Benchmark de performance avec BLAS/LAPACK..."
	@mkdir -p ../images/output ../results/data
	@echo "Taille: 256x256"
	@time ./$(TARGET) 2>&1 | grep "SVD calculée"
	@echo ""
	@echo "Taille: 512x512"
	@echo "Note: Modifiez main.c pour créer une image plus grande"

# Aide
help:
	@echo "╔══════════════════════════════════════════════════════════════╗"
	@echo "║     MAKEFILE - COMPRESSION SVD AVEC BLAS/LAPACK            ║"
	@echo "╚══════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "Cibles disponibles:"
	@echo "  make all         - Compiler le projet"
	@echo "  make check-libs  - Vérifier les bibliothèques"
	@echo "  make run         - Compiler et exécuter"
	@echo "  make clean       - Nettoyer"
	@echo "  make benchmark   - Test de performance"
	@echo "  make help        - Afficher cette aide"
	@echo ""
	@echo "Dépendances:"
	@echo "  sudo apt-get install liblapacke-dev liblapack-dev libblas-dev"
	@echo ""
	@echo "Exemples:"
	@echo "  make clean && make check-libs && make run"
	@echo "  OMP_NUM_THREADS=4 ./svd_compressor image.pgm"