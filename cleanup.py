import os
import shutil
import pathlib

def cleanup():
    print("🚀 Iniciando Limpeza Profunda do Sistema...")
    
    root_dir = pathlib.Path(__file__).parent.resolve()
    
    # 1. Remover __pycache__
    print("🧹 Removendo __pycache__...")
    for pycache in root_dir.rglob("__pycache__"):
        try:
            shutil.rmtree(pycache)
            print(f"   [OK] Removido: {pycache.relative_to(root_dir)}")
        except Exception as e:
            print(f"   [ERRO] Falha ao remover {pycache}: {e}")

    # 2. Limpar chroma_db
    chroma_dir = root_dir / "chroma_db"
    if chroma_dir.exists():
        print("🧹 Resetando ChromaDB...")
        try:
            shutil.rmtree(chroma_dir)
            os.makedirs(chroma_dir)
            print("   [OK] ChromaDB limpo.")
        except Exception as e:
            print(f"   [ERRO] Falha ao limpar ChromaDB: {e}")

    # 3. Remover arquivos .cache e logs temporários
    print("🧹 Removendo caches temporários...")
    cache_patterns = ["*.cache", ".pytest_cache", ".ruff_cache", ".mypy_cache"]
    for pattern in cache_patterns:
        for p in root_dir.rglob(pattern):
            try:
                if p.is_dir():
                    shutil.rmtree(p)
                else:
                    p.unlink()
                print(f"   [OK] Removido: {p.relative_to(root_dir)}")
            except Exception as e:
                print(f"   [ERRO] Falha ao remover {p}: {e}")

    print("\n✅ Limpeza concluída. Sistema pronto para reinicialização limpa.")

if __name__ == "__main__":
    cleanup()
