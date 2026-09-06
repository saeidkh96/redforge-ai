from redforge import __version__
from redforge.repository import RepositoryScanner


def main() -> None:
    snapshot = RepositoryScanner().scan(".")
    print(
        {
            "version": __version__,
            "repository": snapshot.name,
            "files": snapshot.total_files,
            "project_types": snapshot.project_types,
            "frameworks": snapshot.frameworks,
            "dependencies": len(snapshot.dependencies.dependencies),
            "symbols": len(snapshot.symbols.symbols),
            "git_repository": bool(snapshot.git and snapshot.git.is_repository),
        }
    )


if __name__ == "__main__":
    main()
