from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ARQUIVO_CSV = "metricas_simulacao_anual.csv"
PASTA_SAIDA = "graficos_metricas"


def garantir_saida() -> Path:
    pasta = Path(PASTA_SAIDA)
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


def carregar_dados(caminho_csv: str) -> pd.DataFrame:
    df = pd.read_csv(caminho_csv)

    # Converte colunas numéricas
    df["tick"] = pd.to_numeric(df["tick"])
    df["ordens"] = pd.to_numeric(df["ordens"])
    df["transacoes"] = pd.to_numeric(df["transacoes"])
    df["volume"] = pd.to_numeric(df["volume"])
    df["preco_medio"] = pd.to_numeric(df["preco_medio"], errors="coerce")
    df["ultimo_preco"] = pd.to_numeric(df["ultimo_preco"], errors="coerce")

    return df


def salvar_grafico(fig: plt.Figure, caminho: Path) -> None:
    fig.savefig(caminho, bbox_inches="tight")
    plt.close(fig)


def grafico_ordens(df: pd.DataFrame, pasta_saida: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["tick"], df["ordens"])
    ax.set_title("Ordens por tick")
    ax.set_xlabel("Tick")
    ax.set_ylabel("Número de ordens")
    ax.grid(True, alpha=0.3)
    salvar_grafico(fig, pasta_saida / "ordens_por_tick.png")


def grafico_transacoes(df: pd.DataFrame, pasta_saida: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["tick"], df["transacoes"])
    ax.set_title("Transações por tick")
    ax.set_xlabel("Tick")
    ax.set_ylabel("Número de transações")
    ax.grid(True, alpha=0.3)
    salvar_grafico(fig, pasta_saida / "transacoes_por_tick.png")


def grafico_volume(df: pd.DataFrame, pasta_saida: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["tick"], df["volume"])
    ax.set_title("Volume financeiro por tick")
    ax.set_xlabel("Tick")
    ax.set_ylabel("Volume financeiro")
    ax.grid(True, alpha=0.3)
    salvar_grafico(fig, pasta_saida / "volume_por_tick.png")


def grafico_preco_medio(df: pd.DataFrame, pasta_saida: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["tick"], df["preco_medio"])
    ax.set_title("Preço médio das transações por tick")
    ax.set_xlabel("Tick")
    ax.set_ylabel("Preço médio")
    ax.grid(True, alpha=0.3)
    salvar_grafico(fig, pasta_saida / "preco_medio_por_tick.png")


def grafico_ultimo_preco(df: pd.DataFrame, pasta_saida: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["tick"], df["ultimo_preco"])
    ax.set_title("Último preço negociado por tick")
    ax.set_xlabel("Tick")
    ax.set_ylabel("Último preço")
    ax.grid(True, alpha=0.3)
    salvar_grafico(fig, pasta_saida / "ultimo_preco_por_tick.png")


def main() -> None:
    pasta_saida = garantir_saida()
    df = carregar_dados(ARQUIVO_CSV)

    grafico_ordens(df, pasta_saida)
    grafico_transacoes(df, pasta_saida)
    grafico_volume(df, pasta_saida)
    grafico_preco_medio(df, pasta_saida)
    grafico_ultimo_preco(df, pasta_saida)

    print("Gráficos gerados com sucesso em:")
    print(pasta_saida.resolve())


if __name__ == "__main__":
    main()
